"""
Django Docker environment settings.
PostgreSQL + MinIO + Redis 연동.
"""
from .base import *  # noqa: F401, F403

# ──────────────────────────────────────────────
# 데이터베이스 — PostgreSQL
# ──────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),  # noqa: F405
        "USER": env("POSTGRES_USER"),  # noqa: F405
        "PASSWORD": env("POSTGRES_PASSWORD"),  # noqa: F405
        "HOST": env("POSTGRES_HOST", default="db"),  # noqa: F405
        "PORT": env("POSTGRES_PORT", default="5432"),  # noqa: F405
        "CONN_MAX_AGE": 60,
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

# ──────────────────────────────────────────────
# 파일 저장 — MinIO (S3-compatible)
# ──────────────────────────────────────────────
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")  # noqa: F405
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")  # noqa: F405
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="club-uploads")  # noqa: F405
AWS_S3_ENDPOINT_URL = env("MINIO_ENDPOINT_URL")  # noqa: F405
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False
AWS_S3_URL_PROTOCOL = "http:"

# ──────────────────────────────────────────────
# Redis (Phase 3 Celery 대비)
# ──────────────────────────────────────────────
REDIS_URL = env("REDIS_URL", default="redis://redis:6379/0")  # noqa: F405

# Phase 3: Celery 설정 활성화
# CELERY_BROKER_URL = REDIS_URL
# CELERY_RESULT_BACKEND = REDIS_URL

# ──────────────────────────────────────────────
# 리버스 프록시 (Nginx) 헤더 설정
# ──────────────────────────────────────────────
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# ──────────────────────────────────────────────
# 이메일 — 콘솔 백엔드 (개발용)
# ──────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
