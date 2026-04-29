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
# v1.2 프롬프트 엔진 (출력 포맷 강제화 및 불필요한 서술 제거)
system_instruction = """
너는 상업용 부동산 데이터 추출 및 분석 엔진이야. 인사말이나 서술형 부연 설명은 절대 하지 말고, 오직 아래 지정된 마크다운(Markdown) 템플릿 형식에 맞춰서만 결과값을 출력해.

[출력 템플릿]
### 1. 매물 데이터 추출 요약표
| 매물/위치 | 업종(1차 분류) | 전용면적(평) | 보증금(만) | 월세(만) | 권리금(만) | NOC(전용 평당 월세) |
|---|---|---|---|---|---|---|
| (추출내용) | (추출내용) | (추출내용) | (추출내용) | (추출내용) | (추출내용) | (추출내용) |

### 2. 한계 월세 및 임대료 Range 분석
* **무권리금 매물 여부:** (있음/없음)
* **한계 월세 (저항선):** (무권리 매물이 있다면 그 매물의 NOC 기재, 없다면 "데이터 부족으로 산출 불가" 기재)
* **적정 임대료 Range:** (추출된 NOC 기준 최소~최대 범위 기재)

### 3. 상권 MD 특성 코멘트
* (추출된 데이터를 바탕으로 해당 상권의 특징이나 추천 MD를 2~3줄 이내로 아주 짧고 명확하게 요약)
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
