"""
온보딩 화면 컴포넌트

Export 형태:
- from components.onboarding import show_onboarding
- 또는 import components.onboarding as onboarding 후 onboarding.show_onboarding() 형태로 사용
"""
import datetime
import streamlit as st
from utils.saju import analyze_saju, generate_saju_insight

def show_onboarding():
    """온보딩 화면을 표시합니다."""
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.markdown("# ✨ 사주기반 코칭")
    st.markdown("### AI가 당신의 사주를 읽고, 맞춤형 성장법을 제시합니다")
    
    with st.form("onboarding_form"):
        name = st.text_input("이름", placeholder="홍길동")
        birthdate = st.date_input(
            "생년월일", 
            value=datetime.date(1990, 1, 1),
            min_value=datetime.date(1920, 1, 1),
            max_value=datetime.date.today()
        )
        
        birth_hour_options = [
            "23-01시", "01-03시", "03-05시", "05-07시", 
            "07-09시", "09-11시", "11-13시", "13-15시",
            "15-17시", "17-19시", "19-21시", "21-23시",
            "모름"
        ]
        birth_hour = st.selectbox("태어난 시간", options=birth_hour_options, index=len(birth_hour_options)-1)
        
        submit_button = st.form_submit_button("✨ 시작하기")
        
        if submit_button:
            if not name:
                st.error("이름을 입력해주세요.")
            else:
                # 로딩 애니메이션
                with st.spinner("당신의 사주를 분석하고 있어요..."):
                    # 사용자 정보 저장
                    st.session_state['user_info'] = {
                        'name': name,
                        'birthdate': birthdate,
                        'birth_hour': birth_hour
                    }
                    
                    # 사주 분석 수행
                    analysis_result = analyze_saju(name, birthdate, birth_hour)
                    
                    # 분석 결과 저장
                    st.session_state['user_info']['saju_analysis'] = analysis_result['full_analysis']
                    st.session_state['user_info']['core_traits'] = analysis_result['core_traits']
                    
                    # 최초 로드맵 생성
                    roadmap = generate_saju_insight(st.session_state['user_info'])
                    st.session_state['roadmap'] = roadmap
                
                st.session_state['onboarding_complete'] = True
                st.rerun()
    
    # 서비스 설명 섹션
    st.markdown("---")
    st.markdown("### 사주기반 코칭이 당신에게 제공하는 가치")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🎯 개인 맞춤 고민 상담</h3>
            <p>당신의 사주에 맞는 맞춤형 조언으로 현재 고민을 해결합니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📅 나만의 성장 로드맵</h3>
            <p>개인의 특성과 성향에 맞는 성장 계획을 제안합니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>✨ 사주 기반 코칭</h3>
            <p>동양 철학의 지혜와 현대 코칭을 결합한 새로운 접근법을 경험하세요.</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
