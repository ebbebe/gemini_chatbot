import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json
import time

# 페이지 설정
st.set_page_config(
    page_title="나만의 프롬프트 기반 Gemini 챗봇",
    page_icon="🤖",
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
    .role-info {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 10px 15px;
        margin-bottom: 20px;
        border: 1px solid #3a3a3a;
        font-weight: bold;
    }
    .current-role-display {
        background-color: #475063;
        border-radius: 8px;
        padding: 10px 15px;
        margin: 5px 0 15px 0;
        font-size: 0.9em;
    }
    .app-title {
        text-align: center;
        padding: 20px 0;
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

# 사전 정의된 역할 목록 (제거)

# 세션 상태 초기화
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "role" not in st.session_state:
        st.session_state.role = ""
    
    if "role_confirmed" not in st.session_state:
        st.session_state.role_confirmed = False
    
    if "model" not in st.session_state:
        st.session_state.model = None
        
    if "thinking" not in st.session_state:
        st.session_state.thinking = False
        
    if "role_set_success" not in st.session_state:
        st.session_state.role_set_success = False
        
    if "error_message" not in st.session_state:
        st.session_state.error_message = None

# 역할 설정 기능 (사이드바에 구현)
def sidebar_role_setting():
    st.sidebar.title("🎭 역할 설정")
    
    role_input = st.sidebar.text_area(
        "AI의 역할을 입력하세요:",
        placeholder="예: '넌 여행 전문가야' 또는 '심리상담사처럼 대답해줘'",
        height=150
    )
    
    if st.sidebar.button("프롬프트 적용"):
        if role_input.strip():
            # 역할 설정 및 대화 초기화
            st.session_state.role = role_input.strip()
            st.session_state.messages = []
            
            # 모델 초기화
            if st.session_state.model is None:
                st.session_state.model = initialize_genai()
            
            # 역할 확인 상태 변경
            st.session_state.role_confirmed = True
            st.session_state.role_set_success = True
            
            # 페이지 리로드
            st.experimental_rerun()
        else:
            st.sidebar.error("역할을 입력해주세요.")
    
    # 현재 역할 표시
    if st.session_state.role_confirmed and st.session_state.role:
        st.sidebar.markdown("### 📝 현재 역할")
        st.sidebar.markdown(
            f"<div class='current-role-display'>{st.session_state.role}</div>", 
            unsafe_allow_html=True
        )

# 역할 확인 메시지 표시
def show_role_confirmation():
    if st.session_state.role_set_success:
        st.markdown(
            f"<div class='success-message'>역할이 성공적으로 설정되었습니다!</div>",
            unsafe_allow_html=True
        )
        # 3초 후에 메시지 숨기기
        time.sleep(0.1)  # 아주 짧은 지연
        st.session_state.role_set_success = False

# 첫 인사 메시지 생성
def generate_greeting():
    if st.session_state.role_confirmed and st.session_state.role and len(st.session_state.messages) == 0:
        try:
            # 시스템 메시지 추가
            system_message = {
                "role": "system",
                "content": st.session_state.role
            }
            
            # AI의 첫 인사 생성
            st.session_state.thinking = True
            
            response = st.session_state.model.generate_content(
                f"""당신에게 다음과 같은 역할이 주어졌습니다: 
                
                {st.session_state.role}
                
                이 역할에 맞게 자신을 간단히 소개하고 사용자에게 첫 인사를 건네주세요. 
                답변은 200자 이내로 간결하게 작성해주세요."""
            )
            
            greeting = response.text
            
            # 대화 히스토리에 시스템 메시지와 AI 첫 인사 추가
            st.session_state.messages = [
                system_message,
                {"role": "assistant", "content": greeting}
            ]
            
            st.session_state.thinking = False
            
        except Exception as e:
            st.session_state.error_message = f"답변 생성 중 오류가 발생했습니다: {str(e)}"
            st.session_state.thinking = False

# 메시지 표시 기능
def display_messages():
    if len(st.session_state.messages) > 0:
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] != "system":
                if msg["role"] == "user":
                    st.markdown(
                        f"<div class='chat-message user'>"
                        f"<div class='avatar'>"
                        f"<img src='https://api.dicebear.com/7.x/personas/svg?seed=user' alt='User Avatar'>"
                        f"</div>"
                        f"<div class='message'>{msg['content']}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                else:  # assistant
                    st.markdown(
                        f"<div class='chat-message assistant'>"
                        f"<div class='avatar'>"
                        f"<img src='https://api.dicebear.com/7.x/bottts/svg?seed=assistant' alt='AI Avatar'>"
                        f"</div>"
                        f"<div class='message'>{msg['content']}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
    
    # 생각 중 표시
    if st.session_state.thinking:
        st.markdown(
            "<div class='thinking'>AI가 응답을 생성하는 중입니다...</div>",
            unsafe_allow_html=True
        )

# 대화 기능
def chat_interface():
    # 현재 역할 표시
    if st.session_state.role:
        st.markdown(
            f"<div class='role-info'>현재 역할: {st.session_state.role}</div>",
            unsafe_allow_html=True
        )
    
    # 오류 메시지 표시
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        st.session_state.error_message = None
    
    # 메시지 표시
    display_messages()
    
    # 메시지 입력 폼
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area("메시지를 입력하세요:", key="user_input", height=100)
        submit_message = st.form_submit_button("전송")
        
        if submit_message and user_input.strip():
            # 사용자 메시지 추가
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # AI 응답 생성 (비동기적으로 처리)
            st.session_state.thinking = True
            st.experimental_rerun()  # 생각 중 표시를 보여주기 위한 리로드
    
    # 생각 중 상태인 경우 응답 생성
    if st.session_state.thinking and len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
        try:
            # 프롬프트 구성
            prompt = f"""
            # 역할 설정
            {st.session_state.role}
            
            # 대화 내용
            """
            
            for msg in st.session_state.messages:
                if msg["role"] == "system":
                    continue  # 시스템 메시지는 이미 위에 포함됨
                elif msg["role"] == "user":
                    prompt += f"\n사용자: {msg['content']}\n"
                else:
                    prompt += f"\nAI: {msg['content']}\n"
            
            prompt += "\nAI: "
            
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
            st.experimental_rerun()

# 대화 초기화 기능
def reset_conversation():
    if st.sidebar.button("대화 초기화"):
        st.session_state.messages = []
        st.session_state.role_confirmed = False
        st.experimental_rerun()

# 역할 변경 기능
def change_role():
    if st.sidebar.button("역할 변경"):
        st.session_state.role_confirmed = False
        st.session_state.messages = []
        st.experimental_rerun()

# 대화 내보내기 기능
def export_conversation():
    if st.sidebar.button("대화 내보내기"):
        if len(st.session_state.messages) > 0:
            export_data = {
                "role": st.session_state.role,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "messages": [msg for msg in st.session_state.messages if msg["role"] != "system"]
            }
            
            # JSON으로 변환
            json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
            
            # 다운로드 링크 생성
            st.sidebar.download_button(
                label="JSON 파일 다운로드",
                data=json_data,
                file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        else:
            st.sidebar.warning("내보낼 대화가 없습니다.")

# 역할 설정 페이지
def set_role():
    st.title("🤖 나만의 프롬프트 기반 Gemini 챗봇")
    st.markdown(
        "<div class='app-description'>이 챗봇은 사용자가 정한 역할에 따라 문맥을 기억하고 대화합니다.</div>",
        unsafe_allow_html=True
    )
    
    # 역할 설정 폼
    with st.form(key="role_form"):
        role_input = st.text_area(
            "AI의 역할을 입력하세요:",
            placeholder="예: '넌 여행 전문가야' 또는 '심리상담사처럼 대답해줘'",
            height=150
        )
        submit_role = st.form_submit_button("역할 설정하기")
        
        if submit_role:
            if role_input.strip():
                st.session_state.role = role_input.strip()
                st.session_state.role_confirmed = True
                st.session_state.role_set_success = True
                
                # 모델 초기화
                if st.session_state.model is None:
                    st.session_state.model = initialize_genai()
                
                # 페이지 리로드
                st.experimental_rerun()
            else:
                st.error("역할을 입력해주세요.")

# 역할 확인 페이지
def confirm_role():
    st.title("🤖 역할 확인")
    
    st.markdown("### 설정한 역할:")
    st.info(st.session_state.role)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("확인", use_container_width=True):
            st.session_state.role_confirmed = True
            st.session_state.role_set_success = True
            
            # 모델 초기화
            if st.session_state.model is None:
                st.session_state.model = initialize_genai()
                
            # 페이지 리로드
            st.experimental_rerun()
    
    with col2:
        if st.button("취소", use_container_width=True):
            st.session_state.role = ""
            st.experimental_rerun()

# 메인 앱
def main():
    # 세션 상태 초기화
    init_session_state()
    
    # 사이드바
    with st.sidebar:
        st.title("🤖 Gemini 역할 챗봇")
        st.markdown("---")
        
        # 역할 설정 (역할이 확인되지 않은 경우)
        if not st.session_state.role_confirmed:
            sidebar_role_setting()
        
        # 현재 설정된 역할 표시 (역할이 확인된 경우)
        if st.session_state.role_confirmed and st.session_state.role:
            st.markdown("### 📝 현재 역할")
            st.info(st.session_state.role[:100] + "..." if len(st.session_state.role) > 100 else st.session_state.role)
            st.markdown("---")
        
        # 대화 제어 기능
        if st.session_state.role_confirmed:
            st.markdown("### ⚙️ 대화 제어")
            change_role()
            reset_conversation()
            export_conversation()
        
        # 앱 정보
        st.markdown("---")
        st.markdown("### ℹ️ 앱 정보")
        st.markdown("""
        - **모델**: Gemini 1.5 Flash
        - **기능**: 사용자 정의 역할 기반 AI 챗봇
        - **개발**: Streamlit + Google Generative AI
        """)
    
    # 메인 화면
    if not st.session_state.role_confirmed:
        if not st.session_state.role:
            set_role()
        else:
            confirm_role()
    else:
        # 첫 인사 생성
        generate_greeting()
        # 역할 확인 메시지 표시
        show_role_confirmation()
        # 채팅 인터페이스 표시
        chat_interface()

if __name__ == "__main__":
    main()