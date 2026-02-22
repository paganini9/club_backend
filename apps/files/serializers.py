from rest_framework import serializers

from apps.files.models import UploadedFile


# ──────────────────────────────────────────────
# 프론트엔드 UploadedFile 타입 대응 (읽기 전용)
# { id, originalName, s3Key, url, size, mimeType, category, uploadedAt }
# ──────────────────────────────────────────────
class UploadedFileSerializer(serializers.ModelSerializer):
    originalName = serializers.CharField(source="original_name", read_only=True)
    s3Key = serializers.CharField(source="file.name", read_only=True)
    url = serializers.SerializerMethodField()
    mimeType = serializers.CharField(source="mime_type", read_only=True)
    uploadedAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = UploadedFile
        fields = [
            "id",
            "originalName",
            "s3Key",
            "url",
            "size",
            "mimeType",
            "category",
            "uploadedAt",
        ]

    def get_url(self, obj):
        if not obj.file:
            return ""
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url


# ──────────────────────────────────────────────
# 파일 업로드 요청
# ──────────────────────────────────────────────
class FileUploadSerializer(serializers.Serializer):
    """
    multipart/form-data 업로드 요청 검증.

    - file: 업로드 파일 (필수, 다중 파일 시 동일 키로 여러 개)
    - category: 파일 카테고리 (기본 GENERAL)
    - club: 동아리 ID (선택)
    """

    file = serializers.FileField()
    category = serializers.ChoiceField(
        choices=UploadedFile.Category.choices,
        default=UploadedFile.Category.GENERAL,
    )
    club = serializers.IntegerField(required=False, allow_null=True)
