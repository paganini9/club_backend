from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    DRF 예외를 프론트엔드 ApiResponse 형태로 변환.

    {
      "success": false,
      "data": null,
      "error": { "code": "ERROR_CODE", "detail": "..." }
    }
    """
    response = exception_handler(exc, context)

    if response is None:
        return None

    code = _get_error_code(exc, response)
    detail = _normalize_detail(response.data)

    response.data = {
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "detail": detail,
        },
    }

    return response


def _get_error_code(exc, response):
    """HTTP 상태 코드 → 에러 코드 매핑."""
    # DRF 예외에 default_code가 있으면 우선 사용
    if hasattr(exc, "default_code"):
        exc_code = getattr(exc, "default_code", "")
        code_map_by_exc = {
            "not_authenticated": "AUTHENTICATION_ERROR",
            "authentication_failed": "AUTHENTICATION_ERROR",
            "permission_denied": "PERMISSION_DENIED",
            "not_found": "NOT_FOUND",
            "method_not_allowed": "METHOD_NOT_ALLOWED",
            "throttled": "THROTTLED",
            "parse_error": "VALIDATION_ERROR",
        }
        if exc_code in code_map_by_exc:
            return code_map_by_exc[exc_code]

    status_code = response.status_code
    code_map = {
        400: "VALIDATION_ERROR",
        401: "AUTHENTICATION_ERROR",
        403: "PERMISSION_DENIED",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        429: "THROTTLED",
    }
    return code_map.get(status_code, "SERVER_ERROR")


def _normalize_detail(data):
    """
    DRF가 반환하는 다양한 에러 구조를 단일 문자열로 정규화.

    가능한 입력 형태:
      - str:  "Not found."
      - list: ["This field is required."]
      - dict: {"email": ["Enter a valid email."], "name": ["This field is required."]}
      - dict: {"detail": "Authentication credentials were not provided."}
      - dict: {"non_field_errors": ["Unable to log in."]}
    """
    if isinstance(data, str):
        return data

    if isinstance(data, list):
        return " ".join(str(item) for item in data)

    if isinstance(data, dict):
        # "detail" 키가 있으면 우선 사용 (SimpleJWT 등이 {detail, code} 구조 반환)
        if "detail" in data:
            detail = data["detail"]
            return str(detail) if not isinstance(detail, (list, dict)) else _normalize_detail(detail)

        # 필드별 에러를 "필드: 메시지" 형태로 결합
        parts = []
        for field, errors in data.items():
            if isinstance(errors, list):
                msg = " ".join(str(e) for e in errors)
            elif isinstance(errors, str):
                msg = errors
            else:
                msg = str(errors)

            if field == "non_field_errors":
                parts.append(msg)
            else:
                parts.append(f"{field}: {msg}")

        return " | ".join(parts)

    return str(data)


class BusinessLogicError(APIException):
    """비즈니스 로직 에러용 커스텀 예외 (400)."""

    status_code = 400
    default_detail = "요청을 처리할 수 없습니다."
    default_code = "business_error"

    def __init__(self, detail=None, code=None):
        if code:
            self.default_code = code
        super().__init__(detail=detail)
