"""
세션 상태 관리 유틸리티 모듈

Export 형태:
- from utils.session import initialize_session_state
- from utils.session import initialize_gemini_api
- 또는 import utils.session as session 후 session.initialize_session_state() 형태로 사용
"""
import datetime
import streamlit as st
import google.generativeai as genai
from typing import Dict, Any, Optional

def initialize_session_state() -> None:
    """
    애플리케이션에 필요한 세션 상태 변수들을 초기화합니다.
    앱이 시작될 때 한 번만 호출해야 합니다.
    """
    # 온보딩 상태
    if 'onboarding_complete' not in st.session_state:
        st.session_state['onboarding_complete'] = False
        
    # 사용자 정보
    if 'user_info' not in st.session_state:
        st.session_state['user_info'] = {
            'name': '',
            'birthdate': None,
            'birth_hour': ''
        }
        
    # 채팅 관련 상태
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
        
    if 'chat_messages' not in st.session_state:
        st.session_state['chat_messages'] = []
        
    if 'has_initial_greeting' not in st.session_state:
        st.session_state['has_initial_greeting'] = False
    
    # 로드맵 관련 상태
    if 'roadmap' not in st.session_state:
        st.session_state['roadmap'] = []
    
    if 'roadmap_items' not in st.session_state:
        st.session_state['roadmap_items'] = []
    
    # 캘린더 관련 상태
    if 'current_date' not in st.session_state:
        st.session_state['current_date'] = datetime.datetime.now()
        
    if 'tasks' not in st.session_state:
        st.session_state['tasks'] = {}
        
    if 'task_completion' not in st.session_state:
        st.session_state['task_completion'] = {}
        
    if 'streak_days' not in st.session_state:
        st.session_state['streak_days'] = 0

def initialize_gemini_api() -> Optional[genai.GenerativeModel]:
    """
    Gemini API를 초기화하고 모델 객체를 반환합니다.
    
    Returns:
        Optional[genai.GenerativeModel]: 초기화된 Gemini 모델 객체 또는 오류 시 None
    """
    try:
        gemini_api_key = st.secrets["gemini_api_key"]
        genai.configure(api_key=gemini_api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"API 키 설정 오류: {e}")
        st.info("Google Gemini API 키를 .streamlit/secrets.toml 파일에 'gemini_api_key' 항목으로 설정해주세요.")
        return None

def get_user_info() -> Dict[str, Any]:
    """
    현재 세션에 저장된 사용자 정보를 반환합니다.
    
    Returns:
        Dict[str, Any]: 사용자 정보 딕셔너리
    """
    return st.session_state.get('user_info', {
        'name': '',
        'birthdate': None,
        'birth_hour': ''
    })

def update_user_info(name: str = None, birthdate: datetime.date = None, birth_hour: str = None) -> None:
    """
    사용자 정보를 업데이트합니다.
    
    Args:
        name: 사용자 이름 (없으면 기존 값 유지)
        birthdate: 생년월일 (없으면 기존 값 유지)
        birth_hour: 태어난 시간 (없으면 기존 값 유지)
    """
    if 'user_info' not in st.session_state:
        st.session_state['user_info'] = {
            'name': '',
            'birthdate': None,
            'birth_hour': ''
        }
        
    if name is not None:
        st.session_state['user_info']['name'] = name
        
    if birthdate is not None:
        st.session_state['user_info']['birthdate'] = birthdate
        
    if birth_hour is not None:
        st.session_state['user_info']['birth_hour'] = birth_hour
