from logging import getLogger
from pathlib import Path
from time import time
import os
import sys

from django.conf import settings
from django.db import transaction
from django.core.management.base import BaseCommand

from jobs.models import ProcessingJob


class Command(BaseCommand):
    help = "Process the oldest job with status 'PENDING' using d3lta"

    def handle(self, *args, **options):
        start_time = time()
        logger = getLogger(__name__)

        with transaction.atomic():
            job = self.get_oldest_job()

            if not job:
                self.print_finish("Finished. No files to process", start_time)
                return

            job.start()


        self.print(f"Loaded {job.id} from database", start_time)

        try:
            preparation_start = time()

            from pandas import read_csv, isna # lazy import for faster startup time

            df = self.load_file(read_csv, job)
            self.validate_columns(job, df)
            csv_row_count, _ = df.shape
            df = self.get_data_sample(job, df)
            df = self.adjust_columns(job, df)
            truncated_item_count = self.truncate_content(job, df)
            self.print_prepared(job, df, csv_row_count, truncated_item_count, preparation_start)

            matches, clusters = self.process(job, df)
            cluster_ids = clusters["cluster"].unique()

            self.save_results(isna, job, matches, clusters, cluster_ids)
            job.delete_input_file()
            job.finish()

            self.print_finish(f"Finished processing {job.id}", start_time)

        except Exception as err:
            logger.exception(err)
            job.delete_input_file()
            job.delete_output_files()
            job.fail(str(err))
            self.print_error(f"Failed processing {job.id}. {err}", start_time)


    # -== Database operations ==-
    def get_oldest_job(self):
        return (
            ProcessingJob.objects
            .filter(status="PENDING")
            .order_by("created_at")
            .first()
        )


    # -== CSV operations ==-


    def load_file(self, pandas_read_csv, job):
        with job.file.open("rb") as f:
            return pandas_read_csv(f, delimiter=job.column_separator)


    def adjust_columns(self, job, df):
        """
            D3lta expects the data to be in a column named "original", and the index column to be a
            string. Here we adjust the input CSV to match the requirements.
        """
        df = df.rename(columns={job.doc_content: "original"})
        df.index = df.index.astype(str)

        return df


    def get_data_sample(self, job, df):
        if job.use_n_rows > 0 and job.use_n_rows < len(df):
            return df.sample(n=job.use_n_rows).copy()

        return df


    def truncate_content(self, job, df):
        if "original" not in df:
            return 0

        col = df["original"].astype(str)
        truncated_count = (col.str.len() > job.max_content_length).sum() # count the longer entries
        df["original"] = col.str[:job.max_content_length]

        return truncated_count



    def validate_columns(self, job, df):
        if job.doc_content not in df.columns:
            column_list = str(df.columns.tolist())
            raise ValueError(f"Missing content column: '{job.doc_content}' among: {column_list}")


    def process(self, job, df):
        """
            Processes the input dataframe for the given job. The STDERR hack is because TensorFlow
            prints unnecessary log messages that it cannot find and load CUDA drivers and libraries.
            We don't want to pollute the logs, so...

            For more info about "TF_CPP_MIN_LOG_LEVEL", see the link below:
            https://deepreg.readthedocs.io/en/latest/docs/logging.html#tensorflow-logging
        """
        semantic_faiss = None

        prev_tf_log_level = os.environ.get("TF_CPP_MIN_LOG_LEVEL")
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

        with SuppressStderr():
            from d3lta.faissd3lta import semantic_faiss # lazy import for stderr management

        if prev_tf_log_level is None:
            os.environ.pop("TF_CPP_MIN_LOG_LEVEL", None)
        else:
            os.environ["TF_CPP_MIN_LOG_LEVEL"] = prev_tf_log_level

        # end STDERR supression

        if semantic_faiss is None:
            raise ImportError("Failed to import d3lta semantic_faiss processor.")

        return semantic_faiss(
            df=df,
            # embeddings_to_save="realworld_embeddings",
            min_size_txt=job.min_size_txt,
            threshold_grapheme=job.threshold_grapheme,
            threshold_language=job.threshold_language,
            threshold_semantic=job.threshold_semantic
        )


    # -== Output operations ==-


    def save_results(self, pandas_isna, job, matches, clusters, cluster_ids):
        save_dir = Path(settings.MEDIA_ROOT) / settings.DOWNLOAD_DIR
        save_dir.mkdir(parents=True, exist_ok=True)

        # matches
        matches_filename = f"{job.id}_matches.csv"
        matches_path = save_dir / matches_filename
        matches.to_csv(matches_path, index=False)
        job.add_matches(matches_filename, matches_path.stat().st_size, matches.shape[0])

        # all clusters
        clusters_filename = f"{job.id}_clusters.csv"
        clusters_path = save_dir / clusters_filename
        clusters.to_csv(clusters_path, index=False)
        job.add_cluster("all", clusters_filename, clusters_path.stat().st_size, clusters.shape[0])

        # per-cluster results
        for cluster_id in cluster_ids:
            if pandas_isna(cluster_id):
                cluster_df = clusters[clusters["cluster"].isna()]
                cluster_slug = "none"
            else:
                cluster_df = clusters[clusters["cluster"] == cluster_id]
                cluster_slug = f"{cluster_id:g}"

            cluster_filename = f"{job.id}_cluster_{cluster_slug}.csv"
            cluster_path = save_dir / cluster_filename

            cluster_df.to_csv(cluster_path, index=False)
            job.add_cluster(cluster_slug, cluster_filename, cluster_path.stat().st_size, cluster_df.shape[0])



    # -== STDOUT/STDERR ==-


    def print(self, text, step_start_time, style=None):
        elapsed = time() - step_start_time

        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = elapsed % 60

        if hours > 0:
            time_str = f"{hours}h {minutes}m {seconds:.0f}s"
        elif minutes > 0:
            time_str = f"{minutes}m {seconds:.0f}s"
        elif seconds > 1:
            time_str = f"{seconds:.2f} sec"
        else:
            time_str = f"{(elapsed * 1000):.0f} ms"

        output = f"{text}. Took: {time_str}"

        if style is not None:
            output = style(output)

        self.stdout.write(output)


    def print_prepared(self, job, df, csv_rows, truncated_item_count, preparation_start):
        row_count, column_count = df.shape
        status = f"Loaded {row_count} / {csv_rows} rows and {column_count} columns of data"
        if truncated_item_count:
            status += f". Truncated {truncated_item_count} / {row_count} 'content' entries to {job.max_content_length} chars"
        self.print(status, preparation_start)


    def print_finish(self, text, start_time):
        self.print(text, start_time, lambda txt: self.style.SUCCESS(txt))


    def print_error(self, message, start_time):
        self.print(message, start_time, lambda txt: self.style.ERROR(txt))


class SuppressStderr:
    """
        Used to suppress unnecessary TensorFlow errors about missing CUDA libraries when running
        d3lta on CPU-only environments.
    """
    def __enter__(self):
        self.stderr_fd = sys.stderr.fileno()
        self.old_stderr = os.dup(self.stderr_fd)
        self.devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self.devnull, self.stderr_fd)

    def __exit__(self, exc_type, exc, tb):
        os.dup2(self.old_stderr, self.stderr_fd)
        os.close(self.old_stderr)
        os.close(self.devnull)
