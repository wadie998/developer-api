import logging
import mimetypes
from datetime import timedelta

import requests
from minio import Minio
from minio.error import InvalidResponseError, S3Error, ServerError

from settings.configs.media_manager_config import GcloudStorageClient
from settings.configs.minio_config import (
    ENV,
    GCLOUD_BUCKET,
    MINIO_INTERNAL_STORAGE_ADDRESS,
    MINIO_INTERNAL_STORAGE_USE_HTTPS,
    MINIO_MIGRATED_BUCKETS,
    MINIO_MIGRATION_ENABLED,
    MINIO_NEW_INTERNAL_STORAGE_ADDRESS,
    MINIO_NEW_INTERNAL_STORAGE_USE_HTTPS,
    MINIO_NEW_STORAGE_ACCESS_KEY,
    MINIO_NEW_STORAGE_ADDRESS,
    MINIO_NEW_STORAGE_SECRET_KEY,
    MINIO_NEW_STORAGE_USE_HTTPS,
    MINIO_STORAGE_ACCESS_KEY,
    MINIO_STORAGE_ADDRESS,
    MINIO_STORAGE_SECRET_KEY,
    MINIO_STORAGE_USE_HTTPS,
)

logger = logging.getLogger(__name__)


class BucketNames:
    DOCUMENT = "document"
    SIGNED_DOCUMENT = "signed-document"


