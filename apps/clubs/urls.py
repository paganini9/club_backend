from django.urls import path

from apps.clubs.views import (
    ClubMemberDestroyView,
    ClubMemberListCreateView,
    ClubViewSet,
)

# ViewSet → URL 매핑 (Router 없이 명시적으로 연결)
club_list = ClubViewSet.as_view({"get": "list", "post": "create"})
club_detail = ClubViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
)

urlpatterns = [
    path("", club_list, name="club-list"),
    path("<int:pk>/", club_detail, name="club-detail"),
    path(
        "<int:pk>/members/",
        ClubMemberListCreateView.as_view(),
        name="club-member-list",
    ),
    path(
        "<int:pk>/members/<int:member_id>/",
        ClubMemberDestroyView.as_view(),
        name="club-member-remove",
    ),
]
