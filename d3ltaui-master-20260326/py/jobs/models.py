from pathlib import Path
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from .shortcuts import get_csv_preview, remove_file

# ------------------------------------------------------------------
# ProcessingJob
# ------------------------------------------------------------------

def upload_to(instance, original_name):
    if isinstance(original_name, str):
        suffix = Path(original_name).suffix
    else:
        suffix = ''

    path = Path(settings.UPLOAD_DIR) / f"{instance.id}.data{suffix}"
    return path.as_posix()


def validate_content_length(value):
    if value <= 0:
        raise ValidationError("The maximum content length must be a positive number.")


class ProcessingJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # File
    file = models.FileField(blank=True, null=True, upload_to=upload_to)
    original_file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()

    # Analysis parameters
    threshold_grapheme = models.FloatField()
    threshold_language = models.FloatField()
    threshold_semantic = models.FloatField()
    min_size_txt = models.PositiveIntegerField()

    # Analysis filters
    use_n_rows = models.PositiveIntegerField(default=0)
    max_content_length = models.PositiveIntegerField(
        default=settings.PROCESSING_CONTENT_LENGTH,
        validators=[validate_content_length]
    )

    # CSV options
    doc_content = models.TextField()
    column_separator = models.CharField(max_length=1, null=True, blank=True)

    # Processing
    status = models.CharField(
        max_length=20,
        default="PENDING",
        choices=[
            ("PENDING", "Pending"),
            ("PROCESSING", "Processing"),
            ("DONE", "Done"),
            ("EXPIRED", "Expired"),
            ("FAILED", "Failed"),
        ],
    )
    script_message = models.TextField(null=True, blank=True)

    # Lifecycle
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)


    class Meta:
        indexes = [
            models.Index(fields=["status", "finished_at"]),
            models.Index(fields=["status", "created_at"]),
        ]


    # ------------------------------------------------------------------
    # Result creation
    # ------------------------------------------------------------------

    def add_cluster(self, cluster_id, file_name, file_size=0, file_lines=0):
        sort_id = 2

        if cluster_id == "all":
            sort_id = 0

        if cluster_id == "none":
            sort_id = 1

        JobResult.objects.create(
            job=self,
            data_id=cluster_id,
            data_type="cluster",
            file_name=file_name,
            file_size=file_size,
            file_lines=file_lines,
            sort_id=sort_id,
        )


    def add_matches(self, file_name, file_size=0, file_lines=0):
        JobResult.objects.create(
            job=self,
            data_id=f"matches",
            data_type="match",
            file_name=file_name,
            file_size=file_size,
            file_lines=file_lines,
        )

    # ------------------------------------------------------------------
    # Result access helpers
    # ------------------------------------------------------------------

    def clusters(self):
        return self.results.filter(data_type="cluster").order_by("sort_id", "-file_size")

    def matches(self):
        return self.results.filter(data_type="match").first()

    # ------------------------------------------------------------------
    # File cleanup
    # ------------------------------------------------------------------

    def delete_input_file(self):
        if self.file:
            self.file.delete(save=False)
            self.file = None
            self.save(update_fields=["file"])

    def delete_output_files(self):
        self.results.all().delete()

        base_path = Path(settings.MEDIA_ROOT) / settings.DOWNLOAD_DIR
        for cluster_file in base_path.glob(f"{self.id}*.csv"):
            remove_file(cluster_file.as_posix())


    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self):
        self.status = "PROCESSING"
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at"])

    def finish(self):
        self.status = "DONE"
        self.finished_at = timezone.now()
        self.save(update_fields=["status", "finished_at"])

    def fail(self, message):
        self.status = "FAILED"
        self.script_message = message
        self.finished_at = timezone.now()
        self.save(update_fields=["status", "script_message", "finished_at"])

    def abort(self):
        if self.status != "PROCESSING":
            return

        with transaction.atomic():
            self.delete_output_files()
            self.delete_input_file()

            msg = "Job aborted because processing script has crashed."

            if self.script_message:
                self.script_message = f"{self.script_message} {msg}"
            else:
                self.script_message = msg

            self.status = "FAILED"
            self.finished_at = timezone.now()

            self.save(update_fields=["status", "script_message", "finished_at"])

    def expire(self):
        if self.status == "EXPIRED":
            return

        with transaction.atomic():
            self.delete_output_files()
            self.status = "EXPIRED"
            self.expired_at = timezone.now()
            self.save(update_fields=["status", "expired_at"])

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return self.original_file_name.__str__()


# ------------------------------------------------------------------
# JobResult
# ------------------------------------------------------------------

class JobResult(models.Model):
    job = models.ForeignKey(
        "ProcessingJob",
        related_name="results",
        on_delete=models.CASCADE
    )

    id = models.BigAutoField(primary_key=True)

    data_id = models.CharField(max_length=255)
    data_type = models.CharField(
        max_length=10,
        choices=[
            ("cluster", "Cluster"),
            ("match", "Match"),
        ]
    )

    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    file_lines = models.BigIntegerField()
    sort_id = models.SmallIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["job", "data_type"]),
        ]

    def path(self):
        return (
            Path(settings.MEDIA_ROOT)
            / settings.DOWNLOAD_DIR
            / self.file_name
        )

    def url(self):
        return f"{settings.MEDIA_DOWNLOAD_URL}{self.file_name}"

    def preview(self):
        return get_csv_preview(self.path().as_posix())

    def file_size_human(self):
        if self.file_size < 1024:
            return f"{self.file_size} bytes"

        if self.file_size < 1048576:
            return f"{self.file_size / 1024:.2f} kb"

        return f"{self.file_size / 1024 / 1024:.1f} Mb"


    def __str__(self):
        return f"{self.job_id}:{self.data_type}:{self.id}"
