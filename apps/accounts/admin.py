from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """email 기반 CustomUser를 위한 Admin 설정."""

    # 목록 화면
    list_display = ("email", "name", "student_id", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("email", "name", "student_id")
    ordering = ("-date_joined",)

    # 상세/수정 화면
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("개인정보", {"fields": ("name", "student_id", "phone", "role")}),
        (
            "권한",
            {
                "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
                "classes": ("collapse",),
            },
        ),
        ("날짜", {"fields": ("last_login", "date_joined"), "classes": ("collapse",)}),
    )

    # 유저 추가 화면
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "student_id",
                    "phone",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
