import base64
import logging

from google.cloud import storage

from settings.settings import (
    GCS_ACCOUNT_CREDENTIALS_FILE_PATH,
    GCS_BASE_DIR_NAME,
    GCS_BUCKET_NAME,
    GCS_FOLDER_NAME,
)

logger = logging.getLogger(__name__)


class GCSClient:
    GOOGLE_CLOUD_STORAGE_BASE_URL = "https://storage.googleapis.com"
    IMAGES_PREFIX = "id_"
    GCS_BUCKET = GCS_BUCKET_NAME
    GCS_FOLDER = GCS_FOLDER_NAME
    GCS_DIR = GCS_BASE_DIR_NAME
    gcp_client = storage.Client.from_service_account_json(GCS_ACCOUNT_CREDENTIALS_FILE_PATH)

    @classmethod
    def save_image(cls, image_b64: str, image_name: str, extension: str, content_type: str) -> str | None:
        try:
            image_bytes = base64.b64decode(image_b64)
            path = f"{cls.GCS_FOLDER}/{cls.GCS_DIR}/{cls.IMAGES_PREFIX}{image_name}.{extension}"
            bucket = cls.gcp_client.bucket(cls.GCS_BUCKET)
            blob = bucket.blob(path)
            blob.cache_control = "no-cache"
            blob.upload_from_string(image_bytes, content_type=content_type)
            blob.make_public()
            img_url = f"{cls.GOOGLE_CLOUD_STORAGE_BASE_URL}/{cls.GCS_BUCKET}/{path}"
            return img_url
        except Exception as e:
            logger.error(f"Failed to upload image: {e}", exc_info=True)
            return None
