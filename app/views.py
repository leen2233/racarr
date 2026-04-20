from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "home.html")


def add_new(request):
    return render(request, "add_new.html")


def settings(request):
    return render(request, "settings.html")

