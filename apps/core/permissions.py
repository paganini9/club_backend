from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """관리자(ADMIN) 역할만 접근 허용."""

    message = "관리자 권한이 필요합니다."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsLeader(BasePermission):
    """동아리 리더(LEADER) 역할만 접근 허용."""

    message = "동아리 리더 권한이 필요합니다."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "LEADER"
        )


class IsLeaderOrAdmin(BasePermission):
    """동아리 리더(LEADER) 또는 관리자(ADMIN)만 접근 허용."""

    message = "리더 또는 관리자 권한이 필요합니다."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("LEADER", "ADMIN")
        )


class IsClubMember(BasePermission):
    """
    해당 동아리의 멤버인 사용자만 접근 허용.

    URL kwargs에서 동아리 PK를 가져오는 규칙:
      - 'pk', 'club_pk', 'club_id' 순서로 탐색
    관리자는 항상 통과.
    """

    message = "해당 동아리의 멤버만 접근할 수 있습니다."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        # 관리자는 모든 동아리에 접근 가능
        if user.role == "ADMIN":
            return True

        club_pk = (
            view.kwargs.get("pk")
            or view.kwargs.get("club_pk")
            or view.kwargs.get("club_id")
        )
        if club_pk is None:
            return False

        # 순환 import 방지를 위해 함수 내부에서 import
        from apps.clubs.models import ClubMember

        return ClubMember.objects.filter(
            club_id=club_pk,
            user=user,
        ).exists()
