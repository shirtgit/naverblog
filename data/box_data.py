class BoxData:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BoxData, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if BoxData._initialized:
            return  # 이미 초기화된 경우, 바로 리턴

        self.status_rb = None
        self.comment_cb = None
        BoxData._initialized = True

    # 박스 세팅
    def set_status_rb(self, status_rb):
        self.status_rb = status_rb

    def set_comment_cb(self, comment_cb):
        self.comment_cb = comment_cb

    # 박스 활성화 설정
    def comment_cb_Enable(self, boolean):
        self.comment_cb.Enable(boolean)

    # 체크박스 bool 값 가져오기
    def get_cb_value(self):
        return self.comment_cb.GetValue()

    # 라디오박스 값 가져오기
    def get_rb_value(self):
        return self.status_rb.GetSelection()

    def set_rb_index(self, index):
        self.status_rb.SetSelection(index)

    def set_cb_value(self, value):
        self.comment_cb.SetValue(value)
