from django.db import models
import os

class Genre(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self, obj):
        return obj.name


def cover_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f"{instance.name} ({instance.year})/cover.{ext}"

def issue_file_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f"{instance.comic.name} ({instance.comic.year})/Vol {instance.volume}/{instance.comic.name} Vol.{instance.volume} #{instance.issue}.{ext}"


class Comic(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    cover = models.ImageField(upload_to=cover_path)
    year = models.IntegerField(null=True, blank=True)

    rac_link = models.URLField()
    watch = models.BooleanField(default=False)
    
    publisher = models.CharField(max_length=50)
    genres = models.ManyToManyField(Genre)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self, obj):
        return obj.name


class Issue(models.Model):
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, related_name="issues")
    name = models.CharField(max_length=255, blank=True, null=True)
    volume = models.IntegerField(default=1)
    issue = models.IntegerField()
    rac_link = models.URLField()
    
    file = models.FileField(upload_to=issue_file_path, blank=True, null=True)
    
    def __str__(self, obj):
        return f"{obj.comic.name} Vol.{obj.volume} #{instance.issue}.{ext}"

    class Meta:
        unique_together = ("comic", "volume", "issue")


