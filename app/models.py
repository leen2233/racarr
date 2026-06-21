import os
from dataclasses import asdict
from typing import Optional

from django.core.cache import cache
from django.db import models

from app.storage import PreserveSpacesStorage
from app.types import ProxyConfig


class Genre(models.Model):
    name = models.CharField(max_length=50)

    objects = models.Manager()

    def __str__(self):
        return str(self.name)


def cover_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f"{instance.name}/cover{ext}"


def issue_file_path(instance: "Issue", filename: str) -> str:
    ext = os.path.splitext(filename)[1]
    return f"{instance.comic.name}/Vol {instance.volume}/{instance.comic.name} Vol.{instance.volume} #{instance.issue}{ext}"  # type: ignore


class MonitorType(models.TextChoices):
    ALL = "all", "All Issues"
    FUTURE = "future", "Future Issues"
    PAST = "past", "Past Issues"
    FIRST_VOLUME = "first", "First Volume"
    LAST_VOLUME = "last", "Last Volume"
    NONE = "none", "None"


class Comic(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    cover = models.ImageField(upload_to=cover_path)
    year = models.IntegerField(null=True, blank=True)

    remote_id = models.TextField()
    source = models.CharField(max_length=255)

    publisher = models.CharField(max_length=50)
    genres = models.ManyToManyField(Genre)

    monitor = models.CharField(
        max_length=15, choices=MonitorType.choices, default="all"
    )
    format = models.CharField(max_length=20, default="cbz")
    volume_folder = models.BooleanField(default=True)  # type: ignore
    tags = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return str(self.name)

    class Meta:
        unique_together = ("remote_id", "source")


class Issue(models.Model):
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, related_name="issues")
    name = models.CharField(max_length=255, blank=True, null=True)
    original_text = models.CharField(max_length=255, blank=True, null=True)
    volume = models.IntegerField(default=1)  # type: ignore
    issue = models.FloatField(blank=True, null=True)
    is_annual = models.BooleanField(default=False)  # type: ignore
    priority = models.IntegerField(default=0)  # type: ignore
    year = models.IntegerField(null=True, blank=True)

    remote_id = models.TextField()
    source = models.CharField(max_length=255)

    file = models.FileField(upload_to=issue_file_path, blank=True, null=True, storage=PreserveSpacesStorage)  # type: ignore

    objects = models.Manager()

    def __str__(self):
        return f"{self.comic.name} Vol.{self.volume} #{self.issue}"

    class Meta:
        unique_together = ("comic", "original_text")


class Queue(models.Model):
    class Statuses(models.TextChoices):
        PENDING = "pending", "Pending"
        DOWNLOADING = "downloading", "Downloading"
        ERROR = "error", "Error"

    issue = models.OneToOneField(Issue, on_delete=models.CASCADE, related_name="queue")
    status = models.CharField(
        max_length=20, choices=Statuses.choices, default="pending"
    )
    priority = models.IntegerField(default=0)

    error_message = models.TextField(null=True, blank=True)
    next_try = models.DateTimeField(null=True, blank=True)  # if error, for timeout

    objects = models.Manager()

    def set_status_error(self, error: str):
        self.error_message = error
        self.status = Queue.Statuses.ERROR
        self.save()

    def set_status_downloading(self):
        self.status = Queue.Statuses.DOWNLOADING
        self.save()

    class Meta:
        ordering = ["-id"]


class Settings(models.Model):
    # Proxy Settings
    use_proxy = models.BooleanField(default=False)
    proxy_type = models.CharField(max_length=10, blank=True, null=True)
    proxy_host = models.CharField(max_length=255, blank=True, null=True)
    proxy_port = models.CharField(max_length=255, blank=True, null=True)
    proxy_username = models.CharField(max_length=255, blank=True, null=True)
    proxy_password = models.CharField(max_length=255, blank=True, null=True)

    objects = models.Manager()

    def save(
        self, *, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        cache.delete("settings:proxy")
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    @classmethod
    def get_or_create(cls):
        if cls.objects.count() > 0:
            return cls.objects.first()
        cls.objects.create()
        return cls.objects.first()

    @classmethod
    def get_proxy_settings(cls) -> Optional[ProxyConfig]:
        cached_data = cache.get("settings:proxy")
        if cached_data:
            if cached_data.get("skip_proxy"):
                return None
            return ProxyConfig(**cached_data)

        settings = cls.get_or_create()
        if (
            settings.use_proxy
            and settings.proxy_type
            and settings.proxy_host
            and settings.proxy_port
        ):
            proxy = ProxyConfig(
                type=settings.proxy_type,
                host=settings.proxy_host,
                port=settings.proxy_port,
                username=settings.proxy_username,
                password=settings.proxy_password,
            )
            cache.set("settings:proxy", asdict(proxy), 300)  # cache for 5 minutes
            return proxy

        cache.set("settings:proxy", {"skip_proxy": True}, 300)
        return None
