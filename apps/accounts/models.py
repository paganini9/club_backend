from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.accounts.managers import CustomUserManager


class CustomUser(AbstractUser):
    """프론트엔드 User 타입과 1:1 매핑되는 커스텀 유저 모델."""

    class Role(models.TextChoices):
        STUDENT = "STUDENT", "학생"
        LEADER = "LEADER", "리더"
        ADMIN = "ADMIN", "관리자"

    # AbstractUser의 username 필드 비활성화 — email을 로그인 ID로 사용
    username = None
    email = models.EmailField("이메일", unique=True)
    name = models.CharField("이름", max_length=50)
    student_id = models.CharField("학번", max_length=20, unique=True)
    phone = models.CharField("전화번호", max_length=20, blank=True, default="")
    role = models.CharField(
        "역할",
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "student_id"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "사용자"
        verbose_name_plural = "사용자"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.name} ({self.email})"
