"""
사주 분석 및 생성과 관련된 유틸리티 함수 모듈

Export 형태:
- from utils.saju import get_saju_elements
- from utils.saju import generate_saju_insight
- from utils.saju import analyze_saju
- 또는 import utils.saju as saju 후 saju.analyze_saju() 형태로 사용
"""
import datetime
from typing import Optional, Dict, Any
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
        
        사용자 질문: {question}
        
        위 정보를 바탕으로 사용자의 질문에 대한 맞춤형 답변을 제공해주세요. 
        사주를 기반으로 한 인사이트와 실용적인 조언을 포함해 답변해주세요.
        200자에서 300자 사이로 간결하게 답변해주세요.
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
