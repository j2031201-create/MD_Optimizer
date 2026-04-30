import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import requests
import plotly.express as px

st.set_page_config(page_title="상업시설 MD 자동화 툴", page_icon="🏢", layout="wide")

# ==========================================
# 🚨 여기에 아까 복사한 구글 앱스 스크립트 웹앱 URL을 넣어주세요!
GOOGLE_WEBHOOK_URL = "https://script.google.com/macros/s/여기에_복사한_URL_붙여넣기/exec"
# ==========================================

# 누적 데이터를 저장할 세션 상태 초기화
if 'md_data' not in st.session_state:
    st.session_state.md_data = pd.DataFrame(columns=[
        '지역그룹', '상호명', '주소', 'AI분류업종', '면적(평)', '보증금', '월세', '총권리금', '댓글수', '키워드', 'MD솔루션'
    ])

total_count = len(st.session_state.md_data)
st.title(f"🏢 상업시설 MD 데이터 분석 대시보드 (v1.3)")
st.markdown(f"**현재 누적 분석 데이터: {total_count}건** (구글 시트 실시간 동기화 중 🟢)")
st.divider()

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("API 키가 설정되지 않았습니다.")
    st.stop()

# 지역명 보정 및 최적화된 프롬프트 엔진
system_instruction = """
너는 상업용 부동산 데이터 마이닝 및 정규화 AI야. 지정된 JSON 양식으로만 답변해.

[추출 및 정규화 로직]
1. 지역 정규화(Auto-correction): 사용자가 입력한 '지역그룹'과 매물 텍스트의 '주소'를 대조하여, 지역그룹명을 반드시 [OO시/구 OO동] 형식으로 철자와 행정구역을 올바르게 보정해서 출력해. (예: 동작구 상도동)
2. 업종 분류: 상호명과 설명을 바탕으로 객관적인 세부 카테고리 설정.
3. 데이터 슬림화: 숫자 데이터는 쉼표를 제거한 순수 숫자(int/float)로만 추출. 없는 정보는 0으로 처리.

[JSON 출력 양식] - 마크다운 코드블럭(```json) 안에 작성할 것
{
  "지역그룹": "보정된 지역명",
  "상호명": "상호명",
  "주소": "주소",
  "AI분류업종": "세부업종",
  "면적(평)": 숫자,
  "보증금": 숫자,
  "월세": 숫자,
  "총권리금": 숫자,
  "댓글수": 숫자,
  "키워드": "키워드1, 키워드2, 키워드3",
  "MD솔루션": "솔루션 내용 1줄 요약"
}
"""

model = genai.GenerativeModel('gemini-2.5-flash')

with st.sidebar:
    st.header("📥 데이터 수집기")
    region_group = st.text_input("📍 지역 그룹명 (러프하게 적어도 AI가 보정함)", "송파구")
    raw_text = st.text_area("📝 매물 텍스트 복붙 (1건씩)", height=250)
    
    if st.button("데이터 추출 및 클라우드 저장", type="primary", use_container_width=True) and raw_text:
        with st.spinner("AI 분석 및 구글 시트 동기화 중..."):
            prompt = f"{system_instruction}\n\n[사용자 입력 지역]: {region_group}\n[입력 텍스트]\n{raw_text}"
            response = model.generate_content(prompt)
            
            try:
                # 1. JSON 파싱
                result_str = response.text.strip()
                if "```json" in result_str:
                    result_str = result_str.split("```json")[1].split("```")[0].strip()
                new_data = json.loads(result_str)
                
                # 2. 대시보드(Session State) 누적
                new_df = pd.DataFrame([new_data])
                st.session_state.md_data = pd.concat([st.session_state.md_data, new_df], ignore_index=True)
                
                # 3. 구글 시트로 데이터 전송 (Webhook)
                if GOOGLE_WEBHOOK_URL.startswith("https://script.google.com"):
                    res = requests.post(GOOGLE_WEBHOOK_URL, json=new_data)
                    if res.text == "Success":
                        st.success(f"✅ '{new_data['상호명']}' 분석 완료 및 구글 시트 백업 성공!")
                    else:
                        st.warning("분석은 완료되었으나 시트 전송에 오류가 있습니다.")
                else:
                    st.info("💡 구글 웹앱 URL을 입력하면 시트에 영구 저장됩니다.")
                    
            except Exception as e:
                st.error("데이터 추출 오류. 매물 텍스트를 확인해주세요.")

# 대시보드 UI (가독성 향상 및 1번부터 시작)
if not st.session_state.md_data.empty:
    df_display = st.session_state.md_data.copy()
    df_display.index = df_display.index + 1  # 0번이 아닌 1번부터 인덱스 시작
    
    col_chart1, col_chart2 = st.columns([1, 1])
    
    with col_chart1:
        st.subheader("📊 업종별 월세 Range")
        fig_rent = px.box(df_display, x="AI분류업종", y="월세", color="AI분류업종", template="plotly_white")
        st.plotly_chart(fig_rent, use_container_width=True)

    with col_chart2:
        st.subheader("💡 최신 MD 솔루션")
        for idx, row in df_display.tail(3).iterrows(): # 최근 3건만 가독성 있게 보여줌
            st.info(f"**[{row['지역그룹']}] {row['상호명']}**\n\n🔑 {row['키워드']}\n\n🤖 {row['MD솔루션']}")

    st.subheader("📋 전체 매물 Database")
    st.dataframe(df_display, use_container_width=True)
else:
    st.info("👈 사이드바에서 데이터를 입력하면 대시보드와 구글 시트가 동시에 업데이트됩니다.")
