"""
로드맵 및 캘린더 인터페이스 컴포넌트

Export 형태:
- from components.roadmap import show_roadmap_tab
- 또는 import components.roadmap as roadmap 후 roadmap.show_roadmap_tab() 형태로 사용
"""
import datetime
import streamlit as st
from utils.saju import generate_saju_insight
from utils.calendar import (
    get_month_calendar, get_prev_month, get_next_month, 
    get_date_tasks, add_task_to_date, toggle_task_completion,
    get_tasks_stats, format_date, parse_date
)

def show_roadmap_tab():
    """로드맵 탭 UI를 표시합니다."""
    # 쿼리 파라미터에서 선택된 날짜 확인
    if 'selected_date' in st.query_params:
        selected_date = st.query_params['selected_date']
        st.session_state['selected_date'] = selected_date
        # 쿼리 파라미터 제거 (URL 깔끔하게 유지)
        st.query_params.clear()
        
    st.markdown("### 🗺️ 나의 맞춤형 성장 로드맵")
    st.markdown("당신의 사주를 기반으로 개인 맞춤형 성장 계획을 제안합니다.")
    
    # 통계 대시보드
    stats = get_tasks_stats()
    st.markdown("<div class='stats-container'>", unsafe_allow_html=True)
    
    # 진행 중인 로드맵 통계
    st.markdown(f"""
    <div class='stat-card'>
        <div class='stat-value'>{stats['ongoing_roadmaps']}</div>
        <div class='stat-label'>진행 중인 로드맵</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 완료한 태스크 통계
    st.markdown(f"""
    <div class='stat-card'>
        <div class='stat-value'>{stats['completed_tasks']}</div>
        <div class='stat-label'>완료한 태스크</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 연속 실천일수 통계
    st.markdown(f"""
    <div class='stat-card'>
        <div class='stat-value'>{stats['streak_days']}</div>
        <div class='stat-label'>연속 실천일수</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 캘린더 컨테이너
    st.markdown("<div class='calendar-container'>", unsafe_allow_html=True)
    
    # 캘린더 헤더 - 월 네비게이션
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("◀ 이전", key="prev_month"):
            st.session_state['current_date'] = get_prev_month(st.session_state['current_date'])
            st.rerun()
            
    with col2:
        current_month = st.session_state['current_date'].strftime("%Y년 %m월")
        st.markdown(f"<h3 style='text-align: center;'>{current_month}</h3>", unsafe_allow_html=True)
        
    with col3:
        if st.button("다음 ▶", key="next_month"):
            st.session_state['current_date'] = get_next_month(st.session_state['current_date'])
            st.rerun()
    
    # 요일 헤더
    weekdays = ["일", "월", "화", "수", "목", "금", "토"]
    cols = st.columns(7)
    for i, col in enumerate(cols):
        with col:
            day_style = "color: #ff5a5a;" if i == 0 else "color: #5a5aff;" if i == 6 else ""
            st.markdown(f"<div class='calendar-day-header' style='{day_style}'>{weekdays[i]}</div>", unsafe_allow_html=True)
    
    # 캘린더 그리드 생성
    current_year = st.session_state['current_date'].year
    current_month = st.session_state['current_date'].month
    today = datetime.datetime.now().date()
    
    # 이번 달의 캘린더 생성
    calendar_grid = get_month_calendar(current_year, current_month)
    
    # 태스크가 있는 날짜 확인
    days_with_tasks = set()
    for date_str in st.session_state.get('tasks', {}).keys():
        if date_str.startswith(f"{current_year}-{current_month:02d}"):
            days_with_tasks.add(int(date_str.split('-')[2]))
    
    # 달력 표시
    st.markdown("<div class='calendar-grid'>", unsafe_allow_html=True)
    
    # 선택된 날짜를 추적하는 세션 상태 변수
    if 'selected_date' not in st.session_state:
        st.session_state['selected_date'] = format_date(datetime.datetime.now())
    
    for week in calendar_grid:
        for day in week:
            if day == 0:
                # 비어있는 셀
                st.markdown("<div class='calendar-day other-month'></div>", unsafe_allow_html=True)
            else:
                # 날짜 형식화
                date_obj = datetime.date(current_year, current_month, day)
                date_str = format_date(datetime.datetime(current_year, current_month, day))
                
                # CSS 클래스 결정
                day_classes = ['calendar-day']
                if date_obj == today:
                    day_classes.append('today')
                if day in days_with_tasks:
                    day_classes.append('has-tasks')
                
                # 클릭 가능한 날짜 셀 생성
                day_id = f"day_{date_str}"
                st.markdown(f"""
                <div id='{day_id}' class='{' '.join(day_classes)}' 
                    onclick="window.location.href='?selected_date={date_str}'">{day}</div>
                """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # calendar-container 닫기
    
    # 선택된 날짜의 태스크 표시
    selected_date = st.session_state['selected_date']
    selected_date_obj = parse_date(selected_date)
    st.markdown(f"#### {selected_date_obj.strftime('%Y년 %m월 %d일')} 일정")
    
    # 해당 날짜의 태스크 가져오기
    tasks = get_date_tasks(selected_date)
    
    # 새 태스크 추가 폼
    with st.form(key=f"add_task_form_{selected_date}"):
        st.markdown(f"**새 태스크 추가**")
        new_task_title = st.text_input("태스크 제목", key=f"new_task_title_{selected_date}")
        new_task_desc = st.text_area("상세 내용", key=f"new_task_desc_{selected_date}", height=80)
        
        cols = st.columns([3, 1])
        with cols[1]:
            submit_task = st.form_submit_button("추가하기")
            
    if submit_task and new_task_title.strip():
        # 새 태스크 추가
        new_task = {
            'title': new_task_title,
            'description': new_task_desc,
            'added_date': format_date(datetime.datetime.now())
        }
        add_task_to_date(selected_date, new_task)
        st.success(f"태스크 '{new_task_title}'가 추가되었습니다.")
        st.rerun()
    
    # 태스크 목록 표시
    if not tasks:
        st.info(f"{selected_date_obj.strftime('%m월 %d일')}에는 예정된 태스크가 없습니다.")
    else:
        for task in tasks:
            task_id = task['id']
            is_completed = st.session_state.get('task_completion', {}).get(task_id, False)
            
            task_card = f"""
            <div class='roadmap-card'>
                <div class='roadmap-title'>{task['title']}</div>
                <p>{task['description']}</p>
                <div class='roadmap-meta'>
                    <span>추가일: {task['added_date']}</span>
                </div>
            </div>
            """
            
            st.markdown(task_card, unsafe_allow_html=True)
            
            # 완료 체크박스
            if st.checkbox("완료됨" if is_completed else "완료하기", value=is_completed, key=f"task_check_{task_id}"):
                if not is_completed:  # 처음 체크했을 때만 축하 애니메이션
                    st.success('태스크를 완료했습니다! 환상합니다! 🎉')
                    toggle_task_completion(task_id)
                    st.rerun()
    
    st.markdown("---")
    
    # 로드맵 탭 - 두 가지 뷰
    roadmap_tabs = st.tabs(["📜 기본 로드맵", "📋 내가 추가한 계획"])
    
    with roadmap_tabs[0]:
        st.markdown("#### 📓 사주 기반 성장 로드맵")
        
        if st.session_state.get('roadmap'):
            st.markdown(st.session_state['roadmap'])
        else:
            with st.spinner("로드맵 생성 중..."):
                roadmap = generate_saju_insight(st.session_state['user_info'])
                st.session_state['roadmap'] = roadmap
                st.markdown(roadmap)
        
        if st.button("로드맵 다시 생성하기", key="regenerate_roadmap"):
            with st.spinner("로드맵 재생성 중..."):
                roadmap = generate_saju_insight(st.session_state['user_info'])
                st.session_state['roadmap'] = roadmap
                st.rerun()
    
    with roadmap_tabs[1]:
        st.markdown("#### 📅 내가 추가한 계획")
        
        if not st.session_state.get('roadmap_items', []):
            # 빈 상태 안내
            st.markdown("""
            <div class='empty-state'>
                <div class='empty-state-icon'>📝</div>
                <h3>추가한 계획이 없습니다</h3>
                <p>고민 상담실에서 '이 계획을 로드맵에 추가' 버튼을 클릭하여 추가해보세요.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 상담실로 이동 버튼
            if st.button("고민 상담실로 이동하기"):
                st.session_state['active_tab'] = 0  # 현재는 구현되지 않았지만, 탭 전환을 위한 예시
                st.rerun()
        else:
            # 카드 형태로 표시
            for idx, item in enumerate(st.session_state['roadmap_items']):
                # 임의의 진행률 계산 (실제 앱에서는 더 복잡한 로직으로 바꿔야 함)
                progress = (idx * 17) % 100 + 10
                if progress > 100:
                    progress = 100
                
                # 날짜 계산
                date_added = item.get('date_added', '2025-05-31')
                days_passed = (datetime.datetime.now() - datetime.datetime.strptime(date_added, "%Y-%m-%d")).days
                
                # 카드 UI
                st.markdown(f"""
                <div class='roadmap-card'>
                    <div class='roadmap-title'>🎯 {item['question'][:30]}{'...' if len(item['question']) > 30 else ''}</div>
                    <div class='roadmap-progress'>
                        <div class='roadmap-progress-bar' style='width: {progress}%;'></div>
                    </div>
                    <div class='roadmap-meta'>
                        <span>진행률 {progress}%</span>
                        <span>📅 Day {days_passed}/21</span>
                    </div>
                    <div class='roadmap-task'>
                        <input type='checkbox' class='roadmap-checkbox' id='roadmap_task_{idx}'>
                        <label for='roadmap_task_{idx}'>오늘의 태스크: {item['question'][:20]}{'...' if len(item['question']) > 20 else ''}</label>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 삭제 버튼
                if st.button("삭제", key=f"delete_roadmap_{idx}"):
                    st.session_state['roadmap_items'].remove(item)
                    st.rerun()
            
            # 모두 삭제 버튼
            if st.button("모든 계획 삭제", key="clear_roadmap_items"):
                st.session_state['roadmap_items'] = []
                st.rerun()