class MediaManager:
    minio_client = Minio(
        MINIO_INTERNAL_STORAGE_ADDRESS,
        access_key=MINIO_STORAGE_ACCESS_KEY,
        secret_key=MINIO_STORAGE_SECRET_KEY,
        secure=MINIO_INTERNAL_STORAGE_USE_HTTPS,
    )
    public_minio_client = Minio(
        MINIO_STORAGE_ADDRESS,
        access_key=MINIO_STORAGE_ACCESS_KEY,
        secret_key=MINIO_STORAGE_SECRET_KEY,
        secure=MINIO_STORAGE_USE_HTTPS,
    )
    gcloud_client = GcloudStorageClient.getInstance()

    if MINIO_MIGRATION_ENABLED:
        new_minio_client = Minio(
            MINIO_NEW_INTERNAL_STORAGE_ADDRESS,
            access_key=MINIO_NEW_STORAGE_ACCESS_KEY,
            secret_key=MINIO_NEW_STORAGE_SECRET_KEY,
            secure=MINIO_NEW_INTERNAL_STORAGE_USE_HTTPS,
        )
        new_public_minio_client = Minio(
            MINIO_NEW_STORAGE_ADDRESS,
            access_key=MINIO_NEW_STORAGE_ACCESS_KEY,
            secret_key=MINIO_NEW_STORAGE_SECRET_KEY,
            secure=MINIO_NEW_STORAGE_USE_HTTPS,
        )

    @staticmethod
    def _get_public_minio_client(bucket_name):
        if MINIO_MIGRATION_ENABLED and bucket_name in MINIO_MIGRATED_BUCKETS:
            return MediaManager.new_public_minio_client
        return MediaManager.public_minio_client

    def _get_internal_minio_client(bucket_name):
        if MINIO_MIGRATION_ENABLED and bucket_name in MINIO_MIGRATED_BUCKETS:
            return MediaManager.new_minio_client
        return MediaManager.minio_client

    @staticmethod
    def get_from_media_server(bucket_name, object_name, save_path):
        """get_private_object
        :param bucket_name: the name of the bucket to get the object from
        :param object_name: the name of the object to get
        :param save_path: the path to save the file
        """
        try:
            if ENV == "STA":
                signed_url = MediaManager._get_public_minio_client(bucket_name).presigned_get_object(
                    bucket_name, object_name, expires=timedelta(days=1)
                )
                open(save_path, "wb").write(requests.get(signed_url).content)
            else:
                MediaManager._get_internal_minio_client(bucket_name).fget_object(bucket_name, object_name, save_path)
        except (InvalidResponseError, S3Error, ServerError) as err:
            logger.error("Couldn't get :%s from minio server error details: %s", object_name, err)
            raise Exception("Minio Server Error")

    @staticmethod
    def upload_to_media_server(bucket_name, object_name, file_path, content_type="application/octet-stream"):
        """
        :param bucket_name: the name of the bucket to get the object from
        :param object_name: the name of the object to get
        :param file_path: the path where to save the file
        :param content_type: the media type of the file.
        Note:
            For content_type, fill it accordingly:
            - png: image/png
            - jpeg/jpg: image/jpeg
            - other : application/octet-stream
        """
        try:
            MediaManager._get_internal_minio_client(bucket_name).fput_object(
                bucket_name, object_name, file_path, content_type=content_type
            )
        except (InvalidResponseError, S3Error, ServerError) as err:
            logger.error("Couldn't upload :%s from minio server error details: %s", object_name, err)
            raise Exception("Minio Server Error")

    @staticmethod
    def upload_content_to_media_server(bucket_name, object_name, content, insensitive=False):
        """
        :param bucket_name: the name of the bucket to get the object from
        :param object_name: the name of the object to get
        :param content: file content
        :param insensitive: by default false
        """
        try:
            if hasattr(content, "seek") and callable(content.seek):
                content.seek(0)
            if insensitive:
                MediaManager.gcloud_client.upload_object(GCLOUD_BUCKET, bucket_name + "/" + object_name, content)

            else:
                content_size, content_type = examine_file(object_name, content)
                MediaManager._get_internal_minio_client(bucket_name).put_object(
                    bucket_name, object_name, content, content_size, content_type
                )
        except (InvalidResponseError, S3Error, ServerError) as e:
            logger.error("Couldn't upload : %s  to minio server", object_name)
            raise Exception(e)

    @staticmethod
    def get_private_object(bucket_name, object_name, expires_in=timedelta(days=7)):
        """
        :param bucket_name: the name of the bucket to get the object from
        :param object_name: the name of the object to get
        :param expires_in: timedelta of the duration
        :return: the url of the file
        """
        try:
            return MediaManager._get_public_minio_client(bucket_name).presigned_get_object(
                bucket_name, object_name, expires=expires_in
            )
        except (InvalidResponseError, S3Error, ServerError) as err:
            logger.error("Couldn't generate url for :%s from minio server error details: %s", object_name, err)
            raise Exception("Minio Server Error")

    @staticmethod
    def delete_from_media_server(bucket_name, object_name, insensitive=False):
        """
        :param bucket_name: the name of the bucket to get the object from
        :param object_name: the name of the object to get
        :param insensitive: by default false
        """
        try:
            if insensitive:
                MediaManager.gcloud_client.delete_object(GCLOUD_BUCKET, bucket_name + "/" + object_name)
            else:
                MediaManager._get_internal_minio_client(bucket_name).remove_object(bucket_name, object_name)
        except (InvalidResponseError, S3Error, ServerError) as err:
            logger.error("Couldn't delete :%s from minio server error details: %s", object_name, err)
            raise Exception("Minio Server Error")

    @staticmethod
    def generate_presigned_upload_link(bucket_name, object_name, expires_in=timedelta(hours=1)):
        """
        :param bucket_name: the name of the bucket to upload the object to
        :param object_name: the name of the object in the bucket
        :param expires_in: by default 1 hour
        """
        try:
            return MediaManager._get_public_minio_client(bucket_name).presigned_put_object(
                bucket_name, object_name, expires_in
            )
        except (InvalidResponseError, S3Error, ServerError) as err:
            logger.error(
                "Couldn't generate presigned link for :(%s, %s) from minio server error details: %s",
                bucket_name,
                object_name,
                err,
            )
            raise Exception("Minio Server Error")


def examine_file(name, content):
    """Examines a file and produces information necessary for upload.
    Returns a tuple of the form (content_size, content_type,
    sanitized_name)
    """
    content_size = content.size
    content_type = mimetypes.guess_type(name, strict=False)
    content_type = content_type[0] or "application/octet-stream"
    return content_size, content_type
