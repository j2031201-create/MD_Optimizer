import streamlit as st
import google.generativeai as genai

# 페이지 기본 설정
st.set_page_config(page_title="KT에스테이트 MD 최적화 툴", page_icon="🏢", layout="wide")

st.title("🏢 상업시설 MD 최적화 및 공실 분석 조력자 (v1.0)")
st.markdown("**KT에스테이트 Value-add 자산운용 실무용 프로토타입**")

# API 키 설정 (보안을 위해 Streamlit Secrets 사용)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("API 키가 설정되지 않았습니다. Streamlit 세팅에서 API 키를 입력해주세요.")
    st.stop()

# 제미나이 모델 설정
model = genai.GenerativeModel('gemini-2.5-flash')

# v1.0 프롬프트 엔진
system_instruction = """
너는 상업용 부동산 분석 보조 AI야.
사용자가 중개소 매물 설명이나 커뮤니티 텍스트를 입력하면, 다음 항목을 추출해서 표 형태로 요약해 줘.
1. 위치 및 층수
2. 전용면적 (평)
3. 보증금 / 월세 / 권리금
4. 현재 업종
5. 추천 업종
"""

# 화면 레이아웃 분할 (좌측: 입력, 우측: 출력)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("매물 정보 입력")
    raw_text = st.text_area("비정형 매물 텍스트를 복사해서 붙여넣으세요.", height=300, placeholder="예: 나성동 1층 상가, 15평, 보증금 3000/월 200, 무권리, 즉시입주...")
    analyze_btn = st.button("AI 분석 실행")

with col2:
    st.subheader("AI 분석 결과")
    if analyze_btn and raw_text:
        with st.spinner("KT에스테이트 기준에 맞춰 분석 중..."):
            prompt = f"{system_instruction}\n\n[입력된 매물 텍스트]\n{raw_text}"
            response = model.generate_content(prompt)
            st.markdown(response.text)
    elif analyze_btn and not raw_text:
        st.warning("매물 텍스트를 먼저 입력해주세요.")
