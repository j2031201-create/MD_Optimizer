import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import plotly.express as px

# 페이지 기본 설정 (넓은 화면)
st.set_page_config(page_title="상업시설 MD 자동화 툴", page_icon="🏢", layout="wide")

# 누적 데이터를 저장할 세션 상태 초기화 (그룹화 및 누적용)
if 'md_data' not in st.session_state:
    st.session_state.md_data = pd.DataFrame(columns=[
        '지역그룹', '상호명', '주소', '접도유형', 'AI분류업종', '면적(평)', '층수', '주차대수', 
        '보증금', '월세', '총권리금', '영업권리금', '시설권리금', '권리금평가', 
        '댓글수', '선호도', '매출신뢰도', '키워드', 'MD솔루션'
    ])

st.title("🏢 상업시설 MD 데이터 마이닝 및 분석 대시보드 (v1.2)")
st.markdown("**비정형 매물 텍스트 기반 자산운용 및 LM 실무 솔루션**")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("API 키가 설정되지 않았습니다.")
    st.stop()

# JSON 출력을 강제하는 강력한 프롬프트 엔진
system_instruction = """
너는 상업용 부동산 데이터 마이닝 및 상권 분석 AI야. 사용자가 아프니까 사장이다 매물 텍스트를 입력하면, 다음 로직에 따라 분석하고 반드시 지정된 JSON 양식으로만 답변해.

[데이터 추출 및 판단 로직]
1. AI분류업종: 작성자가 등록한 카테고리(예: 한식)를 무시하고, 상호명(예: 멕시카나)과 설명을 바탕으로 정확한 세부 카테고리 재설정 (예: F&B-치킨).
2. 접도유형: 주소를 바탕으로 해당 건물이 접한 도로 성격 유추 (간선도로, 집산도로, 국지도로 등).
3. 선호도 평가: 게시일 대비 댓글 수를 계산하여 '높음/보통/낮음' 평가.
4. 권리금 평가: 총 권리금 중 '영업 권리금' 비중이 크면 "사업성 우수", '시설 권리금' 비중이 크면 "감가상각 주의"로 평가.
5. 매출신뢰도: '순이익에 대한 추가정보'란의 포스기 연동 여부 등을 보고 신뢰도(상/중/하) 평가.
6. 키워드 및 MD솔루션: 매물 설명에서 어필하는 키워드 3개 추출 및 해당 점포 인수 또는 타 업종 전환 시 전략 1줄 제시.

[JSON 출력 양식] - 마크다운 코드블럭(```json) 안에 작성할 것
{
  "지역그룹": "추출된 구/동 이름 (예: 동작구)",
  "상호명": "상호명",
  "주소": "주소",
  "접도유형": "도로 성격",
  "AI분류업종": "세부업종",
  "면적(평)": 숫자만(float),
  "층수": "층 정보",
  "주차대수": 숫자만(int),
  "보증금": 숫자만(단위:만원),
  "월세": 숫자만(단위:만원),
  "총권리금": 숫자만(단위:만원),
  "영업권리금": 숫자만,
  "시설권리금": 숫자만,
  "권리금평가": "평가내용",
  "댓글수": 숫자만,
  "선호도": "평가결과",
  "매출신뢰도": "평가결과",
  "키워드": "키워드1, 키워드2, 키워드3",
  "MD솔루션": "솔루션 내용"
}
"""

model = genai.GenerativeModel('gemini-2.5-flash')

# 사이드바: 데이터 입력부
with st.sidebar:
    st.header("📥 데이터 수집기")
    region_group = st.text_input("지역 그룹명 (예: 송파구 1차조사)", "동작구 상도동")
    raw_text = st.text_area("매물 텍스트 복붙 (1건씩)", height=300)
    
    if st.button("데이터 추출 및 누적", type="primary") and raw_text:
        with st.spinner("AI가 매물 논리를 분석 중입니다..."):
            prompt = f"{system_instruction}\n\n[입력 텍스트]\n{raw_text}"
            response = model.generate_content(prompt)
            
            try:
                # JSON 파싱
                result_str = response.text.strip()
                if "```json" in result_str:
                    result_str = result_str.split("```json")[1].split("```")[0].strip()
                
                new_data = json.loads(result_str)
                new_data['지역그룹'] = region_group # 사용자 지정 그룹명 덮어쓰기
                
                # 데이터프레임에 누적
                new_df = pd.DataFrame([new_data])
                st.session_state.md_data = pd.concat([st.session_state.md_data, new_df], ignore_index=True)
                st.success(f"'{new_data['상호명']}' 데이터 누적 완료!")
            except Exception as e:
                st.error("데이터 추출 오류. 텍스트 형식을 확인해주세요.")

# 메인 화면: 대시보드
if not st.session_state.md_data.empty:
    df = st.session_state.md_data
    
    # 1. 탑 메뉴: 주요 업종 순위 (권리금/월세 기준)
    st.subheader("🏆 Top MD 랭킹 (누적 데이터 기준)")
    top_md = df.groupby('AI분류업종').agg({'총권리금':'mean', '월세':'mean'}).sort_values('총권리금', ascending=False).head(5)
    
    cols = st.columns(len(top_md) if len(top_md) > 0 else 1)
    icons = ["🥇", "🥈", "🥉", "🏅", "🎖️"]
    for i, (idx, row) in enumerate(top_md.iterrows()):
        with cols[i]:
            st.info(f"**{icons[i]} {idx}**\n\n평균권리: {row['총권리금']:,.0f}만\n\n평균월세: {row['월세']:,.0f}만")

    st.divider()

    # 2. 필터링 및 그래프 영역
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 업종별 월세 Range (최소~최대)")
        # Box plot으로 월세 범위 시각화
        fig_rent = px.box(df, x="AI분류업종", y="월세", color="AI분류업종", points="all")
        st.plotly_chart(fig_rent, use_container_width=True)

    with col_chart2:
        st.subheader("💡 AI 추출 키워드 & 솔루션")
        selected_md = st.selectbox("업종 필터링", ["전체"] + list(df['AI분류업종'].unique()))
        
        display_df = df if selected_md == "전체" else df[df['AI분류업종'] == selected_md]
        
        for _, row in display_df.iterrows():
            with st.expander(f"[{row['지역그룹']}] {row['상호명']} ({row['면적(평)']}평 / {row['접도유형']})"):
                st.write(f"**🔑 키워드:** {row['키워드']}")
                st.write(f"**📈 권리금 분석:** 총 {row['총권리금']}만 (영업 {row['영업권리금']} / 시설 {row['시설권리금']}) ➔ {row['권리금평가']}")
                st.write(f"**💬 시장선호도:** 댓글 {row['댓글수']}개 ➔ {row['선호도']}")
                st.write(f"**🤖 MD 솔루션:** {row['MD솔루션']}")

    st.divider()

    # 3. 누적 데이터베이스 (Raw Data)
    st.subheader("📋 누적 매물 Database")
    st.dataframe(df, use_container_width=True)
    
else:
    st.info("👈 좌측 사이드바에서 매물 텍스트를 입력하여 데이터를 누적해주세요.")
