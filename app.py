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
# 1. 사이드바: [작업 모드 선택 토글]
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 작업 모드 선택")
    # 라디오 버튼으로 토글 메뉴 생성
    app_mode = st.radio(
        "현재 진행할 작업을 선택하세요:",
        ["📥 1. 신규 데이터 수집기", "📊 2. 상권 분석 및 MD 추천"],
        label_visibility="collapsed" # 디자인을 위해 라벨 숨김
    )
    st.divider()
    
    # 선택된 모드에 따라 사이드바 하단 안내문구 변경
    if app_mode == "📥 1. 신규 데이터 수집기":
        st.info("새로운 상가 매물 정보를 입력하여 DB에 누적하는 모드입니다.")
    else:
        st.success("누적된 DB를 바탕으로 지역별 시세와 추천 MD를 검색합니다.")

# ---------------------------------------------------------
# 2. 메인 화면 분기 로직
# ---------------------------------------------------------

# [모드 A] 신규 데이터 수집기 화면
if app_mode == "📥 1. 신규 데이터 수집기":
    st.subheader("📥 신규 매물 데이터 수집")
    st.markdown("매물 홍보 텍스트를 아래에 붙여넣으면 AI가 핵심 데이터를 추출합니다.")
    
    # 좁은 사이드바 대신 넓은 메인 화면에서 입력받음
    col1, col2 = st.columns([1, 3])
    with col1:
        input_region = st.text_input("📍 수집 지역 (AI 힌트용)", "송파구")
    with col2:
        raw_text = st.text_area("📝 매물 텍스트 복붙", height=200, placeholder="여기에 매물 설명 텍스트를 붙여넣으세요.")
    
    if st.button("데이터 추출 및 클라우드 저장", type="primary") and raw_text:
        with st.spinner("AI 분석 및 구글 시트 동기화 중..."):
            # (여기에 기존 AI prompt 생성 및 response 추출 로직, 구글 시트 Webhook 코드가 들어갑니다)
            # 기존 코드의 API 호출 및 st.session_state 저장 로직을 그대로 유지하세요.
            pass # (이 부분은 기존 코드를 복붙하시면 됩니다)

# [모드 B] 상권 분석 및 MD 추천 화면
elif app_mode == "📊 2. 상권 분석 및 MD 추천":
    st.subheader("📊 누적 데이터 상권 분석 및 검색")
    
    if not st.session_state.md_data.empty:
        # 상단 검색 필터 바
        existing_regions = st.session_state.md_data['지역그룹'].unique().tolist()
        selected_region = st.selectbox("🔍 조회할 지역 그룹 선택:", ["전체 보기"] + existing_regions)
        
        # 선택된 지역에 맞춰 데이터 필터링
        if selected_region == "전체 보기":
            df_display = st.session_state.md_data.copy()
        else:
            df_display = st.session_state.md_data[st.session_state.md_data['지역그룹'] == selected_region].copy()
            
        df_display.index = range(1, len(df_display) + 1) # 인덱스 1부터 재정렬
        
        st.caption(f"총 {len(df_display)}건의 데이터가 조회되었습니다.")

        col_chart1, col_chart2 = st.columns([1, 1])
        
        with col_chart1:
            st.markdown("##### 📈 업종별 월세 Range")
            if not df_display.empty:
                # 차트 그리기 (기존 코드 유지)
                fig_rent = px.box(df_display, x="AI분류업종", y="월세", color="AI분류업종", template="plotly_white")
                st.plotly_chart(fig_rent, use_container_width=True)
            else:
                st.info("해당 지역에 표시할 차트 데이터가 없습니다.")

        with col_chart2:
            st.markdown("##### 💡 최신 MD 솔루션")
            for idx, row in df_display.tail(3).iterrows(): 
                st.info(f"**[{row['지역그룹']}] {row['상호명']}**\n\n🔑 {row['키워드']}\n\n🤖 {row['MD솔루션']}")

        st.markdown("##### 📋 전체 매물 Database")
        st.dataframe(df_display, use_container_width=True)
    else:
        st.warning("현재 누적된 데이터가 없습니다. 좌측 메뉴에서 '신규 데이터 수집기'로 이동하여 데이터를 먼저 입력해 주세요.")
