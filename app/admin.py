from django.contrib import admin

from app.models import Comic, Genre, Issue, Queue, Settings

# Register your models here.

admin.site.register(Genre)
admin.site.register(Comic)
admin.site.register(Issue)
admin.site.register(Queue)
admin.site.register(Settings)
