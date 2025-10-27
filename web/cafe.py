import clipboard
import platform
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ui import log

from utils.decorators import sleep_after
from web import webdriver
from data.const import *
import time


KEY = Keys.COMMAND if platform.system() == 'Darwin' else Keys.CONTROL

@sleep_after(3)
def enter_cafe(cafe_url):
    print(time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()))
    webdriver.enter_url(cafe_url)

@sleep_after()
def is_signed_up():
    button = webdriver.get_element_xpath("/html/body/div[3]/div/div[5]/div[1]/div[1]/div[1]/div[2]/a")
    print(f"text = {button.text.strip()}")
    if button.text.strip() == "카페 글쓰기":
        return True
    return False

@sleep_after(3)
def click_posting_button():
    webdriver.click_element_xpath("/html/body/div[3]/div/div[5]/div[1]/div[1]/div[1]/div[2]/a")
    time.sleep(1)
    webdriver.switch_window()

@sleep_after(3)
def disable_comment():
    webdriver.click_element_xpath("/html/body/div[1]/div/div/section/div/div[2]/div[2]/div[2]/ul/li[1]/div/label")

@sleep_after()
def click_board_choice():
    # 테스트 용도로 추가
    seconds = 1
    while True:
        try:
            webdriver.click_element_xpath(
                "/html/body/div[1]/div/div/section/div/div[2]/div[1]/div[1]/div/div[1]/div[1]/div/div[1]/button")
            break
        except:
            time.sleep(1)
            log.append_log(f"seconds = {seconds}")
            seconds += 1
            continue
    # 이거 안되면 다음과 같은거 사용
    # //button[contains(text(), '게시판 선택']

    # 테스트를 위해서 주석처리
    # time.sleep(5)
    # webdriver.click_element_xpath("/html/body/div[1]/div/div/section/div/div[2]/div[1]/div[1]/div/div[1]/div[1]/div/div[1]/button")

@sleep_after()
def choose_board(board_name):
    return webdriver.click_element_among_classes("option_text", board_name)

@sleep_after()
def write_title(title):
    webdriver.click_element_xpath("/html/body/div[1]/div/div/section/div/div[2]/div[1]/div[1]/div/div[2]/div/textarea")
    webdriver.send_keys_action(title)

@sleep_after()
def enter_iframe():
    webdriver.switch_frame('mainFrame')

@sleep_after()
def enter_context_input():
    webdriver.click_element_xpath(
        "/html/body/div[1]/div/div/section/div/div[2]/div[1]/div[3]/div/div[1]/div/div[1]/div[2]")

def write_text(content):
    webdriver.send_keys_action(Keys.RETURN)
    webdriver.send_keys_action(content)

    # active_element = webdriver.get_active_element()
    # active_element.send_keys(Keys.RETURN)
    # clipboard.copy(content)
    # webdriver.click_element_css('dev.se-canvas-bottom')
    #
    # actions = ActionChains(webdriver.driver)
    # time.sleep(1)
    # actions.key_down(KEY).send_keys('v').key_up(KEY).perform()
    # time.sleep(2)
    #
    # active_element = webdriver.get_active_element()
    # active_element.send_keys(Keys.RETURN)
    # time.sleep(2)

def insert_enter():
    # webdriver.click_element_xpath(

    #     "/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[2]/div/div/div/div/p/span[2]")
    webdriver.send_keys_action(Keys.RETURN)

@sleep_after()
def click_hashtag():
    webdriver.click_element_xpath("/html/body/div[1]/div/div/section/div/div[2]/div[1]/div[4]/div/div")

@sleep_after()
def send_hashtag(hashtag):
    webdriver.send_keys_action(hashtag)

@sleep_after()
def click_register_button():
    wait = 1
    while True:
        try:
            webdriver.click_element_xpath("/html/body/div[1]/div/div/section/div/div[1]/div/a")
            break
        except:
            time.sleep(1)
            log.append_log(f"wait = {wait}")
            wait += 1
            continue
    # webdriver.click_element_xpath("/html/body/div[1]/div/div/section/div/div[1]/div/a")
    # time.sleep(1)




@sleep_after()
def cancel_continue():
    try:
        webdriver.click_element_xpath("/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/div[3]/button[1]")
    except:
        pass

@sleep_after()
def exit_help():
    try:
        webdriver.click_element_xpath("/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/article/div/header/button")
    except:
        pass

@sleep_after()
def enter_content_input():
    webdriver.click_element_xpath("/html/body/div[1]/div/div/section/div/div[2]/div[1]/div[3]/div/div[1]/div/div[1]/div[2]")

# def write_content(content):
#     # 1. 입력 칸 클릭
#     webdriver.click_element_xpath("/html/body/div[1]/div/div/section/div/div[2]/div[1]/div[3]/div/div[1]/div/div[1]/div[2]")
#     time.sleep(0.5)
#
#     # focused_element = webdriver.driver.switch_to.active_element
#
#     # focused_element.send_keys(Keys.RETURN)
#     # focused_element.send_keys(content)
#
#     # # 2. 진짜로 포커스가 갔는지 확인
#     # WebDriverWait(webdriver.driver, 10).until(
#     #     EC.presence_of_element_located((By.CSS_SELECTOR, 'div.se-canvas-bottom'))
#     # ).click()
#     # time.sleep(0.2)
#     #
#     # # 3. 현재 활성화된 요소에 직접 입력
