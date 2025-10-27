# 네이버 블로그 자동화 도구 보안 설정 가이드

## 🔐 보안 설정 방법

이 프로젝트를 안전하게 사용하기 위해 API 키와 민감한 정보를 외부 설정 파일로 분리했습니다.

### 1. API 키 발급

#### Google Gemini API 키 발급
1. [Google AI Studio](https://aistudio.google.com/app/apikey) 접속
2. "Create API key" 클릭
3. 발급받은 API 키를 복사해 두세요 (AIzaSy로 시작)

### 2. 설정 파일 생성

#### 방법 1: Streamlit Secrets 사용 (권장)
```bash
# .streamlit/secrets.toml.example을 복사
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# 파일을 열어서 실제 API 키로 수정
# GOOGLE_GEMINI_API_KEY = "AIzaSy..." 부분을 실제 키로 교체
```

#### 방법 2: 환경 변수 사용
```bash
# .env.example을 복사
cp .env.example .env

# 파일을 열어서 실제 API 키로 수정
# GOOGLE_GEMINI_API_KEY=AIzaSy... 부분을 실제 키로 교체
```

### 3. 설정 파일 수정 예시

#### .streamlit/secrets.toml
```toml
[general]
GOOGLE_GEMINI_API_KEY = "AIzaSyDo6wlM9Q6SFKS-rpHoS_sJQabVt9OEDnI"  # 실제 키로 교체
DEFAULT_MIN_WAIT = 3
DEFAULT_MAX_WAIT = 7
DEFAULT_USE_DYNAMIC_IP = false

[debug]
ENABLE_DEBUG_LOGS = true
LOG_SELENIUM_ACTIONS = true
```

#### .env
```env
GOOGLE_GEMINI_API_KEY=AIzaSyDo6wlM9Q6SFKS-rpHoS_sJQabVt9OEDnI  # 실제 키로 교체
DEFAULT_MIN_WAIT=3
DEFAULT_MAX_WAIT=7
DEFAULT_USE_DYNAMIC_IP=false
ENABLE_DEBUG_LOGS=true
LOG_SELENIUM_ACTIONS=true
```

### 4. 앱 실행

```bash
# Streamlit 앱 실행
streamlit run main_streamlit.py
```

설정이 올바르면 앱이 시작될 때 API 키가 자동으로 인식됩니다.

## 🛡️ 보안 주의사항

### ⚠️ 절대 하지 말아야 할 것들
- `.env` 파일을 Git에 커밋하지 마세요
- `.streamlit/secrets.toml` 파일을 Git에 커밋하지 마세요
- API 키를 코드에 직접 입력하지 마세요
- API 키를 공개 저장소에 올리지 마세요

### ✅ 안전한 사용 방법
- 예시 파일(`.example`)만 Git에 커밋됩니다
- 실제 설정 파일은 `.gitignore`에 의해 제외됩니다
- API 키는 환경 변수나 secrets 파일에서만 관리됩니다

## 🔧 문제 해결

### API 키를 찾을 수 없다는 오류가 나타날 때
1. `.streamlit/secrets.toml` 또는 `.env` 파일이 존재하는지 확인
2. 파일 내 API 키가 올바르게 설정되었는지 확인
3. API 키가 유효한지 확인 (Google AI Studio에서 확인)

### Streamlit에서 secrets를 인식하지 못할 때
```bash
# Streamlit 캐시 초기화
streamlit cache clear
```

### 환경 변수가 로드되지 않을 때
```python
# python-dotenv 설치
pip install python-dotenv

# 수동으로 .env 로드 (필요시)
from dotenv import load_dotenv
load_dotenv()
```

## 📁 파일 구조

```
naverblog/
├── .streamlit/
│   ├── secrets.toml          # 실제 보안 설정 (Git 제외)
│   └── secrets.toml.example  # 예시 파일 (Git 포함)
├── .env                      # 환경 변수 (Git 제외)
├── .env.example              # 예시 파일 (Git 포함)
├── .gitignore               # Git 제외 파일 목록
└── main_streamlit.py        # 메인 앱
```

## 🚀 배포 시 주의사항

### GitHub에 업로드할 때
- `.gitignore`가 올바르게 설정되어 있는지 확인
- `git status`로 민감한 파일이 추가되지 않았는지 확인
- 예시 파일만 커밋되는지 확인

### Streamlit Cloud 배포 시
1. GitHub 저장소 연결
2. Streamlit Cloud 대시보드에서 secrets 설정
3. `GOOGLE_GEMINI_API_KEY` 환경 변수 추가

이 가이드를 따라하면 API 키와 민감한 정보를 안전하게 관리할 수 있습니다.