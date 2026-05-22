from celery import shared_task
from django.core.files.base import File
import os 

from .models import Queue
from app import sources # type: ignore

@shared_task
def downloader(queue_id):
    print("Processing queue: ", queue_id)

    queue = Queue.objects.get(id=queue_id)
    queue.set_status_downloading()

    try:
        source_instance = getattr(sources, queue.issue.source)
    except Exception:
        print("Unknown source: ", queue.issue.source)
        queue.set_status_error("Unknown Source")
        return
 
    path, error = source_instance.download(queue.issue.remote_id)
    if not path:
        queue.set_status_error(error)
        print("Error downloading: ", error)
        return
    
    # save issue file to issue object
    with open(path, "rb") as f:
        file_name = os.path.basename(path)
        queue.issue.file.save(file_name, File(f))

    queue.delete()

    return

