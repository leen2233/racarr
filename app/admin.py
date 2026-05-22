from django.contrib import admin
from app.models import Genre, Comic, Issue, Queue

# Register your models here.

admin.site.register(Genre)
admin.site.register(Comic)
admin.site.register(Issue)
admin.site.register(Queue)

