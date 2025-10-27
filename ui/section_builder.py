import wx

from data.box_data import BoxData
from data.button_data import ButtonData
from data.left_panel_data import LeftPanelData
from data.list_data import ListData
from data.middle_sizer_data import MiddleSizerData
from cache.upload_cache import show_text
import os

from data.text_data import TextData
from ui.binding import Binding

BUTTON_HEIGHT = 30
LIST_BOX_HEIGHT = 180
MIDDLE_WIDTH = 400

class SectionBuilder:
    def __init__(self):
        # 버튼 데이터 멤버 변수7
        self.button_data = ButtonData()

        # 라벨 멤버 변수 (카페/블로그)
        self.status_label = None

        # 박스 멤버 변수
        self.box_data = BoxData()

        # 버튼 멤버 변수
        self.button_data = ButtonData()

        # 리스트 멤버 변수
        self.list_data = ListData()

        # 텍스트 멤버 변수
        self.text_data = TextData()

        # 왼쪽 패널 데이터들
        self.left_panel_data = LeftPanelData()

        # 중앙 사이저 데이터들
        self.middle_sizer_data = MiddleSizerData()

        # 체크박스 (카페)
        self.cafe_checkbox = None

        # 바인딩 함수 멤버 변수
        self.binding = Binding()

    # 명시적으로 나타내기 위해 함수를 각각 선언 (중복 부분 분리 X)
    # ================================ 좌측 패널 맨 위 ================================================
    # ┌--------------------------------------------------------┐
    # |     [Box]                |         [StaticBox]         |
    # | 현재 상태 (라벨)            |    핸드폰 번호 입력              |
    # | 현재 상태 선택 (라디오 박스)   |    계정 파일 업로드 & 리스트 박스   |
    # └--------------------------------------------------------┘

    # 현재 상태 나타내는 라벨
    def current_status_label(self, panel):
        status_panel = wx.Panel(panel, wx.ID_ANY)
        status_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # "현재 상태: " -> 변하지 않는 값
        current_label =wx.StaticText(status_panel, wx.ID_ANY, "현재 상태:")
        # " 카페/블로그 " -> 변하는 값
        self.status_label = wx.StaticText(status_panel, wx.ID_ANY, "블로그")

        font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.status_label.SetFont(font)

        # 글자 색상 설정 (예: 빨간색)
        self.status_label.SetForegroundColour(wx.Colour(0, 0, 255))

        status_sizer.Add(current_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)  # wx.ALIGN_CENTER_VERTICAL로 수직 가운데 정렬
        status_sizer.Add(self.status_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        status_panel.SetSizer(status_sizer)

        self.left_panel_data.set_status_panel(status_panel)
        self.text_data.set_status_label(self.status_label)

    def platform_radio_box(self, panel):
        rb_panel = wx.Panel(panel, wx.ID_ANY)
        rb_box = wx.StaticBox(rb_panel, wx.ID_ANY)
        rb_sizer = wx.StaticBoxSizer(rb_box, wx.VERTICAL)

        rb_title = wx.StaticText(rb_panel, wx.ID_ANY, "플랫폼 선택")

        rb_labels = ['블로그', '카페', "둘 다"]
        radio_box = wx.RadioBox(rb_panel, -1,
                                size = (-1, -1),
                                choices=rb_labels,
                                majorDimension=3)

        rb_sizer.Add(rb_title, 0, wx.ALL, 5)
        rb_sizer.Add(radio_box, 0, wx.ALL , 5)
        rb_panel.SetSizer(rb_sizer)

        radio_box.Bind(wx.EVT_RADIOBOX, self.binding.on_radio_selected)

        self.left_panel_data.set_rb_panel(rb_panel)
        self.box_data.set_status_rb(radio_box)

    def waiting_section(self, panel):
        waiting_panel = wx.Panel(panel, wx.ID_ANY)
        waiting_box = wx.StaticBox(waiting_panel)
        waiting_sizer = wx.StaticBoxSizer(waiting_box, wx.VERTICAL)

        waiting_label = wx.StaticText(waiting_panel, wx.ID_ANY, "대기시간 설정")
        waiting_sizer.Add(waiting_label, 0, wx.ALL | wx.ALIGN_LEFT, 15)

        grid_box = wx.StaticBox(waiting_panel)
        grid_box_sizer = wx.StaticBoxSizer(grid_box, wx.VERTICAL)

        grid_panel = wx.Panel(waiting_panel, wx.ID_ANY)
        grid_sizer = wx.FlexGridSizer(2, 2, 10, 10)  # (행, 열, 수직 간격, 수평 간격)
        grid_sizer.AddGrowableCol(1, 1)  # 두 번째 열 (input 쪽)을 확장 가능하게 설정

        min_label = wx.StaticText(grid_panel, wx.ID_ANY, "최소 (분)")
        min_input = wx.TextCtrl(grid_panel, wx.ID_ANY, size=wx.Size(100, 20))
        max_label = wx.StaticText(grid_panel, wx.ID_ANY, "최대 (분)")
        max_input = wx.TextCtrl(grid_panel, wx.ID_ANY, size=wx.Size(100, 20))

        grid_sizer.AddMany([
            (min_label, 0, wx.ALIGN_CENTER_VERTICAL),
            (min_input, 0, wx.EXPAND),
            (max_label, 0, wx.ALIGN_CENTER_VERTICAL),
            (max_input, 0, wx.EXPAND),
        ])

        grid_panel.SetSizer(grid_sizer)
        grid_box_sizer.Add(grid_panel, 1, wx.ALL | wx.EXPAND, 10)
        waiting_sizer.Add(grid_box_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_LEFT, 10)

        self.ip_section(waiting_panel)
        waiting_sizer.Add(self.left_panel_data.ip_panel, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 10)

        waiting_panel.SetSizer(waiting_sizer)

        self.left_panel_data.set_waiting_panel(waiting_panel)
        self.text_data.set_waiting_min(min_input)
        self.text_data.set_waiting_max(max_input)

    # 좌측 위 좌측: 라벨 + 라디오박스 패널
    def current_section(self, panel):
        current_panel = wx.Panel(panel, wx.ID_ANY)
        current_sizer = wx.BoxSizer(wx.VERTICAL)

        self.current_status_label(current_panel)
        self.platform_radio_box(current_panel)
        self.waiting_section(current_panel)

        # # ✅ 이미지 삽입 부분
        # # 이미지 경로: 루트 디렉토리에 있는 logo.png
        # root_path = os.path.dirname(os.path.dirname(__file__))
        # image_path = os.path.join(root_path, "logo.png")
        #
        # image = wx.Image(image_path, wx.BITMAP_TYPE_PNG).Scale(160, 160)
        # bitmap = wx.StaticBitmap(current_panel, wx.ID_ANY, wx.BitmapBundle(image))
        # # 이미지 삽입 끝

        current_sizer.Add(self.left_panel_data.status_panel, 0, wx.ALL | wx.ALIGN_LEFT, 5)
        current_sizer.Add(self.left_panel_data.rb_panel, 0, wx.BOTTOM | wx.ALIGN_LEFT, 20)
        # current_sizer.Add(bitmap, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)
        current_sizer.Add(self.left_panel_data.waiting_panel, wx.ALIGN_LEFT)
        current_panel.SetSizer(current_sizer)

        self.left_panel_data.set_current_panel(current_panel)

    # 유동IP 토글 버튼
    def ip_section(self, panel):
        ip_panel = wx.Panel(panel, wx.ID_ANY)
        ip_sizer = wx.BoxSizer(wx.VERTICAL)

        ip_toggle = wx.ToggleButton(ip_panel, wx.ID_ANY, "유동 IP 사용여부")
        ip_toggle.SetValue(True)
        # ip_toggle.Bind(wx.EVT_TOGGLEBUTTON, on_toggled)

        ip_sizer.Add(ip_toggle, 0, wx.TOP | wx.BOTTOM, 8)
        ip_panel.SetSizer(ip_sizer)

        self.left_panel_data.set_ip_panel(ip_panel)
        self.button_data.set_toggle_button(ip_toggle)

    # API KEY 입력
    def api_section(self, panel):
        api_panel = wx.Panel(panel, wx.ID_ANY)
        api_sizer = wx.BoxSizer(wx.VERTICAL)

        api_input_label = wx.StaticText(api_panel, wx.ID_ANY, "API KEY", size=(80, 20))
        api_input = wx.TextCtrl(api_panel, wx.ID_ANY, size=(150, 20))

        api_input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        api_input_sizer.Add(api_input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)  # wx.ALIGN_CENTER_VERTICAL로 수직 가운데 정렬
        api_input_sizer.Add(api_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        api_sizer.Add(api_input_sizer, 0)
        api_panel.SetSizer(api_sizer)

        self.left_panel_data.set_api_panel(api_panel)
        self.text_data.set_api_number(api_input)

    # 핸드폰 번호 입력
    def phone_section(self, panel):
        phone_panel = wx.Panel(panel, wx.ID_ANY)
        phone_sizer = wx.BoxSizer(wx.VERTICAL)

        phone_input_label = wx.StaticText(phone_panel, wx.ID_ANY, "핸드폰 번호", size=(80, 20))
        phone_input = wx.TextCtrl(phone_panel, wx.ID_ANY, size=(150, 20))

        phone_input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        phone_input_sizer.Add(phone_input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)  # wx.ALIGN_CENTER_VERTICAL로 수직 가운데 정렬
        phone_input_sizer.Add(phone_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        phone_sizer.Add(phone_input_sizer, 0)
        phone_panel.SetSizer(phone_sizer)

        self.left_panel_data.set_phone_panel(phone_panel)
        self.text_data.set_phone_number(phone_input)

    # 계정 박스
    def account_section(self, panel):
        account_panel = wx.Panel(panel, wx.ID_ANY)
        account_sizer = wx.BoxSizer(wx.VERTICAL)

        # 업체 버튼 설정
        account_button = wx.Button(account_panel, wx.ID_ANY, "계정 업로드", size=wx.Size(250, BUTTON_HEIGHT))
        account_button.Enable(True)

        account_list = wx.ListCtrl(account_panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN, size=wx.Size(250, LIST_BOX_HEIGHT))
        account_list.InsertColumn(0, "계정명", width=120)
        account_list.InsertColumn(1, "비밀번호")
        account_list.SetColumnWidth(1, 0)
        account_list.InsertColumn(2, "장소", width=120)

        account_sizer.Add(account_button, 0, wx.ALL, border=3)
        account_sizer.Add(account_list, 0, wx.BOTTOM, border=10)
        account_panel.SetSizer(account_sizer)

        account_button.Bind(
            wx.EVT_BUTTON,
            lambda event: self.binding.on_cafe_keyword_button_clicked(event, account_panel)
        )

        self.left_panel_data.set_account_panel(account_panel)
        self.button_data.set_account_button(account_button)
        self.list_data.set_account_list(account_list)

    # 좌측 위 우측: 핸드폰 + 계정
    def phone_account_panel(self, panel):
        phone_account_panel = wx.Panel(panel, wx.ID_ANY)
        phone_account_box = wx.StaticBox(phone_account_panel)
        phone_account_sizer = wx.StaticBoxSizer(phone_account_box, wx.VERTICAL)

        self.api_section(phone_account_panel)
        self.phone_section(phone_account_panel)
        self.account_section(phone_account_panel)
        # self.ip_section(phone_account_panel)
        #
        # phone_account_sizer.Add(self.left_panel_data.ip_panel, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        phone_account_sizer.Add(self.left_panel_data.api_panel, 0, wx.ALL | wx.ALIGN_LEFT, 5)
        phone_account_sizer.Add(self.left_panel_data.phone_panel, 0, wx.ALL | wx.ALIGN_LEFT, 5)
        phone_account_sizer.Add(self.left_panel_data.account_panel, 0, wx.ALL | wx.ALIGN_LEFT, 5)
        phone_account_panel.SetSizer(phone_account_sizer)

        self.left_panel_data.set_phone_account_panel(phone_account_panel)

    def up_section(self, panel):
        up_panel = wx.Panel(panel, wx.ID_ANY)
        up_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.current_section(up_panel)
        self.phone_account_panel(up_panel)

        up_sizer.Add(self.left_panel_data.current_panel, 0, wx.RIGHT, 20)
        up_sizer.Add(self.left_panel_data.phone_account_panel, 0, wx.ALL, 5)
        up_panel.SetSizer(up_sizer)

        self.left_panel_data.set_up_panel(up_panel)

    # 키워드 박스
    def middle_section(self, panel):
        keyword_panel = wx.Panel(panel, wx.ID_ANY)
        keyword_box = wx.StaticBox(keyword_panel)
        keyword_sizer = wx.StaticBoxSizer(keyword_box, wx.VERTICAL)

        # 업체 버튼 설정
        keyword_button = wx.Button(keyword_panel, wx.ID_ANY, "키워드 업로드", size=wx.Size(250, BUTTON_HEIGHT))
        keyword_button.Enable(True)

        keyword_list = wx.ListCtrl(keyword_panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN, size=wx.Size(550, LIST_BOX_HEIGHT))
        keyword_list.InsertColumn(0, "주소", width=120)
        keyword_list.InsertColumn(1, "업체", width=120)
        keyword_list.InsertColumn(2, "파일 경로", width=120)
        keyword_list.InsertColumn(3, "해시태그", width=120)

        keyword_button.Bind(
            wx.EVT_BUTTON,
            lambda event: self.binding.on_cafe_keyword_button_clicked(event, keyword_panel)
        )

        keyword_sizer.Add(keyword_button, 0, wx.ALL, border=3)
        keyword_sizer.Add(keyword_list, 0, wx.ALL, border=3)
        keyword_panel.SetSizer(keyword_sizer)

        self.left_panel_data.set_middle_panel(keyword_panel)
        self.button_data.set_keyword_button(keyword_button)
        self.list_data.set_keyword_list(keyword_list)

    # 블로그 박스
    def blog_section(self, panel):
        blog_panel = wx.Panel(panel, wx.ID_ANY)
        blog_sizer = wx.BoxSizer(wx.VERTICAL)
        # blog_sizer.AddSpacer()

        # 라벨 설정
        blog_label = wx.StaticText(blog_panel, wx.ID_ANY, "* 계정 파일 업로드 시 자동으로 업로드 됩니다.")
        # blog_sizer.Add(blog_label, 0, wx.ALL | wx.ALIGN_LEFT, 15)
        blog_sizer.Add(blog_label, 0, wx.ALL | wx.ALIGN_LEFT, 15)
        # blog_button = wx.Button(blog_panel, wx.ID_ANY, "블로그 업로드", size=wx.Size(250, 50))
        # blog_button.Enable(True)

        blog_list = wx.ListCtrl(blog_panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN, size=wx.Size(250, LIST_BOX_HEIGHT))
        blog_list.InsertColumn(0, "계정", width=120)
        blog_list.InsertColumn(1, "게시판 이름", width=130)

        # blog_button.Bind(
        #     wx.EVT_BUTTON,
        #     lambda event: self.binding.on_cafe_keyword_button_clicked(event, blog_panel)
        # )
        #
        # blog_sizer.Add(blog_button, 0, wx.ALL, 3)
        blog_sizer.Add(blog_list, 0, wx.LEFT, 15)
        blog_panel.SetSizer(blog_sizer)

        self.left_panel_data.set_blog_panel(blog_panel)
        self.list_data.set_blog_list(blog_list)

    # 카페 박스
    def cafe_section(self, panel):
        cafe_panel = wx.Panel(panel, wx.ID_ANY)
        cafe_sizer = wx.BoxSizer(wx.VERTICAL)

        # 업체 버튼 설정
        cafe_button = wx.Button(cafe_panel, wx.ID_ANY, "카페 업로드", size=wx.Size(250, BUTTON_HEIGHT))
        cafe_button.Enable(False)

        cafe_list = wx.ListCtrl(cafe_panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN, size=wx.Size(250, LIST_BOX_HEIGHT))
        cafe_list.InsertColumn(0, "카페 주소", width=120)
        cafe_list.InsertColumn(1, "게시판 이름", width=130)
        cafe_list.Enable(False)

        cafe_button.Bind(
            wx.EVT_BUTTON,
            lambda event: self.binding.on_cafe_keyword_button_clicked(event, cafe_panel)
        )

        cafe_checkbox = wx.CheckBox(cafe_panel, wx.ID_ANY, "댓글 기능 허용")
        cafe_checkbox.Enable(False)

        cafe_sizer.Add(cafe_button, 0, wx.ALL, 3)
        cafe_sizer.Add(cafe_list, 0, wx.ALL, 3)
        cafe_sizer.Add(cafe_checkbox, 0, wx.TOP, 5)
        cafe_panel.SetSizer(cafe_sizer)

        self.left_panel_data.set_cafe_panel(cafe_panel)
        self.button_data.set_cafe_button(cafe_button)
        self.box_data.set_comment_cb(cafe_checkbox)
        self.list_data.set_cafe_list(cafe_list)

    def down_section(self, panel):
        down_panel = wx.Panel(panel, wx.ID_ANY)
        down_box = wx.StaticBox(down_panel)
        down_sizer = wx.StaticBoxSizer(down_box, wx.HORIZONTAL)

        self.blog_section(down_panel)
        self.cafe_section(down_panel)

        down_sizer.Add(self.left_panel_data.blog_panel, 0, wx.RIGHT | wx.ALIGN_TOP, 10)
        down_sizer.Add(self.left_panel_data.cafe_panel, 0, wx.ALL | wx.ALIGN_TOP, 5)
        down_panel.SetSizer(down_sizer)

        self.left_panel_data.set_down_panel(down_panel)


    # ================================ 중앙 패널 ================================================

    # 키워드 박스
    def title_section(self, panel):
        # panel = wx.Panel(panel, wx.ID_ANY)
        # title_box = wx.StaticBox(panel)
        # title_sizer = wx.StaticBoxSizer(title_box, wx.VERTICAL)

        # 업체 버튼 설정
        title_button = wx.Button(panel, wx.ID_ANY, "제목 업로드", size=wx.Size(MIDDLE_WIDTH, BUTTON_HEIGHT))
        title_button.Enable(True)
        title_button.Bind(
            wx.EVT_BUTTON,
            lambda event: self.binding.on_cafe_keyword_button_clicked(event, panel)
        )
        title_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_button_sizer.Add(title_button, 0, wx.TOP | wx.LEFT | wx.RIGHT, 3)


        title_list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN,
                                   size=wx.Size(MIDDLE_WIDTH, LIST_BOX_HEIGHT))
        title_list.InsertColumn(0, "제목", width=380)
        title_list_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_list_sizer.Add(title_list, 0, wx.TOP | wx.LEFT | wx.RIGHT, 3)

        self.middle_sizer_data.set_title_button_sizer(title_button_sizer)
        self.middle_sizer_data.set_title_list_sizer(title_list_sizer)
        self.list_data.set_title_list(title_list)
        self.button_data.set_title_button(title_button)

    # 안내글 표시
    def inform_section(self, panel):
#         inform = """
# [폼 형식 지정 안내글]
#
#
# [제목]을 기준으로 제목과 글이 나뉘어집니다.
#
# 글에서는 [본문]을 기준으로 서론, 본문, 결론으로 나뉘어집니다.
#
# 본문은 AI로 작성한 1500자 내외의 글이며,
# 고객님께서 keyword.csv를 통해 업로드한 이미지 중 랜덤으로 5개가 같이 들어갑니다.
#
# keyword.csv에서 받아온 정보 중에서
# %주소% 문자열은 주소 열의 데이터를, %업체% 문자열은 업체 열의 데이터로 치환됩니다.
#
# %썸네일% 문자열은 썸네일 사진으로, %영상% 문자열은 썸네일 사진을 바탕으로 제작된 영상으로 치환됩니다.
#
# 문자열 치환 예시)
#
# %주소%이고, %업체%입니다.
# %썸네일%
# [본문]
# %영상%
# 감사합니다.
# =======================
# 성수동이고, 설비업체입니다.
# '썸네일 사진'
# 'AI로 작성한 본문'
# '썸네일 사진 기반 영상'
# 감사합니다.
#
#
#         """

        inform = """
[폼 형식 지정 안내글]

[본문]을 기준으로 서론, 본문, 결론으로 나뉘어집니다.

본문은 AI로 작성한 1500자 내외의 글이며,
고객님께서 keyword.csv를 통해 업로드한 이미지 중 랜덤으로 5개가 같이 들어갑니다.

keyword.csv에서 받아온 정보 중에서
%주소% 문자열은 주소 열의 데이터를, %업체% 문자열은 업체 열의 데이터로 치환됩니다.

%썸네일% 문자열은 썸네일 사진으로, %영상% 문자열은 썸네일 사진을 바탕으로 제작된 영상으로 치환됩니다.
        """
        form_label = wx.StaticText(panel, wx.ID_ANY, inform, size=wx.Size(MIDDLE_WIDTH, 300))
        form_label_sizer = wx.BoxSizer(wx.HORIZONTAL)
        form_label_sizer.Add(form_label, 0, wx.ALL, 5)

        self.middle_sizer_data.set_form_label_sizer(form_label_sizer)

    # 텍스트 형식 입력
    def content_input_section(self, panel):
        form_input = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=wx.Size(MIDDLE_WIDTH, 310))
        # 안녕하세요. 헤더입니다. 여기서 등록하는 미디어는 테스트를 위한 임의의 사진 및 영상입니다.
        #
        # [사진]
        #
        # 이곳부터는 AI가 작성할 글이 들어갈 본문입니다.
        #
        # [사진]
        #
        # 이 밑에는 영상이 들어갑니다.
        #
        # [영상]
        #
        # 맺음말입니다.
        form_input_sizer = wx.BoxSizer(wx.VERTICAL)
        form_input_sizer.Add(form_input, 0, wx.TOP | wx.LEFT | wx.RIGHT, 3)

        self.text_data.set_content_input(form_input)
        self.middle_sizer_data.set_form_input_sizer(form_input_sizer)

    # 작업 수행 버튼
    def execute_section(self, panel):
        task_button = wx.Button(panel, wx.ID_ANY, "작업 수행", size=wx.Size(MIDDLE_WIDTH, BUTTON_HEIGHT))
        task_button.Enable(True)

        task_button.Bind(wx.EVT_BUTTON,
                         lambda event: self.binding.on_execute_button_clicked(event, self.text_data.get_content_input())
        )

        task_button_sizer = wx.BoxSizer(wx.VERTICAL)
        task_button_sizer.Add(task_button, 0, wx.ALL, 5)

        self.middle_sizer_data.set_task_button_sizer(task_button_sizer)
        self.button_data.set_execute_button(task_button)
