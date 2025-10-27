# 네이버 블로그 자동화 도구

이 도구는 네이버 블로그와 카페에 자동으로 콘텐츠를 게시하는 Streamlit 웹 애플리케이션입니다.

## 🌟 주요 기능

- **AI 콘텐츠 생성**: Google Gemini API를 활용한 자동 콘텐츠 생성
- **자동 포스팅**: 네이버 블로그/카페 자동 게시
- **이미지 관리**: 다중 이미지 업로드 및 관리
- **계정 관리**: 여러 계정 동시 관리
- **실시간 로그**: 작업 진행 상황 실시간 모니터링

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/shirtgit/naverblog.git
cd naverblog
```

### 2. 의존성 설치

#### 로컬 개발 환경 (전체 기능)
```bash
pip install -r requirements-local.txt
```

#### 클라우드 환경 또는 최소 설치
```bash
pip install -r requirements.txt
```

### 3. 보안 설정
API 키 설정을 위해 [보안 설정 가이드](SECURITY_SETUP.md)를 참조하세요.

### 4. 앱 실행
```bash
streamlit run main_streamlit.py
```

## 🔐 보안 설정

이 프로젝트는 API 키와 민감한 정보를 안전하게 관리합니다:

- ✅ API 키는 외부 설정 파일로 분리
- ✅ `.gitignore`로 민감한 파일 보호
- ✅ 예시 설정 파일 제공

자세한 설정 방법은 [SECURITY_SETUP.md](SECURITY_SETUP.md)를 확인하세요.

## 💡 환경별 지원

### 로컬 환경
- ✅ 모든 기능 완전 지원
- ✅ 파일/폴더 선택 다이얼로그
- ✅ Selenium 브라우저 자동화
- ✅ GUI 기능

### 클라우드 환경 (Streamlit Cloud)
- ✅ AI 콘텐츠 생성
- ✅ 파일 업로드 기능
- ❌ 브라우저 자동화 (Selenium 불가)
- ❌ GUI 파일 선택

> **참고**: 자동 포스팅 기능은 로컬 환경에서만 작동합니다. 클라우드에서는 콘텐츠 생성 및 관리 기능만 사용 가능합니다.

## 📁 프로젝트 구조

```
naverblog/
├── main_streamlit.py        # 메인 Streamlit 앱
├── ai/                      # AI 관련 모듈
│   └── gemini.py           # Gemini API 처리
├── .streamlit/             # Streamlit 설정
│   ├── secrets.toml        # 보안 설정 (Git 제외)
│   └── config.toml         # 일반 설정
├── requirements.txt        # Python 의존성
├── .gitignore             # Git 제외 파일
└── SECURITY_SETUP.md      # 보안 설정 가이드
```

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **AI**: Google Gemini API
- **Automation**: Selenium WebDriver
- **Image Processing**: Pillow
- **File Handling**: Python Standard Library

## 📝 사용 방법

1. **API 키 설정**: Google Gemini API 키를 설정 파일에 추가
2. **계정 정보 입력**: 네이버 계정 정보 입력
3. **콘텐츠 생성**: AI를 활용한 자동 콘텐츠 생성
4. **이미지 업로드**: 포스팅에 사용할 이미지 업로드
5. **자동 포스팅**: 설정된 계정으로 자동 게시

## ⚠️ 주의사항

- 이 도구는 교육 및 개인 사용 목적으로 제작되었습니다
- 네이버의 이용약관을 준수하여 사용하세요
- 과도한 자동화는 계정 제재를 받을 수 있습니다
- API 키와 계정 정보를 안전하게 관리하세요

## 🐛 문제 해결

문제가 발생한 경우:

1. [Issues](https://github.com/shirtgit/naverblog/issues)에서 유사한 문제 검색
2. 새로운 이슈 생성
3. 로그 메시지와 함께 상세한 설명 제공

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

기여를 환영합니다! Pull Request를 보내기 전에:

1. 코드 스타일 가이드 준수
2. 테스트 실행
3. 보안 설정 확인

---

## 📋 개발 로드맵

### ✅ 1주차: 기능 완성 + UI
1. 기능 완성
   - 파일 업로드 (ID,PW / 키워드 / 웹주소)
   - 업로드 한 파일 파싱
   - 캐시값
   - 글 & 사진 & 영상 업로드 자동화
   - 기타 기능
     - 댓글 허용기능 (카페)
     - 대기시간 최소, 최대값: 범위 내 random
2. UI
   1. **공용**
      - ID, PW 업로드 (버튼 + 리스트)
      - 키워드 업로드 (버튼 + 리스트)
      - 전화번호, API KEY 텍스트박스
      - 유동IP on/off버튼 (토글 or 버튼)  
   2. **나눠야 할 것(블로그 / 카페)**
      - 웹주소 업로드 (버튼 + 리스트)

### 🔄 2주차: 사진 및 영상 제작 + 글밥 미리 저장
1. Static 사진
    - 사진 폴더 위치추적
    - 5개를 올려야 하는데 10개가 저장되어 있다면? 최대한 랜덤으로 섞어서
    - 유사문서 방지를 위해 명암, 명도, 채도 등 랜덤으로 변경
2. 생성할 사진
   - RGB 랜덤
   - 형식)  
     전화번호  
     주소  
     업종
   - 키워드 (주소, 업종)은 흰색 또는 검정
   - 미리보기에서 잘리지 않을 비율로 설정
3. 생성할 영상
   - 생성한 사진을 영상으로 제작
   - 이것 역시 비율 고려

### 🎯 3주차: 글 생성 + 유동 IP
1. 글 생성
   - 글밥을 바탕으로 Gemini를 사용하여 글 생성 (소개 및 홍보글)
   - 이 때, 중간중간 사진 삽입 (3~4개)
   - 큰 비중을 차지하는것이 아니라, 여기에 시간을 많이 쏟을 이유는 없음
2. 유동 IP
   - 고객의 핸드폰 테더링을 이용
   - IP를 변경할 때마다 비행기모드 on/off

---

**⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!**