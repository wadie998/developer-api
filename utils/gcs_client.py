import base64
import logging

from google.cloud import storage

from settings.settings import (
    GCS_ACCOUNT_CREDENTIALS_FILE_PATH,
    GCS_BASE_DIR_NAME,
    GCS_BUCKET_NAME,
    GCS_FOLDER_NAME,
    MINIO_IMAGES_PREFIX,
)

logger = logging.getLogger(__name__)


class GCSClient:
    MINIO_IMAGES_PREFIX = MINIO_IMAGES_PREFIX
    GCS_BUCKET = GCS_BUCKET_NAME
    GCS_FOLDER = GCS_FOLDER_NAME
    GCS_DIR = GCS_BASE_DIR_NAME

    def __init__(self):
        self.gcp_client = storage.Client.from_service_account_json(GCS_ACCOUNT_CREDENTIALS_FILE_PATH)

    def save_image(self, img_b64: str, image_name: str) -> str | None:
        logger.debug(f"Uploading image {image_name} to bucket {self.GCS_BUCKET} in folder {self.GCS_FOLDER}")
        try:
            if "," not in img_b64:
                raise ValueError("Invalid base64 string format")

            header_img, bare_img64 = img_b64.split(",")

            if header_img == "data:image/png;base64":
                extension = "png"
                content_type = "image/png"
            elif header_img in ("data:image/jpg;base64", "data:image/jpeg;base64"):
                extension = "jpg"
                content_type = "image/jpeg"
            else:
                raise ValueError(f"Unsupported image type: {header_img}")

            image_bytes = base64.b64decode(bare_img64)
            path = f"{self.GCS_FOLDER}/{self.GCS_DIR}/{self.MINIO_IMAGES_PREFIX}{image_name}.{extension}"

            bucket = self.gcp_client.bucket(self.GCS_BUCKET)
            blob = bucket.blob(path)
            blob.cache_control = "no-cache"
            blob.upload_from_string(image_bytes, content_type=content_type)
            blob.make_public()

            img_url = f"https://storage.googleapis.com/{self.GCS_BUCKET}/{path}"
            return img_url
        except Exception as e:
            logger.error(f"Failed to upload image: {e}", exc_info=True)
            return None
