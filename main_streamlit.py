import streamlit as st
import pandas as pd
import time
import datetime
import os
import glob
from io import StringIO
import requests
import json
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pyperclip
import clipboard
import platform
import random

# 제미나이 API 라이브러리 (호환성 문제가 있을 수 있음)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError as e:
    st.warning(f"Google Generative AI 라이브러리를 사용할 수 없습니다: {e}")
    GEMINI_AVAILABLE = False

# 전역 변수 (기존 webdriver.py와 동일)
main_window = None
actions = None

# 페이지 설정
st.set_page_config(
    page_title="네이버 포스팅 자동화 프로그램",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'account_data' not in st.session_state:
    st.session_state.account_data = pd.DataFrame(columns=['계정명', '비밀번호', '장소'])
if 'keyword_data' not in st.session_state:
    st.session_state.keyword_data = pd.DataFrame(columns=['주소', '업체', '파일경로', '해시태그'])
if 'prompt_data' not in st.session_state:
    st.session_state.prompt_data = pd.DataFrame(columns=['프롬프트'])
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []
if 'api_authenticated' not in st.session_state:
    st.session_state.api_authenticated = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "gemini-1.5-flash"
if 'image_folder' not in st.session_state:
    st.session_state.image_folder = None
if 'image_files' not in st.session_state:
    st.session_state.image_files = []
if 'preview_content' not in st.session_state:
    st.session_state.preview_content = None
if 'main_content' not in st.session_state:
    st.session_state.main_content = None

def log_message(message):
    """로그 메시지 추가"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    st.session_state.log_messages.append(log_entry)
    if len(st.session_state.log_messages) > 100:  # 최대 100개 로그만 유지
        st.session_state.log_messages.pop(0)

def authenticate_api(api_key, model_name=None):
    """제미나이 API 인증 (두 가지 방식 시도)"""
    try:
        if not api_key or len(api_key.strip()) == 0:
            log_message("API 키가 입력되지 않았습니다.")
            return False
        
        # API 키 형식 검증
        if not api_key.startswith('AIza'):
            log_message("API 키 형식이 올바르지 않습니다. 'AIza'로 시작하는 키를 입력해주세요.")
            return False
        
        # 모델명 설정
        if model_name is None:
            model_name = st.session_state.get('selected_model', 'gemini-1.5-flash')
        
        log_message(f"선택된 모델: {model_name}")
        
        # 방법 1: Google Generative AI 라이브러리 사용 (가능한 경우)
        if GEMINI_AVAILABLE:
            try:
                log_message("방법 1: Google Generative AI 라이브러리로 인증 시도...")
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello")
                
                if response and response.text:
                    log_message("✅ Google Generative AI 라이브러리로 인증 성공")
                    log_message(f"테스트 응답: {response.text[:50]}...")
                    return True
                else:
                    log_message("❌ Google Generative AI 라이브러리 응답이 비어있습니다.")
            except Exception as e:
                log_message(f"❌ Google Generative AI 라이브러리 인증 실패: {str(e)}")
        
        # 방법 2: HTTP 요청 방식 (fallback)
        log_message("방법 2: HTTP 요청 방식으로 인증 시도...")
        
        # 제미나이 API 엔드포인트
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        # 테스트 요청 데이터
        data = {
            "contents": [{
                "parts": [{
                    "text": "Hello"
                }]
            }]
        }
        
        # HTTP 요청 헤더
        headers = {
            "Content-Type": "application/json"
        }
        
        # API 요청 실행
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                log_message("✅ HTTP 요청 방식으로 제미나이 API 연결 성공")
                log_message(f"테스트 응답: {result['candidates'][0]['content']['parts'][0]['text'][:50]}...")
                return True
            else:
                log_message("❌ HTTP 요청 방식 API 응답 형식이 올바르지 않습니다.")
                return False
        else:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get('error', {}).get('message', f"HTTP {response.status_code}")
            log_message(f"❌ HTTP 요청 방식 API 요청 실패: {error_msg}")
            
            # 구체적인 오류 메시지 제공
            if response.status_code == 400:
                if "API_KEY_INVALID" in error_msg:
                    log_message("❌ API 키가 유효하지 않습니다. 올바른 API 키를 입력해주세요.")
                elif "INVALID_ARGUMENT" in error_msg:
                    log_message("❌ 요청 형식이 올바르지 않습니다.")
                else:
                    log_message("❌ 잘못된 요청입니다.")
            elif response.status_code == 403:
                if "API_KEY_INVALID" in error_msg:
                    log_message("❌ API 키가 유효하지 않습니다.")
                elif "PERMISSION_DENIED" in error_msg:
                    log_message("❌ API 사용 권한이 없습니다.")
                elif "QUOTA_EXCEEDED" in error_msg:
                    log_message("❌ API 할당량을 초과했습니다.")
                else:
                    log_message("❌ 접근이 거부되었습니다.")
            elif response.status_code == 404:
                log_message("❌ API 엔드포인트를 찾을 수 없습니다.")
            elif response.status_code == 429:
                log_message("❌ 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
            else:
                log_message(f"❌ 서버 오류: {response.status_code}")
            
            return False
            
    except requests.exceptions.Timeout:
        log_message("❌ API 요청 시간 초과. 네트워크 연결을 확인해주세요.")
        return False
    except requests.exceptions.ConnectionError:
        log_message("❌ 네트워크 연결 오류. 인터넷 연결을 확인해주세요.")
        return False
    except Exception as e:
        log_message(f"❌ 예상치 못한 오류: {str(e)}")
        return False

def generate_content_with_gemini(content):
    """제미나이 API를 사용한 콘텐츠 생성 (두 가지 방식 시도)"""
    try:
        if not st.session_state.api_authenticated or not st.session_state.api_key:
            log_message("API가 인증되지 않아 콘텐츠 생성을 건너뜁니다.")
            return None
        
        # 선택된 모델 가져오기
        model_name = st.session_state.get('selected_model', 'gemini-1.5-flash')
        log_message(f"제미나이 AI 콘텐츠 생성 중... (모델: {model_name})")
        
        # 콘텐츠 개선을 위한 프롬프트
        prompt = f"""
        다음 콘텐츠를 더욱 매력적이고 SEO에 최적화된 블로그 포스트로 개선해주세요:
        
        원본 콘텐츠:
        {content}
        
        요구사항:
        1. 1500자 내외의 길이로 작성
        2. SEO에 최적화된 제목과 본문
        3. 자연스러운 한국어로 작성
        4. 독자의 관심을 끌 수 있는 내용으로 구성
        5. 원본의 핵심 내용은 유지하되 더욱 풍부하게 확장
        
        개선된 콘텐츠:
        """
        
        # 방법 1: Google Generative AI 라이브러리 사용 (가능한 경우)
        if GEMINI_AVAILABLE:
            try:
                log_message("방법 1: Google Generative AI 라이브러리로 콘텐츠 생성 시도...")
                genai.configure(api_key=st.session_state.api_key)
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                
                if response and response.text:
                    log_message("✅ Google Generative AI 라이브러리로 콘텐츠 생성 성공")
                    return response.text
                else:
                    log_message("❌ Google Generative AI 라이브러리 응답이 비어있습니다.")
            except Exception as e:
                log_message(f"❌ Google Generative AI 라이브러리 콘텐츠 생성 실패: {str(e)}")
        
        # 방법 2: HTTP 요청 방식 (fallback)
        log_message("방법 2: HTTP 요청 방식으로 콘텐츠 생성 시도...")
        
        # 제미나이 API 엔드포인트
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={st.session_state.api_key}"
        
        # 요청 데이터
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048
            }
        }
        
        # HTTP 요청 헤더
        headers = {
            "Content-Type": "application/json"
        }
        
        # API 요청 실행
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                generated_text = result['candidates'][0]['content']['parts'][0]['text']
                log_message("✅ HTTP 요청 방식으로 제미나이 AI 콘텐츠 생성 성공")
                return generated_text
            else:
                log_message("❌ HTTP 요청 방식 제미나이 AI 응답이 비어있습니다.")
                return None
        else:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get('error', {}).get('message', f"HTTP {response.status_code}")
            log_message(f"❌ HTTP 요청 방식 제미나이 AI 콘텐츠 생성 실패: {error_msg}")
            return None
            
    except requests.exceptions.Timeout:
        log_message("❌ 제미나이 AI 요청 시간 초과")
        return None
    except requests.exceptions.ConnectionError:
        log_message("❌ 제미나이 AI 네트워크 연결 오류")
        return None
    except Exception as e:
        log_message(f"❌ 제미나이 AI 콘텐츠 생성 실패: {str(e)}")
        return None

def main():
    # 헤더
    st.title("📝 네이버 포스팅 자동화 프로그램")
    st.markdown("---")
    
    # 사이드바 - 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 현재 상태 표시
        st.subheader("현재 상태")
        platform = st.radio(
            "플랫폼 선택",
            ["블로그", "카페", "둘 다"],
            index=0
        )
        st.info(f"선택된 플랫폼: **{platform}**")
        
        # 대기시간 설정
        st.subheader("⏱️ 대기시간 설정")
        col1, col2 = st.columns(2)
        with col1:
            min_wait = st.number_input("최소(분)", min_value=1, max_value=60, value=1)
        with col2:
            max_wait = st.number_input("최대(분)", min_value=1, max_value=60, value=3)
        
        # 유동 IP 사용
        use_dynamic_ip = st.checkbox("유동 IP 사용여부", value=True)
        
        # 인증
        st.subheader("📱 인증")
        phone_number = st.text_input("핸드폰 번호", placeholder="010-1234-5678")
        
        # 파일 업로드
        st.subheader("📁 파일 업로드")
        
        # 계정 파일 업로드
        account_file = st.file_uploader(
            "계정 파일 업로드",
            type=['csv'],
            help="CSV 형식의 계정 정보 파일을 업로드하세요"
        )
        
        # 키워드 파일 업로드
        keyword_file = st.file_uploader(
            "키워드 파일 업로드",
            type=['csv'],
            help="CSV 형식의 키워드 정보 파일을 업로드하세요"
        )
        
    
    # 메인 컨텐츠 영역
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 콘텐츠 작성 섹션
        st.header("✍️ 콘텐츠 작성")
        
        # 프롬프트 관리
        with st.expander("📋 프롬프트 관리", expanded=True):
            if not st.session_state.prompt_data.empty:
                st.dataframe(st.session_state.prompt_data, use_container_width=True)
                
                # 프롬프트 삭제 기능
                st.markdown("**프롬프트 삭제**")
                col_del1, col_del2, col_del3 = st.columns([2, 1, 1])
                
                with col_del1:
                    # 프롬프트 선택 드롭다운
                    prompt_list = st.session_state.prompt_data['프롬프트'].tolist()
                    selected_prompt = st.selectbox(
                        "삭제할 프롬프트 선택",
                        options=[""] + prompt_list,
                        key="prompt_delete_select"
                    )
                
                with col_del2:
                    if st.button("🗑️ 선택 삭제", use_container_width=True, key="delete_prompt_btn"):
                        if selected_prompt:
                            st.session_state.prompt_data = st.session_state.prompt_data[st.session_state.prompt_data['프롬프트'] != selected_prompt]
                            log_message(f"프롬프트 삭제: {selected_prompt[:50]}...")
                            st.success(f"프롬프트가 삭제되었습니다!")
                            st.rerun()
                        else:
                            st.warning("삭제할 프롬프트를 선택하세요!")
                
                with col_del3:
                    if st.button("🗑️ 전체 삭제", use_container_width=True, key="delete_all_prompts_btn"):
                        st.session_state.prompt_data = pd.DataFrame(columns=['프롬프트'])
                        log_message("모든 프롬프트가 삭제되었습니다.")
                        st.success("모든 프롬프트가 삭제되었습니다!")
                        st.rerun()
            
            # 프롬프트 직접 입력
            st.markdown("**새 프롬프트 추가**")
            new_prompt = st.text_area("새 프롬프트 추가", height=100, placeholder="프롬프트를 입력하세요...")
            if st.button("프롬프트 추가") and new_prompt:
                new_row = pd.DataFrame({'프롬프트': [new_prompt]})
                st.session_state.prompt_data = pd.concat([st.session_state.prompt_data, new_row], ignore_index=True)
                log_message(f"프롬프트 추가: {new_prompt[:50]}...")
                st.success("프롬프트가 추가되었습니다!")
                st.rerun()
        
    # 이미지 폴더 관리 섹션
    with st.expander("🖼️ 이미지 폴더 관리", expanded=True):
        # 이미지 폴더 선택
        st.markdown("**이미지 폴더 선택**")
        col_img1, col_img2 = st.columns([3, 1])
        
        with col_img1:
            image_folder = st.text_input(
                "이미지 폴더 경로",
                placeholder="C:\\Users\\Username\\Pictures\\blog_images",
                key="image_folder_input"
            )
            
        with col_img2:
            if st.button("📁 폴더 선택", use_container_width=True):
                if image_folder and os.path.exists(image_folder):
                    # 이미지 파일들 가져오기
                    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
                    image_files = []
                    for ext in image_extensions:
                        image_files.extend(glob.glob(os.path.join(image_folder, f"*{ext}")))
                        image_files.extend(glob.glob(os.path.join(image_folder, f"*{ext.upper()}")))
                    
                    if image_files:
                        st.session_state.image_folder = image_folder
                        st.session_state.image_files = image_files
                        log_message(f"이미지 폴더 등록: {image_folder} ({len(image_files)}개 이미지)")
                        st.success(f"이미지 폴더가 등록되었습니다! ({len(image_files)}개 이미지)")
                        st.rerun()
                    else:
                        st.warning("선택한 폴더에 이미지 파일이 없습니다!")
                else:
                    st.warning("올바른 폴더 경로를 입력하세요!")
        
        # 등록된 이미지 폴더 정보 표시
        if 'image_folder' in st.session_state and 'image_files' in st.session_state:
            st.markdown("**등록된 이미지 폴더**")
            col_info1, col_info2, col_info3 = st.columns([2, 1, 1])
            
            with col_info1:
                st.text(f"경로: {st.session_state.image_folder}")
            
            with col_info2:
                st.metric("이미지 수", len(st.session_state.image_files))
            
            with col_info3:
                if st.button("🗑️ 폴더 제거", use_container_width=True):
                    del st.session_state.image_folder
                    del st.session_state.image_files
                    log_message("이미지 폴더가 제거되었습니다.")
                    st.success("이미지 폴더가 제거되었습니다!")
                    st.rerun()
            
            # 이미지 미리보기 (최대 5개)
            if st.session_state.image_files:
                st.markdown("**이미지 미리보기**")
                preview_images = st.session_state.image_files[:5]  # 최대 5개만 미리보기
                
                cols = st.columns(len(preview_images))
                for i, img_path in enumerate(preview_images):
                    with cols[i]:
                        try:
                            # 이미지 파일명만 표시
                            img_name = os.path.basename(img_path)
                            st.text(img_name[:15] + "..." if len(img_name) > 15 else img_name)
                            
                            # 이미지 로드 및 표시
                            image = Image.open(img_path)
                            image.thumbnail((100, 100))  # 썸네일 크기
                            st.image(image, use_column_width=True)
                        except Exception as e:
                            st.error(f"이미지 로드 실패: {os.path.basename(img_path)}")
                
                if len(st.session_state.image_files) > 5:
                    st.info(f"총 {len(st.session_state.image_files)}개 이미지 중 5개만 표시됩니다.")
        else:
            st.info("이미지 폴더를 선택하세요")
        
        # 콘텐츠 템플릿 안내
        with st.expander("📖 사용 안내", expanded=False):
            st.markdown("""
            **폼 형식 지정 안내글**
            
            - [본문]을 기준으로 서론, 본문, 결론으로 나뉘어집니다.
            - 본문은 AI로 작성한 1500자 내외의 글이며, 업로드한 이미지 중 랜덤으로 5개가 같이 들어갑니다.
            - %주소% 문자열은 주소 열의 데이터로, %업체% 문자열은 업체 열의 데이터로 치환됩니다.
            - %썸네일% 문자열은 썸네일 사진으로, %영상% 문자열은 썸네일 사진을 바탕으로 제작된 영상으로 치환됩니다.
            
            **문자열 치환 예시:**
            ```
            %주소%이고, %업체%입니다.
            %썸네일%
            [본문]
            %영상%
            감사합니다.
            ```
            """)
        
        # 프롬프트 미리보기 섹션
        st.subheader("🔍 프롬프트 미리보기")
        
        if not st.session_state.api_authenticated:
            st.info("프롬프트 미리보기를 사용하려면 먼저 API 인증을 완료하세요.")
        else:
            # 프롬프트 입력 방식 선택
            preview_mode = st.radio(
                "미리보기 방식 선택",
                ["새 프롬프트 입력", "등록된 프롬프트 선택"],
                horizontal=True,
                key="preview_mode_select"
            )
            
            if preview_mode == "새 프롬프트 입력":
                # 직접 프롬프트 입력
                st.markdown("**프롬프트 직접 입력**")
                custom_prompt = st.text_area(
                    "미리보기할 프롬프트를 입력하세요",
                    height=100,
                    placeholder="프롬프트를 입력하세요...",
                    key="custom_prompt_input"
                )
                
                if custom_prompt:
                    col_preview1, col_preview2 = st.columns([3, 1])
                    
                    with col_preview1:
                        st.markdown("**입력된 프롬프트:**")
                        st.text_area("프롬프트 내용", value=custom_prompt, height=100, disabled=True)
                    
                    with col_preview2:
                        if st.button("🚀 미리보기 생성", use_container_width=True):
                            with st.spinner("AI가 콘텐츠를 생성 중입니다..."):
                                generated_content = generate_content_with_gemini(custom_prompt)
                                
                                if generated_content:
                                    st.session_state.preview_content = generated_content
                                    log_message("커스텀 프롬프트 미리보기 생성 완료")
                                    st.success("미리보기가 생성되었습니다!")
                                else:
                                    st.error("콘텐츠 생성에 실패했습니다.")
            
            else:  # 등록된 프롬프트 선택
                if st.session_state.prompt_data.empty:
                    st.info("미리보기할 프롬프트를 먼저 추가하세요.")
                else:
                    # 프롬프트 선택
                    prompt_options = st.session_state.prompt_data['프롬프트'].tolist()
                    selected_prompt = st.selectbox(
                        "미리보기할 프롬프트 선택",
                        options=[""] + prompt_options,
                        key="preview_prompt_select"
                    )
                    
                    if selected_prompt:
                        col_preview1, col_preview2 = st.columns([3, 1])
                        
                        with col_preview1:
                            st.markdown("**선택된 프롬프트:**")
                            st.text_area("프롬프트 내용", value=selected_prompt, height=100, disabled=True)
                        
                        with col_preview2:
                            if st.button("🚀 미리보기 생성", use_container_width=True):
                                with st.spinner("AI가 콘텐츠를 생성 중입니다..."):
                                    generated_content = generate_content_with_gemini(selected_prompt)
                                    
                                    if generated_content:
                                        st.session_state.preview_content = generated_content
                                        log_message("등록된 프롬프트 미리보기 생성 완료")
                                        st.success("미리보기가 생성되었습니다!")
                                    else:
                                        st.error("콘텐츠 생성에 실패했습니다.")
            
            # 생성된 콘텐츠 미리보기 (공통)
            if 'preview_content' in st.session_state and st.session_state.preview_content:
                st.markdown("**생성된 콘텐츠 미리보기:**")
                st.text_area(
                    "미리보기 결과",
                    value=st.session_state.preview_content,
                    height=300,
                    disabled=True,
                    key="preview_result"
                )
                
                # 미리보기 콘텐츠를 메인 콘텐츠로 복사
                if st.button("📋 미리보기를 메인 콘텐츠로 복사", use_container_width=True):
                    st.session_state.main_content = st.session_state.preview_content
                    log_message("미리보기 콘텐츠를 메인 콘텐츠로 복사")
                    st.success("메인 콘텐츠로 복사되었습니다!")
                    st.rerun()
        
        # Chrome 드라이버 테스트
        st.subheader("🔧 시스템 테스트")
        col_test1, col_test2 = st.columns(2)
        
        with col_test1:
            if st.button("🧪 Chrome 드라이버 테스트", use_container_width=True):
                with st.spinner("Chrome 드라이버 테스트 중..."):
                    test_result = test_chrome_driver()
                    if test_result:
                        st.success("✅ Chrome 드라이버 테스트 성공!")
                    else:
                        st.error("❌ Chrome 드라이버 테스트 실패!")
            
            if st.button("🔍 로그인 페이지 테스트", use_container_width=True):
                with st.spinner("로그인 페이지 테스트 중..."):
                    test_result = test_login_page()
                    if test_result:
                        st.success("✅ 로그인 페이지 테스트 성공!")
                    else:
                        st.error("❌ 로그인 페이지 테스트 실패!")
            
            if st.button("🔐 로그인 테스트", use_container_width=True):
                if st.session_state.account_data.empty:
                    st.error("❌ 먼저 계정 데이터를 추가해주세요!")
                else:
                    with st.spinner("로그인 테스트 중..."):
                        test_result = test_login_process()
                        if test_result:
                            st.success("✅ 로그인 테스트 성공!")
                        else:
                            st.error("❌ 로그인 테스트 실패!")
        
        with col_test2:
            if st.button("🔄 데이터 초기화", use_container_width=True):
                reset_data()
                st.success("✅ 데이터가 초기화되었습니다!")
                st.rerun()
        
        # 콘텐츠 입력
        st.subheader("📝 콘텐츠 입력")
        
        # 미리보기에서 복사된 콘텐츠가 있으면 사용
        if 'main_content' in st.session_state and st.session_state.main_content:
            default_content = st.session_state.main_content
        else:
            default_content = """안녕하세요. 헤더입니다. 여기서 등록하는 미디어는 테스트를 위한 임의의 사진 및 영상입니다.

[사진]

이곳부터는 AI가 작성할 글이 들어갈 본문입니다.

[사진]

이 밑에는 영상이 들어갑니다.

[영상]

맺음말입니다."""
        
        content = st.text_area(
            "콘텐츠를 입력하세요",
            value=default_content,
            height=300,
            placeholder="""안녕하세요. 헤더입니다. 여기서 등록하는 미디어는 테스트를 위한 임의의 사진 및 영상입니다.

[사진]

이곳부터는 AI가 작성할 글이 들어갈 본문입니다.

[사진]

이 밑에는 영상이 들어갑니다.

[영상]

맺음말입니다.""",
            help="위의 안내에 따라 콘텐츠를 작성하세요"
        )
        
        # 작업 수행 버튼
        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            if st.button("🚀 작업 수행", type="primary", use_container_width=True):
                execute_task(platform, st.session_state.api_key, phone_number, content, min_wait, max_wait, use_dynamic_ip)
        
        with col_btn2:
            if st.button("🔄 초기화", use_container_width=True):
                reset_data()
    
    with col2:
        # API 설정 및 인증 섹션
        st.header("🔑 API 설정 및 인증")
        
        # 제미나이 API 키 입력
        with st.expander("🤖 제미나이 API 설정", expanded=True):
            # API 키 입력
            st.markdown("**제미나이 API 키 입력**")
            st.markdown("Google AI Studio에서 발급받은 API 키를 입력하세요.")
            st.markdown("API 키는 `AIza...` 형태로 시작합니다.")
            
            with st.expander("🔗 API 키 발급 방법", expanded=False):
                st.markdown("""
                1. [Google AI Studio](https://aistudio.google.com/)에 접속
                2. Google 계정으로 로그인
                3. "Get API key" 버튼 클릭
                4. "Create API key" 선택
                5. 생성된 API 키를 복사하여 여기에 입력
                
                **주의사항:**
                - API 키는 비공개로 유지하세요
                - 사용량에 따라 비용이 발생할 수 있습니다
                - API 키가 노출되면 즉시 재발급하세요
                """)
            
            api_key = st.text_input(
                "제미나이 API KEY", 
                value=st.session_state.api_key,
                type="password", 
                help="Google AI Studio에서 발급받은 API 키를 입력하세요 (AIza... 형태)",
                key="api_key_input",
                placeholder="AIza..."
            )
            
            # 모델 선택
            st.markdown("**모델 선택**")
            model_options = {
                "gemini-1.5-flash": "Gemini 1.5 Flash (빠름, 일반적 용도)",
                "gemini-1.5-pro": "Gemini 1.5 Pro (고성능, 복잡한 작업)",
                "gemini-2.0-flash-exp": "Gemini 2.0 Flash (실험적, 최신 기능)",
                "gemini-1.0-pro": "Gemini 1.0 Pro (안정적, 검증된 모델)"
            }
            
            selected_model = st.selectbox(
                "사용할 모델을 선택하세요",
                options=list(model_options.keys()),
                index=0,
                help="각 모델의 특성과 성능이 다릅니다. 용도에 맞게 선택하세요.",
                key="model_selection"
            )
            
            st.info(f"선택된 모델: **{model_options[selected_model]}**")
            
            # API 키 및 모델 저장
            if api_key != st.session_state.api_key:
                st.session_state.api_key = api_key
                st.session_state.api_authenticated = False  # 키가 변경되면 인증 상태 초기화
            
            if selected_model != st.session_state.selected_model:
                st.session_state.selected_model = selected_model
                st.session_state.api_authenticated = False  # 모델이 변경되면 인증 상태 초기화
            
            # 인증 상태 표시
            if st.session_state.api_authenticated:
                st.success("✅ API 인증됨")
            else:
                st.warning("⚠️ API 인증 필요")
            
            # API 키 인증 버튼
            col_auth1, col_auth2 = st.columns([1, 1])
            with col_auth1:
                if st.button("🔐 API 인증", use_container_width=True, disabled=st.session_state.api_authenticated):
                    if api_key:
                        with st.spinner("API 인증 중..."):
                            auth_result = authenticate_api(api_key, selected_model)
                            if auth_result:
                                st.session_state.api_authenticated = True
                                st.success("API 인증 성공!")
                                log_message("제미나이 API 인증 성공")
                                st.rerun()
                            else:
                                st.error("API 인증 실패!")
                                log_message("제미나이 API 인증 실패")
                    else:
                        st.warning("API 키를 입력해주세요!")
            
            with col_auth2:
                if st.button("🔄 재인증", use_container_width=True):
                    st.session_state.api_authenticated = False
                    st.info("API 재인증을 시도합니다...")
                    log_message("API 재인증 시도")
                    st.rerun()
        
        # 데이터 관리 섹션
        st.header("📊 데이터 관리")
        
        # 계정 데이터
        with st.expander("👥 계정 데이터", expanded=True):
            # 계정 추가 폼
            st.markdown("**새 계정 추가**")
            col_acc1, col_acc2, col_acc3 = st.columns([2, 2, 1])
            
            with col_acc1:
                new_account = st.text_input("네이버 아이디", placeholder="naver_id", key="new_account_input")
            with col_acc2:
                new_password = st.text_input("비밀번호", type="password", placeholder="password", key="new_password_input")
            with col_acc3:
                new_location = st.text_input("장소", placeholder="서울", key="new_location_input")
            
            col_add1, col_add2, col_add3 = st.columns([1, 1, 1])
            with col_add1:
                if st.button("➕ 계정 추가", use_container_width=True):
                    if new_account and new_password and new_location:
                        # 중복 체크
                        if new_account in st.session_state.account_data['계정명'].values:
                            st.error(f"계정 '{new_account}'이 이미 존재합니다!")
                            log_message(f"계정 추가 실패: 중복된 계정명 - {new_account}")
                        else:
                            # 새 계정 추가
                            new_row = pd.DataFrame({
                                '계정명': [new_account],
                                '비밀번호': [new_password],
                                '장소': [new_location]
                            })
                            st.session_state.account_data = pd.concat([st.session_state.account_data, new_row], ignore_index=True)
                            log_message(f"새 계정 추가: {new_account}")
                            st.success(f"계정 '{new_account}'이 추가되었습니다!")
                            st.rerun()
                    else:
                        st.warning("모든 필드를 입력해주세요!")
            
            with col_add2:
                if st.button("🗑️ 마지막 삭제", use_container_width=True):
                    if not st.session_state.account_data.empty:
                        deleted_account = st.session_state.account_data.iloc[-1]['계정명']
                        st.session_state.account_data = st.session_state.account_data.iloc[:-1]
                        log_message(f"마지막 계정 삭제: {deleted_account}")
                        st.success(f"계정 '{deleted_account}'이 삭제되었습니다!")
                        st.rerun()
                    else:
                        st.warning("삭제할 계정이 없습니다!")
            
            with col_add3:
                if st.button("🔄 폼 초기화", use_container_width=True):
                    st.rerun()
            
            # 계정 데이터 표시
            if not st.session_state.account_data.empty:
                st.markdown("**등록된 계정 목록**")
                
                # 계정 선택 삭제 기능
                st.markdown("**계정 관리**")
                col_manage1, col_manage2, col_manage3 = st.columns([2, 1, 1])
                
                with col_manage1:
                    # 계정 선택 드롭다운
                    account_list = st.session_state.account_data['계정명'].tolist()
                    selected_account = st.selectbox(
                        "삭제할 계정 선택",
                        options=[""] + account_list,
                        key="account_delete_select"
                    )
                
                with col_manage2:
                    if st.button("🗑️ 선택 삭제", use_container_width=True, key="delete_account_btn"):
                        if selected_account:
                            st.session_state.account_data = st.session_state.account_data[st.session_state.account_data['계정명'] != selected_account]
                            log_message(f"계정 삭제: {selected_account}")
                            st.success(f"계정 '{selected_account}'이 삭제되었습니다!")
                            st.rerun()
                        else:
                            st.warning("삭제할 계정을 선택하세요!")
                
                with col_manage3:
                    if st.button("🗑️ 전체 삭제", use_container_width=True, key="delete_all_accounts_btn"):
                        st.session_state.account_data = pd.DataFrame(columns=['계정명', '비밀번호', '장소'])
                        log_message("모든 계정이 삭제되었습니다.")
                        st.success("모든 계정이 삭제되었습니다!")
                        st.rerun()
                
                # 계정 데이터 테이블
                st.dataframe(st.session_state.account_data, use_container_width=True)
                
                # 계정 통계
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("총 계정 수", len(st.session_state.account_data))
                with col_stat2:
                    if not st.session_state.account_data.empty:
                        unique_locations = st.session_state.account_data['장소'].nunique()
                        st.metric("지역 수", unique_locations)
                with col_stat3:
                    if not st.session_state.account_data.empty:
                        st.metric("마지막 추가", st.session_state.account_data.iloc[-1]['계정명'])
            else:
                st.info("계정을 추가하거나 파일을 업로드하세요")
        
        # 키워드 데이터
        with st.expander("🔍 키워드 데이터", expanded=True):
            if not st.session_state.keyword_data.empty:
                st.dataframe(st.session_state.keyword_data, use_container_width=True)
            else:
                st.info("키워드 파일을 업로드하세요")
        
        # 로그 섹션
        st.header("📋 로그")
        log_container = st.container()
        with log_container:
            for message in st.session_state.log_messages[-20:]:  # 최근 20개 로그만 표시
                st.text(message)
    
    # 파일 처리
    if account_file is not None:
        process_account_file(account_file)
    
    if keyword_file is not None:
        process_keyword_file(keyword_file)
    

def process_account_file(file):
    """계정 파일 처리"""
    try:
        df = pd.read_csv(file)
        required_columns = ['계정명', '비밀번호', '장소']
        
        if all(col in df.columns for col in required_columns):
            st.session_state.account_data = df[required_columns]
            log_message(f"계정 파일 업로드 완료: {len(df)}개 계정")
            st.success(f"계정 파일이 성공적으로 업로드되었습니다! ({len(df)}개 계정)")
        else:
            st.error(f"필요한 컬럼이 없습니다. 필요한 컬럼: {required_columns}")
    except Exception as e:
        st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
        log_message(f"계정 파일 처리 오류: {str(e)}")

def process_keyword_file(file):
    """키워드 파일 처리"""
    try:
        df = pd.read_csv(file)
        required_columns = ['주소', '업체', '파일경로', '해시태그']
        
        if all(col in df.columns for col in required_columns):
            st.session_state.keyword_data = df[required_columns]
            log_message(f"키워드 파일 업로드 완료: {len(df)}개 키워드")
            st.success(f"키워드 파일이 성공적으로 업로드되었습니다! ({len(df)}개 키워드)")
        else:
            st.error(f"필요한 컬럼이 없습니다. 필요한 컬럼: {required_columns}")
    except Exception as e:
        st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
        log_message(f"키워드 파일 처리 오류: {str(e)}")

def setup_chrome_driver():
    """Chrome 드라이버 설정 (기존 webdriver.py 패턴 정확히 적용)"""
    try:
        log_message("=== Chrome 드라이버 설정 시작 ===")
        
        # 기존 webdriver.py의 정확한 패턴 사용
        service = Service(ChromeDriverManager().install())
        chrome_options = Options()
        
        # ✅ 필수: Headless 서버 환경에서 필요한 옵션 (기존 코드와 동일)
        # chrome_options.add_argument('--headless')  # 화면 없이 실행
        chrome_options.add_argument('--no-sandbox')  # 보안 샌드박스 비활성화
        chrome_options.add_argument('--disable-dev-shm-usage')  # 메모리 사용 제한 해제
        chrome_options.add_argument('--disable-gpu')  # GPU 비활성화 (가끔 필요)
        chrome_options.add_argument('--window-size=1920x1080')  # 뷰포트 설정
        
        # 선택 옵션 (기존 코드와 동일)
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 1
        })
        
        # 기존 코드와 동일한 방식으로 드라이버 생성
        driver = webdriver.Chrome(options=chrome_options, service=service)
        log_message("Chrome 웹드라이버 초기화 완료")
        
        # webdriver 속성 제거 (기존 코드와 동일)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """
        })
        
        time.sleep(1)  # 기존 코드의 @sleep_after() 데코레이터와 동일
        
        # 기존 코드와 동일하게 전역 변수 설정
        global main_window, actions
        main_window = driver.current_window_handle
        actions = ActionChains(driver)
        
        log_message("Chrome 드라이버 설정 완료")
        return driver
        
    except Exception as e:
        log_message(f"Chrome 드라이버 설정 실패: {str(e)}")
        import traceback
        log_message(f"상세 오류: {traceback.format_exc()}")
        return None

