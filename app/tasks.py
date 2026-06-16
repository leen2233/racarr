import os

from celery import shared_task
from django.core.files.base import File
from django_eventstream import send_event

from app import sources
from app.types import ProxyConfig  # type: ignore

from .models import Queue, Settings


@shared_task(acks_late=True)
def downloader(queue_id):
    print("Processing queue: ", queue_id)
    send_event(
        "messages", "message", {"text": f"Processing queue: {queue_id}", "type": "info"}
    )
    send_event(
        "activity",
        "message",
        {"queue_id": queue_id, "status": "downloading", "progress": 0},
    )

    queue = Queue.objects.get(id=queue_id)
    queue.set_status_downloading()

    try:
        source_instance = getattr(sources, queue.issue.source)
    except Exception:
        print("Unknown source: ", queue.issue.source)
        queue.set_status_error("Unknown Source")
        send_event(
            "activity",
            "message",
            {
                "queue_id": queue_id,
                "status": "error",
                "error": f"Unknown Source: {queue.issue.source}",
            },
        )
        return

    def report_progress(percentage: int):
        send_event(
            "activity",
            "message",
            {"queue_id": queue_id, "status": "downloading", "progress": percentage},
        )

    # check settings for proxy
    proxy_config = Settings.get_proxy_settings()

    path, error = source_instance.download(
        queue.issue.remote_id,
        proxy_config=proxy_config,
        progress_callback=report_progress,
    )
    if not path:
        queue.set_status_error(error)
        print("Error downloading: ", error)
        send_event(
            "messages",
            "message",
            {
                "text": f"Error downlaoding comic: {queue.issue}. See details at activity page",
                "type": "error",
            },
        )
        send_event(
            "activity",
            "message",
            {"queue_id": queue_id, "status": "error", "error_message": error},
        )
        return

    # save issue file to issue object
    with open(path, "rb") as f:
        file_name = os.path.basename(path)
        queue.issue.file.save(file_name, File(f))

    os.remove(path)

    print("Successfully downloaded comic: ", queue_id)
    send_event(
        "messages",
        "message",
        {"text": f"Successfully downloaded comic: {queue.issue}", "type": "info"},
    )
    send_event("activity", "message", {"queue_id": queue_id, "status": "completed"})
    queue.delete()
    return
