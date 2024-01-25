from decouple import config

MINIO_MIGRATION_ENABLED = config("MINIO_MIGRATION_ENABLED", default=False, cast=bool)
MINIO_MIGRATED_BUCKETS = config("MINIO_MIGRATED_BUCKETS", cast=lambda v: [s.strip() for s in v.split(",")], default="")
MINIO_INTERNAL_STORAGE_ADDRESS = config("MINIO_INTERNAL_STORAGE_ADDRESS", default="")
MINIO_STORAGE_ADDRESS = config("MINIO_STORAGE_ADDRESS", default="")
MINIO_STORAGE_ACCESS_KEY = config("MINIO_STORAGE_ACCESS_KEY", default="")
MINIO_STORAGE_SECRET_KEY = config("MINIO_STORAGE_SECRET_KEY", default="")
MINIO_STORAGE_USE_HTTPS = config("MINIO_STORAGE_USE_HTTPS", default=True, cast=bool)
MINIO_INTERNAL_STORAGE_USE_HTTPS = config("MINIO_INTERNAL_STORAGE_USE_HTTPS", default=False, cast=bool)
