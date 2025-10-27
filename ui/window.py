import wx
from ui.panel_builder import PanelBuilder
from cache import upload_cache
from web import webdriver

MARGIN = 10


def set_caches():
    upload_cache.show_text()
    upload_cache.show_lists()


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, wx.ID_ANY, "Naver Posting")

        self.Bind(wx.EVT_CLOSE, self.on_close)


        self.separator_left = None
        self.separator_right = None

        self.panel = wx.Panel(self, wx.ID_ANY)
        self.ui = PanelBuilder(self.panel)

        # 좌측 패널
        self.ui.add_left()
        # 중앙 패널
        self.ui.add_middle()
        # 우측 패널
        self.ui.add_right()

        self.panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.frame_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.init_ui_separator()
        self.set_layout()
        self.set_position_and_show()

        set_caches()


    def init_ui_separator(self):
        # 구분선 1
        self.separator_left = wx.Panel(self.panel, size=(2, -1))
        self.separator_left.SetBackgroundColour(wx.Colour(200, 200, 200))

        # 구분선 2
        self.separator_right = wx.Panel(self.panel, size=(2, -1))
        self.separator_right.SetBackgroundColour(wx.Colour(200, 200, 200))

    def set_layout(self):

        self.panel_sizer.Add(self.ui.left_panel, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, MARGIN)
        self.panel_sizer.Add(self.separator_left, 0, wx.EXPAND | wx.ALL, 10)
        self.panel_sizer.Add(self.ui.middle_panel, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, MARGIN)
        self.panel_sizer.Add(self.separator_right, 0, wx.EXPAND | wx.ALL, 10)
        self.panel_sizer.Add(self.ui.right_panel, 0, wx.EXPAND | wx.RIGHT | wx.TOP | wx.BOTTOM, MARGIN)

        self.panel.SetSizer(self.panel_sizer)
        self.frame_sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizerAndFit(self.frame_sizer)

    def set_position_and_show(self):
        display_width, display_height = wx.GetDisplaySize()
        frame_width, frame_height = self.GetSize()

        x = (display_width - frame_width) // 2
        y = 30  # 위에서 약간 띄우기

        self.SetPosition(wx.Point(x, y))
        self.Show()

    def on_close(self, event):
        # 리소스 정리 또는 확인 대화창 등을 여기에 넣을 수 있음
        self.Destroy()  # 프레임 제거
        webdriver.driver.quit()
        wx.GetApp().ExitMainLoop()  # 메인 루프 종료 -> 프로세스 종료



