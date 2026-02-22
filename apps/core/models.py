from django.db import models


class ActiveManager(models.Manager):
    """is_active=True 레코드만 반환하는 기본 매니저."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class BaseModel(models.Model):
    """
    모든 앱 모델이 상속하는 추상 기본 모델.

    - created_at / updated_at: 자동 타임스탬프
    - is_active: 소프트 삭제용 플래그
    - objects: is_active=True 만 반환 (기본 쿼리에서 삭제된 행 제외)
    - all_objects: is_active 무관하게 전체 반환 (관리자용)
    """

    created_at = models.DateTimeField("생성일시", auto_now_add=True)
    updated_at = models.DateTimeField("수정일시", auto_now=True)
    is_active = models.BooleanField("활성 여부", default=True, db_index=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def soft_delete(self):
        """소프트 삭제 — is_active를 False로 설정."""
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])
