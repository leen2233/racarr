from rest_framework.serializers import ModelSerializer, SerializerMethodField

from app.helpers import format_size
from app.models import Issue, Queue, Settings


class QueueSerializerMinimized(ModelSerializer):
    class Meta:
        model = Queue
        fields = ["status", "priority"]


class IssueSerializer(ModelSerializer):
    filesize = SerializerMethodField()
    queue = SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            "id",
            "priority",
            "original_text",
            "year",
            "volume",
            "issue",
            "remote_id",
            "source",
            "filesize",
            "queue",
        ]

    def get_filesize(self, obj):
        if obj.file:
            filesize = obj.file.size
            return format_size(filesize)
        else:
            return 0

    def get_queue(self, obj):
        if hasattr(obj, "queue"):
            return QueueSerializerMinimized(obj.queue).data
        return None


class SettingsUpdateSerializer(ModelSerializer):
    class Meta:
        model = Settings
        fields = [
            "use_proxy",
            "proxy_type",
            "proxy_host",
            "proxy_port",
            "proxy_username",
            "proxy_password",
        ]
