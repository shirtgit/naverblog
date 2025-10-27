import streamlit as st
import pandas as pd
import json
import os
import threading
import time
from io import StringIO

# 기존 모듈들 import
from cache import upload_cache
from task.streamlit_task_executor import task_executor
from ai import gemini
from data import text_data, list_data, box_data, button_data
from utils import parsing
from ui import streamlit_log as log

# Streamlit 페이지 설정
st.set_page_config(
    page_title="네이버 블로그/카페 자동 포스팅",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e7d32;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        margin: 0.5rem 0;
    }
    .status-blog {
        background-color: #e3f2fd;
        color: #1976d2;
    }
    .status-cafe {
        background-color: #f3e5f5;
        color: #7b1fa2;
    }
    .status-both {
        background-color: #e8f5e8;
        color: #388e3c;
    }
    .upload-area {
        border: 2px dashed #cccccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Session State 초기화
def init_session_state():
    """세션 상태 초기화"""
    if 'platform_choice' not in st.session_state:
        st.session_state.platform_choice = "블로그"
    if 'use_dynamic_ip' not in st.session_state:
        st.session_state.use_dynamic_ip = True
    if 'allow_comments' not in st.session_state:
        st.session_state.allow_comments = True
    if 'accounts_data' not in st.session_state:
        st.session_state.accounts_data = []
    if 'keywords_data' not in st.session_state:
        st.session_state.keywords_data = []
    if 'blog_data' not in st.session_state:
        st.session_state.blog_data = []
    if 'cafe_data' not in st.session_state:
        st.session_state.cafe_data = []
    if 'titles_data' not in st.session_state:
        st.session_state.titles_data = []
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    if 'api_key_verified' not in st.session_state:
        st.session_state.api_key_verified = False
    if 'api_verification_message' not in st.session_state:
        st.session_state.api_verification_message = ''
    if 'verified_model' not in st.session_state:
        st.session_state.verified_model = 'gemini-2.5-flash'
    if 'naver_id' not in st.session_state:
        st.session_state.naver_id = ''
    if 'naver_password' not in st.session_state:
        st.session_state.naver_password = ''

def load_cache_data():
    """캐시 데이터 로드"""
    try:
        # 텍스트 캐시 로드
        text_cache_path = os.path.join(os.getcwd(), "cache", ".cache_text")
        if os.path.exists(text_cache_path):
            with open(text_cache_path, "r", encoding="utf-8") as f:
                text_cache = json.load(f)
                st.session_state.platform_choice = ["블로그", "카페", "둘 다"][text_cache.get("status_rb", 0)]
                st.session_state.use_dynamic_ip = text_cache.get("toggle_button", True)
                st.session_state.allow_comments = text_cache.get("comment_cb", True)
                st.session_state.api_key = text_cache.get("api_key", "")
                st.session_state.naver_id = text_cache.get("naver_id", "")
                st.session_state.naver_password = text_cache.get("naver_password", "")
                # API 키가 로드되면 재인증 필요
                st.session_state.api_key_verified = False
        
        # CSV 캐시 로드
        cache_files = {
            'accounts_data': '.cache_account',
            'keywords_data': '.cache_keyword', 
            'blog_data': '.cache_blog',
            'cafe_data': '.cache_cafe',
            'titles_data': '.cache_title'
        }
        
        for state_key, cache_file in cache_files.items():
            cache_path = os.path.join(os.getcwd(), "cache", cache_file)
            if os.path.exists(cache_path):
                df = pd.read_csv(cache_path, encoding='utf-8')
                st.session_state[state_key] = df.to_dict('records')
                
    except Exception as e:
        st.error(f"캐시 데이터 로드 중 오류가 발생했습니다: {str(e)}")

def save_cache_data():
    """캐시 데이터 저장"""
    try:
        # 텍스트 캐시 저장
        text_cache = {
            "status_rb": ["블로그", "카페", "둘 다"].index(st.session_state.platform_choice),
            "toggle_button": st.session_state.use_dynamic_ip,
            "comment_cb": st.session_state.allow_comments,
            "waiting_min": st.session_state.get('waiting_min', 5),
            "waiting_max": st.session_state.get('waiting_max', 10),
            "api_key": st.session_state.get('api_key', ''),
            "phone_number": st.session_state.get('phone_number', ''),
            "content_input": st.session_state.get('content_template', ''),
            "naver_id": st.session_state.get('naver_id', ''),
            "naver_password": st.session_state.get('naver_password', '')
        }
        
        text_cache_path = os.path.join(os.getcwd(), "cache", ".cache_text")
        os.makedirs(os.path.dirname(text_cache_path), exist_ok=True)
        with open(text_cache_path, "w", encoding="utf-8") as f:
            json.dump(text_cache, f, ensure_ascii=False, indent=2)
        
        # CSV 캐시 저장
        cache_mappings = {
            'accounts_data': '.cache_account',
            'keywords_data': '.cache_keyword',
            'blog_data': '.cache_blog', 
            'cafe_data': '.cache_cafe',
            'titles_data': '.cache_title'
        }
        
        for state_key, cache_file in cache_mappings.items():
            if st.session_state[state_key]:
                df = pd.DataFrame(st.session_state[state_key])
                cache_path = os.path.join(os.getcwd(), "cache", cache_file)
                df.to_csv(cache_path, index=False, encoding='utf-8')
                
    except Exception as e:
        st.error(f"캐시 데이터 저장 중 오류가 발생했습니다: {str(e)}")

def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        st.markdown("### ⚙️ 설정")
        
        # 플랫폼 선택
        platform_choice = st.radio(
            "플랫폼 선택",
            ["블로그", "카페", "둘 다"],
            index=["블로그", "카페", "둘 다"].index(st.session_state.platform_choice)
        )
        st.session_state.platform_choice = platform_choice
        
        # 현재 상태 표시
        status_class = {
            "블로그": "status-blog",
            "카페": "status-cafe", 
            "둘 다": "status-both"
        }[platform_choice]
        
        st.markdown(f"""
        <div class="status-badge {status_class}">
            현재 상태: {platform_choice}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 대기시간 설정
        st.markdown("#### ⏱️ 대기시간 설정")
        col1, col2 = st.columns(2)
        with col1:
            waiting_min = st.number_input("최소 (분)", min_value=1, max_value=60, value=5, key="waiting_min")
        with col2:
            waiting_max = st.number_input("최대 (분)", min_value=1, max_value=60, value=10, key="waiting_max")
        
        # 유동 IP 설정
        use_dynamic_ip = st.toggle("유동 IP 사용", value=st.session_state.use_dynamic_ip)
        st.session_state.use_dynamic_ip = use_dynamic_ip
        
        st.markdown("---")
        
        # 핸드폰 번호만 사이드바에 유지
        st.markdown("#### � 핸드폰 번호")
        phone_number = st.text_input("핸드폰 번호", value=st.session_state.get('phone_number', ''), key="phone_number")
        
        # 카페 설정 (카페 선택 시에만 표시)
        if platform_choice in ["카페", "둘 다"]:
            st.markdown("#### 💬 카페 설정")
            allow_comments = st.toggle("댓글 기능 허용", value=st.session_state.allow_comments)
            st.session_state.allow_comments = allow_comments

def render_api_auth_section():
    """API 키 인증 섹션 렌더링"""
    st.markdown('<div class="section-header">🔑 Gemini API 인증</div>', unsafe_allow_html=True)
    
    # API 키 입력 및 인증
    col1, col2 = st.columns([3, 1])
    
    with col1:
        api_key = st.text_input(
            "Gemini API 키",
            value=st.session_state.get('api_key', ''),
            type="password",
            key="api_key_input",
            placeholder="여기에 Gemini API 키를 입력하세요...",
            help="Google AI Studio에서 발급받은 API 키를 입력해주세요."
        )
        # 세션 상태 업데이트
        if api_key != st.session_state.get('api_key', ''):
            st.session_state.api_key = api_key
            st.session_state.api_key_verified = False  # 키가 변경되면 재인증 필요
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # 버튼 위치 맞추기
        verify_button = st.button(
            "🔐 인증",
            disabled=not st.session_state.get('api_key', '').strip() or st.session_state.is_running,
            use_container_width=True,
            type="primary"
        )
    
    # 인증 버튼 클릭 시
    if verify_button and st.session_state.get('api_key', '').strip():
        verify_api_key()
    
    # 인증 상태 표시
    if st.session_state.get('api_verification_message', ''):
        if st.session_state.api_key_verified:
            st.success(f"✅ {st.session_state.api_verification_message}")
        else:
            st.error(f"❌ {st.session_state.api_verification_message}")
    
    # API 키 정보 안내
    with st.expander("📋 API 키 발급 방법", expanded=False):
        st.markdown("""
        **Google Gemini API 키 발급 방법:**
        
        1. [Google AI Studio](https://aistudio.google.com/) 접속
        2. 구글 계정으로 로그인
        3. 'Get API Key' 버튼 클릭
        4. 'Create API Key' 선택
        5. 프로젝트 선택 또는 새 프로젝트 생성
        6. 생성된 API 키를 복사하여 위 입력창에 붙여넣기
        
        **주의사항:**
        - API 키는 안전하게 보관하세요
        - 다른 사람과 공유하지 마세요
        - 필요시 언제든 재생성할 수 있습니다
        """)

def verify_api_key():
    """API 키 유효성 검증"""
    try:
        api_key = st.session_state.get('api_key', '').strip()
        
        if not api_key:
            st.session_state.api_verification_message = "API 키를 입력해주세요."
            st.session_state.api_key_verified = False
            return
        
        # 새로운 Gemini API 클라이언트 사용
        from google import genai
        
        # API 키로 클라이언트 초기화
        client = genai.Client(api_key=api_key)
        
        # 최신 모델들을 순서대로 시도
        available_models = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
        
        for model_name in available_models:
            try:
                # 간단한 테스트 요청
                response = client.models.generate_content(
                    model=model_name,
                    contents="안녕하세요"
                )
                
                if response and response.text:
                    st.session_state.api_key_verified = True
                    st.session_state.api_verification_message = f"API 키 인증이 완료되었습니다! (사용 모델: {model_name})"
                    add_log(f"Gemini API 키 인증이 완료되었습니다. 사용 모델: {model_name}", "SUCCESS")
                    
                    # 성공한 모델을 세션에 저장
                    st.session_state.verified_model = model_name
                    return
                    
            except Exception as model_error:
                # 이 모델이 작동하지 않으면 다음 모델 시도
                continue
        
        # 모든 모델이 실패한 경우
        st.session_state.api_key_verified = False
        st.session_state.api_verification_message = "지원되는 Gemini 모델을 찾을 수 없습니다."
        add_log("지원되는 Gemini 모델을 찾을 수 없습니다.", "ERROR")
            
    except Exception as e:
        st.session_state.api_key_verified = False
        error_msg = str(e)
        
        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
            st.session_state.api_verification_message = "유효하지 않은 API 키입니다."
        elif "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
            st.session_state.api_verification_message = "API 할당량이 초과되었습니다."
        elif "permission" in error_msg.lower() or "denied" in error_msg.lower():
            st.session_state.api_verification_message = "API 키 권한이 부족합니다."
        elif "404" in error_msg and "not found" in error_msg.lower():
            st.session_state.api_verification_message = "요청한 모델을 찾을 수 없습니다. API 키를 확인해주세요."
        elif "authentication" in error_msg.lower():
            st.session_state.api_verification_message = "API 키 인증에 실패했습니다."
        else:
            st.session_state.api_verification_message = f"API 키 검증 중 오류가 발생했습니다: {error_msg}"
        
        add_log(f"API 키 인증 실패: {st.session_state.api_verification_message}", "ERROR")

def render_naver_login_section():
    """네이버 로그인 섹션 렌더링"""
    st.markdown('<div class="section-header">🔐 네이버 로그인</div>', unsafe_allow_html=True)
    
    # 네이버 로그인 정보 입력
    col1, col2 = st.columns(2)
    
    with col1:
        naver_id = st.text_input(
            "네이버 아이디",
            value=st.session_state.get('naver_id', ''),
            key="naver_id_input",
            placeholder="네이버 아이디를 입력하세요",
            help="네이버 블로그/카페 자동화에 사용할 네이버 계정 아이디"
        )
        # 세션 상태 업데이트
        if naver_id != st.session_state.get('naver_id', ''):
            st.session_state.naver_id = naver_id
    
    with col2:
        naver_password = st.text_input(
            "네이버 패스워드",
            value=st.session_state.get('naver_password', ''),
            type="password",
            key="naver_password_input",
            placeholder="네이버 패스워드를 입력하세요",
            help="네이버 블로그/카페 자동화에 사용할 네이버 계정 패스워드"
        )
        # 세션 상태 업데이트
        if naver_password != st.session_state.get('naver_password', ''):
            st.session_state.naver_password = naver_password
    
    # 로그인 정보 상태 표시
    if st.session_state.get('naver_id', '').strip() and st.session_state.get('naver_password', '').strip():
        st.success("✅ 네이버 로그인 정보가 입력되었습니다.")
    elif st.session_state.get('naver_id', '').strip() or st.session_state.get('naver_password', '').strip():
        st.warning("⚠️ 아이디와 패스워드를 모두 입력해주세요.")
    else:
        st.info("💡 네이버 블로그/카페 자동화를 위해 네이버 계정 정보를 입력해주세요.")
    
    # 보안 안내
    with st.expander("🔒 보안 및 개인정보 보호", expanded=False):
        st.markdown("""
        **개인정보 보호 안내:**
        
        - 입력된 아이디와 패스워드는 현재 세션에서만 사용됩니다
        - 브라우저를 닫으면 모든 정보가 삭제됩니다
        - 서버나 외부에 저장되지 않습니다
        - 오직 네이버 자동 로그인 용도로만 사용됩니다
        
        **권장사항:**
        - 2단계 인증이 설정된 계정의 경우 앱 비밀번호를 사용하세요
        - 가능하면 테스트 전용 계정을 사용하는 것을 권장합니다
        - 작업 완료 후 브라우저를 닫아 정보를 완전히 삭제하세요
        """)

def render_file_upload_section():
    """파일 업로드 섹션 렌더링"""
    st.markdown('<div class="section-header">📁 파일 관리</div>', unsafe_allow_html=True)
    
    # 탭으로 구분
    tabs = st.tabs(["계정 관리", "키워드 관리", "웹주소 관리", "제목 관리"])
    
    with tabs[0]:  # 계정 관리
        st.markdown("#### 👤 계정 정보")
        uploaded_accounts = st.file_uploader(
            "계정 파일 업로드 (CSV)", 
            type=['csv'], 
            key="accounts_uploader",
            help="형식: 계정명, 비밀번호, 장소"
        )
        
        if uploaded_accounts:
            try:
                df = pd.read_csv(uploaded_accounts, encoding='utf-8')
                st.session_state.accounts_data = df.to_dict('records')
                st.success(f"✅ {len(df)}개의 계정이 업로드되었습니다.")
            except Exception as e:
                st.error(f"파일 업로드 오류: {str(e)}")
        
        # 계정 목록 표시
        if st.session_state.accounts_data:
            df_accounts = pd.DataFrame(st.session_state.accounts_data)
            # 비밀번호 열 숨기기
            display_df = df_accounts.copy()
            if '비밀번호' in display_df.columns:
                display_df['비밀번호'] = '*' * 8
            st.dataframe(display_df, use_container_width=True)
    
    with tabs[1]:  # 키워드 관리
        st.markdown("#### 🔍 키워드 정보")
        uploaded_keywords = st.file_uploader(
            "키워드 파일 업로드 (CSV)",
            type=['csv'],
            key="keywords_uploader", 
            help="형식: 주소, 업체, 파일 경로, 해시태그"
        )
        
        if uploaded_keywords:
            try:
                df = pd.read_csv(uploaded_keywords, encoding='utf-8')
                st.session_state.keywords_data = df.to_dict('records')
                st.success(f"✅ {len(df)}개의 키워드가 업로드되었습니다.")
            except Exception as e:  
                st.error(f"파일 업로드 오류: {str(e)}")
        
        if st.session_state.keywords_data:
            st.dataframe(pd.DataFrame(st.session_state.keywords_data), use_container_width=True)
    
    with tabs[2]:  # 웹주소 관리
        st.markdown("#### 🌐 웹주소 정보")
        
        # 블로그/카페에 따라 다른 업로더 표시
        if st.session_state.platform_choice in ["블로그", "둘 다"]:
            st.markdown("##### 📝 블로그")
            st.info("* 계정 파일 업로드 시 자동으로 업로드 됩니다.")
            if st.session_state.blog_data:
                st.dataframe(pd.DataFrame(st.session_state.blog_data), use_container_width=True)
        
        if st.session_state.platform_choice in ["카페", "둘 다"]:
            st.markdown("##### ☕ 카페")
            uploaded_cafe = st.file_uploader(
                "카페 파일 업로드 (CSV)",
                type=['csv'],
                key="cafe_uploader",
                help="형식: 카페 주소, 게시판 이름"
            )
            
            if uploaded_cafe:
                try:
                    df = pd.read_csv(uploaded_cafe, encoding='utf-8')
                    st.session_state.cafe_data = df.to_dict('records')
                    st.success(f"✅ {len(df)}개의 카페가 업로드되었습니다.")
                except Exception as e:
                    st.error(f"파일 업로드 오류: {str(e)}")
            
            if st.session_state.cafe_data:
                st.dataframe(pd.DataFrame(st.session_state.cafe_data), use_container_width=True)
    
    with tabs[3]:  # 제목 관리
        st.markdown("#### 📰 제목 정보")
        uploaded_titles = st.file_uploader(
            "제목 파일 업로드 (CSV)",
            type=['csv'],
            key="titles_uploader",
            help="형식: 제목"
        )
        
        if uploaded_titles:
            try:
                df = pd.read_csv(uploaded_titles, encoding='utf-8')
                st.session_state.titles_data = df.to_dict('records')
                st.success(f"✅ {len(df)}개의 제목이 업로드되었습니다.")
            except Exception as e:
                st.error(f"파일 업로드 오류: {str(e)}")
        
        if st.session_state.titles_data:
            st.dataframe(pd.DataFrame(st.session_state.titles_data), use_container_width=True)

def render_content_section():
    """콘텐츠 작성 섹션 렌더링"""
    st.markdown('<div class="section-header">✍️ 콘텐츠 작성</div>', unsafe_allow_html=True)
    
    # 안내 메시지 
    with st.expander("📋 폼 형식 지정 안내", expanded=False):
        st.markdown("""
        **[본문]을 기준으로 서론, 본문, 결론으로 나뉘어집니다.**
        
        - 본문은 AI로 작성한 1500자 내외의 글이며, keyword.csv를 통해 업로드한 이미지 중 랜덤으로 5개가 들어갑니다.
        - **%주소%** 문자열은 주소 열의 데이터로 치환됩니다.
        - **%업체%** 문자열은 업체 열의 데이터로 치환됩니다.
        - **%썸네일%** 문자열은 썸네일 사진으로 치환됩니다.
        - **%영상%** 문자열은 썸네일 사진을 바탕으로 제작된 영상으로 치환됩니다.
        
        **예시:**
        ```
        %주소%이고, %업체%입니다.
        %썸네일%
        [본문]
        %영상%
        감사합니다.
        ```
        """)
    
    # 콘텐츠 템플릿 입력
    content_template = st.text_area(
        "콘텐츠 템플릿",
        value=st.session_state.get('content_template', ''),
        height=300,
        key="content_template",
        help="위의 안내에 따라 콘텐츠 템플릿을 작성해주세요."
    )

def render_execution_section():
    """실행 섹션 렌더링"""
    st.markdown('<div class="section-header">🚀 작업 실행</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button(
            "📝 작업 수행", 
            disabled=st.session_state.is_running,
            use_container_width=True,
            type="primary"
        ):
            start_automation()
    
    with col2:
        if st.button("💾 설정 저장", use_container_width=True):
            save_cache_data()
            st.success("✅ 설정이 저장되었습니다!")
    
    with col3:
        if st.button("🔄 설정 불러오기", use_container_width=True):
            load_cache_data()
            st.success("✅ 설정을 불러왔습니다!")
            st.rerun()

def render_log_section():
    """로그 섹션 렌더링"""
    st.markdown('<div class="section-header">📋 실행 로그</div>', unsafe_allow_html=True)
    
    # 자동 새로고침 설정 (작업 실행 중일 때만)
    if st.session_state.is_running:
        st.markdown("🔄 **작업 실행 중... (자동 새로고침)**")
    
    # 로그 표시 영역
    log_container = st.container()
    
    with log_container:
        if st.session_state.logs:
            # 최근 로그부터 표시 (스크롤을 위해 역순으로 표시하지 않음)
            recent_logs = st.session_state.logs[-50:] if len(st.session_state.logs) > 50 else st.session_state.logs
            
            for log_entry in recent_logs:
                timestamp = log_entry.get('timestamp', '')
                message = log_entry.get('message', '')
                level = log_entry.get('level', 'INFO')
                
                # 로그 레벨에 따른 색상 설정
                color = {
                    'INFO': '#333333',
                    'SUCCESS': '#4caf50', 
                    'WARNING': '#ff9800',
                    'ERROR': '#f44336'
                }.get(level, '#333333')
                
                st.markdown(f"""
                <div style="
                    padding: 0.5rem;
                    margin: 0.2rem 0;
                    border-left: 3px solid {color};
                    background-color: #f8f9fa;
                    font-family: monospace;
                    font-size: 0.9rem;
                ">
                    <span style="color: #666;">{timestamp}</span> 
                    <span style="color: {color};">[{level}]</span> 
                    {message}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("아직 실행 로그가 없습니다.")
    
    # 버튼들
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 로그 새로고침"):
            st.rerun()
    
    with col2:
        if st.button("🗑️ 로그 지우기"):
            st.session_state.logs = []
            st.rerun()
    
    # 작업 실행 중일 때 자동 새로고침
    if st.session_state.is_running:
        time.sleep(2)  # 2초마다 새로고침
        st.rerun()

def add_log(message, level="INFO"):
    """로그 추가"""
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.append({
        'timestamp': timestamp,
        'message': message,
        'level': level
    })

def start_automation():
    """자동화 작업 시작"""
    if not validate_inputs():
        return
    
    st.session_state.is_running = True
    add_log("자동화 작업을 시작합니다.", "INFO")
    
    # 별도 스레드에서 작업 실행
    thread = threading.Thread(target=run_automation_task)
    thread.daemon = True
    thread.start()
    
    st.rerun()

def validate_inputs():
    """입력값 검증"""
    # API 키 검증
    if not st.session_state.get('api_key', '').strip():
        st.error("❌ Gemini API 키를 입력해주세요.")
        add_log("API 키가 입력되지 않았습니다.", "ERROR")
        return False
    
    if not st.session_state.get('api_key_verified', False):
        st.error("❌ API 키를 먼저 인증해주세요.")
        add_log("API 키가 인증되지 않았습니다.", "ERROR")
        return False
    
    # 네이버 로그인 정보 검증
    if not st.session_state.get('naver_id', '').strip():
        st.error("❌ 네이버 아이디를 입력해주세요.")
        add_log("네이버 아이디가 입력되지 않았습니다.", "ERROR")
        return False
    
    if not st.session_state.get('naver_password', '').strip():
        st.error("❌ 네이버 패스워드를 입력해주세요.")
        add_log("네이버 패스워드가 입력되지 않았습니다.", "ERROR")
        return False
    
    if not st.session_state.accounts_data:
        st.error("❌ 계정 정보를 업로드해주세요.")
        add_log("계정 정보가 없습니다.", "ERROR")
        return False
    
    if not st.session_state.keywords_data:
        st.error("❌ 키워드 정보를 업로드해주세요.")
        add_log("키워드 정보가 없습니다.", "ERROR")
        return False
    
    if st.session_state.platform_choice == "카페" and not st.session_state.cafe_data:
        st.error("❌ 카페 정보를 업로드해주세요.")
        add_log("카페 정보가 없습니다.", "ERROR")
        return False
    
    if not st.session_state.get('content_template', '').strip():
        st.error("❌ 콘텐츠 템플릿을 작성해주세요.")
        add_log("콘텐츠 템플릿이 없습니다.", "ERROR")
        return False
    
    return True

def run_automation_task():
    """자동화 작업 실행 (별도 스레드)"""
    try:
        add_log("작업 환경을 초기화합니다.", "INFO")
        
        # API 키 설정
        api_key = st.session_state.get('api_key', '')
        task_executor.set_api_key(api_key)
        add_log(f"API 키를 설정했습니다.", "SUCCESS")
        
        # 웹드라이버 초기화
        if not task_executor.init():
            add_log("웹드라이버 초기화에 실패했습니다.", "ERROR")
            return
        add_log("웹드라이버를 초기화했습니다.", "SUCCESS")
        
        # 네이버 로그인 정보 사용 (Streamlit에서 입력한 정보 우선)
        naver_id = st.session_state.get('naver_id', '').strip()
        naver_password = st.session_state.get('naver_password', '').strip()
        
        # 계정 정보에서 장소 정보 가져오기 (첫 번째 계정 사용)
        place = ""
        if st.session_state.accounts_data:
            account = st.session_state.accounts_data[0]
            place = account.get('장소', '')
            # 네이버 로그인 정보가 없으면 계정 데이터 사용 (호환성 유지)
            if not naver_id:
                naver_id = account.get('계정명', '')
            if not naver_password:
                naver_password = account.get('비밀번호', '')
        
        id_val = naver_id
        pw_val = naver_password
        
        add_log(f"로그인을 시도합니다. (계정: {id_val})", "INFO")
        if not task_executor.execute_login(id_val, pw_val):
            add_log("로그인에 실패했습니다.", "ERROR")
            return
        
        # 공통 설정
        waiting_min = st.session_state.get('waiting_min', 5)
        waiting_max = st.session_state.get('waiting_max', 10)
        use_dynamic_ip = st.session_state.get('use_dynamic_ip', False)
        content_template = st.session_state.get('content_template', '')
        
        # 플랫폼에 따른 포스팅 실행
        if st.session_state.platform_choice in ["블로그", "둘 다"]:
            add_log("블로그 포스팅을 시작합니다.", "INFO")
            
            # 블로그는 첫 번째 계정의 장소를 카테고리로 사용
            category_name = place if place else "일반"
            
            task_executor.post_blog(
                contents_data=st.session_state.keywords_data,
                category_name=category_name,
                id_val=id_val,
                pw_val=pw_val,
                place=place,
                titles_data=st.session_state.titles_data,
                content_template=content_template,
                use_dynamic_ip=use_dynamic_ip
            )
            
        if st.session_state.platform_choice in ["카페", "둘 다"]:
            add_log("카페 포스팅을 시작합니다.", "INFO")
            
            allow_comments = st.session_state.get('allow_comments', True)
            
            task_executor.post_cafe(
                contents_data=st.session_state.keywords_data,
                cafe_list=st.session_state.cafe_data,
                id_val=id_val,
                pw_val=pw_val,
                titles_data=st.session_state.titles_data,
                content_template=content_template,
                allow_comments=allow_comments,
                use_dynamic_ip=use_dynamic_ip
            )
        
        add_log("모든 작업이 완료되었습니다.", "SUCCESS")
        
    except Exception as e:
        add_log(f"작업 중 오류가 발생했습니다: {str(e)}", "ERROR")
        
    finally:
        st.session_state.is_running = False

def main():
    """메인 함수"""
    # 초기화
    init_session_state()
    
    # 헤더
    st.markdown('<h1 class="main-header">📝 네이버 블로그/카페 자동 포스팅</h1>', unsafe_allow_html=True)
    
    # 사이드바
    render_sidebar()
    
    # 메인 컨텐츠
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # API 인증 섹션 (최상단에 배치)
        render_api_auth_section()
        
        # 네이버 로그인 섹션
        render_naver_login_section()
        
        # 파일 업로드 섹션
        render_file_upload_section()
        
        # 콘텐츠 작성 섹션
        render_content_section()
        
        # 실행 섹션
        render_execution_section()
    
    with col2:
        # 로그 섹션
        render_log_section()
    
    # 실행 상태 표시
    if st.session_state.is_running:
        st.markdown("""
        <div style="
            position: fixed;
            top: 80px;
            right: 20px;
            background-color: #4caf50;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
            z-index: 1000;
        ">
            🔄 작업 실행 중...
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()