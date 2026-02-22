from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as s
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.serializers import (
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
    RegisterSerializer,
    UserSerializer,
)


# ──────────────────────────────────────────────
# 회원가입
# ──────────────────────────────────────────────
class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: inline_serializer(
                "RegisterResponse",
                fields={"message": s.CharField()},
            ),
        },
        summary="회원가입",
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "회원가입이 완료되었습니다."},
            status=status.HTTP_201_CREATED,
        )


# ──────────────────────────────────────────────
# 로그인
# ──────────────────────────────────────────────
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        responses={
            200: inline_serializer(
                "LoginResponse",
                fields={
                    "accessToken": s.CharField(),
                    "refreshToken": s.CharField(),
                    "user": UserSerializer(),
                },
            ),
        },
        summary="로그인 (JWT 발급)",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# ──────────────────────────────────────────────
# 토큰 갱신
# ──────────────────────────────────────────────
class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=CustomTokenRefreshSerializer,
        responses={
            200: inline_serializer(
                "TokenRefreshResponse",
                fields={
                    "accessToken": s.CharField(),
                    "refreshToken": s.CharField(required=False),
                },
            ),
        },
        summary="토큰 갱신",
    )
    def post(self, request):
        serializer = CustomTokenRefreshSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            raise InvalidToken("유효하지 않거나 만료된 리프레시 토큰입니다.")
        return Response(serializer.validated_data)


# ──────────────────────────────────────────────
# 내 정보 조회
# ──────────────────────────────────────────────
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserSerializer},
        summary="내 정보 조회",
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)
