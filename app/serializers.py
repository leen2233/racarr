import re

from django.core.cache import cache
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.validators import ValidationError

from app.helpers import format_size
from app.models import Issue, Queue, Settings

HOSTNAME_REGEX = (
    r"^(localhost|(?=.{1,253}$)(?!-)(?:[A-Za-z0-9-]{1,63}\.)*[A-Za-z0-9-]{1,63})$"
)
PORT_REGEX = r"^(6553[0-5]|655[0-2]\d|65[0-4]\d{2}|6[0-4]\d{3}|[1-5]?\d{1,4})$"


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

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        # Delete cache key after update
        cache.delete(f"settings:proxy")
        return instance

    def validate_proxy_host(self, value):
        hostname_re = re.compile(HOSTNAME_REGEX)
        if value and not hostname_re.fullmatch(value):
            raise ValidationError("Please write in formats: 127.0.0.1")
        return value

    def validate_proxy_port(self, value):
        port_re = re.compile(PORT_REGEX)
        if value and not port_re.fullmatch(value):
            raise ValidationError("Port should be range in 1-65535")
        return value

    def validate(self, attrs):
        if attrs["use_proxy"]:
            # is use_proxy is true, hostname and port shouldn't be empty
            if (
                not attrs["proxy_host"]
                or not attrs["proxy_port"]
                or not attrs["proxy_type"]
            ):
                raise ValidationError(
                    "If use_proxy is True, proxy Type, Host and Port shouldn't be empty"
                )
        return super().validate(attrs)
