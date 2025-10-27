import wx
from .auth_functions import auth

class AuthDialog(wx.Dialog):
    def __init__(self, parent=None):
        super().__init__(parent, title="인증", size=(300, 200))
        self.auth_success = False

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.username = wx.TextCtrl(panel, style=wx.TE_LEFT)
        self.username.SetHint("아이디")
        self.password = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        self.password.SetHint("비밀번호")

        sizer.Add(wx.StaticText(panel, label="아이디:"), 0, wx.ALL, 5)
        sizer.Add(self.username, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(wx.StaticText(panel, label="비밀번호:"), 0, wx.ALL, 5)
        sizer.Add(self.password, 0, wx.EXPAND | wx.ALL, 5)

        btn = wx.Button(panel, label="확인")
        btn.Bind(wx.EVT_BUTTON, self.on_submit)
        sizer.Add(btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        panel.SetSizer(sizer)
        self.CenterOnScreen()

    def on_submit(self, event):
        username = self.username.GetValue()
        password = self.password.GetValue()
        if auth(username, password):
            self.auth_success = True
            self.Close()
        else:
            wx.MessageBox("인증 실패", "오류", wx.ICON_ERROR)