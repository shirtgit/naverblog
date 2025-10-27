import time
import streamlit as st

# Streamlit 세션 상태에 로그를 저장하기 위한 함수들

def append_log(log):
    """로그 메시지를 추가합니다"""
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    
    current_time = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())
    
    # 로그 레벨 결정
    level = "INFO"
    if '[ERROR]' in log or '오답' in log or 'ERROR' in log:
        level = "ERROR"
    elif '완료' in log or '성공' in log or 'SUCCESS' in log:
        level = "SUCCESS"
    elif '경고' in log or 'WARNING' in log:
        level = "WARNING"
    elif '초기화' in log:
        level = "INFO"
    
    # 로그 추가
    st.session_state.logs.append({
        'timestamp': current_time,
        'message': log,
        'level': level
    })
    
    # 로그가 너무 많아지면 오래된 것부터 제거 (최대 1000개)
    if len(st.session_state.logs) > 1000:
        st.session_state.logs = st.session_state.logs[-1000:]

def clear_logs():
    """모든 로그를 지웁니다"""
    if 'logs' in st.session_state:
        st.session_state.logs = []

def get_logs():
    """현재 로그 목록을 반환합니다"""
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    return st.session_state.logs

def get_recent_logs(count=50):
    """최근 로그만 반환합니다"""
    logs = get_logs()
    return logs[-count:] if len(logs) > count else logs