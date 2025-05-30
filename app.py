import streamlit as st
import google.generativeai as genai
import os
import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from datetime import datetime
import time
import base64
import tempfile
import platform
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import streamlit as st

# 한글 폰트 설정
def setup_korean_fonts():
    system_name = platform.system()
    
    if system_name == "Windows":
        # Windows 기본 폰트
        font_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'malgun.ttf')
        font_name = 'Malgun Gothic'
    elif system_name == "Darwin":  # macOS
        font_path = '/System/Library/Fonts/AppleSDGothicNeo.ttc'
        font_name = 'AppleSDGothicNeo'
    else:  # Linux 등
        font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
        font_name = 'NanumGothic'
        
    # 폰트 파일 존재 확인
    if not os.path.exists(font_path):
        # 대체 폰트 시도
        if system_name == "Windows":
            alt_fonts = ['batang.ttc', 'gulim.ttc', 'dotum.ttc']
            for alt in alt_fonts:
                alt_path = os.path.join(os.environ['WINDIR'], 'Fonts', alt)
                if os.path.exists(alt_path):
                    font_path = alt_path
                    font_name = alt.split('.')[0].capitalize()
                    break
    
    return font_path, font_name

# 한글 폰트 설정 시도
try:
    font_path, font_name = setup_korean_fonts()
    
    # Matplotlib 폰트 설정
    plt.rcParams['font.family'] = font_name
    
    # ReportLab 폰트 설정
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('KoreanFont', font_path))
    
except Exception as e:
    print(f"한글 폰트 설정 오류: {str(e)}")
    # 기본 설정 유지

# 환경변수 설정 방법
# 1. Streamlit Cloud: Streamlit 대시보드에서 'Secrets' 메뉴에 GOOGLE_API_KEY 추가
# 2. 로컬 개발: .streamlit/secrets.toml 파일에 GOOGLE_API_KEY="your-api-key" 추가

