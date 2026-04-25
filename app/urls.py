from django.urls import path
from .views import home, add_new, settings, discover
from .api import get_discover_data, search_remote

urlpatterns = [
    path("", home, name="home"),
    path('add', add_new, name="add_new"),
    path('settings', settings, name="settings"),
    path('discover', discover, name="discover"),


    # API
    path('api/discover', get_discover_data),
    path('api/search-remote', search_remote),
]