def login_to_platform(driver, platform, account_data):
    """플랫폼에 로그인"""
    try:
        log_message(f"=== 플랫폼 로그인 시작 ===")
        log_message(f"플랫폼: {platform}")
        log_message(f"드라이버 상태: {driver is not None}")
        log_message(f"계정 데이터: {account_data}")
        
        if platform == "네이버 블로그":
            log_message("네이버 블로그 로그인 함수 호출")
            result = login_naver_blog(driver, account_data)
            log_message(f"네이버 블로그 로그인 결과: {result}")
            return result
        elif platform == "네이버 카페":
            log_message("네이버 카페 로그인 함수 호출")
            result = login_naver_cafe(driver, account_data)
            log_message(f"네이버 카페 로그인 결과: {result}")
            return result
        else:
            log_message(f"지원하지 않는 플랫폼: {platform}")
            return False
    except Exception as e:
        log_message(f"로그인 실패: {str(e)}")
        import traceback
        log_message(f"상세 오류: {traceback.format_exc()}")
        return False

def login_naver_blog(driver, account_data):
    """네이버 블로그 로그인 (기존 login.py 패턴 정확히 적용)"""
    try:
        from selenium.webdriver import ActionChains
        from selenium.webdriver.common.keys import Keys
        import clipboard
        import platform as platform_module
        
        # 운영체제별 키 설정 (기존 코드와 동일)
        COMCON = Keys.COMMAND if platform_module.system() == "Darwin" else Keys.CONTROL
        
        log_message("=== 네이버 로그인 시작 ===")
        log_message(f"드라이버 상태: {driver is not None}")
        log_message(f"계정 정보: {account_data}")
        
        # 1단계: 네이버 로그인 페이지로 이동 (기존 login.enter_naver_login() 패턴)
        log_message("1단계: 네이버 로그인 페이지로 이동")
        driver.get("https://nid.naver.com/nidlogin.login")
        time.sleep(3)  # @sleep_after() 데코레이터와 동일
        
        # 2단계: ID/전화번호 탭 클릭 (기존 login.click_ID_phone() 패턴)
        log_message("2단계: ID/전화번호 탭 클릭")
        driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[1]/ul/li[1]/a").click()
        time.sleep(3)  # @sleep_after() 데코레이터와 동일
        
        # 3단계: 아이디/비밀번호 입력 (기존 login.input_id_pw() 패턴)
        log_message("3단계: 아이디/비밀번호 입력")
        actions = ActionChains(driver)
        
        # 아이디 입력 (기존 코드와 정확히 동일)
        time.sleep(3)  # 기존 코드와 동일
        clipboard.copy(account_data['계정명'])
        id_input = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[1]/div/div[1]/input")
        id_input.click()
        actions.key_down(COMCON).send_keys('v').key_up(COMCON).perform()
        log_message("아이디 입력 완료")
        
        time.sleep(3)  # 기존 코드와 동일
        
        # 비밀번호 입력 (기존 코드와 정확히 동일)
        clipboard.copy(account_data['비밀번호'])
        pw_input = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[1]/div/div[2]/input")
        pw_input.click()
        actions.key_down(COMCON).send_keys('v').key_up(COMCON).perform()
        log_message("비밀번호 입력 완료")
        
        time.sleep(3)  # @sleep_after() 데코레이터와 동일
        
        # 4단계: 로그인 버튼 클릭 (기존 login.click_login_button() 패턴)
        log_message("4단계: 로그인 버튼 클릭")
        driver.find_element(By.ID, "log.login").click()
        time.sleep(3)  # @sleep_after() 데코레이터와 동일
        
        # 5단계: 캡챠 확인 (기존 login.check_capcha_appear() 패턴)
        log_message("5단계: 캡챠 확인")
        capcha_found = False
        for i in range(5):
            try:
                driver.find_element(By.CLASS_NAME, "captcha_input")
                driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[3]/div[1]/div[2]/div[1]")
                capcha_found = True
                break
            except:
                time.sleep(1)
                continue
        
        if capcha_found:
            log_message("캡챠가 발생했습니다. 수동으로 해제해주세요.")
            # 캡챠 해제 대기 (기존 코드 패턴)
            while True:
                try:
                    driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[3]/div[1]/div[2]/div[1]")
                    time.sleep(1)
                except:
                    break
        else:
            log_message("캡챠 없음 - 정상 진행")
        
        # 6단계: 로그인 성공 확인 (기존 login.check_login_done() 패턴)
        log_message("6단계: 로그인 성공 확인")
        login_success = False
        for i in range(10):  # 최대 10번 시도
            try:
                # 기존 코드의 로그인 성공 확인 방식
                driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/form/fieldset/span[2]/a")
                login_success = True
                break
            except:
                time.sleep(1)
                continue
        
        if login_success:
            log_message("네이버 로그인 성공")
            return True
        else:
            # URL 기반 확인
            current_url = driver.current_url
            log_message(f"로그인 후 URL: {current_url}")
            if "naver.com" in current_url and "nid.naver.com" not in current_url:
                log_message("네이버 로그인 성공 (URL 확인)")
                return True
            else:
                log_message("네이버 로그인 실패")
                return False
            
    except Exception as e:
        log_message(f"네이버 로그인 오류: {str(e)}")
        import traceback
        log_message(f"상세 오류: {traceback.format_exc()}")
        return False

