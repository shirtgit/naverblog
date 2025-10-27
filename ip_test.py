# 윈도우 git bash에서 실행할 목적으로 추가
import sys
import os
import threading
import ip_test_util as itu
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import wx.richtext as rt
import wx
from ip_trans import ip_trans_execute
import time

# 앱 초기화
app = wx.App(False)
frame = wx.Frame(None, title="IP 우회 테스트", size=(300, 600))
panel = wx.Panel(frame)

# 버튼 생성
top_button = wx.Button(panel, label="현재 IP 우회 테스트")
log_text_widget = rt.RichTextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.BORDER_THEME | wx.TE_READONLY,
            size=wx.Size(400, 500)
        )

def ip_test(event):
    task_thread = threading.Thread(target=test_ip, daemon=False)
    # task_thread = threading.Thread(target=test_rb_value(), daemon=False)
    task_thread.start()

def test_ip():
    if not itu.check_usb_connection():
        return

    previous_outer_ip = itu.get_outer_IP()
    append_log("=================================")
    append_log(f"현재 IP = {previous_outer_ip}\n")
    itu.enable_airplane_mode()
    time.sleep(10)

    itu.disable_airplane_mode()
    time.sleep(10)

    if not itu.check_usb_tethering():
        itu.enable_usb_tethering()
        time.sleep(5)

    after_internal_ip, after_interface = itu.get_inner_IP()
    time.sleep(5)
    after_outer_ip = itu.get_outer_IP()

    append_log(f"변환 IP = {after_outer_ip}")
    append_log("=================================")
    time.sleep(120)

# 이벤트 바인딩
top_button.Bind(wx.EVT_BUTTON, ip_test)


def append_log(message):
    current_time = time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime())
    # color = wx.WHITE
    if "=======" not in message:
        message = current_time + message

    def update_ui():
        log_text_widget.BeginTextColour(wx.BLACK)
        log_text_widget.WriteText(message + "\n")
        log_text_widget.EndTextColour()
        log_text_widget.ShowPosition(log_text_widget.GetLastPosition())

    wx.CallAfter(update_ui)

# 수직 정렬
sizer = wx.BoxSizer(wx.VERTICAL)
sizer.Add(top_button, 0, wx.ALIGN_CENTER | wx.TOP, 30)
sizer.Add(log_text_widget, 1, wx.EXPAND | wx.TOP, 30)
# sizer.AddStretchSpacer()
panel.SetSizer(sizer)


# 창 중앙에 표시
frame.Centre()
frame.Show()

# 앱 루프 실행
app.MainLoop()