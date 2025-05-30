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
        상담자 정보:
        - 이름: {user_info['name']}
        - 생년월일: {user_info['birthdate'].strftime('%Y년 %m월 %d일')}
        - 태어난 시간: {user_info['birth_hour']}
        
        상담 내용: {question}
        
        # 답변 가이드라인
        1. **공감과 이해** (1-2문장)
        - 상담자의 사주 특성상 왜 이런 고민이 생겼는지 설명
        - "당신의 {특성}으로 인해 {상황}에서 어려움을 느끼시는 것이 당연합니다"

        2. **핵심 분석** (2-3문장)
        - 문제의 근본 원인을 사주 관점에서 분석
        - 상담자만의 독특한 패턴이나 성향 지적

        3. **맞춤형 해결책** (3-4문장)
        - "일반적으로는 ~하라고 하지만, 당신에게는 ~가 더 맞습니다"
        - 사주 특성에 맞는 구체적인 방법 제시

        4. **실천 방안** (필요시)
        - 당장 오늘 할 수 있는 작은 행동 1가지
        - 이번 주 시도해볼 만한 것 1가지

        5. **마무리 격려** (1문장)
        - 상담자의 강점을 활용한 긍정적 전망

        # 톤 & 매너
        - 따뜻하고 친근한 말투
        - 전문적이지만 딱딱하지 않게
        - 희망적이고 실용적인 조언
        - 반말 사용 (편안한 느낌)
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
    
    반드시 다음 형식으로 응답해주세요:
    Day 1: [제목] - [설명] (30자 내외)
    Day 2: [제목] - [설명] (30자 내외)
    Day 3: [제목] - [설명] (30자 내외)
    Day 4: [제목] - [설명] (30자 내외)
    Day 5: [제목] - [설명] (30자 내외)
    Day 6: [제목] - [설명] (30자 내외)
    Day 7: [제목] - [설명] (30자 내외)
    
    각 날짜별 계획은 구체적이고 실천 가능해야 합니다. 하루에 한 가지 작은 실천에 집중하도록 해주세요.
    전체 계획은 점진적으로 발전하여 7일 후에는 고민을 해결하거나 상당한 진전을 이룰 수 있도록 구성해주세요.
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        plan_text = response.text
        
        # Day 1: [제목] - [설명] 형식의 텍스트를 파싱
        plans = []
        lines = plan_text.strip().split('\n')
        for i in range(min(7, len(lines))):
            line = lines[i].strip()
            if not line:  # 공백 줄 건너뛰기
                continue
                
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
