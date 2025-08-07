# 🤖 신조어 해석기 API

FastAPI 기반의 한국어 신조어 해석 서비스입니다. OpenAI GPT-4o를 활용하여 문맥을 고려한 정확한 신조어 해석을 제공합니다.

## ✨ 주요 기능

### 🧠 AI 기반 문맥 분석
- **문맥 인식**: 사용자가 제공한 문장의 문맥을 분석하여 정확한 의미 추출
- **감정 분석**: 문장의 감정적 톤에 맞는 해석 제공
- **도메인 인식**: 게임, 소셜미디어, 업무, 학교 등 사용 맥락별 해석
- **대화 히스토리**: 이전 대화를 고려한 연속적인 문맥 이해

### 🔍 고급 분석 기능
- **유사어 검색**: 관련된 신조어들 자동 추천
- **모호성 해결**: 문맥이 모호한 경우 명확화 질문 제공
- **일괄 분석**: 여러 신조어를 동시에 분석
- **실시간 캐싱**: Redis를 통한 빠른 응답

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# 저장소 클론
git clone https://github.com/dan0205/llm_server.git
cd llm_server

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 다음 내용을 추가하세요:
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/llm_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your_secret_key_here
```

### 3. 데이터베이스 실행
```bash
# PostgreSQL과 Redis 실행
docker-compose up -d
```

### 4. 서버 실행
```bash
# 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API 사용법

### 기본 신조어 해석
```bash
curl -X GET "http://localhost:8000/api/v1/jargons/interpret/대박"
```

### 문맥 기반 해석
```bash
curl -X POST "http://localhost:8000/api/v1/jargons/interpret-contextual" \
  -H "Content-Type: application/json" \
  -d '{
    "term": "대박",
    "context_sentence": "오늘 시험에서 대박 났어!"
  }'
```

### 대화 분석
```bash
curl -X POST "http://localhost:8000/api/v1/jargons/analyze-conversation" \
  -H "Content-Type: application/json" \
  -d '"오늘 친구가 대박이라고 했는데 무슨 뜻이야?"'
```

### 유사한 신조어 찾기
```bash
curl -X GET "http://localhost:8000/api/v1/jargons/similar/대박"
```

### 모호한 신조어 명확화
```bash
curl -X POST "http://localhost:8000/api/v1/jargons/clarify" \
  -H "Content-Type: application/json" \
  -d '{
    "term": "대박",
    "context": "이 영화 대박이야"
  }'
```

## 🧪 테스트

AI 서비스 기능을 테스트하려면:
```bash
python test_ai_service.py
```

## 🏗️ 프로젝트 구조

```
llm_server/
├── app/
│   ├── api/v1/           # API 라우터
│   │   ├── auth_router.py    # 인증 API
│   │   └── jargon_router.py  # 신조어 API
│   ├── core/             # 핵심 설정
│   │   ├── config.py         # 환경 변수
│   │   ├── database.py       # DB 연결
│   │   └── security.py       # 보안 설정
│   ├── models/           # 데이터베이스 모델
│   ├── schemas/          # Pydantic 스키마
│   ├── services/         # 비즈니스 로직
│   │   ├── ai_service.py     # AI 서비스 (핵심)
│   │   ├── jargon_service.py # 신조어 처리
│   │   └── auth_service.py   # 인증 처리
│   └── main.py          # 애플리케이션 진입점
├── docker-compose.yml   # 컨테이너 설정
├── requirements.txt     # Python 의존성
└── test_ai_service.py  # AI 서비스 테스트
```

## 🧠 AI 서비스 상세 설명

### ContextAnalyzer 클래스
- **감정 분석**: 키워드 기반 감정 감지 (긍정/부정/놀람)
- **격식 분석**: 문장의 격식 수준 판단
- **도메인 분석**: 게임, 소셜미디어, 업무, 학교 등 사용 맥락 분류

### ConversationManager 클래스
- **대화 히스토리 관리**: 최근 10개 메시지 유지
- **문맥 연속성**: 이전 대화를 고려한 해석
- **메모리 효율성**: 자동 히스토리 정리

### 주요 AI 함수들
1. **`interpret_with_llm()`**: 핵심 해석 함수
2. **`analyze_conversation_context()`**: 대화 문맥 분석
3. **`get_similar_terms()`**: 유사어 검색
4. **`clarify_ambiguous_term()`**: 모호성 해결

## 🔧 설정 옵션

### AI 모델 설정
- **모델**: GPT-4o (최신 모델 사용)
- **Temperature**: 0.7 (창의성과 일관성의 균형)
- **Max Tokens**: 1000 (충분한 응답 길이)

### 캐싱 설정
- **Redis TTL**: 1시간 (3600초)
- **캐시 키**: 신조어 + 문맥 해시 조합
- **문맥별 캐싱**: 같은 신조어라도 문맥이 다르면 별도 캐싱

## 🚀 성능 최적화

1. **Redis 캐싱**: 자주 요청되는 신조어는 캐시에서 즉시 응답
2. **비동기 처리**: 모든 AI 호출과 DB 작업이 비동기로 처리
3. **배치 처리**: 여러 신조어를 동시에 분석 가능
4. **문맥별 캐싱**: 문맥이 다른 경우 별도 캐싱으로 정확성 향상

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요. 