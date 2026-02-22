from django.contrib import admin
from django.template.defaultfilters import filesizeformat

from apps.files.models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = (
        "original_name",
        "category",
        "uploaded_by",
        "club",
        "get_size_display",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "is_active", "club")
    search_fields = ("original_name", "uploaded_by__name", "club__name")
    raw_id_fields = ("uploaded_by", "club")
    readonly_fields = ("file", "original_name", "size", "mime_type", "ocr_result")

    @admin.display(description="파일 크기")
    def get_size_display(self, obj):
        return filesizeformat(obj.size)
