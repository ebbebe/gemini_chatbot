"""
캘린더 관련 유틸리티 함수 모듈

Export 형태:
- from utils.calendar import get_month_calendar, get_prev_month, get_next_month
- from utils.calendar import get_date_tasks, add_task_to_date, toggle_task_completion
- from utils.calendar import get_tasks_stats, format_date, parse_date
- 또는 import utils.calendar as calendar_utils 후 calendar_utils.format_date() 형태로 사용
"""
import datetime
import calendar as py_calendar
import streamlit as st
from typing import List, Dict, Any, Union

def get_month_calendar(year: int, month: int) -> List[List[int]]:
    """ 
    해당 월의 달력 그리드 생성 (6주 포함)
    
    Args:
        year: 연도
        month: 월
        
    Returns:
        List[List[int]]: 달력 그리드 (6주 x 7일)
    """
    cal = py_calendar.monthcalendar(year, month)
    
    # 캘린더가 6주가 되도록 행 추가
    while len(cal) < 6:
        cal.append([0] * 7)
    
    return cal

def get_prev_month(date: datetime.datetime) -> datetime.datetime:
    """ 
    이전 월 날짜 가져오기
    
    Args:
        date: 기준 날짜
        
    Returns:
        datetime.datetime: 이전 월의 1일
    """
    first_day = datetime.datetime(date.year, date.month, 1)
    last_month = first_day - datetime.timedelta(days=1)
    return datetime.datetime(last_month.year, last_month.month, 1)

def get_next_month(date: datetime.datetime) -> datetime.datetime:
    """ 
    다음 월 날짜 가져오기
    
    Args:
        date: 기준 날짜
        
    Returns:
        datetime.datetime: 다음 월의 1일
    """
    if date.month == 12:
        return datetime.datetime(date.year + 1, 1, 1)
    else:
        return datetime.datetime(date.year, date.month + 1, 1)

def get_date_tasks(date_str: str) -> List[Dict[str, Any]]:
    """ 
    해당 날짜의 태스크 가져오기
    
    Args:
        date_str: YYYY-MM-DD 형식의 날짜 문자열
        
    Returns:
        List[Dict[str, Any]]: 해당 날짜의 태스크 목록
    """
    if date_str in st.session_state['tasks']:
        return st.session_state['tasks'][date_str]
    return []

def add_task_to_date(date_str: str, task: Dict[str, Any]) -> str:
    """ 
    해당 날짜에 태스크 추가하기
    
    Args:
        date_str: YYYY-MM-DD 형식의 날짜 문자열
        task: 추가할 태스크 정보
        
    Returns:
        str: 생성된 태스크 ID
    """
    if date_str not in st.session_state['tasks']:
        st.session_state['tasks'][date_str] = []
    
    # 태스크 ID 부여
    task_id = f"{date_str}_{len(st.session_state['tasks'][date_str])}"
    task['id'] = task_id
    
    st.session_state['tasks'][date_str].append(task)
    st.session_state['task_completion'][task_id] = False
    
    return task_id

def toggle_task_completion(task_id: str) -> bool:
    """ 
    태스크 완료 상태 토글
    
    Args:
        task_id: 태스크 ID
        
    Returns:
        bool: 토글 후 상태 (True: 완료, False: 미완료)
    """
    current_status = st.session_state['task_completion'].get(task_id, False)
    st.session_state['task_completion'][task_id] = not current_status
    
    # 연속 실천일수 계산
    if not current_status:  # 완료로 변경되었을 때
        st.session_state['streak_days'] += 1
    
    return not current_status

def get_tasks_stats() -> Dict[str, int]:
    """ 
    태스크 관련 통계 계산
    
    Returns:
        Dict[str, int]: 태스크 통계 정보
    """
    total_tasks = sum(len(tasks) for tasks in st.session_state['tasks'].values())
    completed_tasks = sum(1 for status in st.session_state['task_completion'].values() if status)
    ongoing_roadmaps = len(st.session_state['roadmap_items'])
    streak_days = st.session_state['streak_days']
    
    return {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'ongoing_roadmaps': ongoing_roadmaps,
        'streak_days': streak_days
    }

def format_date(date: datetime.datetime) -> str:
    """ 
    날짜를 YYYY-MM-DD 형식의 문자열로 변환
    
    Args:
        date: 변환할 날짜
        
    Returns:
        str: YYYY-MM-DD 형식의 문자열
    """
    return date.strftime("%Y-%m-%d")

def parse_date(date_str: str) -> datetime.datetime:
    """ 
    YYYY-MM-DD 형식의 문자열을 datetime 객체로 변환
    
    Args:
        date_str: YYYY-MM-DD 형식의 날짜 문자열
        
    Returns:
        datetime.datetime: 변환된 datetime 객체
    """
    return datetime.datetime.strptime(date_str, "%Y-%m-%d")
