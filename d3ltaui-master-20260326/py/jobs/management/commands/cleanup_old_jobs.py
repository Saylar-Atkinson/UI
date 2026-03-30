from datetime import timedelta
from subprocess import run

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from jobs.models import ProcessingJob


class Command(BaseCommand):
    BATCH_SIZE = settings.EXPIRE_JOBS_BATCH_SIZE
    MAX_AGE = settings.EXPIRE_JOBS_MAX_AGE_HOURS

    help = f"Expire completed jobs older than {MAX_AGE} hours (batch of {BATCH_SIZE}) or delete stale ones."


    def handle(self, *args, **options):
        self.expire_old()
        self.remove_stale_past()
        self.remove_stale_current()


    def expire_old(self):
        now = timezone.now()
        cutoff = now - timedelta(hours=self.MAX_AGE)

        queryset = (
            ProcessingJob.objects
            .filter(
                status__in=["DONE"],
                finished_at__isnull=False,
                finished_at__lte=cutoff,
            )
            .order_by("finished_at")  # oldest first
        )

        jobs = list(queryset[:self.BATCH_SIZE])
        total = len(jobs)

        if total == 0:
            return

        expired_count = 0

        for job in jobs:
            try:
                job.expire()
                expired_count += 1
                self.stdout.write(f"Expired job {job.id}")
            except Exception as ex:
                self.stderr.write(
                    self.style.ERROR(f"Failed to expire job {job.id}. {ex}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"Expired {expired_count}/{total} jobs older than {self.MAX_AGE} hours")
        )


    def remove_stale_past(self):
        queryset = (
            ProcessingJob.objects
            .filter(status__in=["PROCESSING"])
            .order_by("-started_at")
        )

        jobs = list(queryset[1:self.BATCH_SIZE])
        total = len(jobs)

        if total == 0:
            return

        aborted_count = 0

        for job in jobs:
            try:
                job.abort()
                aborted_count += 1
                self.stdout.write(f"Aborted crashed job {job.id}")
            except Exception as ex:
                self.stderr.write(
                    self.style.ERROR(f"Failed to abort job {job.id}. {ex}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"Aborted {aborted_count}/{total} jobs that have crashed in the past")
        )


    def remove_stale_current(self):
        current_job = ProcessingJob.objects.filter(status__in=["PROCESSING"]).order_by("-started_at").first()

        if current_job is None:
            return

        check_processing_cmd = "ps aux | grep process_jobs | grep -v grep"
        result = run(check_processing_cmd, shell=True, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            return

        try:
            current_job.abort()
            self.stdout.write(
                self.style.SUCCESS(f"Aborted current job {current_job.id} because it has crashed")
            )
        except Exception as ex:
            self.stderr.write(
                self.style.ERROR(f"Failed to abort current job {current_job.id}. {ex}")
            )
