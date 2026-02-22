from rest_framework.renderers import JSONRenderer


class ApiRenderer(JSONRenderer):
    """
    모든 API 응답을 프론트엔드 ApiResponse<T> 구조로 감싸는 렌더러.

    성공 시:
    {
      "success": true,
      "data": { ... },
      "message": "..."
    }

    에러 시 (custom_exception_handler에서 이미 래핑됨):
    {
      "success": false,
      "data": null,
      "error": { "code": "...", "detail": "..." }
    }
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None

        if response is None:
            return super().render(data, accepted_media_type, renderer_context)

        # 204 No Content — 빈 바디
        if response.status_code == 204:
            return b""

        # 에러 응답: custom_exception_handler 또는 뷰에서 직접 구성한 경우
        if response.status_code >= 400:
            # 이미 {"success": false, ...} 형태이면 그대로
            if isinstance(data, dict) and "success" in data:
                return super().render(data, accepted_media_type, renderer_context)
            # 아니면 (직접 Response로 에러를 보낸 경우) 래핑
            return super().render(
                {
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "SERVER_ERROR",
                        "detail": data,
                    },
                },
                accepted_media_type,
                renderer_context,
            )

        # 이미 래핑된 응답이면 다시 래핑하지 않음
        if isinstance(data, dict) and "success" in data and "data" in data:
            return super().render(data, accepted_media_type, renderer_context)

        # 정상 응답 래핑
        wrapped = {
            "success": True,
            "data": data,
            "message": None,
        }
        return super().render(wrapped, accepted_media_type, renderer_context)
