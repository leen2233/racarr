from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
import os

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
    # if discover data available at cache, directly pass to template
    context = {"discover_data": cache.get("discover-data")}

    return render(request, "discover.html", context=context)
