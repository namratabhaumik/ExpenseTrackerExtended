"""Local file storage implementation for development."""

import logging
import uuid

from auth_app.services.file_service import FileStorage

logger = logging.getLogger(__name__)


class LocalFileStorage(FileStorage):
    """Local file storage for development (no actual file persistence)."""

    def upload(self, filename: str, file_data: bytes, user_id: int) -> str:
        """
        Mock file upload for local development.

        In local mode, returns a mock URL without actually storing the file.

        Args:
            filename: Original filename
            file_data: File contents as bytes
            user_id: User uploading the file

        Returns:
            Mock file URL
        """
        try:
            # Generate a mock URL
            file_id = str(uuid.uuid4())
            user_id_str = str(user_id)
            mock_url = f'http://localhost:8000/mock-files/{user_id_str}/{file_id}'

            logger.info(
                f'Mock file upload for user {user_id}: {filename} -> {mock_url}'
            )

            return mock_url

        except Exception as e:
            logger.error(f'Unexpected error during file upload: {str(e)}', exc_info=True)
            raise

    def get_url(self, file_key: str) -> str:
        """
        Get the mock URL for a file.

        Args:
            file_key: File identifier/key

        Returns:
            Mock file URL
        """
        return f'http://localhost:8000/mock-files/{file_key}'
