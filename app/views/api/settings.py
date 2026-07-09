from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from app.models import Settings
from app.serializers import SettingsUpdateSerializer


class SettingsUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SettingsUpdateSerializer

    def get_object(self):
        return Settings.get_or_create()
