import os
import random
import threading
import time
from selenium.webdriver import Keys

from ai import gemini
from web import login, webdriver, blog, cafe
from ip_trans import ip_trans_execute
from media import video, image
from utils import parsing
from data.const import *
from ui import streamlit_log as log

WAIT = 10

class StreamlitTaskExecutor:
    """Streamlit용 작업 실행 클래스"""
    
    def __init__(self):
        self.is_running = False
        self.current_step = ""
        self.progress = 0
        self.api_key = None
        
    def set_api_key(self, api_key):
        """API 키 설정"""
        self.api_key = api_key
        
    def init_gemini_with_streamlit_api_key(self, model_name='gemini-2.5-flash'):
        """Streamlit에서 설정한 API 키로 Gemini 초기화"""
        try:
            if self.api_key:
                # 새로운 Gemini API 방식으로 초기화
                gemini.init_gemini_with_key(self.api_key, model_name)
                log.append_log(f"Streamlit API 키로 Gemini를 초기화했습니다. 사용 모델: {model_name}")
                return True
            else:
                log.append_log("[ERROR] API 키가 설정되지 않았습니다.")
                return False
        except Exception as e:
            log.append_log(f"[ERROR] Gemini 초기화 실패: {str(e)}")
            return False

    def init(self):
        """웹드라이버 초기화"""
        try:
            webdriver.init_chrome()
            log.append_log("웹드라이버를 초기화했습니다.")
            return True
        except Exception as e:
            log.append_log(f"[ERROR] 웹드라이버 초기화 실패: {str(e)}")
            return False

    def execute_login(self, id_val, pw_val):
        """로그인 실행"""
        try:
            log.append_log("Naver 로그인 화면에 접속합니다.")
            login.enter_naver_login()
            self.input_login_value(id_val, pw_val)
            return True
        except Exception as e:
            log.append_log(f"[ERROR] 로그인 실패: {str(e)}")
            return False

    def input_login_value(self, id_val, pw_val):
        """로그인 정보 입력"""
        try:
            login.click_ID_phone()
            log.append_log(f"로그인을 실행합니다.\nid = {id_val}")
            login.input_id_pw(id_val, pw_val)
            login.click_login_button()
            
            # 캡챠 검사
            if login.check_capcha_appear():
                log.append_log("[ERROR] 캡챠가 발생했습니다. 수동으로 해제해주세요.")
                while True:
                    if login.check_capcha_done() is True:
                        break
                        
            login.click_login_not_save()
            log.append_log("로그인을 완료하였습니다.")
            
        except Exception as e:
            log.append_log(f"[ERROR] 로그인 정보 입력 실패: {str(e)}")
            raise

    def post_blog(self, contents_data, category_name, id_val, pw_val, place, titles_data, content_template, use_dynamic_ip=False):
        """블로그 포스팅 실행"""
        try:
            log.append_log("블로그 포스팅을 시작합니다.")
            
            for i, keyword_data in enumerate(contents_data):
                address = keyword_data.get('주소', '')
                company = keyword_data.get('업체', '')
                
                # 제목 생성
                title = self.get_title_from_data(titles_data, address, company)
                
                log.append_log("블로그에 진입합니다.")
                blog.enter_blog(True)
                blog.enter_iframe()
                
                # 이벤트 창 끄기
                webdriver.click_element_css("button.btn_close._btn_close")
                blog.enter_posting_window()
                
                time.sleep(10)
                blog.cancel_continue()
                log.append_log("이어 작성하기를 취소합니다.")
                blog.exit_help()
                log.append_log("도움말 창을 닫습니다.")
                
                # 카테고리 확인
                log.append_log(f"카테고리가 존재하는지 확인합니다.\n카테고리 = {category_name}")
                blog.click_post_button()
                blog.click_category_listbox()
                
                if not blog.choose_category(category_name):
                    log.append_log(f"[ERROR] 카테고리가 존재하지 않습니다. 다음 작업으로 넘어갑니다.")
                    blog.exit_iframe()
                    blog.exit_tab()
                    webdriver.enter_url("https://www.naver.com")
                    self.get_waiting_time()
                    break
                else:
                    log.append_log("존재하는 카테고리입니다. 작성을 계속합니다.")
                    blog.click_category_listbox()
                
                # 제목 작성
                log.append_log(f"제목을 작성합니다.\n제목 = {title}")
                blog.write_title(title)
                log.append_log("본문을 작성합니다.")
                blog.enter_context_input()
                
                # 본문 작성
                article = parsing.parse_contents(address, company, content_template)
                
                # 이미지 업로드
                image_paths = keyword_data.get('파일 경로', '').split(',') if keyword_data.get('파일 경로') else []
                count = sum(1 for text in article if text == PHOTO)
                length = min(len(image_paths), count) if image_paths else 0
                
                self.write_content_blog(address, company, article, image_paths[:length], length)
                self.insert_place(place)
                
                # 발행
                blog.click_post_button()
                blog.click_category_listbox()
                blog.choose_category(category_name)
                
                # 해시태그 추가
                hashtags = keyword_data.get('해시태그', '').split(',') if keyword_data.get('해시태그') else []
                if hashtags:
                    log.append_log("해시태그를 추가합니다.")
                    blog.click_hashtag()
                    for hashtag in hashtags:
                        hashtag = hashtag.replace("%주소%", address).replace("%업체%", company)
                        blog.send_hashtag(hashtag.strip())
                        blog.insert_enter()
                    log.append_log("해시태그 추가를 완료하였습니다.")
                
                blog.complete_posting()
                log.append_log("포스팅을 완료하였습니다.")
                
                blog.exit_iframe()
                blog.exit_tab()
                webdriver.enter_url("https://www.naver.com")
                
                if use_dynamic_ip:
                    ip_trans_execute.trans_ip()
                
                if i < len(contents_data) - 1:
                    self.get_waiting_time()
            
            log.append_log("블로그 포스팅을 완료하였습니다.")
            
        except Exception as e:
            log.append_log(f"[ERROR] 블로그 포스팅 중 오류 발생: {str(e)}")
            raise

    def post_cafe(self, contents_data, cafe_list, id_val, pw_val, titles_data, content_template, allow_comments=True, use_dynamic_ip=False):
        """카페 포스팅 실행"""
        try:
            log.append_log("카페 포스팅을 시작합니다.")
            
            for cafe_index, cafe_data in enumerate(cafe_list):
                url = cafe_data.get('카페 주소', '')
                board_name = cafe_data.get('게시판 이름', '')
                
                for i, keyword_data in enumerate(contents_data):
                    address = keyword_data.get('주소', '')
                    company = keyword_data.get('업체', '')
                    
                    # 제목 생성
                    title = self.get_title_from_data(titles_data, address, company)
                    
                    cafe.enter_cafe(url)
                    
                    # 가입 여부 확인
                    if not cafe.is_signed_up():
                        log.append_log("[ERROR] 가입하지 않은 카페입니다. 다음 카페로 넘어갑니다.")
                        break
                    
                    log.append_log("카페에 진입합니다.")
                    cafe.click_posting_button()
                    
                    # 댓글 설정
                    if not allow_comments:
                        cafe.disable_comment()
                    
                    # 카테고리 선택
                    cafe.click_board_choice()
                    log.append_log(f"카테고리를 선택합니다.\n카테고리 = {board_name}")
                    
                    if not cafe.choose_board(board_name):
                        log.append_log(f"[ERROR] 카테고리가 존재하지 않습니다. 다음 작업으로 넘어갑니다.")
                        self.get_waiting_time()
                        break
                    
                    # 제목 작성
                    log.append_log(f"제목을 작성합니다.\n제목 = {title}")
                    cafe.write_title(title)
                    cafe.enter_content_input()
                    
                    # 본문 작성
                    article = parsing.parse_contents(address, company, content_template)
                    image_paths = keyword_data.get('파일 경로', '').split(',') if keyword_data.get('파일 경로') else []
                    count = sum(1 for text in article if text == PHOTO)
                    length = min(len(image_paths), count) if image_paths else 0
                    
                    log.append_log("본문을 작성합니다.")
                    self.write_content_cafe(address, company, article, image_paths[:length], length)
                    
                    # 해시태그 추가
                    hashtags = keyword_data.get('해시태그', '').split(',') if keyword_data.get('해시태그') else []
                    if hashtags:
                        cafe.click_hashtag()
                        for hashtag in hashtags:
                            hashtag = hashtag.replace("%주소%", address).replace("%업체%", company)
                            cafe.send_hashtag(hashtag.strip())
                            cafe.insert_enter()
                    
                    # 등록
                    cafe.click_register_button()
                    if webdriver.switch_to_alert():
                        login.switch_to_popup()
                        self.input_login_value(id_val, pw_val)
                        login.switch_to_prev_window()
                        cafe.click_register_button()
                    
                    webdriver.exit_tab()
                    log.append_log("포스팅을 완료하였습니다.")
                    
                    if use_dynamic_ip:
                        ip_trans_execute.trans_ip()
                    
                    if cafe_index < len(cafe_list) - 1:
                        self.get_waiting_time()
            
            log.append_log("카페 포스팅을 완료하였습니다.")
            
        except Exception as e:
            log.append_log(f"[ERROR] 카페 포스팅 중 오류 발생: {str(e)}")
            raise

    def write_content_blog(self, address, company, article, image_paths, image_length):
        """블로그 콘텐츠 작성"""
        try:
            # 썸네일 이미지 생성
            log.append_log("썸네일 이미지를 제작합니다.")
            image.generate_image("", address, company)  # 전화번호는 별도로 처리
            
            log.append_log("썸네일 이미지를 이용한 영상을 제작합니다.")
            video.generate_video()
            log.append_log("썸네일 이미지와 영상 제작이 완료되었습니다.")
            
            image_index = 0
            video_path = ""
            
            for content in article:
                if THUMBNAIL in content:
                    image.upload_image(THUMBNAIL_PATH)
                elif PHOTO in content and image_index < image_length:
                    try:
                        if image_index < len(image_paths):
                            image.draw_border_sample(image_paths[image_index])
                            image.upload_image(NEW_IMAGE_PATH)
                            log.append_log(f"이미지를 업로드합니다.\n파일명: {os.path.basename(image_paths[image_index])}")
                            time.sleep(10)
                            image.remove_image(NEW_IMAGE_PATH)
                    except FileNotFoundError:
                        log.append_log(f"[ERROR] 이미지 경로를 찾을 수 없습니다.")
                    finally:
                        image_index += 1
                        image.blog_upload_image_error()
                elif VIDEO in content:
                    video_path = os.path.abspath(VIDEO_PATH)
                    video.upload_video_to_blog(video_path, f"{address} {company}")
                elif ENTER is content:
                    blog.insert_enter()
                else:
                    blog.write_text(content)
            
            # 정리
            if video_path and os.path.exists(video_path):
                video.remove_video(video_path)
            if os.path.exists(THUMBNAIL_PATH):
                image.remove_image(THUMBNAIL_PATH)
                
        except Exception as e:
            log.append_log(f"[ERROR] 블로그 콘텐츠 작성 중 오류 발생: {str(e)}")
            raise

    def write_content_cafe(self, address, company, article, image_paths, image_length):
        """카페 콘텐츠 작성"""
        try:
            # 썸네일 이미지 생성
            image.generate_image("", address, company)
            video.generate_video()
            
            image_index = 0
            video_path = ""
            
            for content in article:
                if THUMBNAIL in content:
                    image.upload_image(THUMBNAIL_PATH)
                elif PHOTO in content and image_index < image_length:
                    try:
                        if image_index < len(image_paths):
                            image.draw_border_sample(image_paths[image_index])
                            image.upload_image(NEW_IMAGE_PATH)
                            log.append_log(f"이미지를 업로드합니다.\n파일명: {os.path.basename(image_paths[image_index])}")
                            time.sleep(10)
                            image.remove_image(NEW_IMAGE_PATH)
                    except FileNotFoundError:
                        log.append_log(f"[ERROR] 이미지 경로를 찾을 수 없습니다.")
                    finally:
                        image_index += 1
                        image.cafe_upload_image_error()
                elif VIDEO in content:
                    video_path = os.path.abspath(VIDEO_PATH)
                    video.upload_video_to_cafe(video_path, f"{address} {company}")
                elif ENTER is content:
                    cafe.insert_enter()
                else:
                    cafe.write_text(content)
            
            # 정리
            if video_path and os.path.exists(video_path):
                video.remove_video(video_path)
            if os.path.exists(THUMBNAIL_PATH):
                image.remove_image(THUMBNAIL_PATH)
                
        except Exception as e:
            log.append_log(f"[ERROR] 카페 콘텐츠 작성 중 오류 발생: {str(e)}")
            raise

    def get_waiting_time(self, min_time=5, max_time=10):
        """대기 시간 처리"""
        try:
            total_time = random.randint(min_time * 60, max_time * 60)  # 분을 초로 변환
            minutes = total_time // 60
            seconds = total_time - minutes * 60
            
            log.append_log(f"다음 작업까지 대기합니다.\n대기시간 = {minutes}분 {seconds}초")
            time.sleep(total_time)
            
            return total_time, minutes, seconds
        except Exception as e:
            log.append_log(f"[ERROR] 대기 시간 처리 중 오류 발생: {str(e)}")
            return 0, 0, 0

    def get_title_from_data(self, titles_data, address, company):
        """제목 데이터에서 제목 선택 또는 생성"""
        try:
            if titles_data and len(titles_data) > 0:
                # 제목 데이터가 있으면 랜덤 선택
                title_item = random.choice(titles_data)
                title = list(title_item.values())[0]  # 첫 번째 값 사용
                # 치환
                title = title.replace("%주소%", address).replace("%업체%", company)
                return title
            else:
                # 제목 데이터가 없으면 AI로 생성
                return self.get_titles_with_ai(address, company, "블로그")
        except Exception as e:
            log.append_log(f"[ERROR] 제목 생성 중 오류 발생: {str(e)}")
            return f"{address} {company}"

    def get_titles_with_ai(self, address, company, platform):
        """AI를 사용한 제목 생성"""
        try:
            time.sleep(1)
            webdriver.enter_url("https://www.naver.com")
            
            webdriver.send_data_by_xpath_loop(
                "/html/body/div[2]/div[1]/div/div[3]/div/div/form/fieldset/div/input",
                f"{address} {company}"
            )
            
            webdriver.click_element_xpath("/html/body/div[2]/div[1]/div/div[3]/div/div/form/fieldset/button")
            webdriver.push_search_blog_cafe_button(platform)
            
            titles = webdriver.get_text_from_css_selector("a.title_link")
            time.sleep(WAIT)
            
            # Streamlit에서 인증된 모델 사용 (세션 상태에서 가져오기)
            import streamlit as st
            verified_model = getattr(st.session_state, 'verified_model', 'gemini-2.5-flash')
            
            # Streamlit API 키로 Gemini 초기화
            if not self.init_gemini_with_streamlit_api_key(verified_model):
                return f"{address} {company}"
            
            response = gemini.create_title(titles, address, company)
            webdriver.enter_url("https://www.naver.com")
            
            return response
        except Exception as e:
            log.append_log(f"[ERROR] AI 제목 생성 중 오류 발생: {str(e)}")
            return f"{address} {company}"

    def insert_place(self, place):
        """장소 삽입"""
        try:
            if not place:
                return
            
            # 장소 삽입 버튼 누르기
            webdriver.click_element_xpath("/html/body/div[1]/div/div[3]/div/div/div[1]/div/header/div[1]/ul/li[14]/button")
            
            # 장소 검색
            webdriver.send_data_by_xpath_loop(
                "/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/div/div[2]/div[1]/div[2]/div/input", 
                place
            )
            
            time.sleep(5)
            webdriver.send_keys_action(Keys.RETURN)
            time.sleep(5)
            
            # 첫 번째 검색 결과 클릭
            webdriver.click_element_xpath("/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/div/div[2]/div[2]/div[1]/ul/li/a")
            webdriver.click_element_xpath("/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/div/div[2]/div[2]/div[1]/ul/li/button")
            
            # 확인 버튼 클릭
            webdriver.click_element_xpath("/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/footer/div/button")
            
        except Exception as e:
            log.append_log(f"[ERROR] 장소 삽입 중 오류 발생: {str(e)}")

# 전역 실행기 인스턴스
task_executor = StreamlitTaskExecutor()