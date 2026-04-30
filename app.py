import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import requests
import plotly.express as px

st.set_page_config(page_title="상업시설 MD 자동화 툴", page_icon="🏢", layout="wide")

GOOGLE_WEBHOOK_URL = "https://script.google.com/macros/s/여기에_복사한_URL_붙여넣기/exec"

if 'md_data' not in st.session_state:
    st.session_state.md_data = pd.DataFrame(columns=[
        '지역그룹', '상호명', '주소', 'AI분류업종', '면적(평)', '보증금', '월세', '총권리금', '댓글수', '키워드', 'MD솔루션'
    ])

total_count = len(st.session_state.md_data)
st.title(f"🏢 상업시설 MD 데이터 분석 대시보드 (v1.3)")
st.markdown(f"**현재 누적 분석 데이터: {total_count}건** (구글 시트 실시간 동기화 중 🟢)")
st.divider()

# API 설정 생략 (기존과 동일)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("API 키가 설정되지 않았습니다.")
    st.stop()
model = genai.GenerativeModel('gemini-2.5-flash')
system_instruction = """(기존 프롬프트 내용 동일)"""

# ---------------------------------------------------------
# 1. 사이드바: [신규 데이터 수집 전용 공간]
# ---------------------------------------------------------
with st.sidebar:
    st.header("📥 신규 매물 수집기")
    st.caption("새로운 매물 텍스트를 AI로 분석하여 DB에 추가합니다.")
    
    # 여기서 입력받는 지역명은 'AI가 주소를 찾을 때 참고할 힌트' 용도
    input_region = st.text_input("📍 수집 지역 (AI 보정용 힌트)", "송파구")
    raw_text = st.text_area("📝 매물 텍스트 복붙 (1건씩)", height=250)
    
    if st.button("데이터 추출 및 클라우드 저장", type="primary", use_container_width=True) and raw_text:
        # (기존 데이터 추출 및 구글 시트 전송 로직 동일하게 유지)
        with st.spinner("AI 분석 및 구글 시트 동기화 중..."):
            prompt = f"{system_instruction}\n\n[사용자 입력 지역]: {input_region}\n[입력 텍스트]\n{raw_text}"
            response = model.generate_content(prompt)
            # ... (JSON 파싱 및 session_state, webhook 처리 코드 생략 - 기존과 동일) ...

# ---------------------------------------------------------
# 2. 메인 화면: [데이터 검색 및 대시보드 공간]
# ---------------------------------------------------------
if not st.session_state.md_data.empty:
    
    # 상단 검색 필터 바
    st.subheader("🔍 상권 데이터 검색 및 필터링")
    
    # DB에 있는 고유한 지역명만 뽑아서 선택 리스트 생성
    existing_regions = st.session_state.md_data['지역그룹'].unique().tolist()
    selected_region = st.selectbox("조회할 지역 그룹을 선택하세요:", ["전체 보기"] + existing_regions)
    
    # 선택된 지역에 맞춰 데이터 필터링
    if selected_region == "전체 보기":
        df_display = st.session_state.md_data.copy()
    else:
        df_display = st.session_state.md_data[st.session_state.md_data['지역그룹'] == selected_region].copy()
        
    df_display.index = range(1, len(df_display) + 1) # 인덱스 1부터 재정렬
    
    # 필터링된 데이터 건수 안내
    st.caption(f"총 {len(df_display)}건의 데이터가 조회되었습니다.")

    col_chart1, col_chart2 = st.columns([1, 1])
    
    with col_chart1:
        st.subheader("📊 업종별 월세 Range")
        if not df_display.empty:
            fig_rent = px.box(df_display, x="AI분류업종", y="월세", color="AI분류업종", template="plotly_white")
            st.plotly_chart(fig_rent, use_container_width=True)
        else:
            st.info("해당 지역에 표시할 차트 데이터가 없습니다.")

    with col_chart2:
        st.subheader("💡 최신 MD 솔루션")
        for idx, row in df_display.tail(3).iterrows(): 
            st.info(f"**[{row['지역그룹']}] {row['상호명']}**\n\n🔑 {row['키워드']}\n\n🤖 {row['MD솔루션']}")

    st.subheader("📋 매물 Database")
    st.dataframe(df_display, use_container_width=True)
else:
    st.info("👈 좌측 사이드바에서 첫 번째 매물 데이터를 입력해 주세요.")
