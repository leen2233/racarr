from django.core.files.storage import FileSystemStorage


class PreserveSpacesStorage(FileSystemStorage):
    def get_valid_name(self, name):
        """
        Purpose of this inheriting is to avoid replacing space with underscores
        """
        return name
