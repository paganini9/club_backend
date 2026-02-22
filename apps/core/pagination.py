from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """
    프론트엔드 PageResponse<T> 구조에 맞춘 페이지네이션.

    Query params:
      - page: 페이지 번호 (1-based, 기본 1)
      - size: 페이지당 항목 수 (기본 20, 최대 100)

    응답 data:
    {
      "content": [...],
      "totalElements": 100,
      "totalPages": 5,
      "page": 1,
      "size": 20
    }

    NOTE: ApiRenderer가 이 응답을 다시 {"success": true, "data": {...}} 로 감쌈.
    """

    page_size = 20
    page_size_query_param = "size"
    max_page_size = 100
    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("content", data),
                    ("totalElements", self.page.paginator.count),
                    ("totalPages", self.page.paginator.num_pages),
                    ("page", self.page.number),
                    ("size", self.get_page_size(self.request) or self.page_size),
                ]
            )
        )

    def get_paginated_response_schema(self, schema):
        """drf-spectacular용 스키마."""
        return {
            "type": "object",
            "required": ["content", "totalElements", "totalPages", "page", "size"],
            "properties": {
                "content": schema,
                "totalElements": {
                    "type": "integer",
                    "description": "전체 항목 수",
                    "example": 100,
                },
                "totalPages": {
                    "type": "integer",
                    "description": "전체 페이지 수",
                    "example": 5,
                },
                "page": {
                    "type": "integer",
                    "description": "현재 페이지 (1-based)",
                    "example": 1,
                },
                "size": {
                    "type": "integer",
                    "description": "페이지당 항목 수",
                    "example": 20,
                },
            },
        }
