import django_eventstream
from django.urls import include, path

from .api import (
    ListComicIssuesView,
    SettingsUpdateView,
    comic,
    delete_queue_item,
    download_issue,
    get_discover_data,
    retry_queue_item,
    search_all_missing,
    search_remote,
)
from .views import activity, add_new, comic_detail_page, discover, home, settings_page

urlpatterns = [
    path("", home, name="home"),
    path("add", add_new, name="add_new"),
    path("settings", settings_page, name="settings"),
    path("discover", discover, name="discover"),
    path("activity", activity, name="activity"),
    path("comic/<str:id>", comic_detail_page, name="comic-detail"),
    # API
    path("api/discover", get_discover_data),
    path("api/search-remote", search_remote),
    path("api/comic", comic),
    path("api/comic/<str:comic_id>/issues", ListComicIssuesView.as_view()),
    path("api/download-issue", download_issue),
    path("api/search-all-missing", search_all_missing),
    path("api/retry-queue-item", retry_queue_item),
    path("api/delete-queue-item", delete_queue_item),
    path("api/settings", SettingsUpdateView.as_view()),
    # Events
    path(
        "api/events/notifications",
        include(django_eventstream.urls),
        {"channels": ["messages"]},
    ),
    path(
        "api/events/activity",
        include(django_eventstream.urls),
        {"channels": ["activity"]},
    ),
]
