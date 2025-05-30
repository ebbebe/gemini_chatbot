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
        
    # 현재 주간 계획이 없으면 상담실로 이동하라는 안내 표시
    if not st.session_state['weekly_plan']:
        st.markdown("""
        <div style='background-color: #f5f5f5; padding: 20px; border-radius: 10px; text-align: center;'>
            <div style='font-size: 30px; margin-bottom: 10px;'>🔮</div>
            <h3>아직 생성된 7일 계획이 없습니다</h3>
            <p>고민 상담실에서 AI와 대화한 후 '이 고민을 7일 계획으로 생성' 버튼을 클릭하면<br>고민을 해결하기 위한 7일간의 실천 계획을 생성해드립니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 상담실로 이동 버튼
        if st.button("고민 상담실로 이동하기"):
            # 탭 인덱스 설정
            st.session_state['active_tab'] = 0
            
            # JavaScript를 사용한 탭 전환
            js = """
            <script>
                window.parent.document.querySelectorAll('.stTabs button[role="tab"]')[0].click();
            </script>
            """
            st.components.v1.html(js, height=0, width=0)
            st.rerun()
    
    # 7일 계획 표시
    if st.session_state['weekly_plan']:
        # 고민 표시
        st.markdown(f"""<div style='background-color: #f0f7ff; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                    <h4 style='margin-top: 0;'>현재 고민 해결하기</h4>
                    <p><strong>"{st.session_state['current_concern']}"</strong></p>
                    </div>""", unsafe_allow_html=True)
        
        # 추가 설명 표시 (있는 경우에만)
        if st.session_state.get('plan_additional_explanation'):
            st.markdown(f"""<div style='background-color: #fffde7; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                        <h4 style='margin-top: 0;'>계획 가이드</h4>
                        <p>{st.session_state['plan_additional_explanation']}</p>
                        </div>""", unsafe_allow_html=True)
        
        # 디버깅 옵션
        with st.expander("디버깅 정보 (AI 응답 & 파싱 결과)"):
            st.subheader("1. AI 원본 응답:")
            st.code(st.session_state.get('debug_raw_response', '응답이 없습니다.'))
            
            st.subheader("2. 파싱된 계획 (데이터 형태):")
            st.json(st.session_state['weekly_plan'])

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
