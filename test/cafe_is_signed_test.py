from web import cafe, webdriver
import time

def is_signed_cafe():
    webdriver.init_chrome()
    cafe.enter_cafe("https://cafe.naver.com/autopostingtest")
    time.sleep(60)
    print(cafe.is_signed_up())


is_signed_cafe()