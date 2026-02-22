from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

User = get_user_model()


# ──────────────────────────────────────────────
# 프론트엔드 User 타입 대응
# ──────────────────────────────────────────────
class UserSerializer(serializers.ModelSerializer):
    """
    프론트엔드 User 인터페이스에 1:1 대응.

    {
      id: number,
      name: string,
      studentId: string,
      email: string,
      role: UserRole,
      phone?: string,
      createdAt: string
    }
    """

    studentId = serializers.CharField(source="student_id", read_only=True)
    createdAt = serializers.DateTimeField(source="date_joined", read_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "studentId", "email", "role", "phone", "createdAt"]
        read_only_fields = ["id", "createdAt"]


# ──────────────────────────────────────────────
# 회원가입
# ──────────────────────────────────────────────
class RegisterSerializer(serializers.Serializer):
    """
    프론트엔드 RegisterRequest 대응.

    입력: { name, studentId, email, password, role }
    """

    name = serializers.CharField(max_length=50)
    studentId = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=["STUDENT", "ADMIN"])

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value

    def validate_studentId(self, value):
        if User.objects.filter(student_id=value).exists():
            raise serializers.ValidationError("이미 등록된 학번입니다.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data["name"],
            student_id=validated_data["studentId"],
            role=validated_data["role"],
        )


# ──────────────────────────────────────────────
# 로그인 (SimpleJWT 커스터마이징)
# ──────────────────────────────────────────────
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    SimpleJWT의 TokenObtainPairSerializer를 확장.

    - USERNAME_FIELD가 email이므로 { email, password } 입력
    - 응답을 프론트엔드 LoginResponse에 맞춤:
      { accessToken, refreshToken, user }
    """

    def validate(self, attrs):
        # 부모 클래스가 인증 + 토큰 생성 처리
        data = super().validate(attrs)

        return {
            "accessToken": data["access"],
            "refreshToken": data["refresh"],
            "user": UserSerializer(self.user).data,
        }


# ──────────────────────────────────────────────
# 토큰 갱신
# ──────────────────────────────────────────────
class CustomTokenRefreshSerializer(serializers.Serializer):
    """
    프론트엔드가 { refreshToken } 으로 요청하고
    { accessToken } 을 응답받는 구조.
    """

    refreshToken = serializers.CharField()

    def validate(self, attrs):
        try:
            refresh = RefreshToken(attrs["refreshToken"])
        except TokenError:
            raise serializers.ValidationError("유효하지 않거나 만료된 리프레시 토큰입니다.")

        result = {
            "accessToken": str(refresh.access_token),
        }

        # ROTATE_REFRESH_TOKENS가 True이면 새 리프레시 토큰도 반환
        from django.conf import settings

        if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False):
            refresh.set_jti()
            refresh.set_exp()
            result["refreshToken"] = str(refresh)

        return result
