import time, clipboard

from selenium.webdriver import Keys

from ui import log
from utils.decorators import sleep_after
from web import webdriver
from data.const import *
from selenium.webdriver.common.by import By
import platform

is_secured = False

COMCON = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL

@sleep_after()
def enter_naver_login():
    webdriver.driver.get(NAVER_LOGIN)

@sleep_after()
def click_ID_phone():
    webdriver.click_element_xpath("/html/body/div[1]/div[2]/div/div[1]/ul/li[1]/a")

# @sleep_after()
# def enter_login_window():
#     webdriver.driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[2]/div[2]/div/div/div[1]/div/a").click()

@sleep_after()
def input_id_pw(id_val, pw_val):
    actions = webdriver.get_actions()

    time.sleep(3)

    clipboard.copy(id_val)
    id_input = webdriver.get_element_xpath("/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[1]/div/div[1]/input")
    id_input.click()
    actions.key_down(COMCON).send_keys('v').key_up(COMCON).perform()

    time.sleep(3)

    clipboard.copy(pw_val)
    pw_input = webdriver.get_element_xpath("/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[1]/div/div[2]/input")
    pw_input.click()
    actions.key_down(COMCON).send_keys('v').key_up(COMCON).perform()

    # # 천천히 입력하여 캡챠 우회 (되는지 확인 필요) -> 안됨
    # id_input = webdriver.get_element_xpath("/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[1]/div/div[1]/input")
    # pw_input = webdriver.get_element_xpath("/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[1]/div/div[2]/input")
    #
    # for ch in id_val:
    #     id_input.send_keys(ch)
    #     time.sleep(0.2)
    #
    # for ch in pw_val:
    #     pw_input.send_keys(ch)
    #     time.sleep(0.2)

@sleep_after()
def check_login_error():
    for i in range(5):
        try:
            webdriver.get_element_xpath("/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[10]/div")
            return False
        except:
            time.sleep(5)
            continue
    return True

def check_login_done():
    while True:
        try:
            webdriver.get_element_xpath("/html/body/div[1]/div[2]/div/form/fieldset/span[2]/a")
            return True
        except:
            time.sleep(5)
            continue
    return False

@sleep_after()
def retry_login():
    log.append_log("[ERROR] 아이디 또는 비밀번호가 잘못되었습니다.\n로그인을 다시 시도해 주세요.")

def input_id_pw_capcha_test(id_val, pw_val):
    # 천천히 입력하여 캡챠 우회 (되는지 확인 필요) -> 안됨
    id_input = webdriver.get_element_xpath("/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[1]/div/div[1]/input")
    pw_input = webdriver.get_element_xpath("/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[1]/div/div[2]/input")

    for ch in id_val:
        id_input.send_keys(ch)
        time.sleep(0.2)

    for ch in pw_val:
        pw_input.send_keys(ch)
        time.sleep(0.2)

@sleep_after()
def click_ip_secure():
    global is_secured
    if not is_secured:
        webdriver.click_element_xpath("/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[2]/div[2]/span")
        is_secured = True

@sleep_after()
def click_login_button():
    # driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[11]/button").click()
    webdriver.driver.find_element(By.ID, "log.login").click()

@sleep_after()
def check_capcha_appear():
    log.append_log("캡챠가 떴는지 확인합니다.")
    for i in range(5):
        try:
            webdriver.get_element_class("captcha_input")
            webdriver.get_element_xpath("/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[3]/div[1]/div[2]/div[1]")
            return True
        except:
            time.sleep(1)
            # log.append_log("캡챠를 찾을 수 없습니다.")
            continue
    return False

@sleep_after()
def check_capcha_done():
    try:
        webdriver.get_element_xpath("/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[3]/div[1]/div[2]/div[1]")
        return False
    except:
        return True

@sleep_after()
def click_login_not_save():
    try:
        webdriver.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/form/fieldset/span[2]/a").click()
    except:
        pass

@sleep_after()
def click_logout():
    webdriver.click_element_xpath("/html/body/div[2]/div[2]/div[2]/div[2]/div/div/div[1]/div[1]/div/button")

def switch_to_popup():
    webdriver.switch_window()

def switch_to_prev_window():
    webdriver.switch_window()