"""Abstract file storage interface and factory."""

from abc import ABC, abstractmethod

from django.conf import settings


class FileStorage(ABC):
    """Abstract interface for file storage operations."""

    @abstractmethod
    def upload(self, filename: str, file_data: bytes, user_id: str) -> str:
        """
        Upload a file and return its URL/path.

        Args:
            filename: Original filename
            file_data: File contents as bytes
            user_id: User uploading the file

        Returns:
            URL or path to the uploaded file
        """
        pass

    @abstractmethod
    def get_url(self, file_key: str) -> str:
        """
        Get the URL for a stored file.

        Args:
            file_key: File identifier/key

        Returns:
            Full URL or path to the file
        """
        pass


def get_file_storage() -> FileStorage:
    """
    Factory function to get appropriate file storage based on environment.

    Returns:
        LocalFileStorage if IS_LOCAL_DEMO=true, else S3FileStorage
    """
    is_local_demo = settings.IS_LOCAL_DEMO if hasattr(settings, 'IS_LOCAL_DEMO') else False

    if is_local_demo:
        from local_app.implementations.local_file_storage import LocalFileStorage
        return LocalFileStorage()
    else:
        from cloud_app.implementations.s3_file_storage import S3FileStorage
        return S3FileStorage()
