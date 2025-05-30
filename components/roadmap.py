"""
주간 계획 및 로드맵 인터페이스 컴포넌트

사용자의 고민을 7일간의 실천 계획으로 변환하여 표시합니다.

Export 형태:
- from components.roadmap import show_roadmap_tab
- 또는 import components.roadmap as roadmap 후 roadmap.show_roadmap_tab() 형태로 사용
"""
import datetime
import re
import streamlit as st
from utils.saju import generate_saju_insight, generate_weekly_plan
from utils.calendar import (
    get_date_tasks, add_task_to_date, toggle_task_completion,
    get_tasks_stats, format_date, parse_date
)

def show_roadmap_tab():
    """주간 계획 및 로드맵 탭 UI를 표시합니다."""
    st.markdown("### 🗺️ 7일 실천 계획")
    st.markdown("당신의 사주를 기반으로 7일간의 맞춤형 실천 계획을 제안합니다.")
    
    # 고민 입력 및 계획 생성
    if 'weekly_plan' not in st.session_state:
        st.session_state['weekly_plan'] = []
        
    if 'current_concern' not in st.session_state:
        st.session_state['current_concern'] = ""
        
    # 현재 주간 계획이 없으면 입력 폼 표시
    if not st.session_state['weekly_plan']:
        st.markdown("#### 😌 지금 가장 해결하고 싶은 고민이 무엇인가요?")
    
    # 고민 입력 폼 추가
    if not st.session_state['weekly_plan']:
        with st.form(key="concern_form"):
            concern = st.text_area("고민을 입력해주세요", 
                                 value=st.session_state['current_concern'],
                                 height=100,
                                 placeholder="예: 직장에서 엄청한 스트레스를 받고 있어요. 어떻게 해결해야 할까요?")
            
            st.markdown("※ 고민을 입력하면 사주를 기반으로 7일간의 실천 계획을 제안해드립니다.")
            submit_button = st.form_submit_button("계획 생성하기")
            
            if submit_button and concern.strip():
                st.session_state['current_concern'] = concern
                with st.spinner("맞춤형 7일 계획을 생성하고 있습니다..."):
                    # AI를 통해 7일 계획 생성
                    weekly_plan = generate_weekly_plan(st.session_state['user_info'], concern)
                    st.session_state['weekly_plan'] = weekly_plan
                    
                    # 태스크도 추가
                    current_date = datetime.datetime.now().date()
                    for i, plan in enumerate(weekly_plan):
                        task_date = current_date + datetime.timedelta(days=i)
                        task_id = f"{task_date.strftime('%Y-%m-%d')}_plan_{i}"
                        
                        # 태스크 추가
                        add_task_to_date(task_date.strftime('%Y-%m-%d'), {
                            'id': task_id,
                            'title': plan['title'],
                            'description': plan['description'],
                            'completed': False,
                            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                    
                    st.rerun()
    
    # 7일 계획 표시
    if st.session_state['weekly_plan']:
        # 고민 표시
        st.markdown(f"""<div style='background-color: #f0f7ff; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                    <h4 style='margin-top: 0;'>현재 고민 해결하기</h4>
                    <p><strong>"{st.session_state['current_concern']}"</strong></p>
                    </div>""", unsafe_allow_html=True)

        # 통계 카드
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style='background-color: #f5f5f5; padding: 15px; border-radius: 10px; text-align: center;'>
                <h2 style='margin:0; color: #1e88e5;'>{len([p for p in st.session_state['weekly_plan'] if p.get('completed', False)])}/7</h2>
                <p style='margin:0;'>완료한 활동</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            today = datetime.datetime.now().date()
            start_date = today
            end_date = today + datetime.timedelta(days=6)
            st.markdown(f"""
            <div style='background-color: #f5f5f5; padding: 15px; border-radius: 10px; text-align: center;'>
                <h3 style='margin:0; color: #43a047;'>{start_date.strftime('%m.%d')} - {end_date.strftime('%m.%d')}</h3>
                <p style='margin:0;'>실천 기간</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # 오늘이 7일 중 몇일째인지 계산
            days_passed = min(7, (datetime.datetime.now().date() - datetime.datetime.now().date()).days + 1)
            progress = int((days_passed / 7) * 100)
            st.markdown(f"""
            <div style='background-color: #f5f5f5; padding: 15px; border-radius: 10px; text-align: center;'>
                <h2 style='margin:0; color: #e53935;'>{progress}%</h2>
                <p style='margin:0;'>진행률</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 7일 계획 표시
        st.markdown("### 일주일 실천 계획")
        
        # 다시 생성 버튼
        if st.button("다른 계획 생성하기"):
            st.session_state['weekly_plan'] = []
            st.session_state['current_concern'] = ""
            st.rerun()
        
        # 각 날짜별 활동 표시
        today = datetime.datetime.now().date()
        for i, plan in enumerate(st.session_state['weekly_plan']):
            plan_date = today + datetime.timedelta(days=i)
            date_str = plan_date.strftime("%Y-%m-%d")
            is_today = plan_date == today
            is_future = plan_date > today
            
            # 날짜에 해당하는 태스크 가져오기
            date_tasks = get_date_tasks(date_str)
            task_id = f"{date_str}_plan_{i}" if date_tasks else None
            task = None
            
            # 해당 ID의 태스크 찾기
            if task_id and date_tasks:
                for t in date_tasks:
                    if t.get('id') == task_id:
                        task = t
                        break
            
            # 완료 상태 가져오기
            is_completed = task and task.get('completed', False)
            
            # 스타일 설정
            bg_color = "#e8f5e9" if is_completed else "#fff8e1" if is_today else "#f5f5f5" if is_future else "#ffffff"
            border_color = "#2e7d32" if is_completed else "#fb8c00" if is_today else "#bdbdbd"
            
            # 카드 UI
            st.markdown(f"""
            <div style='background-color: {bg_color}; border-left: 5px solid {border_color}; padding: 15px; border-radius: 5px; margin-bottom: 10px;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <h4 style='margin: 0; color: #333;'>Day {i+1}: {plan_date.strftime('%m월 %d일')} ({['월','화','수','목','금','토','일'][plan_date.weekday()]})</h4>
                        <h3 style='margin: 5px 0; color: {'#2e7d32' if is_completed else '#333'};'>{plan['title']}</h3>
                        <p style='margin: 0;'>{plan['description']}</p>
                    </div>
                    <div>
                        {'✅' if is_completed else '⏳' if is_today else '▶️' if is_future else '⏹️'}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 오늘 할일이면 완료 버튼 표시
            if is_today and not is_completed and task_id:
                if st.button(f"활동 완료 표시", key=f"complete_task_{task_id}"):
                    toggle_task_completion(task_id)
                    plan['completed'] = True
                    st.success('오늘의 활동을 완료했습니다! 환상합니다! 🎉')
                    st.rerun()
                    
    st.markdown("---")
    
    st.markdown("### 📜 사주 기반 성장 인사이트")
    
    if st.session_state.get('roadmap'):
        st.markdown(st.session_state['roadmap'])
    else:
        with st.spinner("인사이트 생성 중..."):
            roadmap = generate_saju_insight(st.session_state['user_info'])
            st.session_state['roadmap'] = roadmap
            st.markdown(roadmap)
    
    if st.button("새로운 인사이트 생성하기", key="regenerate_insight"):
        with st.spinner("인사이트 재생성 중..."):
            roadmap = generate_saju_insight(st.session_state['user_info'])
            st.session_state['roadmap'] = roadmap
            st.rerun()
    
    # 고민 기록 관리
    st.markdown("---")
    st.markdown("### 📋 나의 고민 기록")
    
    # 이전 고민 기록 저장
    if 'previous_concerns' not in st.session_state:
        st.session_state['previous_concerns'] = []
    
    # 새 고민이 추가되면 기록에 추가
    if st.session_state['weekly_plan'] and st.session_state['current_concern']:
        # 현재 고민이 이미 저장되어 있는지 확인
        existing_concern = next((c for c in st.session_state['previous_concerns'] 
                               if c['concern'] == st.session_state['current_concern']), None)
        
        # 새 고민이면 추가
        if not existing_concern and len(st.session_state['current_concern']) > 0:
            st.session_state['previous_concerns'].append({
                'concern': st.session_state['current_concern'],
                'created_at': datetime.datetime.now().strftime('%Y-%m-%d')
            })
    
    if not st.session_state.get('previous_concerns', []):
        # 이전 고민이 없을 때 표시할 내용
        st.markdown("""
        <div style='background-color: #f5f5f5; padding: 20px; border-radius: 10px; text-align: center;'>
            <div style='font-size: 30px; margin-bottom: 10px;'>📝</div>
            <h3>이전 고민 기록이 없습니다</h3>
            <p>새로운 고민을 추가하여 7일 계획을 세워보세요.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 이전 고민 목록 표시
        for idx, concern in enumerate(st.session_state.get('previous_concerns', [])):
            created_date = concern.get('created_at', datetime.datetime.now().strftime('%Y-%m-%d'))
            days_ago = (datetime.datetime.now().date() - datetime.datetime.strptime(created_date, "%Y-%m-%d").date()).days
            
            st.markdown(f"""
            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 10px;'>
                <div style='display: flex; justify-content: space-between;'>
                    <div>
                        <h4 style='margin: 0;'>고민: {concern['concern'][:40]}{'...' if len(concern['concern']) > 40 else ''}</h4>
                        <p style='margin: 5px 0; color: #666;'>생성일: {created_date} ({days_ago}일 전)</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 다시 보기 버튼
            if st.button("다시 실천하기", key=f"view_concern_{idx}"):
                st.session_state['current_concern'] = concern['concern']
                # 주간 계획 다시 생성
                with st.spinner("주간 계획 생성 중..."):
                    weekly_plan = generate_weekly_plan(st.session_state['user_info'], concern['concern'])
                    st.session_state['weekly_plan'] = weekly_plan
                    st.rerun()
            
            # 삭제 버튼
            if st.button("삭제", key=f"delete_concern_{idx}"):
                st.session_state['previous_concerns'].pop(idx)
                st.rerun()
        
        # 모두 삭제 버튼
        if st.button("모든 고민 기록 삭제", key="clear_all_concerns"):
            st.session_state['previous_concerns'] = []
            st.rerun()
