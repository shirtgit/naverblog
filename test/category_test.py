from web import webdriver, blog

def blog_category_test():
    webdriver.init_chrome()
    webdriver.enter_url("https://blog.naver.com/minsoo1101")
    blog.enter_iframe()
    blog.is_category_exist("<UNK>")

blog_category_test()