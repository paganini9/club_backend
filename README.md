# 창업동아리 관리 시스템 — Backend

대구대학교 창업동아리 관리 및 사업비 정산 자동화 플랫폼의 Django REST API 서버입니다.

## 기술 스택

- Python 3.12 / Django 5.0 / Django REST Framework 3.14
- SQLite (개발) → PostgreSQL (프로덕션)
- JWT 인증 (djangorestframework-simplejwt)
- Swagger UI (drf-spectacular)

## 로컬 실행 방법

```bash
cd club_backend

# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements/base.txt

# 3. 환경변수 설정 (.env 파일이 이미 있으면 생략)
cp .env.example .env

# 4. 데이터베이스 마이그레이션
python manage.py migrate

# 5. 시드 데이터 생성
python manage.py seed_data

# 6. 개발 서버 실행
python manage.py runserver
```

서버가 http://localhost:8000 에서 실행됩니다.

## API 문서

- Swagger UI: http://localhost:8000/api/docs/
- OpenAPI Schema (JSON): http://localhost:8000/api/schema/
- Django Admin: http://localhost:8000/admin/

## 테스트 계정

| 이메일 | 비밀번호 | 역할 | 이름 |
|--------|---------|------|------|
| student@test.com | password123 | STUDENT | 김학생 |
| leader@test.com | password123 | LEADER | 이팀장 |
| admin@test.com | password123 | ADMIN | 박관리자 |

## API 엔드포인트

### 인증 (accounts)
| Method | URL | 설명 |
|--------|-----|------|
| POST | /api/accounts/register/ | 회원가입 |
| POST | /api/accounts/login/ | 로그인 (JWT 발급) |
| POST | /api/accounts/token/refresh/ | 토큰 갱신 |
| GET | /api/accounts/me/ | 내 정보 조회 |

### 동아리 (clubs)
| Method | URL | 설명 |
|--------|-----|------|
| GET | /api/clubs/ | 동아리 목록 |
| POST | /api/clubs/ | 동아리 생성 (Admin) |
| GET | /api/clubs/{id}/ | 동아리 상세 |
| PATCH | /api/clubs/{id}/ | 동아리 수정 |
| DELETE | /api/clubs/{id}/ | 동아리 삭제 (Admin) |
| GET | /api/clubs/{id}/members/ | 멤버 목록 |
| POST | /api/clubs/{id}/members/ | 멤버 추가 |
| DELETE | /api/clubs/{id}/members/{member_id}/ | 멤버 제거 |

### 파일 (files)
| Method | URL | 설명 |
|--------|-----|------|
| GET | /api/files/ | 파일 목록 |
| POST | /api/files/upload/ | 파일 업로드 |
| GET | /api/files/{id}/ | 파일 정보 |
| DELETE | /api/files/{id}/ | 파일 삭제 |

## 프론트엔드 연결

프론트엔드(`bolt_startup_club/`)의 `.env` 파일에 아래 설정을 추가합니다:

```
VITE_API_BASE_URL=http://localhost:8000/api
```

백엔드의 CORS 설정에 `http://localhost:5173`이 이미 허용되어 있습니다.

## 프로젝트 구조

```
club_backend/
├── config/                  # 프로젝트 설정
│   ├── settings/
│   │   ├── base.py          # 공통 설정
│   │   └── local.py         # 개발 설정 (SQLite)
│   └── urls.py              # URL 라우팅
├── apps/
│   ├── core/                # 공통 모듈 (BaseModel, 예외, 페이지네이션, 퍼미션)
│   ├── accounts/            # 사용자/인증 (JWT)
│   ├── clubs/               # 동아리 관리
│   └── files/               # 파일 업로드
├── requirements/
│   ├── base.txt             # 필수 패키지
│   └── local.txt            # 개발 패키지
└── manage.py
```
