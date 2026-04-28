from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
import os
from app import sources # type: ignore

# Create your views here.
def home(request):
    return render(request, "home.html")


def add_new(request):
    context = {
        "media_path": os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT)
    }
    return render(request, "add_new.html", context=context)


def settings_page(request):
    return render(request, "settings.html")


def discover(request):
    source = sources.default

    # if discover data available at cache, directly pass to template
    context = {"discover_data": cache.get(f"discover-data-{source}")}

    return render(request, "discover.html", context=context)
