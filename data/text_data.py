class TextData:
    _instance = None
    _initialized = False  # 여기서 플래그 설정

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TextData, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if TextData._initialized:
            return  # 이미 초기화된 경우, 바로 리턴

        self.status_label = None
        self.phone_number = None
        self.waiting_max = None
        self.waiting_min = None
        self.api_number = None
        self.content_input = None

        self.title = None
        self.body = None

        TextData._initialized = True

    def set_status_label(self, status_label):
        self.status_label = status_label

    def set_phone_number(self, phone_number):
        self.phone_number = phone_number

    def set_waiting_max(self, waiting_max):
        self.waiting_max = waiting_max

    def set_waiting_min(self, waiting_min):
        self.waiting_min = waiting_min

    def set_api_number(self, api_number):
        self.api_number = api_number

    def set_content_input(self, content_input):
        self.content_input = content_input

    # 데이터로 변환
    def get_content_input(self):
        return self.content_input.GetValue()

    def get_phone_number(self):
        return self.phone_number.GetValue()

    def get_waiting_max(self):
        return int(self.waiting_max.GetValue()) * 60

    def get_waiting_min(self):
        return int(self.waiting_min.GetValue()) * 60

    def get_api_number(self):
        return self.api_number.GetValue()

    # 수정
    # def divide_title_body(self):
    #     self.title, self.body = self.content_input.GetValue().split("[제목]")

    def get_title(self):
        return self.title.strip()

    def get_body(self):
        return self.body.strip()

    def replace_title(self, address, company):
        self.title = self.title.replace("%주소%", address)
        self.title = self.title.replace("%업체%", company)