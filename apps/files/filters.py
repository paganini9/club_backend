from django_filters import rest_framework as filters

from apps.files.models import UploadedFile


class FileFilterSet(filters.FilterSet):
    """
    파일 목록 필터.

    Query params:
      - club: 동아리 ID (exact match)
      - category: 파일 카테고리 (exact match)
    """

    club = filters.NumberFilter(field_name="club_id")
    category = filters.ChoiceFilter(choices=UploadedFile.Category.choices)

    class Meta:
        model = UploadedFile
        fields = ["club", "category"]
