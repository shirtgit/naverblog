from data.box_data import BoxData
from data.button_data import ButtonData
from data.list_data import ListData
from data.parsing_data import ParseData
from data.text_data import TextData
import wx, csv

from task.task_thread import make_thread_task
from ui import log

class Binding:
    def __init__(self):
        self.buttons = ButtonData()
        self.boxes = BoxData()
        self.texts = TextData()
        self.lists = ListData()
        self.parsing_data = ParseData()

        self.parse_setter = []
        self.parse_getter = []
        self.list_collection = []
        self.LABEL_LIST = ["키워드", "카페", "계정", "제목"]

    def on_radio_selected(self, event):
        selected = event.GetString()
        self.texts.status_label.SetLabel(selected)
        if selected == "카페":
            self.on_radio_selected_utils(False)
        elif selected == "블로그":
            self.on_radio_selected_utils(True)
        else:
            self.on_radio_selected_utils(True, False)

    def on_radio_selected_utils(self, boolean, is_each=True):
        # 블로그 활성화 다중 설정
        # self.buttons.blog_button_Enable(boolean)
        self.lists.blog_list_Enable(boolean)

        # 카페 활성화 다중 설정
        self.buttons.cafe_button_Enable(not boolean if is_each else boolean)
        self.lists.cafe_list_Enable(not boolean if is_each else boolean)
        self.boxes.comment_cb_Enable(not boolean if is_each else boolean)

    def on_cafe_keyword_button_clicked(self, event, panel):

        self.set_collection()

        text = event.GetEventObject().GetLabel()
        index = -1
        found_indexes = [i for i, label in enumerate(self.LABEL_LIST) if label in text]
        if found_indexes:
            index = found_indexes[0]

        # 파일 불러오기 & 데이터 파싱
        self.upload_data(index, panel)

        # 멤버 변수를 지역 변수로 치환 (인덱스 접근 X)
        # csv_data = self.parse_getter[index]()
        # list_data = self.list_collection[index]

        # ListCtrl에 표시
        if index == 2:
            self.upload_account_blog_list(index)
        elif index == 3:
            self.upload_title_list(index)
        else:
            self.upload_keyword_cafe_list(index)

    def set_collection(self):
        self.parse_setter = [
            self.parsing_data.set_keyword_data,
            self.parsing_data.set_cafe_data,
            self.parsing_data.set_account_data,
            self.parsing_data.set_blog_data,
            self.parsing_data.set_title_data
        ]

        self.parse_getter = [
            self.parsing_data.get_keyword_data,
            self.parsing_data.get_cafe_data,
            self.parsing_data.get_account_data,
            self.parsing_data.get_blog_data,
            self.parsing_data.get_title_data
        ]

        self.list_collection = [
            self.lists.keyword_list, self.lists.cafe_list, self.lists.account_list, self.lists.blog_list, self.lists.title_list,
        ]

    def upload_data(self, index, panel):
        # 파일 불러오기
        with wx.FileDialog(panel, "CSV 파일 선택", wildcard="CSV 파일 (*.csv)|*.csv",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return

            path = dialog.GetPath()
            try:
                with open(path, newline='', encoding='cp949') as csvfile:
                    reader = csv.reader(csvfile)
                    self.parse_setter[index](list(reader))
            except FileNotFoundError as e:
                print(f"파일을 열 수 업습니다.\n{e}")

    # 카페, 키워드
    def upload_keyword_cafe_list(self, index):
        csv_data = self.parse_getter[index]()
        list_data = self.list_collection[index]
        list_data.DeleteAllItems()


        print(index)
        print("컬럼 개수:", list_data.GetColumnCount())

        # 유효성 검사 할 것 (데이터 열 개수와 리스트 행 개수가 맞는지)
        if len(csv_data[0]) != list_data.GetColumnCount():
            log.append_log("[ERROR] 데이터의 열 개수와 리스트의 열 개수가 맞지 않습니다.파일의 열 개수를 다시 확인해주세요.")
            return

        # for i in range(len(csv_data)):
        #     index = list_data.InsertItem(list_data.GetItemCount(), csv_data[i][0])
        #     for j in range(1, len(csv_data[i])):
        #         list_data.SetItem(index, j, csv_data[i][j])
        for row in csv_data[1:]:
            if not row:  # 빈 줄이면 건너뜀
                continue
            index = list_data.InsertItem(list_data.GetItemCount(), row[0])
            for j in range(1, len(row)):
                list_data.SetItem(index, j, row[j])

        if index == 0:
            list_data.SetColumnWidth(2, 200)
        else:
            list_data.SetColumnWidth(0, 100)
            list_data.SetColumnWidth(1, 100)

        # 제목
    def upload_title_list(self, index):
        csv_data = self.parse_getter[index]()
        list_data = self.list_collection[index]
        list_data.DeleteAllItems()

        # 유효성 검사 할 것 (데이터 열 개수와 리스트 행 개수가 맞는지)
        if len(csv_data[0]) != list_data.GetColumnCount():
            log.append_log("[ERROR] 데이터의 열 개수와 리스트의 열 개수가 맞지 않습니다.파일의 열 개수를 다시 확인해주세요.")
            return

        # for i in range(len(csv_data)):
        #     index = list_data.InsertItem(list_data.GetItemCount(), csv_data[i][0])
        #     for j in range(1, len(csv_data[i])):
        #         list_data.SetItem(index, j, csv_data[i][j])
        for row in csv_data[1:]:
            if not row:  # 빈 줄이면 건너뜀
                continue
            index = list_data.InsertItem(list_data.GetItemCount(), row[0])
            for j in range(1, len(row)):
                list_data.SetItem(index, j, row[j])

        list_data.SetColumnWidth(0, 380)

    def upload_account_blog_list(self, index):
        csv_data = self.parse_getter[index]()
        for i in range(2, 4):
            list_data = self.list_collection[i]
            list_data.DeleteAllItems()

            print(index)
            print("컬럼 개수:", list_data.GetColumnCount())

            if i == 2:
                new_csv_data = [[row[0], row[1], row[3]] for row in csv_data]
            else:
                new_csv_data = [[row[0], row[2]] for row in csv_data]
            for row in new_csv_data[1:]:
                if not row:  # 빈 줄이면 건너뜀
                    continue
                idx = list_data.InsertItem(list_data.GetItemCount(), row[0])
                for j in range(1, len(row)):
                    list_data.SetItem(idx, j, row[j])

            if i == 2:
                list_data.SetColumnWidth(0, 120)
                list_data.SetColumnWidth(1, 0)
                list_data.SetColumnWidth(2, 120)
            else:
                list_data.SetColumnWidth(0, 100)
                list_data.SetColumnWidth(1, 100)

    def on_execute_button_clicked(self, event, content_value):
        self.parsing_data.content_data = content_value
        make_thread_task()

