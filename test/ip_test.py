# 윈도우 git bash에서 실행할 목적으로 추가
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import wx
from ip_trans import ip_trans, ip_trans1, ip_trans_execute
import time

# 앱 초기화
app = wx.App(False)
frame = wx.Frame(None, title="IP 우회 테스트", size=(300, 200))
panel = wx.Panel(frame)

# 버튼 생성
top_button = wx.Button(panel, label="현재 IP 우회 테스트")

def ip_test(event):
    while True:
        ip_trans2.trans_ip()
        time.sleep(120)

# 이벤트 바인딩
top_button.Bind(wx.EVT_BUTTON, ip_test)

# 수직 정렬
sizer = wx.BoxSizer(wx.VERTICAL)
sizer.Add(top_button, 0, wx.ALIGN_CENTER | wx.TOP, 30)
sizer.AddStretchSpacer()
panel.SetSizer(sizer)

# 창 중앙에 표시
frame.Centre()
frame.Show()

# 앱 루프 실행
app.MainLoop()