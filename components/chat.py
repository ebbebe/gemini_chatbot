"""
채팅 인터페이스 컴포넌트

Export 형태:
- from components.chat import show_chat_tab
- 또는 import components.chat as chat 후 chat.show_chat_tab() 형태로 사용
"""
import datetime
import streamlit as st
from utils.saju import generate_saju_insight

def show_chat_tab():
    """채팅 탭 UI를 표시합니다."""
    st.markdown("### 💬 고민 상담실")
    
    # 세션 상태 초기화
    if 'chat_messages' not in st.session_state:
        st.session_state['chat_messages'] = []
        
    if 'has_initial_greeting' not in st.session_state:
        st.session_state['has_initial_greeting'] = False
    
    # 초기 인사 메시지 추가 (첫 방문 시에만)
    if not st.session_state['has_initial_greeting'] and st.session_state['user_info'].get('core_traits'):
        greeting_message = f"안녕하세요 {st.session_state['user_info']['name']}님! 당신을 위한 AI 코치입니다. 어떤 고민이 있으신가요?"
        st.session_state['chat_messages'].append({
            'role': 'assistant',  # st.chat_message에서는 'ai' 대신 'assistant' 사용
            'content': greeting_message
        })
        st.session_state['has_initial_greeting'] = True
    
    # 채팅 메시지 표시 영역
    chat_container = st.container()
    
    # 메시지 표시 - Streamlit 내장 컴포넌트 사용
    with chat_container:
        # 마지막 AI 메시지를 찾기 위한 변수
        last_ai_msg_idx = -1
        for idx, msg in enumerate(st.session_state['chat_messages']):
            if msg['role'] == 'assistant':
                last_ai_msg_idx = idx
        
        # 메시지 표시
        for idx, msg in enumerate(st.session_state['chat_messages']):
            role = msg['role']
            # st.chat_message 컴포넌트는 'ai' 대신 'assistant' 사용
            with st.chat_message(role if role != 'ai' else 'assistant'):
                st.write(msg['content'])
                
                # 마지막 AI 메시지에만 7일 계획 생성 버튼 표시
                if role == 'assistant' and idx == last_ai_msg_idx and idx > 0:
                    # 이전 메시지가 사용자 메시지인지 확인
                    if st.session_state['chat_messages'][idx-1]['role'] == 'user':
                        if st.button("📅 대화를 요약해서 7일 계획으로 생성", key=f"add_roadmap_{idx}"):
                            from utils.saju import generate_weekly_plan, summarize_conversation
                            
                            with st.spinner("대화 내용을 분석하고 7일 계획을 생성하고 있습니다..."):
                                # 전체 대화 내용을 분석하여 핵심 고민 추출
                                extracted_concern = summarize_conversation(st.session_state['chat_messages'])
                                st.info(f"{extracted_concern}")
                                
                                # 추출된 핵심 고민을 기반으로 7일 계획 생성
                                weekly_plan = generate_weekly_plan(st.session_state['user_info'], extracted_concern)
                                
                                # 새 계획으로 설정
                                st.session_state['weekly_plan'] = weekly_plan
                                st.session_state['current_concern'] = extracted_concern
                                
                                # 태스크 추가
                                current_date = datetime.datetime.now().date()
                                for i, plan in enumerate(weekly_plan):
                                    task_date = current_date + datetime.timedelta(days=i)
                                    task_id = f"{task_date.strftime('%Y-%m-%d')}_plan_{i}"
                                    
                                    # 태스크 추가 (from utils.calendar import add_task_to_date)
                                    from utils.calendar import add_task_to_date
                                    add_task_to_date(task_date.strftime('%Y-%m-%d'), {
                                        'id': task_id,
                                        'title': plan['title'],
                                        'description': plan['description'],
                                        'completed': False,
                                        'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    })
                                
                                # 이전 고민 기록에도 추가 (필요한 경우)
                                if 'previous_concerns' not in st.session_state:
                                    st.session_state['previous_concerns'] = []
                                
                                # 이미 있는 고민인지 확인
                                existing = False
                                for concern in st.session_state['previous_concerns']:
                                    if concern['concern'] == extracted_concern:
                                        existing = True
                                        break
                                        
                                if not existing:
                                    st.session_state['previous_concerns'].append({
                                        'concern': extracted_concern,
                                        'created_at': datetime.datetime.now().strftime('%Y-%m-%d')
                                    })
                            
                            msg['add_to_roadmap'] = True
                            st.success("✓ 7일 계획이 생성되었습니다! '나의 7일 계획' 탭에서 확인해보세요.")
    
    # 빠른 질문 칩 버튼들
    st.markdown('<div class="quick-chips">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    quick_questions = {
        "커리어 고민": "제 적성에 맞는 커리어 방향은 무엇일까요?",
        "인간관계": "인간관계에서 제가 개선해야 할 부분이 있을까요?",
        "자기계발": "제가 집중해서 발전시켜야 할 역량은 무엇인가요?",
        "스트레스 관리": "제 사주를 고려할 때 스트레스를 줄이는 방법은 무엇인가요?"
    }
    
    with col1:
        if st.button("💼 커리어 고민", key="career_chip"):
            st.session_state['chat_messages'].append({
                'role': 'user',
                'content': quick_questions["커리어 고민"]
            })
            
            with st.spinner("답변 생성 중..."):
                response = generate_saju_insight(st.session_state['user_info'], quick_questions["커리어 고민"])
                st.session_state['chat_messages'].append({
                    'role': 'assistant',  # 'ai'에서 'assistant'로 변경
                    'content': response,
                    'add_to_roadmap': False
                })
            
            # 페이지 리렌더링
            st.rerun()
    
    with col2:
        if st.button("👥 인간관계", key="relationship_chip"):
            st.session_state['chat_messages'].append({
                'role': 'user',
                'content': quick_questions["인간관계"]
            })
            
            with st.spinner("답변 생성 중..."):
                response = generate_saju_insight(st.session_state['user_info'], quick_questions["인간관계"])
                st.session_state['chat_messages'].append({
                    'role': 'assistant',  # 'ai'에서 'assistant'로 변경
                    'content': response,
                    'add_to_roadmap': False
                })
            
            # 페이지 리렌더링
            st.rerun()
    
    with col3:
        if st.button("📚 자기계발", key="development_chip"):
            st.session_state['chat_messages'].append({
                'role': 'user',
                'content': quick_questions["자기계발"]
            })
            
            with st.spinner("답변 생성 중..."):
                response = generate_saju_insight(st.session_state['user_info'], quick_questions["자기계발"])
                st.session_state['chat_messages'].append({
                    'role': 'assistant',  # 'ai'에서 'assistant'로 변경
                    'content': response,
                    'add_to_roadmap': False
                })
            
            # 페이지 리렌더링
            st.rerun()
    
    with col4:
        if st.button("🧘 스트레스 관리", key="stress_chip"):
            st.session_state['chat_messages'].append({
                'role': 'user',
                'content': quick_questions["스트레스 관리"]
            })
            
            with st.spinner("답변 생성 중..."):
                response = generate_saju_insight(st.session_state['user_info'], quick_questions["스트레스 관리"])
                st.session_state['chat_messages'].append({
                    'role': 'assistant',  # 'ai'에서 'assistant'로 변경
                    'content': response,
                    'add_to_roadmap': False
                })
            
            # 페이지 리렌더링
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 채팅 입력 사용
    user_question = st.chat_input("질문을 입력하세요...")
    if user_question:
        st.session_state['chat_messages'].append({
            'role': 'user',
            'content': user_question
        })
        
        with st.spinner("답변 생성 중..."):
            response = generate_saju_insight(st.session_state['user_info'], user_question)
            st.session_state['chat_messages'].append({
                'role': 'assistant',  # 'ai'에서 'assistant'로 변경
                'content': response,
                'add_to_roadmap': False
            })
            
            if 'chat_history' not in st.session_state:
                st.session_state['chat_history'] = []
            
            st.session_state['chat_history'].append({
                'question': user_question,
                'answer': response
            })
        
        # 페이지 리렌더링
        st.rerun()
