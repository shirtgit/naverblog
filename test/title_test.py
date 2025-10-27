import wx
import csv, random, time

class TestFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="CSV 업로드 테스트", size=wx.Size(500, 650))
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        # 버튼
        self.button = wx.Button(panel, label="CSV 업로드")
        vbox.Add(self.button, 0, wx.EXPAND | wx.ALL, 5)

        # 리스트 컨트롤
        self.list_ctrl = wx.ListCtrl(panel, style=wx.LC_REPORT)
        self.list_ctrl.InsertColumn(0, "데이터", width=480)
        vbox.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 5)

        # 추출 버튼 추가
        self.extract_button = wx.Button(panel, label="추출")
        vbox.Add(self.extract_button, 0, wx.EXPAND | wx.ALL, 5)

        self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=wx.Size(480, 300))
        vbox.Add(self.text_ctrl, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(vbox)

        # 버튼 이벤트
        self.button.Bind(wx.EVT_BUTTON, self.on_button_click)
        self.extract_button.Bind(wx.EVT_BUTTON, self.on_extract_click)


        self.title_list = []

    def on_button_click(self, event):
        with wx.FileDialog(self, "CSV 파일 선택", wildcard="CSV files (*.csv)|*.csv",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # 취소하면 아무것도 안 함

            path = fileDialog.GetPath()
            self.load_csv_to_list(path)

    def load_csv_to_list(self, path):
        """CSV 파일 읽어서 ListCtrl에 표시"""
        self.list_ctrl.DeleteAllItems()  # 기존 데이터 초기화

        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:  # 빈 줄은 건너뛰기
                    self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), row[0])
        self.upload_to_multi_text()

    def upload_to_multi_text(self):
        """ListCtrl의 값을 self.title_list와 멀티라인 텍스트에 업데이트"""
        self.title_list.clear()  # 기존 데이터 초기화
        for idx in range(1, self.list_ctrl.GetItemCount()):
            value = self.list_ctrl.GetItemText(idx)
            self.title_list.append(value)

        # 멀티라인 텍스트에 한 번에 표시
        self.text_ctrl.SetValue("\n".join(self.title_list))
        self.button.Enable(False)

    def on_extract_click(self, event):
        self.extract_button.Enable(False)
        self.transfer_title("성수동", "설비업체")
        self.get_one_title_random()
        self.extract_button.Enable(True)

    def transfer_title(self, address, company):
        for idx in range(0, len(self.title_list)):
            self.title_list[idx] = self.title_list[idx].replace("%주소%", address)
            self.title_list[idx] = self.title_list[idx].replace("%업체%", company)

    def get_one_title_random(self):
        self.text_ctrl.SetValue(random.choice(self.title_list))

if __name__ == "__main__":
    app = wx.App(False)
    frame = TestFrame()
    frame.Show()
    app.MainLoop()