import re

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel


def _sanitize_path_segment(name):
    """디렉토리명에 사용할 수 없는 문자를 제거/치환."""
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = re.sub(r"[\s_]+", "_", name).strip("_")
    return name or "unknown"


def upload_to(instance, filename):
    """
    파일 저장 경로 자동 생성.

    형식: {year}/{club_name}/{category}/{filename}
    예시: 2026/스타트업동아리A/RECEIPT/영수증_001.jpg

    club이 없으면 no_club 디렉토리에 저장.
    """
    year = timezone.now().strftime("%Y")
    club_name = (
        _sanitize_path_segment(instance.club.name) if instance.club else "no_club"
    )
    category = instance.category or "GENERAL"
    return f"{year}/{club_name}/{category}/{filename}"


class UploadedFile(BaseModel):
    """업로드 파일 모델 — 프론트엔드 UploadedFile 타입 대응."""

    class Category(models.TextChoices):
        RECEIPT = "RECEIPT", "영수증"
        REPORT = "REPORT", "보고서"
        INSPECTION = "INSPECTION", "점검"
        ACHIEVEMENT = "ACHIEVEMENT", "성과물"
        GENERAL = "GENERAL", "일반"

    file = models.FileField("파일", upload_to=upload_to)
    original_name = models.CharField("원본 파일명", max_length=255)
    size = models.PositiveIntegerField("파일 크기 (bytes)")
    mime_type = models.CharField("MIME 타입", max_length=100)
    category = models.CharField(
        "카테고리",
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL,
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_files",
        verbose_name="업로더",
    )
    club = models.ForeignKey(
        "clubs.Club",
        on_delete=models.CASCADE,
        related_name="files",
        verbose_name="동아리",
        null=True,
        blank=True,
    )
    # Phase 3에서 AI OCR 결과를 저장할 필드
    ocr_result = models.JSONField(
        "OCR 결과",
        null=True,
        blank=True,
        help_text="Phase 3 AI OCR 처리 결과 (JSON)",
    )

    class Meta:
        verbose_name = "업로드 파일"
        verbose_name_plural = "업로드 파일"
        ordering = ["-created_at"]

    def __str__(self):
        return self.original_name
