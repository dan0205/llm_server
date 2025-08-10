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

## 🔧 API 엔드포인트

### 신조어 해석
```
GET /api/v1/jargons/interpret/{term}?context={context}
```

**응답 예시:**
```json
{
  "term": "갑분싸",
  "meaning": "갑자기 분위기가 싸해진다는 뜻",
  "example": "회의 중에 갑분싸가 됐어.",
  "context_analysis": {
    "detected_emotion": "neutral",
    "formality_level": "casual",
    "usage_domain": "general"
  },
  "additional_info": {
    "similar_terms": ["갑작스러운", "분위기 전환"],
    "usage_tips": "일상 대화에서 자주 사용",
    "origin": "갑자기 + 분위기 + 싸하다"
  }
}
```

## 🎯 사용법

1. **웹페이지에서 신조어 선택**: 마우스로 드래그하여 신조어 선택
2. **자동 해석**: 선택된 텍스트가 자동으로 분석됨
3. **툴팁 확인**: 상세한 해석 결과를 툴팁으로 확인
4. **캐시 활용**: 동일한 신조어는 즉시 응답

## 🔍 캐싱 전략

- **Redis 캐시**: 24시간 TTL로 해석 결과 저장
- **문맥 기반 키**: 신조어 + 문맥 해시로 고유 캐시 키 생성
- **계층적 조회**: 캐시 → DB → OpenAI API 순서로 조회

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

- **비동기 처리**: FastAPI의 비동기 특성 활용
- **연결 풀링**: 데이터베이스 및 Redis 연결 풀 사용
- **배치 처리**: 여러 신조어 동시 해석 지원

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