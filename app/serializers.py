from rest_framework.serializers import ModelSerializer, SerializerMethodField
from app.models import Issue
from app.helpers import format_size

class IssueSerializer(ModelSerializer):
    filesize = SerializerMethodField()

    class Meta:
        model = Issue
        fields = ['priority', 'original_text', 'year', 'volume', 'issue', 
                  'filesize'] 

    def get_filesize(self, obj):
        if obj.file:
            filesize = obj.file.size
            return format_size(filesize)
        else:
            return 0
