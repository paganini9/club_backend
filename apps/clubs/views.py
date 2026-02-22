from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.clubs.filters import ClubFilterSet
from apps.clubs.models import Club, ClubMember
from apps.clubs.permissions import IsAdminOrClubLeader
from apps.clubs.serializers import (
    AddMemberSerializer,
    ClubCreateSerializer,
    ClubDetailSerializer,
    ClubListSerializer,
    ClubMemberSerializer,
    ClubUpdateSerializer,
)
from apps.core.exceptions import BusinessLogicError
from apps.core.permissions import IsAdmin

User = get_user_model()


# ──────────────────────────────────────────────
# Club CRUD — ModelViewSet
# ──────────────────────────────────────────────
class ClubViewSet(ModelViewSet):
    """
    동아리 CRUD ViewSet.

    list:           GET    /api/clubs/
    create:         POST   /api/clubs/           (Admin)
    retrieve:       GET    /api/clubs/{pk}/
    partial_update: PATCH  /api/clubs/{pk}/       (Admin or Club Leader)
    destroy:        DELETE /api/clubs/{pk}/       (Admin)
    """

    filterset_class = ClubFilterSet
    # PUT은 사용하지 않음 — PATCH만 허용
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = Club.objects.all()

        # STUDENT는 자기가 속한 동아리만 조회
        if self.request.user.role == "STUDENT":
            qs = qs.filter(memberships__user=self.request.user)

        # list: annotation으로 멤버 수 계산 (N+1 방지)
        if self.action == "list":
            qs = qs.annotate(member_count=Count("memberships"))
        else:
            # retrieve/update/delete: 멤버 정보 prefetch
            qs = qs.prefetch_related("memberships__user")

        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return ClubListSerializer
        if self.action == "create":
            return ClubCreateSerializer
        if self.action in ("update", "partial_update"):
            return ClubUpdateSerializer
        return ClubDetailSerializer

    def get_permissions(self):
        if self.action in ("create", "destroy"):
            return [IsAdmin()]
        if self.action in ("update", "partial_update"):
            return [IsAdminOrClubLeader()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """생성 후 ClubDetailSerializer로 응답."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        club = serializer.save()
        return Response(
            ClubDetailSerializer(club, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """수정 후 ClubDetailSerializer로 응답 (prefetch 포함)."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # 수정된 데이터를 members 포함하여 다시 조회
        instance = Club.objects.prefetch_related("memberships__user").get(pk=instance.pk)
        return Response(
            ClubDetailSerializer(instance, context=self.get_serializer_context()).data,
        )

    def perform_destroy(self, instance):
        """하드 삭제 대신 소프트 삭제."""
        instance.soft_delete()


# ──────────────────────────────────────────────
# ClubMember 목록 / 추가
# ──────────────────────────────────────────────
class ClubMemberListCreateView(APIView):
    """
    GET  /api/clubs/{pk}/members/     → 멤버 목록
    POST /api/clubs/{pk}/members/     → 멤버 추가 (Admin or Club Leader)
    """

    permission_classes = [IsAuthenticated]

    def _get_club(self, pk):
        try:
            return Club.objects.get(pk=pk)
        except Club.DoesNotExist:
            return None

    def _check_leader_or_admin(self, request, club):
        """Admin이 아니면 해당 동아리 리더인지 확인."""
        if request.user.role == "ADMIN":
            return
        is_leader = club.memberships.filter(
            user=request.user, role="LEADER"
        ).exists()
        if not is_leader:
            self.permission_denied(request, message="리더 또는 관리자 권한이 필요합니다.")

    def get(self, request, pk):
        club = self._get_club(pk)
        if club is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        members = club.memberships.select_related("user").all()
        return Response(ClubMemberSerializer(members, many=True).data)

    def post(self, request, pk):
        club = self._get_club(pk)
        if club is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        self._check_leader_or_admin(request, club)

        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(id=serializer.validated_data["userId"])

        if ClubMember.objects.filter(club=club, user=user).exists():
            raise BusinessLogicError("이미 동아리에 가입된 멤버입니다.")

        member = ClubMember.objects.create(
            club=club,
            user=user,
            role=serializer.validated_data["role"],
        )

        # 멤버 추가 시 해당 유저의 role이 STUDENT이고 LEADER로 추가된 경우, 유저 role 업데이트
        if serializer.validated_data["role"] == "LEADER" and user.role == "STUDENT":
            user.role = "LEADER"
            user.save(update_fields=["role"])

        return Response(
            ClubMemberSerializer(member).data,
            status=status.HTTP_201_CREATED,
        )


# ──────────────────────────────────────────────
# ClubMember 삭제
# ──────────────────────────────────────────────
class ClubMemberDestroyView(APIView):
    """
    DELETE /api/clubs/{pk}/members/{member_id}/ → 멤버 제거 (Admin or Club Leader)
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, member_id):
        try:
            club = Club.objects.get(pk=pk)
        except Club.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 권한 확인
        if request.user.role != "ADMIN":
            is_leader = club.memberships.filter(
                user=request.user, role="LEADER"
            ).exists()
            if not is_leader:
                self.permission_denied(request, message="리더 또는 관리자 권한이 필요합니다.")

        try:
            membership = club.memberships.get(user_id=member_id)
        except ClubMember.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
