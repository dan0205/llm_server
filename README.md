# 신조어 해석 Chrome 확장 프로그램

OpenAI API를 활용하여 한국어 신조어를 실시간으로 해석하고, Redis 캐시와 PostgreSQL 데이터베이스를 통해 빠른 응답을 제공하는 Chrome 확장 프로그램입니다.

## 🚀 주요 기능

- **실시간 신조어 해석**: OpenAI GPT 모델을 사용한 정확한 신조어 해석
- **문맥 기반 분석**: 선택된 텍스트의 주변 문맥을 고려한 해석 제공
- **스마트 캐싱**: Redis를 통한 빠른 응답과 중복 요청 방지
- **데이터 영속성**: PostgreSQL을 통한 해석 결과 저장
- **사용자 친화적 UI**: 직관적인 툴팁 인터페이스

## 🏗️ 아키텍처

```
Chrome Extension (content_simple.js)
           ↓
    FastAPI Backend
           ↓
    ┌─────────────┐
    │   Redis     │ ← 캐싱
    └─────────────┘
           ↓
    ┌─────────────┐
    │ PostgreSQL  │ ← 데이터 저장
    └─────────────┘
           ↓
    ┌─────────────┐
    │ OpenAI API  │ ← AI 해석
    └─────────────┘
```

## 📋 요구사항

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+
- Chrome 브라우저

## 🛠️ 설치 및 설정

### 1. 환경 변수 설정

`.env` 파일을 생성하고 다음 정보를 입력하세요:

```bash
# OpenAI API 설정 (필수)
OPENAI_API_KEY=sk-your-openai-api-key-here

# 데이터베이스 설정 (필수)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/llm_db

# Redis 설정 (필수)
REDIS_URL=redis://localhost:6379

# JWT 보안 설정 (필수)
SECRET_KEY=your_super_secret_key_change_this_in_production
```

### 2. 백엔드 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션 (필요시)
# alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Docker Compose 사용 (권장)

```bash
# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

### 4. Chrome 확장 프로그램 설치

1. Chrome에서 `chrome://extensions/` 접속
2. "개발자 모드" 활성화
3. "압축해제된 확장 프로그램을 로드합니다" 클릭
4. `llm_server` 폴더 선택

#### **Manifest 설정 상세**

**필수 권한:**
```json
{
  "permissions": [
    "scripting",      // 동적 스크립트 주입
    "activeTab",      // 현재 활성 탭 접근
    "storage"         // 로컬 캐시 및 사전 저장
  ]
}
```

**선택 권한:**
```json
{
  "optional_permissions": [
    "webNavigation"   // 페이지 내비게이션 감지 (권장)
  ]
}
```

**웹 접근 리소스:**
```json
{
  "web_accessible_resources": [
    {
      "resources": ["assets/*"],
      "matches": ["<all_urls>"]
    }
  ]
}
```

**권한 설명:**
- **`scripting`**: 동적으로 스크립트를 주입하여 페이지 컨텍스트에서 history API 후킹
- **`activeTab`**: 현재 활성 탭에서만 스크립트 실행 (보안 강화)
- **`storage`**: 로컬 캐시와 30개 신조어 사전을 Chrome Storage에 저장
- **`webNavigation`**: SPA 내비게이션과 페이지 전환을 확실하게 감지
- **`web_accessible_resources`**: assets 폴더의 slang_30.json 파일에 접근하여 로컬 사전 로드

## 🔧 API 엔드포인트

### 신조어 해석
```
GET /api/v1/jargons/interpret/{term}?context={context}
```

**파라미터:**
- `term` (필수): 해석할 신조어
- `context` (선택): 문맥 문장 (최대 220자)
- `nocache` (선택): 캐시 무시하고 LLM 직접 호출
- `refresh` (선택): 캐시 강제 갱신

**응답 예시:**
```json
{
  "meaning_line": "알고리즘 탔다: 알고리즘 추천에 노출되어 조회수가 급증함."
}
```

### 디버그 엔드포인트
```
GET /__health                    # 서버 상태 확인
GET /__debug/redis              # Redis 연결 상태
GET /__debug/openai             # OpenAI API 키 상태
GET /__debug/llm                # LLM 테스트 호출
GET /__debug/cache              # 캐시 시스템 상태
GET /__debug/cache/{term}       # 특정 term 캐시 내용
DELETE /__debug/cache/{term}    # 특정 term 캐시 삭제
```

## 🧠 동작 원리

### 1. 전체 시스템 아키텍처
```
사용자 드래그 → Content Script → Background Script → FastAPI → OpenAI → 응답
                    ↓              ↓              ↓
                로컬 캐시    탭 간 동기화    Redis 캐시
```

### 2. 우선순위 기반 해석 시스템
```
1순위: 탭 간 공유 캐시 (가장 빠름, 0ms)
2순위: 로컬 사전 30개 (오프라인 지원)
3순위: 네트워크 API (온라인에서만)
```