def login_naver_cafe(driver, account_data):
    """네이버 카페 로그인"""
    try:
        from selenium.webdriver import ActionChains
        from selenium.webdriver.common.keys import Keys
        import clipboard
        import platform as platform_module
        
        # 운영체제별 키 설정
        COMCON = Keys.COMMAND if platform_module.system() == "Darwin" else Keys.CONTROL
        
        log_message("=== 네이버 카페 로그인 시작 ===")
        driver.get("https://nid.naver.com/nidlogin.login")
        time.sleep(2)
        
        # ID/전화번호 탭 클릭
        try:
            id_tab_xpath = "/html/body/div[1]/div[2]/div/div[1]/ul/li[1]/a"
            driver.find_element(By.XPATH, id_tab_xpath).click()
            time.sleep(1)
            log_message("ID/전화번호 탭 클릭 완료")
        except Exception as e:
            log_message(f"ID/전화번호 탭 클릭 실패: {str(e)}")
        
        # 아이디 입력 (클립보드 사용)
        try:
            clipboard.copy(account_data['계정명'])
            id_input_xpath = "/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[1]/div/div[1]/input"
            id_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, id_input_xpath))
            )
            id_input.click()
            time.sleep(1)
            
            actions = ActionChains(driver)
            actions.key_down(COMCON).send_keys('v').key_up(COMCON).perform()
            log_message("아이디 입력 완료")
        except Exception as e:
            log_message(f"아이디 입력 실패: {str(e)}")
            return False
        
        time.sleep(2)
        
        # 비밀번호 입력 (클립보드 사용)
        try:
            clipboard.copy(account_data['비밀번호'])
            pw_input_xpath = "/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[1]/div/div[2]/input"
            pw_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, pw_input_xpath))
            )
            pw_input.click()
            time.sleep(1)
            
            actions = ActionChains(driver)
            actions.key_down(COMCON).send_keys('v').key_up(COMCON).perform()
            log_message("비밀번호 입력 완료")
        except Exception as e:
            log_message(f"비밀번호 입력 실패: {str(e)}")
            return False
        
        time.sleep(2)
        
        # 로그인 버튼 클릭
        try:
            login_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "log.login"))
            )
            login_btn.click()
            log_message("로그인 버튼 클릭 완료")
        except Exception as e:
            log_message(f"로그인 버튼 클릭 실패: {str(e)}")
            return False
        
        time.sleep(5)
        
        # 로그인 성공 확인
        try:
            for i in range(10):  # 최대 10초 대기
                try:
                    success_element = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/form/fieldset/span[2]/a")
                    if success_element:
                        log_message("네이버 카페 로그인 성공")
                        return True
                except:
                    pass
                
                current_url = driver.current_url
                if "naver.com" in current_url and "nid.naver.com" not in current_url:
                    log_message("네이버 카페 로그인 성공 (URL 확인)")
                    return True
                
                time.sleep(1)
            
            log_message("네이버 카페 로그인 실패")
            return False
                
        except Exception as e:
            log_message(f"로그인 확인 중 오류: {str(e)}")
            return False
            
    except Exception as e:
        log_message(f"네이버 카페 로그인 오류: {str(e)}")
        return False

