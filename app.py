import streamlit as st
import google.generativeai as genai

# 페이지 기본 설정
st.set_page_config(page_title="상업시설 MD 최적화 툴", page_icon="🏢", layout="wide")

st.title("🏢 상업시설 MD 최적화 및 공실 분석 조력자 (v1.1)")
st.markdown("**Value-add 자산운용 및 LM(Leasing Management) 실무용 프로토타입**")
st.markdown("*Target: 서울 송파구 상권 / Logic: 무권리금 = 한계월세(저항선) 기준*")

# API 키 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("API 키가 설정되지 않았습니다.")
    st.stop()

model = genai.GenerativeModel('gemini-2.5-flash')

# v1.1 핵심 프롬프트 엔진 (기업명 제거, 범용 AMC/PM 전문가 롤 부여)
system_instruction = """
너는 종합부동산회사 및 자산운용사(AMC)의 10년 차 상업용 부동산 LM(Leasing Management) 전문가야.
사용자가 서울 송파구 일대의 비정형 상가 매물 텍스트를 여러 개 입력하면, 다음 기준에 따라 분석 리포트를 마크다운 표와 텍스트로 작성해 줘.

[분석 기준]
1. 업종 1차 분류: 매물 설명에 기반하여 F&B, 리테일, 서비스업 등으로 카테고리화.
2. 계약 조건 정량화: 전용면적(평), 보증금, 월세, 권리금 추출.
3. 전용 평당 월세(NOC) 추정: (월세 / 전용면적)을 계산하여 표기.
4. 🚨[핵심] 한계 월세 및 Range 도출: 입력된 매물 중 '권리금이 0원(무권리)'인 매물이 있다면, 그 매물의 평당 월세를 해당 상권/업종의 영업이익 마지노선인 '한계 월세'로 규정해. 이를 바탕으로 적정 임대료 Range(최소~최대)를 제안할 것.
"""

# 화면 레이아웃 분할
col1, col2 = st.columns([4, 5])

with col1:
    st.subheader("데이터 수집 (Input)")
    st.info("부동산 커뮤니티(아프니까 사장이다 등)에서 수집한 매물 데이터를 한 번에 붙여넣으세요.")
    raw_text = st.text_area("매물 텍스트 입력", height=400, placeholder="매물1: 송파동 1층, 20평, 5000/350, 권리금 3000...\n매물2: 석촌동 1층, 15평, 3000/300, 무권리...")
    analyze_btn = st.button("실무 분석 실행", type="primary")

with col2:
    st.subheader("MD 및 임대료 최적화 리포트 (Output)")
    if analyze_btn and raw_text:
        with st.spinner("임대료 Range 및 한계 월세 역산 중..."):
            prompt = f"{system_instruction}\n\n[수집된 매물 데이터]\n{raw_text}"
            response = model.generate_content(prompt)
            st.markdown(response.text)
    elif analyze_btn and not raw_text:
        st.warning("데이터를 입력해야 분석이 가능합니다.")
