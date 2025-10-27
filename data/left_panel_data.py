from data.button_data import ButtonData

class LeftPanelData:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LeftPanelData, cls).__new__(cls)
            cls._instance._initialized = False  # 여기서 플래그 설정
        return cls._instance

    def __init__(self):
        if self._initialized:
            return  # 이미 초기화된 경우, 바로 리턴

        # 한 번만 초기화할 내용
        self.left_panel = None

        self.status_panel = None
        self.rb_panel = None
        self.current_panel = None
        self.ip_panel = None
        self.waiting_panel = None
        self.api_panel = None
        self.phone_panel = None
        self.account_panel = None
        self.phone_account_panel = None
        self.up_panel = None
        self.middle_panel = None
        self.blog_panel = None
        self.cafe_panel = None
        self.down_panel = None

        self._initialized = True  # 이제 초기화 완료

    def set_status_panel(self, status_panel):
        self.status_panel = status_panel

    def set_rb_panel(self, rb_panel):
        self.rb_panel = rb_panel

    def set_current_panel(self, current_panel):
        self.current_panel = current_panel

    def set_ip_panel(self, ip_panel):
        self.ip_panel = ip_panel

    def set_waiting_panel(self, waiting_panel):
        self.waiting_panel = waiting_panel

    def set_phone_panel(self, phone_panel):
        self.phone_panel = phone_panel

    def set_account_panel(self, account_panel):
        self.account_panel = account_panel

    def set_phone_account_panel(self, phone_account_panel):
        self.phone_account_panel = phone_account_panel

    def set_up_panel(self, left_up_panel):
        self.up_panel = left_up_panel

    def set_middle_panel(self, left_middle_panel):
        self.middle_panel = left_middle_panel

    def set_blog_panel(self, blog_panel):
        self.blog_panel = blog_panel

    def set_cafe_panel(self, cafe_panel):
        self.cafe_panel = cafe_panel

    def set_down_panel(self, down_panel):
        self.down_panel = down_panel

    def set_api_panel(self, api_panel):
        self.api_panel = api_panel