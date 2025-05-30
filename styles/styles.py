"""
사주기반 코칭 - AI 사주 코치 앱의 스타일 관련 유틸리티 모듈
"""
import streamlit as st

def load_styles():
    """
    앱에 사용되는 CSS 스타일을 로드합니다.
    스타일은 Streamlit의 markdown 함수를 통해 직접 삽입됩니다.
    """
    st.markdown("""
    <style>
        /* Global styles */
        [data-testid="stAppViewContainer"] {
            background-color: #f8f9fa;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #333;
            font-family: 'Pretendard', sans-serif;
        }
        
        /* Main title */
        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        /* Subtitle */
        h3 {
            font-size: 1.2rem;
            font-weight: 400;
            margin-bottom: 2rem;
            color: #666;
        }
        
        /* Feature cards */
        .feature-card {
            background-color: #fff;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        
        .feature-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Buttons */
        .stButton button {
            background-color: #6c5ce7;
            color: white;
            font-weight: 600;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            transition: all 0.3s;
            border: none;
            width: 100%;
        }
        
        .stButton button:hover {
            background-color: #5649c0;
            transform: translateY(-2px);
        }
        
        /* Form inputs */
        [data-testid="stForm"] {
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        
        /* User info box */
        .user-info-box {
            background-color: #f0f0f7;
            border-radius: 8px;
            padding: 10px 15px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #f0f0f7;
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: white;
            border-bottom: 2px solid #6c5ce7;
        }
        
            /* 화면 전환 애니메이션 */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    
        .main-content {
            animation: fadeIn 0.5s ease-in-out;
        }
    
        /* 확장 패널 스타일링 */
        .stExpander {
            border: none;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            border-radius: 8px;
            margin-bottom: 1rem;
        }
    
        /* 캡션 스타일링 */
        [data-testid="caption"] {
            font-style: italic;
            font-weight: 500;
            color: #6c5ce7;
        }
        
        /* 채팅 컨테이너 */
        .chat-container {
            height: 500px;
            overflow-y: auto;
            padding: 10px;
            margin-bottom: 10px;
            background-color: #f5f7f9;
            border-radius: 12px;
            border: 1px solid #e6e6e6;
            display: flex;
            flex-direction: column;
        }
        
        /* 메시지 공통 스타일 */
        .message {
            display: flex;
            margin-bottom: 10px;
        }
        
        /* 사용자 메시지 */
        .user-message {
            justify-content: flex-end;
        }
        
        /* AI 메시지 */
        .ai-message {
            justify-content: flex-start;
        }
        
        /* 메시지 말풍선 공통 */
        .message-bubble {
            max-width: 80%;
            padding: 10px 15px;
            border-radius: 18px;
            animation: fadeIn 0.3s ease;
            word-wrap: break-word;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        
        /* 사용자 말풍선 */
        .user-bubble {
            background-color: #6c5ce7;
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        /* AI 말풍선 */
        .ai-bubble {
            background-color: #e9ecef;
            color: #333;
            border-bottom-left-radius: 4px;
        }
        
        /* 빠른 질문 칩 */
        .quick-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 15px 0;
        }
        
        .chip {
            background-color: #f0f0f7;
            color: #555;
            border: none;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }
        
        .chip:hover {
            background-color: #e0e0f0;
            transform: translateY(-2px);
        }
        
        /* 채팅 입력창 */
        .chat-input-container {
            position: sticky;
            bottom: 0;
            background-color: white;
            padding: 10px 0;
            width: 100%;
        }
        
        /* 로드맵 추가 버튼 */
        .add-to-roadmap {
            display: inline-block;
            margin-top: 5px;
            font-size: 0.8rem;
            color: #6c5ce7;
            padding: 5px 10px;
            background-color: #f0f0f7;
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .add-to-roadmap:hover {
            background-color: #e0e0f0;
            transform: translateY(-2px);
        }
        
        /* 타이핑 애니메이션 */
        @keyframes typing {
            from { width: 0 }
            to { width: 100% }
        }
        
        .typing-animation {
            display: inline-block;
            overflow: hidden;
            white-space: nowrap;
            animation: typing 2s steps(40, end);
        }
        
        /* 모바일 최적화 */
        @media (max-width: 768px) {
            .chat-container {
                height: 70vh;
            }
            
            .message-bubble {
                max-width: 90%;
            }
            
            .calendar-grid {
                grid-template-columns: repeat(7, 1fr);
            }
            
            .calendar-weekly {
                display: grid;
            }
            
            .calendar-monthly {
                display: none;
            }
        }
        
        /* 캘린더 스타일 */
        .calendar-container {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .calendar-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .calendar-nav {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .calendar-nav-btn {
            background-color: #f0f0f7;
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .calendar-nav-btn:hover {
            background-color: #e0e0f0;
        }
        
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 5px;
        }
        
        .calendar-day-header {
            text-align: center;
            font-weight: 600;
            padding: 5px 0;
            color: #666;
        }
        
        .calendar-day {
            aspect-ratio: 1/1;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            position: relative;
            transition: all 0.2s;
            font-size: 0.9rem;
        }
        
        .calendar-day:hover {
            background-color: #f0f0f7;
        }
        
        .calendar-day.today {
            background-color: #e0e0f0;
            font-weight: 600;
            color: #6c5ce7;
        }
        
        .calendar-day.has-tasks:after {
            content: "";
            position: absolute;
            bottom: 5px;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: #6c5ce7;
        }
        
        .calendar-day.other-month {
            color: #ccc;
        }
        
        /* 로드맵 카드 스타일 */
        .roadmap-card {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #6c5ce7;
            transition: all 0.2s;
        }
        
        .roadmap-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .roadmap-title {
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 8px;
            color: #333;
        }
        
        .roadmap-progress {
            width: 100%;
            height: 6px;
            background-color: #f0f0f7;
            border-radius: 10px;
            margin: 8px 0;
            overflow: hidden;
        }
        
        .roadmap-progress-bar {
            height: 100%;
            background-color: #6c5ce7;
            border-radius: 10px;
            transition: width 0.5s ease;
        }
        
        .roadmap-meta {
            display: flex;
            justify-content: space-between;
            color: #666;
            font-size: 0.85rem;
        }
        
        .roadmap-task {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 10px;
            margin-top: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .roadmap-checkbox {
            appearance: none;
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            border: 2px solid #6c5ce7;
            border-radius: 4px;
            cursor: pointer;
            position: relative;
        }
        
        .roadmap-checkbox:checked {
            background-color: #6c5ce7;
        }
        
        .roadmap-checkbox:checked:after {
            content: '\2713';
            position: absolute;
            color: white;
            font-size: 12px;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        
        /* 통계 대시보드 */
        .stats-container {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            flex: 1;
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #6c5ce7;
            margin: 5px 0;
        }
        
        .stat-label {
            font-size: 0.8rem;
            color: #666;
            text-align: center;
        }
        
        /* 애니메이션 */
        @keyframes celebrateCheckmark {
            0% { transform: scale(1); }
            50% { transform: scale(1.5); }
            100% { transform: scale(1); }
        }
        
        .celebrate {
            animation: celebrateCheckmark 0.5s ease;
        }
        
        /* 로드맵 없을 때 */
        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
            text-align: center;
            background-color: #f8f9fa;
            border-radius: 12px;
            margin: 20px 0;
        }
        
        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 20px;
            color: #d1d1e0;
        }
    </style>
    """, unsafe_allow_html=True)

def get_custom_css():
    """
    CSS 스타일을 문자열로 반환합니다.
    이 함수는 스타일을 직접 삽입하지 않고 문자열만 반환하므로,
    특정 컴포넌트에만 스타일을 적용하고 싶을 때 유용합니다.
    
    Returns:
        str: CSS 스타일 문자열
    """
    return """
    <style>
        /* 여기에 필요한 CSS 스타일을 추가할 수 있습니다 */
        /* 이 함수는 향후 확장성을 위해 준비되었습니다 */
    </style>
    """
