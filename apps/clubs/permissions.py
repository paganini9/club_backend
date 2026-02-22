from rest_framework.permissions import BasePermission


class IsAdminOrClubLeader(BasePermission):
    """
    관리자(ADMIN) 또는 해당 동아리의 리더(LEADER)만 허용.

    - has_permission: 인증된 사용자 통과 (object-level에서 상세 확인)
    - has_object_permission: ADMIN이면 무조건 통과,
      아니면 해당 Club의 LEADER 멤버십 확인
    """

    message = "관리자 또는 해당 동아리 리더만 접근할 수 있습니다."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == "ADMIN":
            return True
        return obj.memberships.filter(
            user=request.user,
            role="LEADER",
        ).exists()
