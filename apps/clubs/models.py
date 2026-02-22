from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class Club(BaseModel):
    """동아리 모델 — 프론트엔드 Club 타입 대응."""

    class Phase(models.TextChoices):
        RECRUITING = "RECRUITING", "모집 중"
        SELECTED = "SELECTED", "선발 완료"
        OPERATING = "OPERATING", "운영 중"
        COMPLETED = "COMPLETED", "완료"

    name = models.CharField("동아리명", max_length=100)
    description = models.TextField("설명", blank=True, default="")
    logo = models.ImageField(
        "로고",
        upload_to="clubs/logos/",
        null=True,
        blank=True,
    )
    phase = models.CharField(
        "단계",
        max_length=20,
        choices=Phase.choices,
        default=Phase.OPERATING,
    )

    class Meta:
        verbose_name = "동아리"
        verbose_name_plural = "동아리"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class ClubMember(models.Model):
    """동아리 멤버 — 프론트엔드 ClubMember 타입 대응."""

    class MemberRole(models.TextChoices):
        LEADER = "LEADER", "리더"
        MEMBER = "MEMBER", "멤버"

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name="동아리",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="club_memberships",
        verbose_name="사용자",
    )
    role = models.CharField(
        "멤버 역할",
        max_length=10,
        choices=MemberRole.choices,
        default=MemberRole.MEMBER,
    )
    joined_at = models.DateTimeField("가입일시", auto_now_add=True)

    class Meta:
        verbose_name = "동아리 멤버"
        verbose_name_plural = "동아리 멤버"
        unique_together = ("club", "user")
        ordering = ["-joined_at"]

    def __str__(self):
        return f"{self.user.name} @ {self.club.name} ({self.role})"
