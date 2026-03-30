import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .models import ProcessingJob
from .shortcuts import sort_clusters

DEFAULT_TITLE = "Task Status"
DEFAULT_NAV_ITEM = "jobs"


def index(request):
    context = {
        "nav_selected_item": DEFAULT_NAV_ITEM,
        "title": DEFAULT_TITLE
    }
    return render(request, "job_search.html", context)


def cluster_preview(request, job_id, cluster_id):
    cluster = None

    try:
        job_uuid = uuid.UUID(str(job_id)) # Validate UUID format first
        job = ProcessingJob.objects.get(id=job_uuid)
        cluster = job.clusters().get(data_id=cluster_id)
    except (ValueError, TypeError, ObjectDoesNotExist):
        pass

    if not cluster:
        return HttpResponse(status=404)

    return render(request, "job_cluster_preview.html", {"cluster": cluster})


def search(request):
    if request.method == "POST":
        return redirect("job_status", job_id=request.POST.get("job_id"))

    return redirect("jobs")


def status(request, job_id):
    context = {
        "nav_selected_item": DEFAULT_NAV_ITEM,
        "title": DEFAULT_TITLE,
    }

    try:
        job_uuid = uuid.UUID(str(job_id)) # Validate UUID format first
        job = ProcessingJob.objects.get(id=job_uuid)
    except (ValueError, TypeError, ObjectDoesNotExist):
        context["job_id"] = job_id
        context["status"] = None
        return render(request, "job_status.html", context, status=404)

    context["job_id"] = job.id
    context["status"] = job.status
    context["job"] = job

    return render(request, "job_status.html", context)


def status_minimal(request, job_id):
    try:
        job_uuid = uuid.UUID(str(job_id)) # Validate UUID format first
        job = ProcessingJob.objects.only('status').get(id=job_uuid)
    except (ValueError, TypeError, ObjectDoesNotExist):
        return HttpResponse(status=404)

    return HttpResponse(
        job.status,
        headers={
            "Content-Type": "text/plain",
            "Cache-Control": 'no-store',
        }
    )