# 페이지 설정
st.set_page_config(
    page_title="나다움: 사주 기반 AI 라이프코칭",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 추가
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
    }
    .chat-message.user {
        background-color: #475063;
        margin-left: 15%;
        border-bottom-right-radius: 0.2rem;
    }
    .chat-message.assistant {
        background-color: #2b313e;
        margin-right: 15%;
        border-bottom-left-radius: 0.2rem;
    }
    .chat-message .avatar {
        width: 15%;
    }
    .chat-message .avatar img {
        max-width: 50px;
        max-height: 50px;
        border-radius: 50%;
        object-fit: cover;
    }
    .chat-message .message {
        width: 85%;
        padding: 0 1.5rem;
    }
    .stTextInput input {
        border-radius: 10px;
    }
    .css-1cpxqw2 {
        width: 100%;
        padding: 1rem;
    }
    .feature-card {
        background-color: #475063;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .feature-title {
        font-weight: bold;
        margin-bottom: 10px;
        font-size: 1.2em;
    }
    .feature-description {
        font-size: 0.9em;
    }
    .element-card {
        background-color: #2b313e;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 5px solid;
    }
    .wood-card {
        border-left-color: #4CAF50;
    }
    .fire-card {
        border-left-color: #FF5722;
    }
    .earth-card {
        border-left-color: #FFC107;
    }
    .metal-card {
        border-left-color: #9E9E9E;
    }
    .water-card {
        border-left-color: #2196F3;
    }
    .app-title {
        text-align: center;
        padding: 20px 0;
        font-size: 2.5em;
        font-weight: bold;
        color: white;
    }
    .app-description {
        text-align: center;
        font-size: 1.1em;
        margin-bottom: 30px;
        color: #c2c2c2;
    }
    .success-message {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        animation: fadeOut 5s forwards;
    }
    @keyframes fadeOut {
        0% {opacity: 1;}
        70% {opacity: 1;}
        100% {opacity: 0;}
    }
    div[data-testid="stSidebarUserContent"] {
        padding-top: 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
    }
    div.stTextArea textarea {
        min-height: 100px;
    }
    .thinking {
        font-style: italic;
        color: #cccccc;
        margin: 10px 0;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% {opacity: 0.6;}
        50% {opacity: 1;}
        100% {opacity: 0.6;}
    }
    .characteristic-card {
        background-color: #2b313e;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #4CAF50;
    }
    .chart-container {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .tab-content {
        padding: 20px 0;
    }
    .like-button {
        background-color: #FF5722;
        color: white;
        border: none;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.9em;
        margin-top: 10px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    .manual-section {
        margin-bottom: 30px;
    }
    .manual-section h4 {
        border-bottom: 1px solid #3a3a3a;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Gemini API 설정
def initialize_genai():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"API 키가 설정되지 않았거나 연결에 문제가 있습니다: {str(e)}")
        return None

# 세션 상태 초기화
def init_session_state():
    # 사용자 정보 관련 세션 상태
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    
    if "birth_year" not in st.session_state:
        st.session_state.birth_year = None
    
    if "birth_month" not in st.session_state:
        st.session_state.birth_month = None
    
    if "birth_day" not in st.session_state:
        st.session_state.birth_day = None
    
    if "birth_hour" not in st.session_state:
        st.session_state.birth_hour = None
        
    if "birth_minute" not in st.session_state:
        st.session_state.birth_minute = None
        
    if "calendar_type" not in st.session_state:
        st.session_state.calendar_type = "양력"
    
    if "saju_analyzed" not in st.session_state:
        st.session_state.saju_analyzed = False
    
    # 사주 분석 결과 관련 세션 상태
    if "saju_result" not in st.session_state:
        st.session_state.saju_result = {}
    
    if "element_distribution" not in st.session_state:
        st.session_state.element_distribution = {}
    
    if "characteristics" not in st.session_state:
        st.session_state.characteristics = []
    
    if "like_count" not in st.session_state:
        st.session_state.like_count = 0
    
    # 채팅 관련 세션 상태
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "model" not in st.session_state:
        st.session_state.model = None
    
    if "thinking" not in st.session_state:
        st.session_state.thinking = False
    
    if "error_message" not in st.session_state:
        st.session_state.error_message = None

# 사이드바 사용자 정보 입력
def sidebar_user_info():
    st.sidebar.title("✨ 나다움: 사주 기반 AI 라이프코칭")
    st.sidebar.markdown("---")
    
    # 사용자 정보 입력 폼
    st.sidebar.subheader("👤 사용자 정보")
    
    # 이름 입력
    user_name = st.sidebar.text_input(
        "이름", 
        value=st.session_state.user_name,
        placeholder="이름을 입력해주세요",
        key="sidebar_user_name_input")
    
    if user_name:
        st.session_state.user_name = user_name
    
    # 양력/음력 선택
    calendar_type = st.sidebar.radio(
        "생년월일 유형",
        options=["양력", "음력"],
        index=0 if st.session_state.calendar_type == "양력" else 1,
        key="sidebar_calendar_type"
    )
    st.session_state.calendar_type = calendar_type
    
    # 생년월일시 입력 (셀렉트박스 사용)
    col1, col2 = st.sidebar.columns(2)
    
    # 연도 선택
    years = list(range(1950, 2026))
    with col1:
        birth_year = st.selectbox(
            "출생년도", 
            options=years,
            index=years.index(1990) if st.session_state.birth_year is None else years.index(st.session_state.birth_year),
            key="sidebar_birth_year"
        )
    
    # 월 선택
    months = list(range(1, 13))
    with col2:
        birth_month = st.selectbox(
            "출생월", 
            options=months,
            index=0 if st.session_state.birth_month is None else months.index(st.session_state.birth_month),
            key="sidebar_birth_month"
        )
    
    # 일 선택
    days = list(range(1, 32))  # 간단히 1~31일로 설정
    with col1:
        birth_day = st.selectbox(
            "출생일", 
            options=days,
            index=0 if st.session_state.birth_day is None else days.index(st.session_state.birth_day),
            key="sidebar_birth_day"
        )
    
    # 시간 선택 (시/분 선택)
    with col2:
        # 시 선택 (0-23시)
        hours = list(range(24))
        birth_hour = st.selectbox(
            "출생시", 
            options=hours,
            index=0 if st.session_state.birth_hour is None else st.session_state.birth_hour,
            key="sidebar_birth_hour"
        )
    
    # 분 선택 (0-59분)
    with col1:
        minutes = list(range(60))
        birth_minute = st.selectbox(
            "출생분", 
            options=minutes,
            index=0 if st.session_state.birth_minute is None else st.session_state.birth_minute,
            key="sidebar_birth_minute"
        )
    
    # 세션 상태 업데이트
    st.session_state.birth_year = birth_year
    st.session_state.birth_month = birth_month
    st.session_state.birth_day = birth_day
    st.session_state.birth_hour = birth_hour
    st.session_state.birth_minute = birth_minute
    
    st.sidebar.markdown("---")
    
    # 사주 분석 버튼
    analyze_button = st.sidebar.button("🔮 내 사주 분석하기", use_container_width=True, key="sidebar_analyze_button")
    
    if analyze_button:
        if not user_name:
            st.sidebar.error("이름을 입력해주세요.")
            return
        
        # 모델 초기화
        if st.session_state.model is None:
            st.session_state.model = initialize_genai()
        
        # 사주 분석 시작
        with st.sidebar:
            with st.spinner("사주를 분석하고 있습니다..."):
                analyze_saju()
        
        # 분석 완료 표시
        if st.session_state.saju_analyzed:
            st.sidebar.success("사주 분석이 완료되었습니다!")
            st.balloons()
    
    # 분석된 경우 관련 정보 표시
    if st.session_state.saju_analyzed:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📈 오행 분포")
        
        # 오행 분포 표시
        element_names = ["목(목)", "화(화)", "토(토)", "글(글)", "수(수)"]
        element_values = [
            st.session_state.element_distribution.get("목", 0),
            st.session_state.element_distribution.get("화", 0),
            st.session_state.element_distribution.get("토", 0),
            st.session_state.element_distribution.get("글", 0),
            st.session_state.element_distribution.get("수", 0)
        ]
        element_colors = ["#4CAF50", "#FF5722", "#FFC107", "#9E9E9E", "#2196F3"]
        
        fig, ax = plt.subplots(figsize=(3, 2))
        ax.bar(element_names, element_values, color=element_colors)
        ax.set_ylabel('비중')
        ax.set_ylim(0, max(element_values) + 1 if element_values else 1)
        plt.tight_layout()
        
        st.sidebar.pyplot(fig)
        st.sidebar.markdown("---")
        
        # 사용자 링크
        st.sidebar.markdown("👉 [아이콘 출처](https://www.flaticon.com/)")
        st.sidebar.markdown("👉 [개발: 나다움 팀](https://www.nadaum.ai)")

# 사주 분석 함수
def analyze_saju():
    # 사용자 정보 가져오기
    name = st.session_state.user_name
    year = st.session_state.birth_year
    month = st.session_state.birth_month
    day = st.session_state.birth_day
    hour = st.session_state.birth_hour
    minute = st.session_state.birth_minute
    calendar_type = st.session_state.calendar_type
    
    # Gemini에게 사주 분석 요청
    try:
        prompt = f"""
        당신은 한국 사주학 전문가입니다. 다음 정보를 바탕으로 사주를 분석해주세요.
        
        이름: {name}
        양/음력: {calendar_type}
        출생년도: {year}
        출생월: {month}
        출생일: {day}
        출생시간: {hour}시 {minute}분
        
        다음 형식으로 JSON 형태로 결과를 제공해주세요:
        
        1. 사주표: 인명구성 4글자(천간지지)
        2. 오행분포: 오행(목화토글수)의 점수 분포를 숫자로 표시
        3. 핵심특성: 사주에서 도출할 수 있는 3가지 핵심 특성
        4. 강점: 사주상 강점을 3가지 나열
        5. 약점: 사주상 약점을 3가지 나열
        6. 커뮤니케이션스타일: 사주 기반으로 적합한 커뮤니케이션 방식 3가지
        7. 스트레스해소법: 사주 기반으로 적합한 스트레스 해소법 3가지
        
        오행분포는 0~10 사이의 숫자로 표현해주세요. 각 오행의 총합은 중요하지 않으나, 상대적인 값을 비교할 수 있어야 합니다.
        """
        
        # Gemini API 호출
        response = st.session_state.model.generate_content(prompt)
        
        # JSON 파싱
        try:
            saju_result = json.loads(response.text)
        except json.JSONDecodeError:
            # 응답이 JSON 형식이 아닌 경우, 추출 시도
            import re
            json_str = re.search(r'\{[\s\S]*\}', response.text)
            if json_str:
                saju_result = json.loads(json_str.group(0))
            else:
                # 백업 데이터 사용
                saju_result = {
                    "사주표": {"천간": "경인", "지지": "사지묘오"},
                    "오행분포": {"목": 3, "화": 2, "토": 4, "글": 1, "수": 5},
                    "핵심특성": ["내면적 타이프", "분석적 사고", "충실한 실행력"],
                    "강점": ["차분한 논리적 사고", "안정적인 직관력", "깨어있는 계획적 생활"],
                    "약점": ["과도한 완벽주의", "위기 회피 성향", "자기 과신"],
                    "커뮤니케이션스타일": ["직접적이지만 온화한 소통", "깊이 있는 1:1 대화", "심사숙고한 결과 전달"],
                    "스트레스해소법": ["자연 속에서 휴식", "가볍게 걸으며 생각하기", "수기를 통한 명상"]
                }
        
        # 세션 상태 저장
        st.session_state.saju_result = saju_result
        st.session_state.element_distribution = saju_result.get("오행분포", {})
        st.session_state.characteristics = saju_result.get("핵심특성", [])
        st.session_state.saju_analyzed = True
        
    except Exception as e:
        st.error(f"사주 분석 중 오류가 발생했습니다: {str(e)}")
        st.session_state.error_message = str(e)

# 탭 1: 내 사주 분석 페이지
def tab_saju_analysis():
    st.header("🔮 내 사주 분석")
    
    if not st.session_state.saju_analyzed:
        st.info("👉 사이드바에서 사용자 정보를 입력한 후 '사주 분석' 버튼을 클릭해주세요.")
        return
    
    # 사주 정보 표시
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📊 오행 분포")
        st.markdown("""
        <div class="chart-container">
            <h4>오행 기운 분포</h4>
        """, unsafe_allow_html=True)
        
        # 오행 분포 차트 생성
        element_names = ["목(목)", "화(화)", "토(토)", "글(글)", "수(수)"]
        element_values = [
            st.session_state.element_distribution.get("목", 0),
            st.session_state.element_distribution.get("화", 0),
            st.session_state.element_distribution.get("토", 0),
            st.session_state.element_distribution.get("글", 0),
            st.session_state.element_distribution.get("수", 0)
        ]
        element_colors = ["#4CAF50", "#FF5722", "#FFC107", "#9E9E9E", "#2196F3"]
        
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(element_names, element_values, color=element_colors)
        
        # 값 표시 추가
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height}',
                    ha='center', va='bottom')
        
        ax.set_ylabel('강도')
        ax.set_ylim(0, max(element_values) + 1 if element_values else 1)
        plt.tight_layout()
        
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # "맞아요!" 버튼
        like_button = st.button("👍 맞아요!", use_container_width=True)
        if like_button:
            st.session_state.like_count += 1
            st.success(f"현재 {st.session_state.like_count}명이 이 분석에 공감했습니다.")
            st.balloons()
    
    with col2:
        st.subheader("🌸 나의 핵심 특성")
        
        # 핵심 특성 카드
        if st.session_state.characteristics:
            for i, characteristic in enumerate(st.session_state.characteristics):
                st.markdown(f"""
                <div class="characteristic-card">
                    <h3>#{i+1}. {characteristic}</h3>
                </div>
                """, unsafe_allow_html=True)
        
        # 사주 해석 결과
        st.subheader("📖 사주 정보")
        
        # 기본 사주 정보
        saju_data = st.session_state.saju_result.get("사주표", {})
        
        # 사주표 데이터 형식 처리
        if isinstance(saju_data, dict):
            # 디셔너리인 경우 get 메소드 사용
            cheongan = saju_data.get('천간', '')
            jiji = saju_data.get('지지', '')
            saju_info = f"{cheongan}, {jiji}"
        elif isinstance(saju_data, str):
            # 문자열인 경우 그대로 표시
            saju_info = saju_data
        else:
            # 기타 형태인 경우 문자열로 변환
            saju_info = str(saju_data)
            
        st.markdown(f"""
        <div class="element-card">
            <strong>천간지지:</strong> {saju_info}
        </div>
        """, unsafe_allow_html=True)

