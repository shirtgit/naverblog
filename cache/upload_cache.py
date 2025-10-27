import os, json, csv
from data import list_data, text_data, box_data, button_data

lists = list_data.ListData()
texts = text_data.TextData()
boxes = box_data.BoxData()
buttons = button_data.ButtonData()
is_exist = False

# def is_JSON_exist():
#     file_path = os.path.join(os.getcwd(), "cache", ".cache_text")
#     if os.path.isfile(file_path):
#         return True
#     else:
#         return False

def upload_JSON():
    file_path = os.path.join(os.getcwd(), "cache", ".cache_text")
    if os.path.isfile(file_path):
        print("✅ .cache_text 파일이 존재합니다.")
        with open("cache/.cache_text", "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}


def show_text():
    text_json = upload_JSON()
    text_list = [
        texts.waiting_max, texts.waiting_min, texts.api_number, texts.phone_number, texts.content_input
    ]
    text_keys = [
        "waiting_max", "waiting_min", "api_number", "phone_number", "content_input"
    ]
    for text_input, key in zip(text_list, text_keys):
        text_input.SetValue(text_json.get(key, ""))

    rb_data = text_json.get("status_rb", 0)
    boxes.set_rb_index(rb_data)

    if rb_data == 0:
        set_rb_index_utils(True)
        texts.status_label.SetLabel("블로그")
    elif rb_data == 1:
        set_rb_index_utils(False)
        texts.status_label.SetLabel("카페")
    else:
        set_rb_index_utils(True, False)
        texts.status_label.SetLabel("둘 다")

    cb_data = text_json.get("comment_cb", True)
    boxes.set_cb_value(cb_data)


def set_rb_index_utils(boolean, is_each=True):
    # 블로그 활성화 다중 설정
    # self.buttons.blog_button_Enable(boolean)
    lists.blog_list_Enable(boolean)

    # 카페 활성화 다중 설정
    buttons.cafe_button_Enable(not boolean if is_each else boolean)
    lists.cafe_list_Enable(not boolean if is_each else boolean)
    boxes.comment_cb_Enable(not boolean if is_each else boolean)

def upload_CSV(file_name):
    file_path = os.path.join(os.getcwd(), "cache", file_name)
    if os.path.isfile(file_path):
        print("✅ .cache_text 파일이 존재합니다.")
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            return [row for row in reader]
    else:
        return None


def show_lists():
    list_ctrl_list = [lists.account_list, lists.keyword_list, lists.blog_list, lists.cafe_list, lists.title_list]
    csv_names = [".cache_account", ".cache_keyword", ".cache_blog", ".cache_cafe", ".cache_title"]

    for idx in range(len(csv_names)):
        data = upload_CSV(csv_names[idx])
        if not data or len(data) < 1:
            continue  # 데이터가 없거나 비어 있으면 넘어감

        list_ctrl = list_ctrl_list[idx]
        list_ctrl.DeleteAllItems()  # 기존 항목 삭제

        headers = data[0]
        rows = data[1:]

        # 컬럼 초기화
        for col in range(list_ctrl.GetColumnCount()):
            list_ctrl.DeleteColumn(0)
        for col_idx, header in enumerate(headers):
            list_ctrl.InsertColumn(col_idx, header)

        # 데이터 삽입
        for row in rows:
            if not row:
                continue
            item_index = list_ctrl.InsertItem(list_ctrl.GetItemCount(), row[0])
            for col_idx in range(1, len(row)):
                list_ctrl.SetItem(item_index, col_idx, row[col_idx])

    lists.account_list.SetColumnWidth(0, 120)
    lists.account_list.SetColumnWidth(1, 0)
    lists.account_list.SetColumnWidth(2, 120)

    lists.keyword_list.SetColumnWidth(2, 200)

    lists.blog_list.SetColumnWidth(0, 100)
    lists.blog_list.SetColumnWidth(1, 100)

    lists.cafe_list.SetColumnWidth(0, 100)
    lists.cafe_list.SetColumnWidth(1, 100)