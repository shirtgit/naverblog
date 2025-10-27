# 싱글톤으로 제작
class ButtonData:
    _instance = None
    _initialized = False  # 여기서 플래그 설정

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ButtonData, cls).__new__(cls)
        return cls._instance
    def __init__(self):
        if ButtonData._initialized:
            return  # 이미 초기화된 경우, 바로 리턴

        # 한 번만 초기화할 내용
        self.account_button = None
        self.keyword_button = None
        self.cafe_button = None
        self.blog_button = None
        self.title_button = None
        self.execute_button = None
        self.stop_button = None
        self.toggle_button = None

        ButtonData._initialized = True  # 이제 초기화 완료

    # 버튼 세팅
    def set_account_button(self, account_button):
        self.account_button = account_button

    def set_keyword_button(self, keyword_button):
        self.keyword_button = keyword_button

    def set_cafe_button(self, cafe_button):
        self.cafe_button = cafe_button

    def set_blog_button(self, blog_button):
        self.blog_button = blog_button

    def set_title_button(self, title_button):
        self.title_button = title_button

    def set_execute_button(self, execute_button):
        self.execute_button = execute_button

    def set_stop_button(self, stop_button):
        self.stop_button = stop_button

    def set_toggle_button(self, toggle_button):
        self.toggle_button = toggle_button

    # 버튼 활성화 설정
    def account_button_Enable(self, boolean):
        self.account_button.Enable(boolean)

    def keyword_button_Enable(self, boolean):
        self.keyword_button.Enable(boolean)

    def cafe_button_Enable(self, boolean):
        self.cafe_button.Enable(boolean)

    def blog_button_Enable(self, boolean):
        self.blog_button.Enable(boolean)

    def title_button_Enable(self, boolean):
        self.title_button.Enable(boolean)

    def execute_button_Enable(self, boolean):
        self.execute_button.Enable(boolean)

    def toggle_button_Enable(self, boolean):
        self.toggle_button.Enable(boolean)

    def stop_button_Enable(self, boolean):
        self.stop_button.Enable(boolean)

    def get_toggle_value(self):
        return self.toggle_button.GetValue()

    def set_all_buttons(self, boolean):
        self.account_button.Enable(boolean)
        self.keyword_button.Enable(boolean)
        self.cafe_button.Enable(boolean)
        self.title_button.Enable(boolean)
        self.execute_button.Enable(boolean)
        self.toggle_button.Enable(boolean)