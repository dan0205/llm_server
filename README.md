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
* Railway를 활용해 PostgreSQL 클라우드 데이터베이스를 생성하고, Flask 앱에서 연결 실습
* Redis의 개념을 이해하고 Docker 기반 Redis 환경을 구성하여 기본 명령어 및 Flask 연동 실습 진행

## 실습 내용
### Railway를 활용한 PostgreSQL 클라우드 DB 생성
1. Public Network 설정을 통해 외부 접속용 커넥션 URL 확인
2. SQLAlchemy에서 사용할 수 있도록 .env 파일에 DATABASE_URL 등록
### Flask 프로젝트에서 PostgreSQL 연결 구성
1. Python 가상환경(venv) 설정 및 활성화
2. flask, flask_sqlalchemy, python-dotenv, psycopg2 설치
3. SQLAlchemy로 모델 정의 및 Flask 앱과 연결

### Redis란?
* Redis(REmote DIctionary Server)는 인메모리 기반의 Key-Value 저장소로, 매우 빠른 읽기/쓰기 성능을 제공하는 NoSQL 데이터베이스이다.
* 데이터를 디스크가 아닌 RAM에 저장하여, DB에 접근하는 속도가 매우 빠르며 캐시, 세션 저장소, 메시지 브로커 등 다양한 용도로 활용된다.
* Redis는 단일 스레드로 동작하지만, CPU 연산보다 I/O 병목이 더 큰 캐시 용도에서는 오히려 높은 성능을 발휘한다.
* 데이터 유형으로는 문자열(String), 리스트(List), 해시(Hash), 셋(Set), 정렬된 셋(Sorted Set) 등이 있으며, TTL(Time to Live) 설정을 통해 자동 만료 기능도 지원한다.
### Docker 기반 Redis 환경을 구성하여 기본 명령어 및 Flask 연동 실습 진행
```
docker run -d --name redis-container -p 6379:6379 redis
```

