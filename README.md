# 1주차
## 실습 목표
* GitHub Pages, AWS Free Tier, Railway를 활용한 클라우드 배포 기초 학습

## 실습 내용
### GitHub Pages
1. GitHub 저장소 생성
2. Settings > Pages 에서 배포 브랜치 및 폴더 설정
3. * https://hyeonuk02.github.io/Mogakso_LLM/
   * 직접 배포한 테스트용 웹페이지입니다.

### Railway
1. Railway에서 프로젝트 생성
2. GitHub 저장소 연결 후 자동 배포 설정


# 2주차
## 실습 목표
- Railway를 활용해 PostgreSQL 클라우드 데이터베이스를 생성하고 Flask 앱에서 연동 실습
- Redis의 개념을 이해하고, Docker 기반 Redis 환경을 구성하여 기본 명령어 및 Flask 연동 실습 수행
---
## 실습 내용
  * **PostgreSQL**
    * Railway에서 PostgreSQL 클라우드 DB 생성
    * Public Network 설정을 통해 외부 접속용 커넥션 URL 확보  
    * SQLAlchemy에서 사용할 수 있도록 .env 파일에 DATABASE_URL 등록  
    * Flask 프로젝트에서 PostgreSQL 연결 구성 
    * Python 가상환경(venv) 설정 및 활성화 
    * flask, flask_sqlalchemy, python-dotenv, psycopg2 설치
    * SQLAlchemy로 모델 정의 및 Flask 앱과 연결

  * **Redis**
    * Redis란?
      * Redis(REmote DIctionary Server)는 인메모리 기반의 Key-Value 저장소로, 매우 빠른 읽기/쓰기 성능을 제공하는 NoSQL 데이터베이스이다. 
      * 데이터를 디스크가 아닌 RAM에 저장하여 빠른 접근 속도를 제공하며, 캐시, 세션 저장소, 메시지 브로커 등 다양한 용도로 활용된다.  
      * 단일 스레드 기반이지만, 캐시 용도로는 I/O 병목이 작아 높은 성능을 발휘한다.      
      * 지원 데이터 유형: 문자열(String), 리스트(List), 해시(Hash), 셋(Set), 정렬된 셋(Sorted Set) 등     
      * TTL(Time to Live) 기능으로 데이터의 자동 만료 설정 가능
      
  * **Docker 기반 Redis 환경을 구성하여 기본 명령어 및 Flask 연동 실습 진행**
  ```
  docker run -d --name redis-container -p 6379:6379 redis
  ```
    * Flask에서 redis-py로 Redis와 연동
    * set 및 get 명령어를 통해 Redis에 데이터 저장 및 조회
    * 브라우저를 통해 “Hello from Redis!” 응답 확인
    
## 3주차
### 실습 목표

- GitHub Actions를 활용해 코드 푸쉬 시 Railway로 자동 배포되는 CI/CD 파이프라인 구성
- 배포 자동화 과정에서 발생하는 인증, 서비스 ID 설정 문제 등을 해결하며 실전 경험 확보
- Railway 환경에서 배포 자동화 후 애플리케이션 정상 작동 확인
- 서버 상태 확인 및 로그 파일 기록을 통한 모니터링 및 로깅 기초 구현

---

### 실습 내용

#### GitHub Actions 설정
- `.github/workflows/deploy.yml` 파일 생성
- `main` 브랜치에 push 시 자동으로 배포되는 workflow 정의
- 공식 railway CLI 도커 이미지 (`ghcr.io/railwayapp/cli:latest`) 사용
- `RAILWAY_TOKEN`을 GitHub Secrets에 등록하여 인증 처리
- `railway up` 명령어를 사용해 배포 자동화 구성 완료

#### Railway CLI 및 프로젝트 연동
- 로컬에서 `railway login` 후, `railway link` 명령어로 프로젝트 연동
- 프로젝트 ID 및 서비스 ID 확보
- `.railway/project.json` 파일 자동 생성되지 않는 경우 수동 처리

#### 문제 해결 과정
- GitHub Actions에서 `Unauthorized. Please login with 'railway login'` 오류 발생
- 원인: `RAILWAY_TOKEN` 미등록 또는 잘못된 서비스 ID
- 해결: Secrets 등록 및 `.yml` 파일 수정 → 재배포 성공

#### 결과 확인
- GitHub Actions 로그에서 workflow 실행 확인
- Railway Dashboard에서 최신 커밋으로 배포 완료 확인
- 브라우저 접속 시 애플리케이션 정상 작동 확인

---

### 로그 관리 및 서버 모니터링 기초

#### 로그 관리
- Python `logging` 모듈을 사용해 로그 파일 저장 설정
    ```python
    logging.basicConfig(
        filename='logs/app.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    ```
- `logs` 폴더가 존재하지 않을 경우 자동 생성 처리
- Flask 앱 시작, DB 초기화, 요청 수신 등의 이벤트에 로그 삽입
- 로그 파일(`logs/app.log`)에 실시간으로 기록되는지 확인

#### 모니터링 기초
- `/` 경로 접속 시 Flask에서 DB 조회 결과 반환
- 정상 요청은 `logging.info()`, 오류 발생 시 `logging.error()`로 기록
- 브라우저 또는 curl을 통해 서버 상태 확인 및 로그 변화 추적

---

### 활용 기술 스택 및 도구

- **GitHub Actions** (CI/CD 자동화)
- **Railway CLI** / 배포용 Docker 이미지
- **GitHub Secrets** (RAILWAY_TOKEN)
- **Python Flask 앱** 기반의 클라우드 배포
- **Python logging 모듈** 기반의 로그 파일 저장
- **간단한 헬스 체크 및 로그 추적을 통한 서버 상태 모니터링**

---

### 요약

이번 실습을 통해 **자동 배포(CI/CD)**, **프로젝트 연동 및 문제 해결 경험**, **애플리케이션 상태 확인**, 그리고 **로그 기록 및 모니터링**까지 서버 운영에 필수적인 흐름을 처음부터 끝까지 경험할 수 있었습니다.