### 3. 문맥 기반 해석 과정
1. **텍스트 선택**: 사용자가 웹페이지에서 신조어 드래그
2. **문맥 추출**: 선택된 단어 주변 220자 문장 자동 추출
3. **캐시 확인**: 로컬/원격 캐시에서 기존 해석 검색
4. **LLM 호출**: 캐시 미스 시 OpenAI GPT-4o-mini 호출
5. **결과 저장**: 성공한 해석을 캐시에 저장 (7일 TTL)
6. **탭 동기화**: 모든 탭에 새로운 캐시 데이터 전파

### 4. 오프라인 지원
- **로컬 사전**: 30개 핵심 신조어 번들
- **오프라인 감지**: `navigator.onLine` API 사용
- **폴백 메시지**: 네트워크 없이도 기본 기능 제공

### 5. 캐시 전략
- **계층적 캐시**: 로컬 → Redis → LLM
- **문맥별 키**: `term + context_hash` 조합으로 고유 식별
- **TTL 관리**: 7일 자동 만료로 최신성 보장
- **실패 방지**: fallback 응답은 캐시에 저장하지 않음

## 🎯 사용법

### 기본 사용법
1. **웹페이지에서 신조어 선택**: 마우스로 드래그하여 신조어 선택
2. **자동 해석**: 선택된 텍스트가 자동으로 분석됨
3. **툴팁 확인**: 해석 결과를 툴팁으로 확인
4. **캐시 활용**: 동일한 신조어는 즉시 응답

### 고급 기능
- **문맥 고려**: 선택된 단어 주변 문장을 자동으로 포함하여 해석
- **탭 간 동기화**: 한 탭에서 해석한 결과를 다른 탭에서도 즉시 사용
- **오프라인 지원**: 네트워크 없이도 기본 신조어 해석 가능

### 디버그 모드
```bash
# 캐시 무시하고 새로 해석
curl "http://localhost:8000/api/v1/jargons/interpret/테스트?nocache=true"

# 캐시 강제 갱신
curl "http://localhost:8000/api/v1/jargons/interpret/테스트?refresh=true"

# 캐시 상태 확인
curl "http://localhost:8000/__debug/cache/테스트"
```

## 🔍 캐싱 전략

### 계층적 캐시 시스템
- **1단계: 로컬 캐시** (Chrome Storage)
  - 탭 간 공유, 7일 TTL
  - 가장 빠른 응답 (0ms)
  - 오프라인에서도 사용 가능

- **2단계: Redis 캐시** (서버)
  - 서버 재시작 후에도 유지
  - 7일 TTL로 최신성 보장
  - fallback 응답은 저장하지 않음

- **3단계: LLM API** (OpenAI)
  - 캐시 미스 시에만 호출
  - 문맥 기반 정확한 해석
  - 성공한 결과만 캐시에 저장

### 캐시 키 생성
```
키 형식: jargon:v2:{term}:{context_hash}
예시: jargon:v2:알고리즘탔다:abc12345
```

### 성능 최적화
- **문맥별 분리**: 같은 단어라도 문맥이 다르면 별도 캐시
- **해시 기반**: 빠른 검색을 위한 효율적인 키 구조
- **자동 만료**: TTL로 메모리 효율성 확보

## 🚨 문제 해결

### 백엔드 연결 오류
- 서버가 실행 중인지 확인
- `.env` 파일의 설정값 확인
- 방화벽 설정 확인

### OpenAI API 오류
- API 키 유효성 확인
- API 사용량 한도 확인
- 네트워크 연결 상태 확인

### 데이터베이스 오류
- PostgreSQL 서비스 상태 확인
- 데이터베이스 연결 문자열 확인
- 테이블 스키마 확인

## 📊 성능 최적화

### 시스템 레벨 최적화
- **비동기 처리**: FastAPI의 비동기 특성 활용
- **연결 풀링**: 데이터베이스 및 Redis 연결 풀 사용
- **배치 처리**: 여러 신조어 동시 해석 지원

### 캐시 레벨 최적화
- **로컬 우선**: Chrome Storage를 통한 즉시 응답
- **탭 동기화**: 한 번 해석하면 모든 탭에서 재사용
- **문맥 인덱싱**: 빠른 해시 기반 검색

### LLM 레벨 최적화
- **프롬프트 최적화**: 간결하고 명확한 시스템 프롬프트
- **재시도 로직**: 네트워크 오류 시 자동 재시도
- **타임아웃 관리**: 20초 제한으로 응답성 보장

### 성능 지표
- **캐시 히트율**: 90%+ (반복 사용 시)
- **응답 시간**: 캐시 히트 시 0ms, API 호출 시 2-5초
- **동시 사용자**: 탭별 독립적 캐시로 확장성 확보

## 🔒 보안 고려사항

- API 키는 환경 변수로 관리
- JWT 토큰 기반 인증
- 입력값 검증 및 sanitization
- CORS 설정으로 허용된 도메인만 접근

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해 주세요.

---

**참고**: 이 프로젝트는 교육 및 연구 목적으로 제작되었습니다. 상업적 사용 시 OpenAI API 사용 정책을 준수해 주세요. 