def write_blog_post(driver, platform, content, keyword_data):
    """블로그 글 작성"""
    try:
        if platform == "네이버 블로그":
            return write_naver_blog_post(driver, content, keyword_data)
        elif platform == "네이버 카페":
            return write_naver_cafe_post(driver, content, keyword_data)
        else:
            log_message(f"지원하지 않는 플랫폼: {platform}")
            return False
    except Exception as e:
        log_message(f"글 작성 실패: {str(e)}")
        return False

def write_naver_blog_post(driver, content, keyword_data):
    """네이버 블로그 글 작성 (기존 코드 정확한 패턴 적용)"""
    try:
        from selenium.webdriver import ActionChains
        from selenium.webdriver.common.keys import Keys
        import pyperclip
        import platform as platform_module
        
        # 운영체제별 키 설정
        COMCON = Keys.COMMAND if platform_module.system() == "Darwin" else Keys.CONTROL
        
        log_message("=== 네이버 블로그 글 작성 시작 ===")
        
        # 1단계: 네이버 메인 페이지로 이동
        log_message("1단계: 네이버 메인 페이지로 이동")
        try:
            log_message(f"이동 전 URL: {driver.current_url}")
            driver.get("https://www.naver.com")
            log_message("네이버 메인 페이지 로드 요청 완료")
            
            # 페이지 로딩 대기
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            log_message("네이버 메인 페이지 로딩 완료")
            
            log_message(f"이동 후 URL: {driver.current_url}")
            log_message(f"페이지 제목: {driver.title}")
            
            time.sleep(3)
        except Exception as e:
            log_message(f"네이버 메인 페이지 로드 실패: {str(e)}")
            import traceback
            log_message(f"상세 오류: {traceback.format_exc()}")
            return False
        
        # 2단계: 블로그 메뉴 클릭 (기존 코드 패턴)
        log_message("2단계: 블로그 메뉴 클릭")
        try:
            # 네이버 메인에서 블로그 메뉴 클릭
            blog_menu_xpath = "/html/body/div[2]/div[2]/div[2]/div[2]/div/div/div[1]/div[2]/div/div/ul/li[3]/a"
            driver.find_element(By.XPATH, blog_menu_xpath).click()
            time.sleep(3)
            log_message("블로그 메뉴 클릭 완료")
        except Exception as e:
            log_message(f"블로그 메뉴 클릭 실패: {str(e)}")
            # 직접 블로그 URL로 이동
            driver.get("https://blog.naver.com")
            time.sleep(3)
        
        # 3단계: 글쓰기 버튼 클릭
        log_message("3단계: 글쓰기 버튼 클릭")
        try:
            # 기존 코드의 글쓰기 버튼 XPath 사용
            write_button_xpath = "/html/body/div[2]/div[2]/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div[1]/a[2]"
            driver.find_element(By.XPATH, write_button_xpath).click()
            time.sleep(3)
            log_message("글쓰기 버튼 클릭 완료")
        except Exception as e:
            log_message(f"글쓰기 버튼 클릭 실패, 링크 텍스트로 시도: {str(e)}")
            try:
                driver.find_element(By.LINK_TEXT, "글쓰기").click()
                time.sleep(3)
                log_message("글쓰기 링크 클릭 완료")
            except Exception as e2:
                log_message(f"글쓰기 링크 클릭도 실패, 직접 URL 이동: {str(e2)}")
                driver.get("https://blog.naver.com/PostWriteForm.naver")
                time.sleep(5)
        
        # 4단계: 새 창으로 전환
        log_message("4단계: 새 창으로 전환")
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            log_message("새 창으로 전환 완료")
        else:
            log_message("새 창이 없음, 현재 창 사용")
        
        time.sleep(3)
        
        # 5단계: 제목 입력
        log_message("5단계: 제목 입력")
        title = "AI가 작성한 블로그 포스트"
        if not keyword_data.empty and '키워드' in keyword_data.columns:
            title = keyword_data.iloc[0]['키워드']
        
        try:
            # 기존 코드의 정확한 XPath 사용
            title_xpath = "/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[1]/div[1]/div/div/p/span[2]"
            title_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, title_xpath))
            )
            title_element.click()
            time.sleep(1)
            
            # 제목 입력 (기존 코드 방식)
            pyperclip.copy(title)
            actions = ActionChains(driver)
            actions.key_down(COMCON).send_keys('v').key_up(COMCON).perform()
            log_message(f"제목 입력 완료: {title}")
        except Exception as e:
            log_message(f"제목 입력 실패: {str(e)}")
            return False
        
        time.sleep(2)
        
        # 6단계: 본문 입력 영역 클릭
        log_message("6단계: 본문 입력 영역 클릭")
        try:
            # 기존 코드의 정확한 XPath 사용
            content_xpath = "/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[2]/div/div/div/div/p/span[2]"
            content_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, content_xpath))
            )
            content_element.click()
            time.sleep(1)
            log_message("본문 입력 영역 클릭 완료")
        except Exception as e:
            log_message(f"본문 입력 영역 클릭 실패: {str(e)}")
            return False
        
        # 7단계: 본문 내용 입력
        log_message("7단계: 본문 내용 입력")
        try:
            # 기존 코드의 정확한 방식 사용
            pyperclip.copy(content)
            actions = ActionChains(driver)
            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            log_message("본문 입력 완료")
        except Exception as e:
            log_message(f"본문 입력 실패: {str(e)}")
            return False
        
        time.sleep(3)
        
        # 8단계: 발행 버튼 클릭
        log_message("8단계: 발행 버튼 클릭")
        try:
            # 기존 코드의 정확한 XPath 사용
            publish_xpath = "/html/body/div[1]/div/div[1]/div/div[3]/div[2]/button"
            publish_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, publish_xpath))
            )
            publish_element.click()
            log_message("발행 버튼 클릭 완료")
            time.sleep(5)
        except Exception as e:
            log_message(f"발행 버튼 클릭 실패: {str(e)}")
            return False
        
        log_message("=== 네이버 블로그 글 작성 완료 ===")
        return True
        
    except Exception as e:
        log_message(f"네이버 블로그 글 작성 오류: {str(e)}")
        return False

