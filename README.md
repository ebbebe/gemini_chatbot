# 나만의 프롬프트 기반 Gemini 챗봇

이 프로젝트는 Streamlit과 Google Gemini API를 활용하여 사용자가 정의한 역할에 따라 대화하는 챗봇을 구현한 애플리케이션입니다.

## 기능

- 사용자가 AI의 역할을 직접 정의할 수 있습니다
- 정의된 역할에 맞게 AI가 대화를 이어갑니다
- 대화 내용을 기억하고 문맥을 유지합니다
- 대화 내용을 JSON 형식으로 내보낼 수 있습니다
- 직관적인 채팅 인터페이스를 제공합니다

## 설치 방법

1. 저장소를 클론합니다:
```
git clone https://github.com/yourusername/gemini_chatbot_gpts.git
cd gemini_chatbot_gpts
```

2. 가상 환경을 생성하고 활성화합니다:
```
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

3. 필요한 패키지를 설치합니다:
```
pip install -r requirements.txt
```

4. Google API 키를 설정합니다:
   - `.streamlit/secrets.toml` 파일에 API 키를 추가합니다:
   ```
   GOOGLE_API_KEY = "your_google_api_key_here"
   ```

## 실행 방법

가상 환경이 활성화된 상태에서 다음 명령어를 실행합니다:

```
streamlit run app.py
```

## 사용 방법

1. 애플리케이션이 시작되면 AI의 역할을 정의합니다 (예: "넌 여행 전문가야", "심리상담사처럼 대답해줘")
2. 역할을 설정하면 AI가 해당 역할에 맞는 첫 인사를 건넵니다
3. 메시지를 입력하여 대화를 시작합니다
4. 사이드바에서 대화 초기화, 역할 변경, 대화 내보내기 등의 기능을 사용할 수 있습니다

## 기술 스택

- Python 3.8+
- Streamlit 1.12.0
- Google Generative AI (Gemini 1.5 Flash)
- Pandas, NumPy 등 데이터 처리 라이브러리

## 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다.
