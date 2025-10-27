class MiddleSizerData:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MiddleSizerData, cls).__new__(cls)
            cls._instance._initialized = False  # 여기서 플래그 설정
        return cls._instance

    def __init__(self):
        if self._initialized:
            return  # 이미 초기화된 경우, 바로 리턴

        self.title_button_sizer = None
        self.title_list_sizer = None
        self.form_label_sizer = None
        self.form_input_sizer = None
        self.task_button_sizer = None
        self._initialized = True

    def set_title_button_sizer(self, title_button_sizer):
        self.title_button_sizer = title_button_sizer

    def set_title_list_sizer(self, title_list_sizer):
        self.title_list_sizer = title_list_sizer

    def set_form_label_sizer(self, form_label_sizer):
        self.form_label_sizer = form_label_sizer

    def set_form_input_sizer(self, form_input_sizer):
        self.form_input_sizer = form_input_sizer

    def set_task_button_sizer(self, task_button_sizer):
        self.task_button_sizer = task_button_sizer