def write_naver_cafe_post(driver, content, keyword_data):
    """네이버 카페 글 작성 (기본 구현)"""
    try:
        from selenium.webdriver import ActionChains
        from selenium.webdriver.common.keys import Keys
        import pyperclip
        import platform as platform_module
        
        # 운영체제별 키 설정
        COMCON = Keys.COMMAND if platform_module.system() == "Darwin" else Keys.CONTROL
        
        log_message("=== 네이버 카페 글 작성 시작 ===")
        
        # 카페 메인 페이지로 이동 (실제 카페 URL 필요)
        log_message("카페 글쓰기 페이지로 이동")
        driver.get("https://cafe.naver.com")
        time.sleep(3)
        
        # 카페별로 다르므로 기본적인 글쓰기 시도
        try:
            # 글쓰기 버튼 찾기
            write_buttons = [
                "//a[contains(text(), '글쓰기')]",
                "//button[contains(text(), '글쓰기')]",
                "//a[contains(@href, 'write')]"
            ]
            
            write_clicked = False
            for xpath in write_buttons:
                try:
                    driver.find_element(By.XPATH, xpath).click()
                    write_clicked = True
                    break
                except:
                    continue
            
            if not write_clicked:
                log_message("글쓰기 버튼을 찾을 수 없습니다.")
                return False
                
        except Exception as e:
            log_message(f"글쓰기 버튼 클릭 실패: {str(e)}")
            return False
        
        time.sleep(3)
        
        # 제목 입력
        title = "AI가 작성한 카페 포스트"
        if not keyword_data.empty and '키워드' in keyword_data.columns:
            title = keyword_data.iloc[0]['키워드']
        
        try:
            # 제목 입력 필드 찾기
            title_selectors = [
                "//input[@placeholder='제목을 입력하세요']",
                "//input[contains(@class, 'title')]",
                "//div[@contenteditable='true' and contains(@class, 'title')]"
            ]
            
            title_input = None
            for selector in title_selectors:
                try:
                    title_input = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if title_input:
                title_input.click()
                time.sleep(1)
                pyperclip.copy(title)
                actions = ActionChains(driver)
                actions.key_down(COMCON).send_keys('v').key_up(COMCON).perform()
                log_message(f"제목 입력 완료: {title}")
            else:
                log_message("제목 입력 필드를 찾을 수 없습니다.")
                
        except Exception as e:
            log_message(f"제목 입력 실패: {str(e)}")
        
        time.sleep(2)
        
        # 본문 입력
        try:
            # 본문 입력 필드 찾기
            content_selectors = [
                "//div[@contenteditable='true' and contains(@class, 'content')]",
                "//textarea[contains(@class, 'content')]",
                "//div[contains(@class, 'editor')]//div[@contenteditable='true']"
            ]
            
            content_input = None
            for selector in content_selectors:
                try:
                    content_input = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if content_input:
                content_input.click()
                time.sleep(1)
                pyperclip.copy(content)
                actions = ActionChains(driver)
                actions.key_down(COMCON).send_keys('v').key_up(COMCON).perform()
                log_message("본문 입력 완료")
            else:
                log_message("본문 입력 필드를 찾을 수 없습니다.")
                
        except Exception as e:
            log_message(f"본문 입력 실패: {str(e)}")
        
        time.sleep(3)
        
        # 발행 버튼 클릭
        try:
            publish_selectors = [
                "//button[contains(text(), '발행')]",
                "//button[contains(text(), '등록')]",
                "//button[contains(text(), '작성')]",
                "//button[contains(@class, 'publish')]"
            ]
            
            publish_clicked = False
            for selector in publish_selectors:
                try:
                    publish_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    publish_btn.click()
                    publish_clicked = True
                    break
                except:
                    continue
            
            if publish_clicked:
                log_message("발행 버튼 클릭 완료")
                time.sleep(5)
            else:
                log_message("발행 버튼을 찾을 수 없습니다.")
                
        except Exception as e:
            log_message(f"발행 버튼 클릭 실패: {str(e)}")
        
        log_message("=== 네이버 카페 글 작성 완료 ===")
        return True
        
    except Exception as e:
        log_message(f"네이버 카페 글 작성 오류: {str(e)}")
        return False

