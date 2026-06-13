from rest_framework.serializers import ModelSerializer, SerializerMethodField
from app.models import Issue, Queue
from app.helpers import format_size


class QueueSerializerMinimized(ModelSerializer):
    class Meta:
        model = Queue
        fields = ["status", "priority"] 

class IssueSerializer(ModelSerializer):
    filesize = SerializerMethodField()
    queue = SerializerMethodField()

    class Meta:
        model = Issue
        fields = ['id', 'priority', 'original_text', 'year', 'volume', 'issue', 
                  'remote_id', 'source', 'filesize', 'queue']

    def get_filesize(self, obj):
        if obj.file:
            filesize = obj.file.size
            return format_size(filesize)
        else:
            return 0

    def get_queue(self, obj):
        if hasattr(obj, 'queue'):
            return QueueSerializerMinimized(obj.queue).data
        return None

