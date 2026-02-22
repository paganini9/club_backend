from django.conf import settings
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.clubs.models import Club
from apps.core.exceptions import BusinessLogicError
from apps.core.pagination import CustomPageNumberPagination
from apps.files.filters import FileFilterSet
from apps.files.models import UploadedFile
from apps.files.serializers import FileUploadSerializer, UploadedFileSerializer


# ──────────────────────────────────────────────
# 파일 업로드 (다중 파일 지원)
# ──────────────────────────────────────────────
class FileUploadView(APIView):
    """POST /api/files/upload/ — multipart 파일 업로드."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "array",
                        "items": {"type": "string", "format": "binary"},
                        "description": "업로드할 파일 (다중 가능)",
                    },
                    "category": {
                        "type": "string",
                        "enum": [c.value for c in UploadedFile.Category],
                        "default": "GENERAL",
                    },
                    "club": {
                        "type": "integer",
                        "nullable": True,
                        "description": "동아리 ID (선택)",
                    },
                },
                "required": ["file"],
            }
        },
        responses={201: UploadedFileSerializer(many=True)},
        summary="파일 업로드 (다중 지원)",
    )
    def post(self, request):
        files = request.FILES.getlist("file")
        if not files:
            raise BusinessLogicError("파일이 필요합니다.")

        category = request.data.get("category", "GENERAL")
        if category not in UploadedFile.Category.values:
            raise BusinessLogicError(
                f"유효하지 않은 카테고리입니다: {category}"
            )

        # 동아리 확인
        club = None
        club_id = request.data.get("club")
        if club_id:
            try:
                club = Club.objects.get(pk=club_id)
            except Club.DoesNotExist:
                raise NotFound("존재하지 않는 동아리입니다.")

        # 파일 크기 검증 + 저장
        max_size = settings.MAX_UPLOAD_SIZE
        uploaded = []
        for f in files:
            if f.size > max_size:
                raise BusinessLogicError(
                    f"파일 크기가 {max_size // (1024 * 1024)}MB를 초과합니다: {f.name}"
                )

            obj = UploadedFile.objects.create(
                file=f,
                original_name=f.name,
                size=f.size,
                mime_type=f.content_type or "application/octet-stream",
                category=category,
                uploaded_by=request.user,
                club=club,
            )
            uploaded.append(obj)

        serializer = UploadedFileSerializer(
            uploaded, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ──────────────────────────────────────────────
# 파일 상세 / 삭제
# ──────────────────────────────────────────────
class FileDetailView(APIView):
    """
    GET    /api/files/{id}/   → 파일 정보 조회
    DELETE /api/files/{id}/   → 파일 삭제 (소프트 삭제)
    """

    permission_classes = [IsAuthenticated]

    def _get_object(self, pk):
        try:
            return UploadedFile.objects.get(pk=pk)
        except UploadedFile.DoesNotExist:
            raise NotFound("파일을 찾을 수 없습니다.")

    @extend_schema(
        responses={200: UploadedFileSerializer},
        summary="파일 정보 조회",
    )
    def get(self, request, pk):
        obj = self._get_object(pk)
        serializer = UploadedFileSerializer(obj, context={"request": request})
        return Response(serializer.data)

    @extend_schema(
        responses={204: None},
        summary="파일 삭제 (소프트 삭제)",
    )
    def delete(self, request, pk):
        obj = self._get_object(pk)
        obj.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ──────────────────────────────────────────────
# 파일 목록 (필터, 페이지네이션)
# ──────────────────────────────────────────────
class FileListView(APIView):
    """GET /api/files/ — 동아리별/카테고리별 파일 목록."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("club", int, description="동아리 ID로 필터"),
            OpenApiParameter(
                "category",
                str,
                enum=[c.value for c in UploadedFile.Category],
                description="카테고리로 필터",
            ),
            OpenApiParameter("page", int, description="페이지 번호 (1-based)"),
            OpenApiParameter("size", int, description="페이지당 항목 수"),
        ],
        responses={200: UploadedFileSerializer(many=True)},
        summary="파일 목록 (필터, 페이지네이션)",
    )
    def get(self, request):
        queryset = UploadedFile.objects.select_related("club", "uploaded_by").all()

        # django-filter 적용
        filterset = FileFilterSet(request.query_params, queryset=queryset)
        queryset = filterset.qs

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = UploadedFileSerializer(
            page, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)
