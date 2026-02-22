from django.contrib import admin

from apps.clubs.models import Club, ClubMember


class ClubMemberInline(admin.TabularInline):
    model = ClubMember
    extra = 0
    raw_id_fields = ("user",)
    readonly_fields = ("joined_at",)


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("name", "phase", "get_member_count", "is_active", "created_at")
    list_filter = ("phase", "is_active")
    search_fields = ("name",)
    inlines = [ClubMemberInline]

    @admin.display(description="멤버 수")
    def get_member_count(self, obj):
        return obj.memberships.count()


@admin.register(ClubMember)
class ClubMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "club", "role", "joined_at")
    list_filter = ("role", "club")
    search_fields = ("user__name", "user__email", "club__name")
    raw_id_fields = ("user", "club")
