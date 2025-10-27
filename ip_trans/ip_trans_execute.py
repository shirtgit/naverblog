# print 구문은 전부 log로 바꾸기
import subprocess
import time
from ui import log
import requests

transferred_ip = None

def check_usb_connection():
    result = (subprocess.run(["adb", "devices"], capture_output=True, text=True, shell=True)
              .stdout.strip())
    result_lines = result.splitlines()

    if len(result_lines) <= 1 or "device" not in result:
        print("연결된 디바이스가 없습니다.")
        return False
    print(f"연결된 디바이스: {result_lines[1:]}")
    return True

# 내부 ip_trans, interface 반환
def get_inner_IP():
    results = subprocess.check_output(["adb", "shell", "ip", "addr"], shell=True).decode('utf-8')
    for result in results.splitlines():
        if "inet" in result and "inet6" not in result and "rmnet" in result:
            ip = result.split()[1].split('/')[0]
            interface = result.split()[-1]
            print(f"inner IP : {ip}")
            print(f"interface : {interface}")
            return ip, interface
    return "no IP", "no interface"

# 외부 IP 반환
def get_outer_IP():
    ip = requests.get("https://api.ipify.org").text.strip()
    print(f"outer IP : {ip}")
    return ip

# 테더링 상태 확인
def check_usb_tethering():
    # subprocess.check_output(["adb", "shell", "settings", "get",  "global", "tether_dun_required"], shell=True).decode('utf-8').strip()
    result = subprocess.check_output(["adb", "shell", "settings", "get",  "global", "tether_dun_required"], shell=True).decode('utf-8').strip()
    is_enable = result == '0'
    print(f"테더링 상태: {'활성화' if is_enable else '비활성화'}")
    return is_enable

# 테더링 활성화하기
def enable_usb_tethering():
    subprocess.run(["adb", "shell", "svc", "usb", "setFunctions", "rndis"], shell=True, check=True)
    time.sleep(5)
    subprocess.run(["adb", "shell", "svc", "usb", "setFunctions", "rndis,mtp"], shell=True)
    print("USB 테더링 활성화 완료")
    return True

def disable_airplane_mode():
    subprocess.run(["adb", "shell", "su", "-c", "\'settings put global airplane_mode_on 0\'"], shell=True)
    subprocess.run(
        ["adb", "shell", "su", "-c",  "\'am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false\'"], shell=True)
    print("비행기 모드를 비활성화합니다.")
    # log.append_log("비행기 모드를 비활성화합니다.")

def enable_airplane_mode():
    subprocess.run(["adb", "shell", "su", "-c", "\'settings put global airplane_mode_on 1\'"], shell=True)
    subprocess.run(
        ["adb", "shell", "su", "-c", "\'am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true\'"],
        shell=True)
    print("비행기 모드를 활성화합니다.")
    # log.append_log("비행기 모드를 활성화합니다.")

def trans_ip():
    global transferred_ip

    if not check_usb_connection():
        return

    previous_internal_ip, interface = get_inner_IP()
    previous_outer_ip = get_outer_IP()
    log.append_log(f"초기 내부 IP : {previous_internal_ip}")
    print(f"초기 외부 IP : {previous_outer_ip}\n")

    if transferred_ip is None:
        transferred_ip = {previous_outer_ip}

    for i in range(30):
        print("========================================")
        log.append_log(f"IP를 변경합니다.\n현재 IP = {previous_outer_ip}\n")
        enable_airplane_mode()
        time.sleep(10)

        disable_airplane_mode()
        time.sleep(10)

        if not check_usb_tethering():
            enable_usb_tethering()
            time.sleep(5)

        after_internal_ip, after_interface = get_inner_IP()
        time.sleep(5)
        after_outer_ip = get_outer_IP()

        print(f"\n내부 IP : {after_internal_ip}")
        print(f"인터페이스: {after_interface}")
        print(f"외부 IP : {after_outer_ip}")

        if after_outer_ip not in transferred_ip:
            transferred_ip.add(previous_outer_ip)
            log.append_log("새로운 IP에 연결했습니다.")
            log.append_log(f"IP = {after_outer_ip}")
            print("========================================")
            break
        print("========================================")
        time.sleep(120)






