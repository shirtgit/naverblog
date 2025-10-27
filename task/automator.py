from task.task_functions import *
from data import parsing_data, text_data, content_data, list_data, title_data
from cache import download_cache
from ui import log

import os

def start_task():
    # 캐시 먼저 저장
    os.makedirs("cache", exist_ok=True)

    download_cache.download_JSON()
    download_cache.download_CSV()
    log.append_log("캐시 값을 저장합니다.")

    text_collection = text_data.TextData()
    parse_collection = parsing_data.ParseData()

    # 크롬 초기화
    init()

    # 계정 정보 가져오기
    login_list = list_data.get_list_data(list_data.ListData().account_list)

    # 키워드 리스트(4열) 불러오기
    keywords = list_data.get_list_data(list_data.ListData().keyword_list)

    # 키워드, 이미지 경로 저장
    # 이미지 경로 셔플은 블로그 진입 및 컨텐츠 작성 전에 수행
    contents = content_data.ContentData()
    contents.set_keywords([(row[0], row[1]) for row in keywords])
    contents.combinate_keywords()
    # print(contents.keywords)
    contents.set_image_path([row[2] for row in keywords])

    contents.set_hashtags([row[3] for row in keywords])

    cafe_list = list_data.get_list_data(list_data.ListData().cafe_list)
    blog_data = list_data.get_list_data(list_data.ListData().blog_list)
    blog_dict = dict(blog_data)

    # 로그인 반복
    for i in range(len(login_list)):
        category_name = blog_dict.get(login_list[i][0])
        log.append_log(f"카테고리를 탐색합니다.\n카테고리 = {category_name}")
        execute_login(login_list[i][0], login_list[i][1])
        # 여기서는 키워드 X 키워드대로 글을 생성하여 자동 포스팅 -> 반복문으로 감쌀 것 (for문은 한개만 사용!)

        # 로그인 다중 접속을 위한 테스트
        # 블로그 / 카페 / 둘다
        task_index = box_data.BoxData().get_rb_value()

        # 맵 / 딕셔너리로 코드 간단하게 구현할 수는 있지만
        # 성능 최적화를 위해서 if문으로 단순하게 구현
        if task_index == 0:
            post_blog(contents, category_name, login_list[i][0], login_list[i][1], login_list[i][2], True)
        elif task_index == 1:
            post_cafe(contents, cafe_list, login_list[i][0], login_list[i][1])
        elif task_index == 2:
            post_blog(contents, category_name, login_list[i][0], login_list[i][1], login_list[i][2], False)
            post_cafe(contents, cafe_list, login_list[i][0], login_list[i][1])

        log.append_log(f"{login_list[i][0]} 계정으로 모든 포스팅을 완료하였습니다.")

        webdriver.enter_url(NAVER)
        login.click_logout()

        # 대기시간 설정(안 해도 될듯)
        # if i < len(login_list) - 1:
        #     total_time, minutes, seconds = get_waiting_time()
        #     log.append_log(f"다음 작업까지 대기합니다.\n대기시간 = {minutes}분 {seconds}초")
        #     time.sleep(total_time)
        if i == len(login_list) - 1:
            log.append_log("모든 작업을 완료하였습니다.")
            button_data.ButtonData().execute_button_Enable(True)

        # # 테스트 코드
        # if button_data.ButtonData().get_toggle_value() is True:
        #     log.append_log("IP를 변경합니다.")
        #     ip_trans.toggle_airplane_mode()
        #     curren_ip = ip_trans.get_current_ip()
        #     log.append_log(f"현재 IP = {curren_ip}")
    button_data.ButtonData().set_all_buttons(True)

def get_waiting_time():
    min_time = text_data.TextData().get_waiting_min()
    max_time = text_data.TextData().get_waiting_max()
    print(f"min_time = {min_time}")
    print(f"max_time = {max_time}")
    total_time = random.randint(min_time, max_time)
    minutes = total_time // 60
    seconds = total_time - minutes * 60
    return total_time, minutes, seconds