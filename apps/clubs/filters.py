from django_filters import rest_framework as filters

from apps.clubs.models import Club


class ClubFilterSet(filters.FilterSet):
    """
    동아리 목록 필터.

    Query params:
      - keyword: 동아리명 검색 (icontains)  — 프론트엔드 clubApi.ts 대응
      - phase: 동아리 단계 필터 (exact match)
    """

    keyword = filters.CharFilter(field_name="name", lookup_expr="icontains")
    phase = filters.ChoiceFilter(choices=Club.Phase.choices)

    class Meta:
        model = Club
        fields = ["keyword", "phase"]
