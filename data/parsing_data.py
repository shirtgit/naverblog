class ParseData:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ParseData, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if ParseData._initialized:
            return

        # 한 번만 초기화할 내용
        self.keyword_data = []
        self.account_data = []
        self.blog_data = []
        self.cafe_data = []
        self.title_data = []
        self.content_data = ""

        ParseData._initialized = True  # 이제 초기화 완료

    def set_keyword_data(self, keyword_data):
        self.keyword_data = keyword_data

    def set_account_data(self, account_data):
        self.account_data = account_data

    def set_blog_data(self, blog_data):
        self.blog_data = blog_data

    def set_cafe_data(self, cafe_data):
        self.cafe_data = cafe_data

    def set_title_data(self, title_data):
        self.title_data = title_data

    def set_content_data(self, content_data):
        self.content_data = content_data

    def get_keyword_data(self):
        return self.keyword_data

    def get_account_data(self):
        return self.account_data

    def get_blog_data(self):
        return self.blog_data

    def get_cafe_data(self):
        return self.cafe_data

    def get_title_data(self):
        return self.title_data

    def get_content_data(self):
        return self.content_data
