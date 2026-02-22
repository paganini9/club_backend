from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.clubs.models import Club, ClubMember

User = get_user_model()


# ──────────────────────────────────────────────
# ClubMember — 프론트엔드 ClubMember 타입 대응
# { userId, name, studentId, email, phone?, role, joinedAt }
# ──────────────────────────────────────────────
class ClubMemberSerializer(serializers.ModelSerializer):
    userId = serializers.IntegerField(source="user.id", read_only=True)
    name = serializers.CharField(source="user.name", read_only=True)
    studentId = serializers.CharField(source="user.student_id", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)
    joinedAt = serializers.DateTimeField(source="joined_at", read_only=True)

    class Meta:
        model = ClubMember
        fields = ["userId", "name", "studentId", "email", "phone", "role", "joinedAt"]


# ──────────────────────────────────────────────
# Club 목록용 — memberCount만 포함 (N+1 방지)
# ──────────────────────────────────────────────
class ClubListSerializer(serializers.ModelSerializer):
    """
    GET /api/clubs/ 목록 응답.

    members 배열 대신 memberCount(정수)를 반환하여 페이로드 최소화.
    ViewSet에서 annotate(member_count=Count("memberships"))로 주입.
    """

    logoUrl = serializers.SerializerMethodField()
    memberCount = serializers.IntegerField(source="member_count", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Club
        fields = [
            "id",
            "name",
            "description",
            "logoUrl",
            "phase",
            "memberCount",
            "createdAt",
        ]

    def get_logoUrl(self, obj):
        if not obj.logo:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.logo.url)
        return obj.logo.url


# ──────────────────────────────────────────────
# Club 상세용 — members 배열 포함
# 프론트엔드 Club 타입 1:1 대응
# { id, name, description, logoUrl?, phase, members, budget?, createdAt }
# ──────────────────────────────────────────────
class ClubDetailSerializer(serializers.ModelSerializer):
    logoUrl = serializers.SerializerMethodField()
    members = ClubMemberSerializer(source="memberships", many=True, read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Club
        fields = [
            "id",
            "name",
            "description",
            "logoUrl",
            "phase",
            "members",
            "createdAt",
        ]

    def get_logoUrl(self, obj):
        if not obj.logo:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.logo.url)
        return obj.logo.url


# ──────────────────────────────────────────────
# 동아리 생성
# ──────────────────────────────────────────────
class ClubCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["name", "description", "logo"]
        extra_kwargs = {
            "logo": {"required": False, "allow_null": True},
        }


# ──────────────────────────────────────────────
# 동아리 수정 — 프론트엔드 ClubUpdateRequest 대응
# { name?, description?, logo? }
# ──────────────────────────────────────────────
class ClubUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["name", "description", "logo", "phase"]
        extra_kwargs = {
            "name": {"required": False},
            "description": {"required": False},
            "logo": {"required": False},
            "phase": {"required": False},
        }


# ──────────────────────────────────────────────
# 멤버 추가 요청
# ──────────────────────────────────────────────
class AddMemberSerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    role = serializers.ChoiceField(choices=ClubMember.MemberRole.choices)

    def validate_userId(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 사용자입니다.")
        return value
