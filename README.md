# 전세 대출 Q&A 시스템

RAG(Retrieval-Augmented Generation) 기술을 활용한 전세 대출 관련 질문-답변 시스템입니다.

## 주요 기능

- 문서 업로드 및 자동 임베딩
  - 텍스트(.txt) 및 PDF(.pdf) 파일 지원
  - 문서 자동 분할 및 벡터화
  - ChromaDB를 이용한 벡터 저장소 관리

- 질문-답변
  - 자연어 질문 처리
  - 관련 문서 검색 및 답변 생성
  - 처리 과정 로깅 및 표시

## 기술 스택

- Backend
  - FastAPI
  - LangChain
  - ChromaDB
  - HuggingFace Embeddings
  - OpenAI GPT

- Frontend
  - Streamlit
  - React (예정)

## 프로젝트 구조

```
rag-project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 백엔드
│   └── services/
│       ├── __init__.py
│       ├── rag_service.py   # RAG 서비스 로직
│       └── document_loader.py # 문서 로더
├── frontend/
│   └── main.py              # Streamlit 프론트엔드
├── data/                    # 업로드된 문서 저장
├── chroma_db/              # 벡터 저장소
└── pyproject.toml          # 의존성 관리
```

## 설치 및 설정

1. Python 3.9 이상 설치

2. Poetry 설치
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. 프로젝트 의존성 설치
```bash
poetry install
```

4. 환경 변수 설정
`.env` 파일을 프로젝트 루트에 생성하고 다음 변수를 설정:
```env
OPENAI_API_KEY=your_openai_api_key
```

## 실행 방법

1. 백엔드 서버 실행
```bash
# 프로젝트 루트 디렉토리에서
uvicorn app.main:app --reload --app-dir .
```

2. 프론트엔드 실행
```bash
# 새로운 터미널에서
streamlit run frontend/main.py
```

3. API 문서 확인
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 사용 방법

1. 문서 업로드
   - 사이드바의 문서 업로드 영역에서 파일 선택
   - 지원 형식: .txt, .pdf

2. 질문하기
   - 질문 입력창에 자연어로 질문 입력
   - 시스템이 관련 문서를 검색하고 답변 생성

3. 처리 과정 확인
   - "처리 과정 보기" 버튼으로 상세 로그 확인
   - 검색된 문서, 생성된 답변 등 확인 가능

## 주의사항

- OpenAI API 키가 필요합니다
- 초기 문서 로딩 시 시간이 걸릴 수 있습니다
- PDF 파일의 경우 텍스트 추출 품질에 따라 결과가 달라질 수 있습니다