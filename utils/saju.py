"""
사주 분석 및 생성과 관련된 유틸리티 함수 모듈

Export 형태:
- from utils.saju import get_saju_elements
- from utils.saju import generate_saju_insight
- from utils.saju import analyze_saju
- 또는 import utils.saju as saju 후 saju.analyze_saju() 형태로 사용
"""
import datetime
import random
import re
from typing import Dict, Any, Optional, List

import google.generativeai as genai
import streamlit as st

def get_saju_elements(birthdate: datetime.date, birth_hour: str) -> Dict[str, str]:
    """
    생년월일과 태어난 시간을 기반으로 사주 요소를 생성합니다.
    간략화된 버전으로, 실제 사주 계산은 더 복잡합니다.
    
    Args:
        birthdate: 생년월일 (datetime.date 객체)
        birth_hour: 태어난 시간 (예: "23-01시", "07-09시" 등)
        
    Returns:
        Dict[str, str]: 사주 요소를 담은 딕셔너리
    """
    year = birthdate.year
    month = birthdate.month
    day = birthdate.day
    
    # 간략화된 사주 요소 계산 (실제 계산과는 다름)
    elements = {
        "천간": ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"][(year - 4) % 10],
        "지지": ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"][(year - 4) % 12],
        "월지": ["인", "묘", "진", "사", "오", "미", "신", "유", "술", "해", "자", "축"][month - 1],
        "일간": ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"][(day - 1) % 10],
        "시지": {
            "23-01시": "자", "01-03시": "축", "03-05시": "인", "05-07시": "묘", 
            "07-09시": "진", "09-11시": "사", "11-13시": "오", "13-15시": "미",
            "15-17시": "신", "17-19시": "유", "19-21시": "술", "21-23시": "해",
            "모름": "미정"
        }.get(birth_hour, "미정")
    }
    
    return elements

def generate_saju_insight(user_info: Dict[str, Any], question: Optional[str] = None) -> str:
    """
    사주 정보를 기반으로 Gemini API를 통해 인사이트를 생성합니다.
    
    Args:
        user_info: 사용자 정보 딕셔너리 (이름, 생년월일, 태어난 시간 포함)
        question: 선택적 질문 (없으면 일반적인 사주 분석 제공)
        
    Returns:
        str: 생성된 사주 인사이트 텍스트
    """
    try:
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        return f"API 설정이 필요합니다: {e}"
    
    saju_elements = get_saju_elements(user_info['birthdate'], user_info['birth_hour'])
    
    if question:
        prompt = f"""
        당신은 사주 전문 상담사입니다. 
        대화형 상담을 진행하며, 한 번에 너무 많이 말하지 않습니다.
        
        상담자 정보:
        - 이름: {user_info['name']}
        - 생년월일: {user_info['birthdate'].strftime('%Y년 %m월 %d일')}
        - 태어난 시간: {user_info['birth_hour']}
        
        상담 내용: {question}
        
        # 중요한 규칙
        1. 2-3문장으로 짧게 답변
        2. 질문을 통해 상담자가 스스로 깨달을 수 있도록 유도
        3. 사주 특성은 자연스럽게 녹여서 표현
        4. 조언보다는 공감과 탐색이 우선

        # 답변 구조
        1. 공감 (1문장)
        2. 사주 특성 언급 + 탐색 질문 (1-2문장)

        # 예시
        "적성 찾기가 정말 어렵죠. 
        당신의 사주를 보니 [특성]이 강해서, 여러 분야에 관심이 많으실 것 같은데, 
        최근에 가장 흥미롭게 느꼈던 일이 뭐였나요?"

        # 피해야 할 것
        - 긴 설명
        - 일방적인 조언
        - 섣부른 해결책 제시
        """
    else:
        prompt = f"""
        사용자 정보:
        - 이름: {user_info['name']}
        - 생년월일: {user_info['birthdate'].strftime('%Y년 %m월 %d일')}
        - 태어난 시간: {user_info['birth_hour']}
        
        사주 정보:
        - 천간: {saju_elements['천간']}
        - 지지: {saju_elements['지지']}
        - 월지: {saju_elements['월지']}
        - 일간: {saju_elements['일간']}
        - 시지: {saju_elements['시지']}
        
        위 정보를 바탕으로 사용자의 사주를 분석하고 간략한 성장 로드맵을 제안해주세요.
        사주의 특성을 바탕으로 한 성격, 장단점, 적성, 그리고 3개월/6개월/1년 단위의 간략한 성장 목표를 제안해주세요.
        전체 400자에서 600자 사이로 작성해주세요.
        """
    
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"생성 중 오류가 발생했습니다: {str(e)}"


