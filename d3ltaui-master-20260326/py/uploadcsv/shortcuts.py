from django.http import JsonResponse
from django.shortcuts import redirect


def get_default_context():
    return {
        "nav_selected_item": "uploadcsv",
        "title": "Upload CSV"
    }


def send_error(json, context, status_code):
    if json:
        return JsonResponse(context, status=status_code)

    if context.get("invalid_file"):
        return redirect("save_csv_failed", filename=context.get("invalid_file"))

    if context.get("invalid_input"):
        return redirect("upload_form_invalid")

    return redirect("upload_csv_failed")


def send_success(json, context):
    if json:
        return JsonResponse(context)

    return redirect("job_status", job_id=context.get("job_id"))
