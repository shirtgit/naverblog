import clipboard
import pyperclip
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from ui import log
from utils.decorators import sleep_after
from web import webdriver
import time
import platform

# 윈도우일 경우 다르게 (혹은 운영체제 감지해서 다르게 작동하게)
KEY = Keys.COMMAND if platform.system() == 'Darwin' else Keys.CONTROL

@sleep_after()
def enter_blog(is_initial = False):
    time.sleep(3)
    if is_initial:
        webdriver.click_element_xpath("/html/body/div[2]/div[2]/div[2]/div[2]/div/div/div[1]/div[2]/div/div/ul/li[3]/a")
        # webdriver.click_element_xpath("/html/body/div[2]/div[2]/div[2]/div[2]/div/div/div[1]/div[2]/div/div/ul/li[3]/a")
        time.sleep(3)
    webdriver.click_element_xpath("/html/body/div[2]/div[2]/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div[1]/a[2]")
    time.sleep(3)
    webdriver.switch_window()


@sleep_after(3)
def enter_posting_window():
    # webdriver.click_element_xpath("/html/body/div[6]/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[1]/div/div[2]/div[2]/a[1]")
    # webdriver.click_element_xpath("/html/body/div[7]/div[1]/div[2]/div[2]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/div[2]/a[1]")
    webdriver.click_element_link_text("글쓰기")
    time.sleep(3)
    # print(time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()))
    # webdriver.enter_url(f"{BLOG}/?Redirect=Write&")

@sleep_after()
def is_category_exist(category_name):
    webdriver.find_category(category_name)

@sleep_after()
def enter_iframe():
    webdriver.switch_frame('mainFrame')

# 수정
@sleep_after()
def cancel_continue():
    try:
        webdriver.click_element_xpath_error("/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/div[3]/button[1]")
    except:
        pass


@sleep_after()
def exit_help():
    try:
        time.sleep(3)
        webdriver.click_element_xpath_error("/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/article/div/header/button")
    except:
        pass

@sleep_after(3)
def write_title(title):
    webdriver.click_element_xpath("/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[1]/div[1]/div/div/p/span[2]")
    webdriver.send_keys_action(title)
    # title_input = webdriver.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[1]/div[1]/div/div/p/span[2]")
    # title_input.click()
    # actions = ActionChains(webdriver.driver)
    # actions.send_keys(title).perform()

@sleep_after()
def enter_context_input():
    webdriver.click_element_xpath(
        "/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[2]/div/div/div/div/p/span[2]")

def write_text(content):
    # webdriver.send_keys_action(Keys.RETURN)
    # webdriver.send_keys_action(content)
    actions = ActionChains(webdriver.driver)
    pyperclip.copy(content)
    # 테스트 용도로 주석처리
    actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    # actions.key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND).perform()

def insert_enter():
    # webdriver.click_element_xpath(

    #     "/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[2]/div/div/div/div/p/span[2]")
    webdriver.send_keys_action(Keys.RETURN)

@sleep_after()
def click_post_button():
    time.sleep(3)
    webdriver.click_element_xpath("/html/body/div[1]/div/div[1]/div/div[3]/div[2]/button")
    # webdriver.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[3]/div[2]/button").click()

@sleep_after()
def click_category_listbox():
    webdriver.click_element_xpath("/html/body/div[1]/div/div[1]/div/div[3]/div[2]/div/div/div/div[1]/div/div/button")

@sleep_after()
def choose_category(category_name):
    return webdriver.click_element_among_classes("text__sraQE", category_name)

@sleep_after()
def click_hashtag():
    # webdriver.click_element_xpath("/html/body/div[1]/div/div[1]/div/div[3]/div[2]/div/div/div/div[6]/div[2]/div/div/div/input")
    webdriver.click_element_xpath("/html/body/div[1]/div/div[1]/div/div[3]/div[2]/div/div/div/div[6]/div[2]/div/div/div")

@sleep_after()
def send_hashtag(hashtag):
    webdriver.send_keys_action(hashtag)

@sleep_after()
def complete_posting():
    webdriver.click_element_xpath_error("/html/body/div[1]/div/div[1]/div/div[3]/div[2]/div/div/div/div[8]/div/button")
    # webdriver.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[3]/div[2]/div/div/div/div[8]/div/button").click()

@sleep_after()
def exit_iframe():
    webdriver.switch_frame_to_default()

@sleep_after()
def exit_tab():
    webdriver.exit_tab()