def summarize_conversation(messages: List[Dict[str, str]]) -> str:
    """
    대화 내용을 분석하여 핵심 고민을 추출합니다.
    
    Args:
        messages: 사용자와 AI 간의 대화 메시지 목록
        
    Returns:
        str: 추출된 핵심 고민
    """
    try:
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        return f"대화 요약 중 오류: {e}"
    
    # 대화 내용 정리 (사용자 메시지와 AI 응답 번갈아가며)
    conversation_text = ""
    for i, msg in enumerate(messages):
        role = "사용자" if msg['role'] == 'user' else "AI"
        content = msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content']
        conversation_text += f"{role}: {content}\n\n"
    
    prompt = f"""
    다음은 사용자와 AI 간의 대화입니다:
    
    {conversation_text}
    
    위 대화를 분석하여 사용자의 핵심 고민을 한 문장으로 요약해주세요.
    사용자가 여러 주제를 언급했다면, 가장 중요하거나 반복적으로 언급된 고민을 파악해주세요.
    요약은 '어떻게 [문제/고민]을 해결할 수 있을까요?'와 같은 질문 형식으로 작성해주세요.
    
    핵심 고민: 
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        extracted_concern = response.text.strip()
        # 너무 짧은 경우 원본 마지막 질문 사용
        if len(extracted_concern) < 10 and len(messages) > 0:
            last_user_msg = next((msg['content'] for msg in reversed(messages) if msg['role'] == 'user'), None)
            if last_user_msg:
                return last_user_msg
        return extracted_concern
    except Exception as e:
        if len(messages) > 0:
            # 오류 발생 시 마지막 사용자 메시지 사용
            last_user_msg = next((msg['content'] for msg in reversed(messages) if msg['role'] == 'user'), None)
            if last_user_msg:
                return last_user_msg
        return f"대화를 요약할 수 없습니다: {e}"

def generate_weekly_plan(user_info: Dict[str, Any], concern: str) -> List[Dict[str, str]]:
    """
    사용자의 고민을 7일간의 실천 계획으로 변환합니다.
    
    Args:
        user_info: 사용자 정보 딕셔너리 (이름, 생년월일, 태어난 시간 포함)
        concern: 사용자의 고민/질문
        
    Returns:
        List[Dict[str, str]]: 7일간의 실천 계획 목록
    """
    try:
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        return [{'day': f'Day {i+1}', 'title': '계획을 생성할 수 없습니다', 'description': f"API 설정이 필요합니다: {e}"} for i in range(7)]
    
    saju_elements = get_saju_elements(user_info['birthdate'], user_info['birth_hour'])
    
    prompt = f"""
    사용자 정보:
    - 이름: {user_info['name']}
    - 생년월일: {user_info['birthdate'].strftime('%Y년 %m월 %d일')}
    - 태어난 시간: {user_info['birth_hour']}
    
    사주 정보:
    - 천간: {saju_elements['천간']}
    - 지지: {saju_elements['지지']}
    - 월지: {saju_elements['월지']}
    - 일간: {saju_elements['일간']}
    - 시지: {saju_elements['시지']}
    
    사용자 고민: {concern}
    
    위 정보를 바탕으로 사용자의 고민을 해결하기 위한 7일간의 실천 계획을 만들어주세요.
    사주를 고려하여 사용자의 특성과 성향에 맞는 단계적 접근법을 제시해주세요.
    
    응답형식:
    1) 첫째로, 7일 계획을 정확히 다음 형식으로 제시하세요:
    Day 1: [제목] - [설명] (30자 내외)
    Day 2: [제목] - [설명] (30자 내외)
    Day 3: [제목] - [설명] (30자 내외)
    Day 4: [제목] - [설명] (30자 내외)
    Day 5: [제목] - [설명] (30자 내외)
    Day 6: [제목] - [설명] (30자 내외)
    Day 7: [제목] - [설명] (30자 내외)
    
    2) 둘째로, 아래에 다음 형식으로 추가 설명을 제시하세요:
    
    ADDITIONAL_EXPLANATION: 이 계획이 사주 특성과 어떻게 연관되는지 설명해주세요. (100자 내외)
    
    각 날짜별 계획은 구체적이고 실천 가능해야 합니다. 다른 형식은 추가하지 마세요.
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        plan_text = response.text
        
        # 디버깅용: 세션 상태에 원본 응답 저장
        st.session_state['debug_raw_response'] = plan_text
        
        # 추가 설명 추출
        additional_explanation = ""
        explanation_match = re.search(r'ADDITIONAL_EXPLANATION:\s*(.*?)(?:\n|$)', plan_text, re.DOTALL)
        if explanation_match:
            additional_explanation = explanation_match.group(1).strip()
        st.session_state['plan_additional_explanation'] = additional_explanation
        
        # Day 1-7 형식의 라인만 추출
        day_lines = []
        for line in plan_text.strip().split('\n'):
            if re.match(r'Day \d+:', line.strip()):
                day_lines.append(line.strip())
        
        # 추출된 라인을 파싱
        plans = []
        for i in range(min(7, len(day_lines))):
            line = day_lines[i]
                
            try:
                # 다양한 형식 처리
                # 1. "Day 1: 제목 - 설명" 형식
                day_match = re.match(r'Day \d+:\s*(.*?)\s*-\s*(.*)', line)
                if day_match:
                    title, description = day_match.groups()
                    plans.append({
                        'day': f'Day {i+1}',
                        'title': title.strip() or f'일일 계획 {i+1}',
                        'description': description.strip() or f'{i+1}일차 활동 내용을 제시해드립니다.'
                    })
                    continue
                
                # 2. "Day 1: 제목" 형식 (설명 없음)
                day_title_match = re.match(r'Day \d+:\s*(.*)', line)
                if day_title_match:
                    title = day_title_match.group(1).strip()
                    # 다음 줄 확인해서 설명으로 처리
                    description = ""
                    if i + 1 < len(lines) and not re.match(r'Day \d+:', lines[i+1]):
                        description = lines[i+1].strip()
                    
                    plans.append({
                        'day': f'Day {i+1}',
                        'title': title or f'일일 계획 {i+1}',
                        'description': description or f'{i+1}일차 활동을 진행하세요.'
                    })
                    continue
                
                # 3. 다른 형식의 경우 - 전체 내용을 설명으로 처리
                plans.append({
                    'day': f'Day {i+1}',
                    'title': f'일일 활동 {i+1}',
                    'description': line
                })
            except Exception as e:
                plans.append({
                    'day': f'Day {i+1}',
                    'title': f'일일 계획 {i+1}',
                    'description': f'{i+1}일차 실천 계획입니다.'
                })
        
        # 7일이 채워지지 않았을 경우 나머지 채우기
        while len(plans) < 7:
            i = len(plans)
            plans.append({
                'day': f'Day {i+1}',
                'title': f'추가 활동 {i+1}',
                'description': '추가 실천 계획을 세워보세요.'
            })
            
        return plans
    except Exception as e:
        return [{'day': f'Day {i+1}', 'title': '계획을 생성할 수 없습니다', 'description': f"오류: {str(e)}"} for i in range(7)]

