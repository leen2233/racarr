from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
import os
from app import sources # type: ignore
from app.models import Comic, Queue
from app.helpers import get_dir_size

# Create your views here.
def home(request):
    comics = Comic.objects.all()
    for comic in comics:
        comic.total_count = comic.issues.count()
        comic.downloaded_count = comic.issues.exclude(file="").exclude(file=None).count()

    context = {"comics": comics}

    return render(request, "home.html", context=context)


def add_new(request):    
    default_source = request.GET.get("source", sources.default)
    query = request.GET.get("query", "")

    sources_obj = [
        {
            "name": getattr(sources, source).NAME, 
            "id": source,
            "selected": source == default_source,
        }
        for source in sources.__all__
    ]

    cache_key = f"search-data-{query.replace(' ', '-')}-{default_source}"

    context = {
        "media_path": os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT),
        "search_results": cache.get(cache_key),
        "sources": sources_obj,
        "default_source": default_source,
        "query": query
    }
    print("query: " ,query)
    return render(request, "add_new.html", context=context)


def settings_page(request):
    return render(request, "settings.html")


def discover(request):
    default_source = request.GET.get("source", sources.default)

    sources_obj = [
        {
            "name": getattr(sources, source).NAME, 
            "id": source,
            "selected": source == default_source, # make default source or selected source at query selected by default
        }
        for source in sources.__all__
    ]

    # if discover data available at cache, directly pass to template
    context = {
        "discover_data": cache.get(f"discover-data-{default_source}"),
        "sources": sources_obj,
        "default_source": default_source
    }

    return render(request, "discover.html", context=context)


def comic_detail_page(request, id):
    comic = Comic.objects.get(id=id)
    comic.folder = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT, comic.name)
    comic.folder_size = get_dir_size(comic.folder)

    context = {
        "comic": comic,
    }

    return render(request, "comic_detail.html", context=context)


def activity(request):
    queue = Queue.objects.all()
    context = {
            "queue": queue
    }
    return render(request, "activity.html", context=context)

