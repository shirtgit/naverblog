from ai import gemini
from data import const, text_data, list_data
import re
from ui import log

PATTERN = r'  |\n+'

def parse_contents(address, company):
    header, footer = parse_boilerplate()
    log.append_log("Gemini를 통해 본문을 생성합니다.")
    body = get_body(address, company)
    log.append_log("본문 생성이 완료되었습니다.")
    content = []
    header = parse_header(header, address, company)
    content.extend(header)
    content.extend(body)
    content.extend(footer)
    # print(content)
    return content


def get_body(address, company):
    log.append_log("Gemini를 초기화합니다.")
    gemini.init_gemini()
    log.append_log("Gemini에게 요청을 전송합니다.")
    response = gemini.create_content([const.CONTENT_EX1, const.CONTENT_EX2], address, company)
    log.append_log("Gemini로부터 응답을 전달받습니다.")
    response = response.replace("**", "")
    contents = [item.strip() for item in re.split(PATTERN, response)]
    # index = 0
    # for content in contents:
    #     print(f"[{index}]: {content}")
    #     index += 1
    return contents


def parse_boilerplate():
    boilerplate = get_boilerplate()
    for i in range(2):
        boilerplate[i] = [item.strip() for item in re.split(PATTERN, boilerplate[i])]
    return boilerplate[0], boilerplate[1]

# def get_boilerplate():
#     text = text_data.TextData().get_body()
#     print(text)
#     return re.split(r"\[본문\]", text)

def get_boilerplate():
    text = text_data.TextData().get_content_input()
    return re.split(r"\[본문\]", text)

def parse_header(headers, address, company):
    result = []
    # print(f"[headers] = {headers}")
    for header in headers:
        # print(f"[header] = {header}")
        if "%주소%" in header:
            header = header.replace("%주소%", address)
        if "%업체%" in header:
            header = header.replace("%업체%", company)
        result.append(header)
        # print(f"[result] = {result}")
    return result