def test_chrome_driver():
    """Chrome 드라이버 테스트"""
    try:
        log_message("=== Chrome 드라이버 테스트 시작 ===")
        driver = setup_chrome_driver()
        
        if not driver:
            log_message("Chrome 드라이버 설정 실패")
            return False
        
        # 1단계: 구글 페이지 테스트
        log_message("1단계: 구글 페이지 테스트")
        driver.get("https://www.google.com")
        time.sleep(3)
        log_message(f"구글 페이지 로드 완료: {driver.current_url}")
        log_message(f"구글 페이지 제목: {driver.title}")
        
        # 2단계: 네이버 메인 페이지 테스트
        log_message("2단계: 네이버 메인 페이지 테스트")
        driver.get("https://www.naver.com")
        time.sleep(3)
        log_message(f"네이버 메인 페이지 로드 완료: {driver.current_url}")
        log_message(f"네이버 메인 페이지 제목: {driver.title}")
        
        # 3단계: 네이버 로그인 페이지 테스트
        log_message("3단계: 네이버 로그인 페이지 테스트")
        driver.get("https://nid.naver.com/nidlogin.login")
        time.sleep(5)
        log_message(f"네이버 로그인 페이지 로드 완료: {driver.current_url}")
        log_message(f"네이버 로그인 페이지 제목: {driver.title}")
        
        # 4단계: 페이지 요소 확인
        log_message("4단계: 로그인 페이지 요소 확인")
        try:
            # ID 입력 필드 확인
            id_input = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[1]/div/div[1]/input")
            log_message("ID 입력 필드 발견")
            
            # 비밀번호 입력 필드 확인
            pw_input = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[1]/div/div[2]/input")
            log_message("비밀번호 입력 필드 발견")
            
            # 로그인 버튼 확인
            login_btn = driver.find_element(By.ID, "log.login")
            log_message("로그인 버튼 발견")
            
            log_message("모든 로그인 요소가 정상적으로 발견됨")
            
        except Exception as e:
            log_message(f"로그인 페이지 요소 확인 실패: {str(e)}")
            return False
        
        driver.quit()
        log_message("Chrome 드라이버 테스트 완료")
        return True
        
    except Exception as e:
        log_message(f"Chrome 드라이버 테스트 실패: {str(e)}")
        import traceback
        log_message(f"상세 오류: {traceback.format_exc()}")
        return False

