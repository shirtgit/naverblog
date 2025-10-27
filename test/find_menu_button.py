from web import webdriver
import time
webdriver.init_chrome()
webdriver.enter_url("https://www.naver.com")
webdriver.send_data_by_xpath_loop("/html/body/div[2]/div[1]/div/div[3]/div/div/form/fieldset/div/input", "광진구 설비업체")
webdriver.click_element_xpath("/html/body/div[2]/div[1]/div/div[3]/div/div/form/fieldset/button")

time.sleep(1)

webdriver.push_search_blog_cafe_button("블로그")