# 탭 2: AI 라이프코칭 페이지
def tab_life_coaching():
    st.header("💬 AI 라이프코칭")
    
    if not st.session_state.saju_analyzed:
        st.info("👉 먼저 사이드바에서 사주를 분석해주세요.")
        return
    
    # 채팅 인터페이스
    st.subheader("나만을 위한 사주 기반 맞춤형 조언")
    st.markdown("👉 당신의 사주와 오행 분포를 이해한 AI가 맞춤형 조언을 제공합니다.")
    
    # 채팅 히스토리 표시
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user">
                <div class="avatar">
                    <img src="https://api.dicebear.com/7.x/personas/svg?seed=user" alt="User Avatar">
                </div>
                <div class="message">{message['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:  # assistant
            st.markdown(f"""
            <div class="chat-message assistant">
                <div class="avatar">
                    <img src="https://api.dicebear.com/7.x/bottts/svg?seed=assistant" alt="AI Avatar">
                </div>
                <div class="message">{message['content']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 생각 중 표시
    if st.session_state.thinking:
        st.markdown("""
        <div class="thinking">AI가 응답을 생성하는 중입니다...</div>
        """, unsafe_allow_html=True)
    
    # 사용자 입력
    user_input = st.text_area("나에 대한 고민을 입력해보세요", height=100)
    
    if st.button("질문하기", use_container_width=True):
        if user_input.strip():
            # 사용자 메시지 추가
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # AI 응답 생성 (비동기적으로 처리)
            st.session_state.thinking = True
            st.experimental_rerun()  # 생각 중 표시를 보여주기 위한 리로드
    
    # 생각 중 상태인 경우 응답 생성
    if st.session_state.thinking and len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
        try:
            # 오행 분포 정보 가져오기
            element_dist = st.session_state.element_distribution
            characteristics = st.session_state.characteristics
            strengths = st.session_state.saju_result.get("강점", [])
            weaknesses = st.session_state.saju_result.get("약점", [])
            
            # 프롬프트 구성
            prompt = f"""
            당신은 사주 기반 라이프코칭 전문가입니다. 다음 사주 정보와 사용자의 질문을 바탕으로 맞춤형 조언을 제공해주세요.
            
            
            # 사용자 사주 정보
            오행 분포: {element_dist}
            핵심 특성: {characteristics}
            강점: {strengths}
            약점: {weaknesses}
            
            # 중요 지침
            1. 일반적인 조언이 아닌, 사주 정보를 기반으로 한 맞춤형 조언을 제공하세요.
            2. 예를 들어, "운동하세요"가 아닌 "수(水) 기운이 강한 당신에게는 요가나 수영이 좋아요"와 같이 구체적인 조언을 제공하세요.
            3. 사주의 오행 분포를 고려하여 각 사람에게 맞는 활동, 직업, 생활방식을 제안하세요.
            4. 공감적이고 따뜻한 톤을 유지하며, 진정성 있는 조언을 제공하세요.
            
            # 사용자 질문
            {st.session_state.messages[-1]['content']}
            """
            
            # 응답 생성
            response = st.session_state.model.generate_content(prompt)
            assistant_response = response.text
            
            # AI 응답 추가
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
            # 생각 중 상태 해제
            st.session_state.thinking = False
            
            # 화면 갱신
            st.experimental_rerun()
            
        except Exception as e:
            st.session_state.error_message = f"답변 생성 중 오류가 발생했습니다: {str(e)}"
            st.session_state.thinking = False
            st.error(st.session_state.error_message)

# 탭 3: 나의 사용설명서 페이지
def tab_user_manual():
    st.header("📖 나의 사용설명서")
    
    if not st.session_state.saju_analyzed:
        st.info("👉 먼저 사이드바에서 사주를 분석해주세요.")
        return
    
    # 사용설명서 내용
    saju_data = st.session_state.saju_result
    
    # 강점 섹션
    st.subheader("💪 강점")
    st.markdown("<div class='manual-section'>", unsafe_allow_html=True)
    strengths = saju_data.get("강점", [])
    for strength in strengths:
        st.markdown(f"- {strength}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 약점 섹션
    st.subheader("🐋 약점")
    st.markdown("<div class='manual-section'>", unsafe_allow_html=True)
    weaknesses = saju_data.get("약점", [])
    for weakness in weaknesses:
        st.markdown(f"- {weakness}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 커뮤니케이션 스타일 섹션
    st.subheader("💬 커뮤니케이션 스타일")
    st.markdown("<div class='manual-section'>", unsafe_allow_html=True)
    comm_styles = saju_data.get("커뮤니케이션스타일", [])
    for style in comm_styles:
        st.markdown(f"- {style}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 스트레스 해소법 섹션
    st.subheader("🌿 스트레스 해소법")
    st.markdown("<div class='manual-section'>", unsafe_allow_html=True)
    stress_relief = saju_data.get("스트레스해소법", [])
    for relief in stress_relief:
        st.markdown(f"- {relief}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # PDF 다운로드 버튼
    if st.button("💾 PDF로 다운로드", use_container_width=True):
        pdf_data = generate_pdf()
        st.download_button(
            label="다운로드 시작",
            data=pdf_data,
            file_name=f"{st.session_state.user_name}_사용설명서.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# PDF 생성 함수
def generate_pdf():
    # PDF 생성
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # 제목
    p.setFont("Helvetica-Bold", 24)
    p.drawString(50, height - 50, f"{st.session_state.user_name}님의 사용설명서")
    
    # 강점
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 100, "강점:")
    p.setFont("Helvetica", 12)
    y = height - 120
    for strength in st.session_state.saju_result.get("강점", []):
        p.drawString(70, y, f"- {strength}")
        y -= 20
    
    # 약점
    y -= 20
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "약점:")
    p.setFont("Helvetica", 12)
    y -= 20
    for weakness in st.session_state.saju_result.get("약점", []):
        p.drawString(70, y, f"- {weakness}")
        y -= 20
    
    # 커뮤니케이션 스타일
    y -= 20
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "커뮤니케이션 스타일:")
    p.setFont("Helvetica", 12)
    y -= 20
    for style in st.session_state.saju_result.get("커뮤니케이션스타일", []):
        p.drawString(70, y, f"- {style}")
        y -= 20
    
    # 스트레스 해소법
    y -= 20
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "스트레스 해소법:")
    p.setFont("Helvetica", 12)
    y -= 20
    for relief in st.session_state.saju_result.get("스트레스해소법", []):
        p.drawString(70, y, f"- {relief}")
        y -= 20
    
    # 날짜 추가
    p.setFont("Helvetica", 10)
    p.drawString(50, 40, f"생성일자: {datetime.now().strftime('%Y-%m-%d')}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer.getvalue()

# 메인 앱
def main():
    # 세션 상태 초기화
    init_session_state()
    
    # 모델 초기화
    if st.session_state.model is None:
        st.session_state.model = initialize_genai()
    
    # 사이드바 구성
    sidebar_user_info()
    
    # 메인 제목
    st.title("✨ 나다움: 사주 기반 AI 라이프코칭")
    st.markdown("""
    <div class="app-description">
        당신의 사주 정보를 분석하여 개성화된 라이프코칭을 제공합니다.
        탭을 선택하여 다양한 서비스를 이용해보세요.
    </div>
    """, unsafe_allow_html=True)
    
    # 오류 메시지 표시
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        st.session_state.error_message = None
    
    # 탭 섹션 구성
    tab1, tab2, tab3 = st.tabs(["🔮 내 사주 분석", "💬 AI 라이프코칭", "📖 나의 사용설명서"])
    
    # 탭 1: 사주 분석
    with tab1:
        tab_saju_analysis()
    
    # 탭 2: AI 라이프코칭
    with tab2:
        tab_life_coaching()
    
    # 탭 3: 나의 사용설명서
    with tab3:
        tab_user_manual()

if __name__ == "__main__":
    main()