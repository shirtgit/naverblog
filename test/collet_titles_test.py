import time

from data.const import NAVER
from web import webdriver
from ai import gemini

WAIT = 3

def collect_titles(address, company):
    webdriver.init_chrome()

    time.sleep(1)
    webdriver.enter_url(NAVER)

    webdriver.send_data_by_xpath_loop("/html/body/div[2]/div[1]/div/div[3]/div/div/form/fieldset/div/input", f"{address} {company}")

    webdriver.click_element_xpath("/html/body/div[2]/div[1]/div/div[3]/div/div/form/fieldset/button")

    webdriver.click_element_xpath("/html/body/div[3]/div[1]/div/div[2]/div[1]/div/div[1]/div/div[1]/div[1]/a")
    time.sleep(WAIT)

    titles = webdriver.get_text_from_css_selector("a.title_link")

    time.sleep(WAIT)

    gemini.init_gemini()

    response = gemini.create_title(titles, address, company)
    print(response)

collect_titles("성수동", "설비업체")