def test_login_page():
    """로그인 페이지 전용 테스트"""
    try:
        log_message("=== 로그인 페이지 테스트 시작 ===")
        driver = setup_chrome_driver()
        
        if not driver:
            log_message("Chrome 드라이버 설정 실패")
            return False
        
        # 네이버 로그인 페이지로 직접 이동
        log_message("네이버 로그인 페이지로 이동")
        driver.get("https://nid.naver.com/nidlogin.login")
        time.sleep(5)
        
        log_message(f"현재 URL: {driver.current_url}")
        log_message(f"페이지 제목: {driver.title}")
        
        # 페이지 소스 일부 확인
        page_source = driver.page_source
        if "로그인" in page_source or "login" in page_source.lower():
            log_message("로그인 관련 텍스트 발견")
        else:
            log_message("경고: 로그인 관련 텍스트를 찾을 수 없음")
        
        # 스크린샷 저장 (디버깅용)
        try:
            driver.save_screenshot("login_page_debug.png")
            log_message("로그인 페이지 스크린샷 저장됨: login_page_debug.png")
        except Exception as e:
            log_message(f"스크린샷 저장 실패: {str(e)}")
        
        driver.quit()
        log_message("로그인 페이지 테스트 완료")
        return True
        
    except Exception as e:
        log_message(f"로그인 페이지 테스트 실패: {str(e)}")
        import traceback
        log_message(f"상세 오류: {traceback.format_exc()}")
        return False

