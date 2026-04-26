from django.shortcuts import render
from django.core.cache import cache


# Create your views here.
def home(request):
    return render(request, "home.html")


def add_new(request):
    return render(request, "add_new.html")


def settings(request):
    return render(request, "settings.html")


def discover(request):
    # if discover data available at cache, directly pass to template
    context = {"discover_data": cache.get("discover-data")}

    return render(request, "discover.html", context=context)
