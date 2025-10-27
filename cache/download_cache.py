from data import text_data, box_data
from data import list_data
import json, csv
import os
from ui import log

lists = list_data.ListData()
texts = text_data.TextData()
boxes = box_data.BoxData()

def convert_JSON():
    global texts
    return {
        "waiting_max": texts.waiting_max.GetValue(),
        "waiting_min": texts.waiting_min.GetValue(),
        "phone_number": texts.phone_number.GetValue(),
        "api_number": texts.api_number.GetValue(),
        "content_input": texts.content_input.GetValue(),
        "status_rb": boxes.status_rb.GetSelection(),
        "comment_cb": boxes.comment_cb.GetValue(),
    }

def download_JSON():
    log.append_log("캐시 파일을 저장합니다.")
    converted_data = convert_JSON()
    # print(f"converted data: {converted_data}")
    with open("cache/.cache_text", "w", encoding="utf-8") as f:
        json.dump(converted_data, f, indent=4, ensure_ascii=False)

def download_CSV():
    list_ctrl_list = [lists.account_list, lists.keyword_list, lists.blog_list, lists.cafe_list, lists.title_list]
    csv_names = [".cache_account", ".cache_keyword", ".cache_blog", ".cache_cafe", ".cache_title"]

    for i in range(len(csv_names)):
        row_count = list_ctrl_list[i].GetItemCount()
        col_count = list_ctrl_list[i].GetColumnCount()

        with open(f"cache/{csv_names[i]}", "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            # 1. 헤더 저장
            headers = [list_ctrl_list[i].GetColumn(col).GetText() for col in range(col_count)]
            writer.writerow(headers)

            # 2. 데이터 저장
            for row in range(row_count):
                row_data = []
                for col in range(col_count):
                    item = list_ctrl_list[i].GetItem(row, col)
                    row_data.append(item.GetText())
                writer.writerow(row_data)

        # print(f"✅ 저장 완료: {csv_names[i]}")