def test_login_process():
    """실제 로그인 과정 테스트"""
    try:
        log_message("=== 로그인 과정 테스트 시작 ===")
        driver = setup_chrome_driver()
        
        if not driver:
            log_message("Chrome 드라이버 설정 실패")
            return False
        
        # 첫 번째 계정으로 로그인 테스트
        account_data = st.session_state.account_data.iloc[0].to_dict()
        log_message(f"테스트 계정: {account_data['계정명']}")
        
        # 로그인 시도
        login_result = login_naver_blog(driver, account_data)
        
        if login_result:
            log_message("로그인 테스트 성공!")
            # 스크린샷 저장
            try:
                driver.save_screenshot("login_success_debug.png")
                log_message("로그인 성공 스크린샷 저장됨: login_success_debug.png")
            except Exception as e:
                log_message(f"스크린샷 저장 실패: {str(e)}")
        else:
            log_message("로그인 테스트 실패!")
            # 실패 스크린샷 저장
            try:
                driver.save_screenshot("login_failed_debug.png")
                log_message("로그인 실패 스크린샷 저장됨: login_failed_debug.png")
            except Exception as e:
                log_message(f"스크린샷 저장 실패: {str(e)}")
        
        driver.quit()
        log_message("로그인 과정 테스트 완료")
        return login_result
        
    except Exception as e:
        log_message(f"로그인 과정 테스트 실패: {str(e)}")
        import traceback
        log_message(f"상세 오류: {traceback.format_exc()}")
        return False

def execute_task(platform, api_key, phone_number, content, min_wait, max_wait, use_dynamic_ip):
    """작업 수행"""
    # API 인증 상태 확인
    if not st.session_state.api_authenticated:
        st.error("❌ API 인증이 필요합니다. 먼저 API 키를 입력하고 인증해주세요.")
        log_message("작업 수행 실패: API 인증 필요")
        return
    
    # 계정 데이터 확인
    if st.session_state.account_data.empty:
        st.error("❌ 계정 데이터가 없습니다. 먼저 계정을 추가해주세요.")
        log_message("작업 수행 실패: 계정 데이터 없음")
        return
    
    log_message("=== 작업 수행 시작 ===")
    log_message(f"플랫폼: {platform}")
    log_message(f"API KEY: {'인증됨' if st.session_state.api_authenticated else '인증되지 않음'}")
    log_message(f"핸드폰 번호: {phone_number or '설정되지 않음'}")
    log_message(f"대기시간: {min_wait}~{max_wait}분")
    log_message(f"유동 IP 사용: {'예' if use_dynamic_ip else '아니오'}")
    log_message(f"콘텐츠 길이: {len(content)} 문자")
    log_message(f"계정 수: {len(st.session_state.account_data)}")
    log_message(f"키워드 수: {len(st.session_state.keyword_data)}")
    log_message(f"프롬프트 수: {len(st.session_state.prompt_data)}")
    
    # 진행률 표시
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    driver = None
    success_count = 0
    
    try:
        # Chrome 드라이버 설정
        status_text.text("Chrome 드라이버 설정 중...")
        progress_bar.progress(0.1)
        log_message("Chrome 드라이버 설정 시작")
        driver = setup_chrome_driver()
        
        if not driver:
            st.error("❌ Chrome 드라이버 설정에 실패했습니다.")
            log_message("Chrome 드라이버 설정 실패")
            return
        
        log_message(f"Chrome 드라이버 설정 완료: {driver is not None}")
        log_message(f"드라이버 세션 ID: {driver.session_id if hasattr(driver, 'session_id') else 'N/A'}")
        
        # 드라이버 상태 확인
        try:
            current_url = driver.current_url
            page_title = driver.title
            log_message(f"드라이버 초기 상태 - URL: {current_url}, 제목: {page_title}")
        except Exception as e:
            log_message(f"드라이버 상태 확인 실패: {str(e)}")
        
        # 네이버 메인 페이지로 이동 테스트
        log_message("네이버 메인 페이지 이동 테스트")
        try:
            driver.get("https://www.naver.com")
            time.sleep(3)
            log_message(f"네이버 메인 페이지 이동 완료: {driver.current_url}")
            log_message(f"네이버 메인 페이지 제목: {driver.title}")
        except Exception as e:
            log_message(f"네이버 메인 페이지 이동 실패: {str(e)}")
            return
        
        # AI 콘텐츠 생성
        status_text.text("AI 콘텐츠 생성 중...")
        progress_bar.progress(0.2)
        generated_content = generate_content_with_gemini(content)
        if generated_content:
            log_message("AI 콘텐츠 생성 완료")
            final_content = generated_content
        else:
            log_message("AI 콘텐츠 생성 실패 - 원본 콘텐츠 사용")
            final_content = content
        
        # 각 계정으로 작업 수행
        total_accounts = len(st.session_state.account_data)
        
        for idx, (_, account) in enumerate(st.session_state.account_data.iterrows()):
            try:
                status_text.text(f"계정 {idx + 1}/{total_accounts} 처리 중: {account['계정명']}")
                progress_bar.progress(0.3 + (idx * 0.6 / total_accounts))
                
                # 로그인
                log_message(f"계정 {account['계정명']} 로그인 시도 시작")
                log_message(f"현재 URL: {driver.current_url}")
                
                login_result = login_to_platform(driver, platform, account)
                log_message(f"로그인 결과: {login_result}")
                
                if login_result:
                    log_message(f"계정 {account['계정명']} 로그인 성공")
                    log_message(f"로그인 후 URL: {driver.current_url}")
                    
                    # 글 작성
                    log_message(f"계정 {account['계정명']} 글 작성 시작")
                    write_result = write_blog_post(driver, platform, final_content, st.session_state.keyword_data)
                    log_message(f"글 작성 결과: {write_result}")
                    
                    if write_result:
                        log_message(f"계정 {account['계정명']} 글 작성 성공")
                        success_count += 1
                    else:
                        log_message(f"계정 {account['계정명']} 글 작성 실패")
                    
                    # 대기시간 적용
                    wait_time = random.randint(min_wait * 60, max_wait * 60)
                    log_message(f"대기시간: {wait_time}초")
                    time.sleep(wait_time)
                else:
                    log_message(f"계정 {account['계정명']} 로그인 실패")
                    log_message(f"로그인 실패 후 URL: {driver.current_url}")
                
            except Exception as e:
                log_message(f"계정 {account['계정명']} 처리 중 오류: {str(e)}")
                continue
        
        # 완료
        status_text.text("작업 완료!")
        progress_bar.progress(1.0)
        
        log_message(f"=== 작업 수행 완료 ===")
        log_message(f"성공한 계정: {success_count}/{total_accounts}")
        
        if success_count > 0:
            st.success(f"✅ {success_count}개 계정에서 작업이 성공적으로 완료되었습니다!")
        else:
            st.error("❌ 모든 계정에서 작업이 실패했습니다.")
            
    except Exception as e:
        log_message(f"작업 수행 중 오류: {str(e)}")
        st.error(f"❌ 작업 수행 중 오류가 발생했습니다: {str(e)}")
    
    finally:
        if driver:
            driver.quit()
            log_message("Chrome 드라이버 종료")

def reset_data():
    """데이터 초기화"""
    st.session_state.account_data = pd.DataFrame(columns=['계정명', '비밀번호', '장소'])
    st.session_state.keyword_data = pd.DataFrame(columns=['주소', '업체', '파일경로', '해시태그'])
    st.session_state.prompt_data = pd.DataFrame(columns=['프롬프트'])
    st.session_state.log_messages = []
    st.session_state.api_authenticated = False
    st.session_state.api_key = ""
    st.session_state.selected_model = "gemini-1.5-flash"
    st.session_state.image_folder = None
    st.session_state.image_files = []
    st.session_state.preview_content = None
    st.session_state.main_content = None
    log_message("모든 데이터가 초기화되었습니다.")
    st.rerun()

if __name__ == "__main__":
    main()
