import wx
import wx.richtext as rt
from selenium.webdriver.support.expected_conditions import none_of

from ui import section_builder
from ui import log
from ui.section_builder import SectionBuilder

# 여기서는 left, middle, right 큰 축을 설정
class PanelBuilder:
    def __init__(self, parent_panel):
        self.parent_panel = parent_panel

        self.section_builder = SectionBuilder()

        self.left_panel = None
        self.middle_panel = None
        self.right_panel = None

        # # 버튼 멤버 변수
        # self.keyword_button = None
        # self.account_button = None
        # self.web_button = None
        # self.execute_button = None
        #
        # # 리스트 멤버 변수
        # self.keyword_list = None
        # self.account_list = None
        # self.web_list = None

    def add_left(self):
        self.left_panel = wx.Panel(self.parent_panel, wx.ID_ANY)
        box = wx.StaticBox(self.left_panel)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        self.section_builder.up_section(self.left_panel)
        self.section_builder.middle_section(self.left_panel)
        self.section_builder.down_section(self.left_panel)

        sizer.Add(self.section_builder.left_panel_data.up_panel, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.section_builder.left_panel_data.middle_panel, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.section_builder.left_panel_data.down_panel, 0, wx.EXPAND | wx.ALL, 5)
        self.left_panel.SetSizer(sizer)

    def add_middle(self):
        self.middle_panel = wx.Panel(self.parent_panel, wx.ID_ANY)
        box = wx.StaticBox(self.middle_panel)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        self.section_builder.title_section(self.middle_panel)
        self.section_builder.inform_section(self.middle_panel)
        self.section_builder.content_input_section(self.middle_panel)
        self.section_builder.execute_section(self.middle_panel)

        sizer.Add(self.section_builder.middle_sizer_data.title_button_sizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND,
                  3)
        sizer.Add(self.section_builder.middle_sizer_data.title_list_sizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND,
                  3)
        sizer.Add(self.section_builder.middle_sizer_data.form_label_sizer, 1, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 3)
        sizer.Add(self.section_builder.middle_sizer_data.form_input_sizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 3)
        sizer.Add(self.section_builder.middle_sizer_data.task_button_sizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 3)

        self.middle_panel.SetSizer(sizer)

    def add_right(self):
        self.right_panel = wx.Panel(self.parent_panel, wx.ID_ANY)
        box = wx.StaticBox(self.right_panel)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        log_label = wx.StaticText(self.right_panel, wx.ID_ANY, "로그 화면", size=(80, 20))

        log_label_sizer = wx.BoxSizer(wx.HORIZONTAL)
        log_label_sizer.Add(log_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        log_text_widget = rt.RichTextCtrl(
            self.right_panel,
            style=wx.TE_MULTILINE | wx.BORDER_THEME | wx.TE_READONLY,
            size=wx.Size(400, 500)
        )
        log.set_log_widget(log_text_widget)

        sizer.Add(log_label_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(log_text_widget, 1, wx.EXPAND | wx.ALL, 5)

        self.right_panel.SetSizer(sizer)
