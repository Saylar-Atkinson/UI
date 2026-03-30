from logging import getLogger

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.http import require_POST

from jobs.models import ProcessingJob
from .shortcuts import get_default_context, send_error, send_success

logger = getLogger(__name__)


def index(request):
    context = get_default_context()
    context["max_processing_length"] = settings.PROCESSING_MAX_CONTENT_LENGTH
    context["processing_length"] = settings.PROCESSING_CONTENT_LENGTH
    return render(request, "upload_form.html", context)


def invalid_input(request):
    context = get_default_context()
    context["invalid_input"] = True
    return render(request, "upload_result_failed.html", context, status=400)


def upload_failed(request):
    return render(request, "upload_result_failed.html", get_default_context(), status=400)


def save_failed(request, filename):
    context = get_default_context()
    context["invalid_file"] = filename
    return render(request, "upload_result_failed.html", context, status=500)


@require_POST
def accept_csv(request):
    is_json = "application/json" in request.headers.get("Accept", "")

    uploaded_file = request.FILES.get("csv_file")
    if not uploaded_file:
        return send_error(is_json, {}, 400)

    column_separator = request.POST.get("column_separator") or None
    if column_separator == "\\t":
        column_separator = "\t"

    if column_separator is not None:
        allowed_separators = {",", ";", "|", "\t"}
        if column_separator not in allowed_separators:
            logger.warning("Invalid column_separator received: %r", column_separator)
            return send_error(is_json, {"invalid_input": True}, 400)


    try:
        max_content_length = int(
            request.POST.get("truncate_size_txt") or settings.PROCESSING_CONTENT_LENGTH
        )
        if max_content_length <= 0:
            max_content_length = settings.PROCESSING_CONTENT_LENGTH

        max_content_length = min(settings.PROCESSING_MAX_CONTENT_LENGTH, max_content_length)


        job = ProcessingJob.objects.create(
            file=uploaded_file,
            original_file_name=uploaded_file.name,
            file_size=uploaded_file.size,

            threshold_grapheme=float(request.POST["threshold_grapheme"]),
            threshold_language=float(request.POST["threshold_language"]),
            threshold_semantic=float(request.POST["threshold_semantic"]),
            min_size_txt=int(request.POST["min_size_txt"]),

            doc_content=request.POST["doc_content"].strip(),

            # optional
            column_separator=column_separator,
            max_content_length=max_content_length,
            use_n_rows=int(request.POST.get("use_n_rows") or 0)
        )
    except (KeyError, ValueError, TypeError) as err:
        logger.exception(err)
        return send_error(is_json, { "invalid_input": True }, 400)
    except Exception as err:
        logger.exception(err)
        return send_error(is_json, { "invalid_file": uploaded_file.name }, 500)

    return send_success(is_json, {"job_id": job.id})
