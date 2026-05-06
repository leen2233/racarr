from django.urls import path
from .views import home, add_new, settings_page, discover, comic_detail_page
from .api import get_discover_data, search_remote, add_comic

urlpatterns = [
    path("", home, name="home"),
    path('add', add_new, name="add_new"),
    path('settings', settings_page, name="settings"),
    path('discover', discover, name="discover"),
    path('comic/<str:id>', comic_detail_page, name="comic-detail"),


    # API
    path('api/discover', get_discover_data),
    path('api/search-remote', search_remote),
    path('api/add-comic', add_comic),
]
