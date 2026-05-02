from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
import os
from app import sources # type: ignore
from app.models import Comic

# Create your views here.
def home(request):
    return render(request, "home.html")


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


def view_comic_page(request, id):
    comic = Comic.objects.get(id=id)

    context = {
            "comic": comic,
            }

    return render(request, "view_comic.html", context=context)

