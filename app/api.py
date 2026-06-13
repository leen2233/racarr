from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import reverse, get_object_or_404
from rest_framework import status
from django.core.cache import cache
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django_eventstream import send_event
import requests

from app import sources # type: ignore
from app.models import Comic, Issue, Genre, Queue
from app.tasks import downloader
from app.serializers import IssueSerializer


@api_view(["GET"])
def get_discover_data(request):
    source = request.GET.get("source", sources.default)

    cache_key = f"discover-data-{source}"
    # if exists return from cache
    if cache.get(cache_key):
        return Response(cache.get(cache_key))

    try:
        source_instance = getattr(sources, source)
    except Exception:
        return Response({"error": "Unknown source"}, status=status.HTTP_400_BAD_REQUEST)

    result, error = source_instance.discover()

    if error:
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    result_json = []
    for item in result:
        result_json.append(item.serialize())

    # cache before returning
    cache.set(cache_key, result_json, 60 * 60)

    return Response(result_json)


@api_view(["GET"])
def search_remote(request):
    query = request.GET.get("query")
    source = request.GET.get("source", sources.default)

    cache_key = f"search-data-{query.replace(' ', '-')}-{source}"
    # if exists return from cache
    if cache.get(cache_key):
        return Response(cache.get(cache_key))

    try:
        source_instance = getattr(sources, source)
    except Exception:
        return Response({"error": "Source not found"}, status=status.HTTP_400_BAD_REQUEST)

    result, error = source_instance.search(query)

    if error:
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    result_json = []
    for item in result:
        result_json.append(item.serialize())

    # cache before returning
    cache.set(cache_key, result_json, 60 * 60)

    return Response(result_json)


@api_view(["POST", "DELETE"])
def comic(request):
    if request.method == "POST":
        id = request.data.get("id")
        source = request.data.get("source", sources.default)
        monitor = request.data.get("monitor", "all")
        format = request.data.get("format", "cbz")
        volume_folder = request.data.get("volume_folder", True)
        tags = request.data.get("tags", "")
        search_missing = request.data.get("search_missing", False)

        if Comic.objects.filter(remote_id=id, source=source).exists():
            comic_obj = Comic.objects.get(remote_id=id, source=source)
            view_comic_url = reverse("comic-detail", args=[comic_obj.id])
            return Response({"status": "already exists", "url": view_comic_url})

        try:
            source_instance = getattr(sources, source)
        except Exception:
            return Response({"error": "Source not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        comic, error = source_instance.get(id)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        comic_obj = Comic.objects.create(
                    name = comic.name,
                    description = comic.description,
                    year = comic.year,
                    remote_id = comic.id,
                    source = source,
                    publisher = comic.publisher,
                    monitor = monitor,
                    format = format,
                    volume_folder = volume_folder,
                    tags = tags
                )

        # save genres
        for item in comic.genres:
            genre, _ = Genre.objects.get_or_create(name=item)
            comic_obj.genres.add(genre)

        # save cover
        try:
            response = requests.get(comic.cover)
            if response.status_code == 200:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(response.content)
                img_temp.flush()
                comic_obj.cover.save("cover.jpg", File(img_temp), save=True)
            else:
                print(f"Couldn't download cover, response status code: {response.status_code}")
             
        except Exception as e:
            print(f"Couldn't download cover for comic, error: {e}")

        # save issues
        issues_to_save = []
        for item in comic.issues:
            issue = Issue(
                    comic = comic_obj,
                    name = item.name,
                    original_text = item.original_text,
                    volume = item.volume,
                    issue = item.issue,
                    is_annual = item.is_annual,
                    priority = item.priority,
                    remote_id = item.id,
                    source = source,
                    year = item.year,
                )
            issues_to_save.append(issue)
        
        Issue.objects.bulk_create(issues_to_save)

        if search_missing:
            print("search_missing is true")
            for issue in comic_obj.issues.all():
                queue, created = Queue.objects.get_or_create(issue=issue)
                if created:
                    downloader.delay_on_commit(queue.id)

        view_comic_url = reverse("comic-detail", args=[comic_obj.id])
        return Response({"status": "success", "url": view_comic_url})
    elif request.method == "DELETE":
        id = request.data.get("id")
        comic = get_object_or_404(Comic, id=id)
        comic.delete()
        return Response({"status": "success"})



@api_view(["POST"])
def download_issue(request):
    id = request.data.get("id")
    issue = get_object_or_404(Issue, id=id)

    queue, _ = Queue.objects.get_or_create(issue=issue)

    downloader.delay_on_commit(queue.id)    

    send_event("messages", "message", {"text": f"{queue.issue} added to queue", "type": "info"})
    return Response({"status": "success"})


@api_view(["POST"])
def search_all_missing(request):
    id = request.data.get("id")
    comic = get_object_or_404(Comic, id=id)

    new_added_counter = 0
    for issue in comic.issues.all():
        queue, added = Queue.objects.get_or_create(issue=issue)
        if added:
            new_added_counter += 1
            downloader.delay_on_commit(queue.id)

    send_event("messages", "message", {"text": f"{new_added_counter} issues added to queue", "type": "info"})
    return Response({"status": "success"})


@api_view(["POST"])
def retry_queue_item(request):
    id = request.data.get("id")

    queue = get_object_or_404(Queue, id=id)
    downloader.delay(queue.id)
    return Response({"status": "success"})


@api_view(["POST"])
def delete_queue_item(request):
    id = request.data.get("id")

    queue = get_object_or_404(Queue, id=id)
    queue.delete()
    return Response({"status": "success"})


class ListComicIssuesView(ListAPIView):
    serializer_class = IssueSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["original_text"]
    ordering_fields = ["priority", "original_text", "year", "volume", "issue", "file"]

    def get_queryset(self):
        comic = get_object_or_404(Comic, id=self.kwargs["comic_id"])
        return comic.issues.all()

