from web import login, webdriver
import time

account = [
    ["minsoo1101", "msLee9164@@"],
    ["sum_sory", "Dlwo8319!!"]
]

def login_test():
    webdriver.init_chrome()
    for id_val, pw_val in account:
        login.enter_naver_login()
        login.input_id_pw(id_val, pw_val)
        login.click_ip_secure()
        login.click_login_button()
        login.click_login_not_save()
        time.sleep(30)
        login.click_logout()
        time.sleep(1200)

login_test()