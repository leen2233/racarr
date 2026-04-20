from django.urls import path
from .views import home, add_new, settings

urlpatterns = [
    path("", home, name="home"),
    path('add', add_new, name="add_new"),
    path('settings', settings, name="settings"),
]
