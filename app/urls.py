from django.urls import path, include
from .views import home, add_new, settings_page, discover, comic_detail_page, activity
from .api import get_discover_data, search_remote, comic, download_issue, search_all_missing
from .api import retry_queue_item, delete_queue_item

import django_eventstream

urlpatterns = [
    path("", home, name="home"),
    path('add', add_new, name="add_new"),
    path('settings', settings_page, name="settings"),
    path('discover', discover, name="discover"),
    path('activity', activity, name="activity"),
    path('comic/<str:id>', comic_detail_page, name="comic-detail"),


    # API
    path('api/discover', get_discover_data),
    path('api/search-remote', search_remote),
    path('api/comic', comic),
    path('api/download-issue', download_issue),
    path('api/search-all-missing', search_all_missing),
    path('api/retry-queue-item', retry_queue_item),
    path('api/delete-queue-item', delete_queue_item),

    path('api/events/', include(django_eventstream.urls), {"channels": ["messages"]}),
]
