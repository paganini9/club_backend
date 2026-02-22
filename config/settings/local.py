"""
Django local (development) settings.
"""
from .base import *  # noqa: F401, F403

# ──────────────────────────────────────────────
# 디버그
# ──────────────────────────────────────────────
DEBUG = True

# ──────────────────────────────────────────────
# 데이터베이스 — 개발 중 SQLite 사용
# PostgreSQL 전환 시 아래 주석 해제 후 .env에 DATABASE_URL 설정
# ──────────────────────────────────────────────
# DATABASES = {
#     "default": env.db("DATABASE_URL"),  # noqa: F405
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# ──────────────────────────────────────────────
# 이메일 — 콘솔 백엔드 (개발용)
# ──────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ──────────────────────────────────────────────
# 파일 저장 — 로컬 (Phase 1)
# S3 전환 시 django-storages 설정으로 교체
# ──────────────────────────────────────────────
# DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
# AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
# AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
# AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="ap-northeast-2")
# AWS_S3_FILE_OVERWRITE = False
# AWS_DEFAULT_ACL = None

# ──────────────────────────────────────────────
# Django Debug Toolbar (선택)
# ──────────────────────────────────────────────
try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS = ["127.0.0.1"]
except ImportError:
    pass

# ──────────────────────────────────────────────
# DRF — 개발 중 BrowsableAPI 추가
# ──────────────────────────────────────────────
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] += [  # noqa: F405
    "rest_framework.renderers.BrowsableAPIRenderer",
]