def analyze_saju(name: str, birthdate: datetime.date, birth_hour: str) -> Dict[str, str]:
    """
    사용자의 사주를 분석하고 결과를 반환합니다.
    
    Args:
        name: 사용자 이름
        birthdate: 생년월일 (datetime.date 객체)
        birth_hour: 태어난 시간 (예: "23-01시", "07-09시" 등)
        
    Returns:
        Dict[str, str]: 분석 결과를 담은 딕셔너리 (full_analysis, core_traits 키 포함)
    """
    try:
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        return {
            "full_analysis": f"API 설정이 필요합니다: {e}",
            "core_traits": "분석 오류"
        }
    
    saju_elements = get_saju_elements(birthdate, birth_hour)
    
    prompt = f"""
    사용자 정보:
    - 이름: {name}
    - 생년월일: {birthdate.strftime('%Y년 %m월 %d일')}
    - 태어난 시간: {birth_hour}
    
    사주 정보:
    - 천간: {saju_elements['천간']}
    - 지지: {saju_elements['지지']}
    - 월지: {saju_elements['월지']}
    - 일간: {saju_elements['일간']}
    - 시지: {saju_elements['시지']}
    
    위 정보를 바탕으로 사용자의 사주를 분석해주세요. 다음 구조로 답변해주세요:
    
    1. 핵심 특성: (한 문장으로 간결하게)
    2. 성격과 기질: (200자 내외)
    3. 적성과 재능: (200자 내외)
    4. 대인관계와 소통방식: (200자 내외)
    5. 성장을 위한 제안: (200자 내외)
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        analysis = response.text
        
        # 핵심 특성 추출 (첫 번째 줄)
        core_traits = "분석 중..."
        for line in analysis.split('\n'):
            if "핵심 특성:" in line:
                core_traits = line.replace("핵심 특성:", "").strip()
                break
        
        return {
            "full_analysis": analysis,
            "core_traits": core_traits
        }
    except Exception as e:
        return {
            "full_analysis": f"분석 중 오류가 발생했습니다: {str(e)}",
            "core_traits": "분석 오류"
        }
