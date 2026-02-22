"""
시드 데이터 생성 커맨드.

사용법:
    python manage.py seed_data          # 기존 데이터 유지하고 추가
    python manage.py seed_data --reset  # 기존 데이터 삭제 후 재생성
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.clubs.models import Club, ClubMember

User = get_user_model()

# ──────────────────────────────────────────────
# 테스트 계정 데이터
# ──────────────────────────────────────────────
USERS = [
    {
        "email": "student@test.com",
        "password": "password123",
        "name": "김학생",
        "student_id": "20210001",
        "role": "STUDENT",
    },
    {
        "email": "leader@test.com",
        "password": "password123",
        "name": "이팀장",
        "student_id": "20210002",
        "role": "LEADER",
    },
    {
        "email": "admin@test.com",
        "password": "password123",
        "name": "박관리자",
        "student_id": "00000000",
        "role": "ADMIN",
        "is_staff": True,
    },
    # 동아리 멤버용 추가 계정
    {
        "email": "student2@test.com",
        "password": "password123",
        "name": "최민수",
        "student_id": "20210003",
        "role": "STUDENT",
    },
    {
        "email": "student3@test.com",
        "password": "password123",
        "name": "정유진",
        "student_id": "20210004",
        "role": "STUDENT",
    },
    {
        "email": "student4@test.com",
        "password": "password123",
        "name": "한서윤",
        "student_id": "20210005",
        "role": "STUDENT",
    },
    {
        "email": "leader2@test.com",
        "password": "password123",
        "name": "강리더",
        "student_id": "20210006",
        "role": "LEADER",
    },
]

# ──────────────────────────────────────────────
# 동아리 데이터
# ──────────────────────────────────────────────
CLUBS = [
    {
        "name": "AI 스타트업",
        "description": "인공지능 기술을 활용한 창업 아이디어를 발굴하고 실현하는 동아리입니다.",
        "phase": "OPERATING",
        "members": [
            # (user email, member role)
            ("leader@test.com", "LEADER"),
            ("student@test.com", "MEMBER"),
            ("student2@test.com", "MEMBER"),
        ],
    },
    {
        "name": "핀테크 랩",
        "description": "블록체인과 핀테크 서비스를 연구·개발하는 창업 동아리입니다.",
        "phase": "OPERATING",
        "members": [
            ("leader2@test.com", "LEADER"),
            ("student3@test.com", "MEMBER"),
        ],
    },
    {
        "name": "바이오헬스",
        "description": "바이오·헬스케어 분야의 창업을 목표로 하는 동아리입니다.",
        "phase": "OPERATING",
        "members": [
            ("student4@test.com", "LEADER"),
            ("student2@test.com", "MEMBER"),
            ("student3@test.com", "MEMBER"),
        ],
    },
]


class Command(BaseCommand):
    help = "테스트용 시드 데이터를 생성합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="기존 시드 데이터를 삭제 후 재생성합니다.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self._reset()

        users = self._create_users()
        self._create_clubs(users)

        self.stdout.write(self.style.SUCCESS("\n시드 데이터 생성 완료!"))
        self.stdout.write(
            "\n테스트 계정:\n"
            "  student@test.com / password123  (STUDENT)\n"
            "  leader@test.com  / password123  (LEADER)\n"
            "  admin@test.com   / password123  (ADMIN)\n"
        )

    def _reset(self):
        self.stdout.write("기존 시드 데이터 삭제 중...")
        emails = [u["email"] for u in USERS]
        ClubMember.objects.filter(user__email__in=emails).delete()
        club_names = [c["name"] for c in CLUBS]
        Club.all_objects.filter(name__in=club_names).delete()
        User.objects.filter(email__in=emails).delete()
        self.stdout.write(self.style.WARNING("  삭제 완료"))

    def _create_users(self):
        self.stdout.write("사용자 생성 중...")
        user_map = {}
        for data in USERS:
            email = data["email"]
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": data["name"],
                    "student_id": data["student_id"],
                    "role": data["role"],
                    "is_staff": data.get("is_staff", False),
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()
                self.stdout.write(f"  [생성] {user.name} ({email}) - {user.role}")
            else:
                self.stdout.write(f"  [존재] {user.name} ({email}) - {user.role}")
            user_map[email] = user
        return user_map

    def _create_clubs(self, user_map):
        self.stdout.write("동아리 생성 중...")
        for club_data in CLUBS:
            club, created = Club.all_objects.get_or_create(
                name=club_data["name"],
                defaults={
                    "description": club_data["description"],
                    "phase": club_data["phase"],
                },
            )
            if created:
                self.stdout.write(f"  [생성] {club.name}")
            else:
                # soft-delete된 동아리 복원
                if not club.is_active:
                    club.is_active = True
                    club.save(update_fields=["is_active"])
                self.stdout.write(f"  [존재] {club.name}")

            for email, role in club_data["members"]:
                user = user_map.get(email)
                if user is None:
                    continue
                _, mem_created = ClubMember.objects.get_or_create(
                    club=club,
                    user=user,
                    defaults={"role": role},
                )
                status_tag = "추가" if mem_created else "존재"
                self.stdout.write(
                    f"    [{status_tag}] {user.name} → {club.name} ({role})"
                )
