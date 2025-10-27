import requests, time, subprocess
from ui import log
from utils.decorators import sleep_after

@sleep_after()
def get_current_ip():
    try:
        response = requests.get("https://api.ipify.org", timeout=5, headers={"Cache-Control": "no-cache"})
        return response.text
    except Exception as e:
        return f"IP 확인 실패: {e}"

# 안드로이드 개발자 옵션 활성화 + USB 디버깅 허용 필수
def disable_mobile_data():
    print("모바일 데이터를 끕니다.")
    subprocess.run(["adb", "shell", "svc", "data", "disable"])
    time.sleep(5)

def enable_mobile_data():
    print("모바일 데이터를 켭니다.")
    subprocess.run(["adb", "shell", "svc", "data", "enable"])
    time.sleep(3)

def get_network_info():
    result = subprocess.check_output(["adb", "shell", "dumpsys", "connectivity"])
    return result.decode(errors="ignore")

def wait_for_mobile_network(timeout=30):
    for _ in range(timeout):
        try:
            output = (
                subprocess.check_output(["adb", "shell", "dumpsys", "connectivity"],
                                        stderr=subprocess.DEVNULL).decode(errors="ignore"))
            if "NetworkAgentInfo" in output and "MOBILE" in output and "CONNECTED" in output:
                return True
        except Exception as e:
            pass
        time.sleep(1)
    return False


def run_cycle():
    ip_before = get_current_ip()
    print(f"현재 IP = {ip_before}")
    disable_mobile_data()
    enable_mobile_data()

    if wait_for_mobile_network():
        time.sleep(3)
        ip_after = get_current_ip()
        print(f"변경 IP = {get_current_ip()}")
    else:
        ip_after = "연결 실패"
        print("모바일 네트워크 연결 실패")

    print("\n======= 결과 요약 =======")
    print(f"이전 IP = {ip_before}")
    print(f"현재 IP = {ip_after}")
    print("=======================")



    print(f"네트워크 정보 = {get_network_info()}")
    print("================================================")