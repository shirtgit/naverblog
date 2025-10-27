def get_list_data(list_name):
    row_count = list_name.GetItemCount()
    col_count = list_name.GetColumnCount()

    data = []

    for row in range(row_count):
        row_data = []
        for col in range(col_count):
            item_text = list_name.GetItemText(row, col)
            row_data.append(item_text)
        data.append(row_data)

    return data


class ListData:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ListData, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if ListData._initialized:
            return  # 이미 초기화된 경우, 바로 리턴

        self.account_list = None
        self.keyword_list = None
        self.blog_list = None
        self.cafe_list = None
        self.title_list = None

        ListData._initialized = True

    # 리스트 세팅
    def set_account_list(self, account_list):
        self.account_list = account_list

    def set_keyword_list(self, keyword_list):
        self.keyword_list = keyword_list

    def set_blog_list(self, blog_list):
        self.blog_list = blog_list

    def set_cafe_list(self, cafe_list):
        self.cafe_list = cafe_list

    def set_title_list(self, title_list):
        self.title_list = title_list

    # 리스트 활성화 설정
    def account_list_Enable(self, boolean):
        self.account_list.Enable(boolean)

    def keyword_list_Enable(self, boolean):
        self.keyword_list.Enable(boolean)

    def blog_list_Enable(self, boolean):
        self.blog_list.Enable(boolean)

    def cafe_list_Enable(self, boolean):
        self.cafe_list.Enable(boolean)

    def title_list_Enable(self, boolean):
        self.title_list.Enable(boolean)

    # 리스트 값 불러오기
