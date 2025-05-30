import streamlit as st
import datetime

# 스타일 및 유틸리티 모듈 임포트
from styles.styles import load_styles
from utils.session import initialize_session_state, initialize_gemini_api
from utils.saju import analyze_saju, generate_saju_insight
from components.onboarding import show_onboarding
from components.chat import show_chat_tab
from components.roadmap import show_roadmap_tab

# Requirements.txt:
# streamlit==1.32.0
# google-generativeai==0.3.1
# python-dotenv==1.0.0

# Page configuration
st.set_page_config(
    page_title="사주기반 멘토",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 스타일 로드
load_styles()

# 세션 상태 초기화
initialize_session_state()

# Gemini API 초기화
gemini_model = initialize_gemini_api()


def show_main_screen():
    """메인 화면을 표시합니다."""
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # 상단 헤더
    col1, col2, col3 = st.columns([2,1,1])
    
    with col1:
        st.markdown(f"### 안녕하세요, {st.session_state['user_info']['name']}님! ✨")
        st.caption(f"당신의 사주: {st.session_state['user_info'].get('core_traits', '분석 중...')}")
    
    with col3:
        if st.button("처음으로", key="reset_button"):
            # 세션 스테이트 초기화
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # 사주 분석 결과 expander
    with st.expander("📜 내 사주 자세히 보기"):
        st.markdown("### 📊 사주 분석 결과")
        st.markdown(st.session_state['user_info'].get('saju_analysis', '분석 결과가 없습니다.'))
    
    # 세션 상태에 탭 인덱스가 없으면 초기화
    if 'active_tab' not in st.session_state:
        st.session_state['active_tab'] = 0
    
    # 탭 구성 - 활성화된 탭 번호 지정
    tabs = st.tabs(["🔮 고민 상담실", "🗺️ 나의 7일 계획"])
    
    # 채팅 탭
    with tabs[0]:
        show_chat_tab()
    
    # 로드맵 탭
    with tabs[1]:
        show_roadmap_tab()
        
    # 자동 탭 선택 (JavaScript 사용)
    if st.session_state['active_tab'] > 0:
        js = f"""
        <script>
            window.parent.document.querySelectorAll('.stTabs button[role="tab"]')[{st.session_state['active_tab']}].click();
        </script>
        """
        st.components.v1.html(js, height=0, width=0)
    
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    """애플리케이션의 메인 실행 함수"""
    if not st.session_state.get('onboarding_complete', False):
        show_onboarding()
    else:
        show_main_screen()


if __name__ == "__main__":
    main()
