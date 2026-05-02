from django.db import models
import os


class Genre(models.Model):
    name = models.CharField(max_length=50)

    objects = models.Manager()

    def __str__(self):
        return str(self.name)


def cover_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f"{instance.name} ({instance.year})/cover.{ext}"


def issue_file_path(instance: "Issue", filename: str) -> str:
    ext = os.path.splitext(filename)[1]
    return f"{instance.comic.name} ({instance.comic.year})/Vol {instance.volume}/{instance.comic.name} Vol.{instance.volume} #{instance.issue}.{ext}"  # type: ignore


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

    monitor = models.CharField(max_length=15, choices=MonitorType.choices, default="all")
    format = models.CharField(max_length=20, default="cbz") 
    volume_folder = models.BooleanField(default=True) # type: ignore
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
    is_annual = models.BooleanField(default=False) # type: ignore
    priority = models.IntegerField(default=0) # type: ignore
    year = models.IntegerField(null=True, blank=True)

    remote_id = models.TextField()
    source = models.CharField(max_length=255)

    file = models.FileField(upload_to=issue_file_path, blank=True, null=True)  # type: ignore

    objects = models.Manager()

    def __str__(self):
        return f"{self.comic.name} Vol.{self.volume} #{self.issue}"

    class Meta:
        unique_together = ("comic", "original_text")
