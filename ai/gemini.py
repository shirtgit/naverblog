import re

from ui import log
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

from data import text_data

# gemini_key = "AIzaSyDo6wlM9Q6SFKS-rpHoS_sJQabVt9OEDnI"
model = None


def init_gemini():
    global model
    # 테스트 용도로 주석처리
    api_key = text_data.TextData().get_api_number()
    genai.configure(api_key=api_key)

    # genai.configure(api_key=gemini_key)

    model = genai.GenerativeModel('gemini-1.5-flash')
    # dotenv.load_dotenv()
    # genai.configure(api_key=os.getenv("API_KEY"))
    # model = genai.GenerativeModel('gemini-1.5-flash')
    # model = genai.GenerativeModel('gemini-1.0-pro')

def create_title(titles, address, company):
    global model
    titles_str = "\n".join(titles)
    try:
        response = model.generate_content(f"""
                    내가 제목을 작성을 할 거야. 주소 키워드는 {address}, 업체 키워드는 {company}야.
                    한 마디로, 나는 {address} 지역에서 {company}를 운영하는데, "홍보 글의 제목"을 작성하고 싶어.
                    내가 수집한 제목 리스트를 보여줄게. 이 리스트들은 상위 노출된 10개 글의 제목들이야.
                    
                    {titles_str}
                    
                    내가 쓰는 글도 상위 노출이 될 수 있게끔 저 리스트들을 참고해서 제목을 하나 작성해 줘.
                    대신에 주소, 업체 키워드가 꼭 들어가야 해.
                    그리고 **과 같은 마크다운 언어는 쓰지 마.
                    그리고 너가 준 제목으로 바로 포스팅을 할거야. 다른 제목 옵션 주지 말고 그냥 제목 딱 한줄만 넘겨줘.
                    그래야 글이 꼬이지 않아.
                    .""")

        return response.text
    except ResourceExhausted as e:
        match = re.search(r'quota_id: "(.*?)"', str(e))
        if match:
            quota_id = match.group(1)
            log.append_log(f"[ERROR] 무료 요금제의 하루 일일 요청을 초과하였습니다.\nquota_id: {quota_id}")
            log.append_log("[ERROR] 충분한 시간이 흐른 뒤에 프로그램을 재시작해 주세요.")
        raise
    except Exception as e2:
        log.append_log("[ERROR] Gemini 소통 중 오류가 발생하였습니다.")
        log.append_log(f"[ERROR] 오류 이름: {type(e2).__name__}")
        raise

def create_content(contents, address, company):
    global model
    try:
        response = model.generate_content(f"""
                내가 글을 쓸건데, 주소 키워드는 {address}, 업체 키워드는 {company}야.
                예시 글들을 보여줄게.
                
                예시 1:
                {contents[0]}
        
                예시 2:
                {contents[1]}
    
                중간에 사진을 10장 넣을 건데, 너가 생성한 글에서 사진을 넣을 만한 장소에 %사진% 이라고 써 주고, 1500자 내외의 글로 작성해 줘.
                반드시 사진을 10장 넣게 해 줘야 해. 꼭.
                문장이 . ? ! 이런 끝맺음 기호로 끝날 때마다 줄바꿈은 꼭 해줘야 해.
                사진이 들어가는 공간은 문맥을 해치지 말아야 해. 예를 들면 본문이 하나 끝나고, 소제목이 들어가기 전에 넣어주면 좋겠어. 
                그리고 사진에 대한 설명을 적으면 글을 파싱하기 어려우니까, 사진에 대한 설명은 반드시 빼 줘.
                연락처, 주소, 홈페이지 같은 정보는 적지 않아도 돼
                또한, 인사말과 끝맺음말은 내가 직접 적을 거니까 그건 빼줘.
                그리고 **과 같은 마크다운 언어는 쓰지 마.
                .""")

        return response.text
    except ResourceExhausted as e:
        match = re.search(r'quota_id: "(.*?)"', str(e))
        if match:
            quota_id = match.group(1)
            log.append_log(f"[ERROR] 무료 요금제의 하루 일일 요청을 초과하였습니다.\nquota_id: {quota_id}")
            log.append_log("[ERROR] 충분한 시간이 흐른 뒤에 프로그램을 재시작해 주세요.")
        raise
    except Exception as e2:
        log.append_log("[ERROR] Gemini 소통 중 오류가 발생하였습니다.")
        log.append_log(f"[ERROR] 오류 이름: {type(e2).__name__}")
        raise


# def create_title(address, company, article):
#     global model
#
#     response = model.generate_content(f"""
#                 다음은 너가 써 준 글이야.
#
#                 {article}
#
#                 이 글에 맞는 제목을 작성하고 싶어.
#
#
#
#                 내가 글을 쓸건데, 키워드는 {address}, {company}야.
#                 예시 글들을 보여줄게.
#
#                 예시 1:
#                 {contents[0]}
#
#                 예시 2:
#                 {contents[1]}
#
#                 중간에 사진을 10장 넣을 건데, 너가 생성한 글에서 사진을 넣을 만한 장소에 %사진% 이라고 써 주고, 1500자 내외의 글로 작성해 줘.
#                 반드시 사진을 10장 넣게 해 줘야 해.
#                 문장이 . ? ! 이런 끝맺음 기호로 끝날 때마다 줄바꿈은 꼭 해줘야 해.
#                 사진이 들어가는 공간은 문맥을 해치지 말아야 해. 예를 들면 본문이 하나 끝나고, 소제목이 들어가기 전에 넣어주면 좋겠어.
#                 그리고 사진에 대한 설명을 적으면 글을 파싱하기 어려우니까, 사진에 대한 설명은 반드시 빼 줘.
#                 연락처, 주소, 홈페이지 같은 정보는 적지 않아도 돼
#                 또한, 인사말과 끝맺음말은 내가 직접 적을 거니까 그건 빼줘.
#                 그리고 **과 같은 마크다운 언어는 쓰지 마.
#                 .""")
#
#     return response.text