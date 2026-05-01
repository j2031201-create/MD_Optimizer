import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="KT Estate MD Optimizer",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# 커스텀 CSS (모던 스타트업 다크 테마)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── 전역 배경 & 폰트 ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0A0A0F !important;
    color: #E8E6F0 !important;
}

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background: #0F0F1A !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    color: #A09EC0 !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    margin: 2px 0 !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(122, 90, 248, 0.12) !important;
    color: #D4CCFF !important;
}

/* ── 메인 영역 ── */
.main .block-container {
    padding: 2rem 2.5rem !important;
    max-width: 1400px !important;
}

/* ── 히어로 헤더 ── */
.hero-header {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.1;
    background: linear-gradient(135deg, #FFFFFF 0%, #9D8FFF 60%, #6B5CE7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.25rem;
}
.hero-sub {
    font-size: 14px;
    color: #5E5A80;
    font-weight: 300;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.1rem;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(34, 197, 94, 0.12);
    border: 1px solid rgba(34, 197, 94, 0.25);
    color: #4ADE80;
    font-size: 11px;
    font-weight: 500;
    padding: 4px 12px;
    border-radius: 100px;
    letter-spacing: 0.05em;
}

/* ── KPI 카드 ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 1.5rem 0;
}
.kpi-card {
    background: #13131F;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 20px 22px;
    transition: border-color 0.2s;
}
.kpi-card:hover { border-color: rgba(122,90,248,0.35); }
.kpi-label {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4A4870;
    margin-bottom: 8px;
}
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1;
}
.kpi-unit { font-size: 14px; color: #6B68A0; margin-left: 4px; }
.kpi-delta { font-size: 12px; margin-top: 8px; color: #4ADE80; }
.kpi-delta.neg { color: #F87171; }

/* ── 섹션 타이틀 ── */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #FFFFFF;
    letter-spacing: -0.01em;
    margin: 1.8rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.06);
}

/* ── MD 추천 카드 ── */
.md-card {
    background: #13131F;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 10px;
    transition: all 0.2s;
}
.md-card:hover {
    border-color: rgba(122,90,248,0.3);
    background: #17172A;
}
.md-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 10px;
}
.md-tag {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.06em;
    padding: 3px 10px;
    border-radius: 100px;
    background: rgba(122,90,248,0.15);
    color: #A58EFF;
    border: 1px solid rgba(122,90,248,0.25);
}
.md-name {
    font-family: 'Syne', sans-serif;
    font-size: 15px;
    font-weight: 600;
    color: #E8E6FF;
    margin-bottom: 4px;
}
.md-meta { font-size: 12px; color: #4A4870; }
.md-solution {
    font-size: 13px;
    color: #8885B0;
    line-height: 1.6;
    border-top: 1px solid rgba(255,255,255,0.05);
    padding-top: 10px;
    margin-top: 6px;
}

/* ── 수익성 분석 카드 ── */
.profit-card {
    background: linear-gradient(135deg, #13131F 0%, #1A1330 100%);
    border: 1px solid rgba(122,90,248,0.2);
    border-radius: 16px;
    padding: 22px 24px;
}
.profit-title {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #7A5AF8;
    margin-bottom: 16px;
}
.profit-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 13px;
    color: #6B68A0;
}
.profit-row:last-child { border-bottom: none; }
.profit-num { font-weight: 600; color: #C4C0FF; font-family: 'Syne', sans-serif; }
.profit-highlight { color: #4ADE80 !important; font-size: 15px !important; }

/* ── 입력 필드 ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background: #13131F !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #E8E6F0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(122,90,248,0.5) !important;
    box-shadow: 0 0 0 3px rgba(122,90,248,0.1) !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label {
    color: #4A4870 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

/* ── 버튼 ── */
.stButton > button {
    background: linear-gradient(135deg, #7A5AF8, #6B5CE7) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 22px !important;
    transition: all 0.2s !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(122,90,248,0.35) !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #A09EC0 !important;
}

/* ── 데이터프레임 ── */
.stDataFrame {
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrameContainer"] {
    border-radius: 12px !important;
}

/* ── 경고/알림 박스 ── */
.stAlert {
    background: #13131F !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: #8885B0 !important;
}

/* ── 구분선 ── */
hr { border-color: rgba(255,255,255,0.05) !important; }

/* ── 탭 스타일 ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.07) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #4A4870 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #A58EFF !important;
    border-bottom-color: #7A5AF8 !important;
}

/* ── 스피너 ── */
.stSpinner > div { border-top-color: #7A5AF8 !important; }

/* ── 사이드바 로고 ── */
.sidebar-logo {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #FFFFFF;
    margin-bottom: 4px;
}
.sidebar-tagline { font-size: 11px; color: #3A3860; letter-spacing: 0.08em; text-transform: uppercase; }

/* ── 슬라이더 ── */
.stSlider > div > div > div { background: #7A5AF8 !important; }

/* ── 숨기기 ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 상수 & 설정
# ─────────────────────────────────────────────
GOOGLE_WEBHOOK_URL = st.secrets.get("GOOGLE_WEBHOOK_URL", "")

# ─────────────────────────────────────────────
# 세션 상태 초기화
# ─────────────────────────────────────────────
COLS = ['지역그룹', '상호명', '주소', 'AI분류업종', '면적_평', '보증금_만원',
        '월세_만원', '총권리금_만원', '댓글수', '키워드', 'MD솔루션',
        '권장임대료_만원', '권장분양가_만원', '예상수익률_pct', '수집일시']

if 'md_data' not in st.session_state:
    st.session_state.md_data = pd.DataFrame(columns=COLS)
if 'last_extracted' not in st.session_state:
    st.session_state.last_extracted = None

# ─────────────────────────────────────────────
# Gemini API 설정
# ─────────────────────────────────────────────
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')
except KeyError:
    st.error("⚠ GEMINI_API_KEY가 설정되지 않았습니다. Streamlit Secrets를 확인하세요.")
    st.stop()

# ─────────────────────────────────────────────
# AI 프롬프트 (토큰 최적화 버전)
# ─────────────────────────────────────────────
EXTRACTION_PROMPT = """
당신은 부동산·상업시설 MD 전문가입니다.
아래 매물 텍스트에서 정보를 추출하고 분석하여 JSON으로만 반환하세요 (다른 설명 없이).

지역힌트: {region}

매물텍스트:
{text}

반환 형식(JSON만, 없는 항목은 null):
{{
  "상호명": "...",
  "주소": "...",
  "AI분류업종": "F&B|패션|뷰티|라이프스타일|서비스|의료|교육|기타 중 1개",
  "면적_평": 숫자,
  "보증금_만원": 숫자,
  "월세_만원": 숫자,
  "총권리금_만원": 숫자,
  "댓글수": 숫자,
  "키워드": "핵심키워드 3개 쉼표구분",
  "MD솔루션": "이 상권에 적합한 업종과 이유 (2~3문장)",
  "권장임대료_만원": 숫자 (면적·입지 기반 적정 임대료 추정),
  "권장분양가_만원": 숫자 (수익환원법: 월세×12 / 0.045 기준),
  "예상수익률_pct": 숫자 (연간임대수익/분양가×100)
}}
"""

MD_RECOMMEND_PROMPT = """
부동산 MD 전문가로서 아래 데이터를 바탕으로 분석하세요. JSON으로만 답하세요.

데이터 요약:
- 지역: {region}
- 평균 월세: {avg_rent}만원/평
- 평균 보증금: {avg_deposit}만원
- 주요 업종: {top_sectors}
- 건수: {count}건

반환형식:
{{
  "상권등급": "A|B|C|D",
  "등급이유": "...",
  "추천MD_1": {{"업종": "...", "이유": "...", "권장임대료": 숫자}},
  "추천MD_2": {{"업종": "...", "이유": "...", "권장임대료": 숫자}},
  "추천MD_3": {{"업종": "...", "이유": "...", "권장임대료": 숫자}},
  "리스크": "주요 리스크 1문장",
  "기회": "주요 기회 1문장"
}}
"""


# ─────────────────────────────────────────────
# 유틸 함수
# ─────────────────────────────────────────────
def safe_json(text: str) -> dict:
    """모델 응답에서 JSON 추출 (코드블록 제거)"""
    text = re.sub(r'```json|```', '', text).strip()
    try:
        return json.loads(text)
    except Exception:
        return {}

def to_gsheet(row: dict):
    """구글 시트 Webhook 전송 (설정 없으면 skip)"""
    if not GOOGLE_WEBHOOK_URL or "여기에" in GOOGLE_WEBHOOK_URL:
        return
    try:
        requests.post(GOOGLE_WEBHOOK_URL, json=row, timeout=5)
    except Exception:
        pass

def fmt_num(v, suffix=""):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return f"{int(v):,}{suffix}"

def calc_profitability(monthly_rent, area, purchase_price):
    """수익성 지표 계산"""
    if not all([monthly_rent, area, purchase_price]) or purchase_price == 0:
        return {}
    annual_rent = monthly_rent * 12
    yield_rate = (annual_rent / purchase_price) * 100
    payback_years = purchase_price / annual_rent if annual_rent > 0 else 0
    rent_per_pyeong = monthly_rent / area if area > 0 else 0
    return {
        "연간임대수익": annual_rent,
        "수익률": round(yield_rate, 2),
        "회수기간_년": round(payback_years, 1),
        "평당임대료": round(rent_per_pyeong, 1)
    }


# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">◈ KT Estate</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">MD Optimizer · v2.0</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    app_mode = st.radio(
        "mode",
        ["📥  데이터 수집", "📊  상권 분석", "💰  수익성 계산기"],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    total = len(st.session_state.md_data)
    st.markdown(f"""
    <div style='font-size:11px; color:#3A3860; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;'>누적 데이터</div>
    <div style='font-family:Syne,sans-serif; font-size:2rem; font-weight:700; color:#FFFFFF;'>{total}<span style='font-size:14px; color:#4A4870; margin-left:4px;'>건</span></div>
    """, unsafe_allow_html=True)

    if total > 0:
        regions = st.session_state.md_data['지역그룹'].value_counts()
        st.markdown("<div style='margin-top:12px;'>", unsafe_allow_html=True)
        for region, cnt in regions.items():
            pct = int(cnt / total * 100)
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; font-size:12px; margin-bottom:6px; color:#4A4870;'>
                <span>{region}</span>
                <span style='color:#6B68A0;'>{cnt}건</span>
            </div>
            <div style='background:#1A1A2E; border-radius:4px; height:3px; margin-bottom:8px;'>
                <div style='background:#7A5AF8; width:{pct}%; height:3px; border-radius:4px;'></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 히어로 헤더
# ─────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="hero-sub">Commercial Real Estate Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-header">상업시설 MD 최적화 플랫폼</div>', unsafe_allow_html=True)
with col_h2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    sync_status = "🟢 구글시트 동기화" if (GOOGLE_WEBHOOK_URL and "여기에" not in GOOGLE_WEBHOOK_URL) else "⚪ 로컬 모드"
    st.markdown(f'<div class="hero-badge">{sync_status}</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# KPI 대시보드 (데이터 있을 때만)
df_all = st.session_state.md_data
if not df_all.empty:
    avg_rent = df_all['월세_만원'].mean() if '월세_만원' in df_all else 0
    avg_yield = df_all['예상수익률_pct'].mean() if '예상수익률_pct' in df_all else 0
    avg_sale = df_all['권장분양가_만원'].mean() if '권장분양가_만원' in df_all else 0
    top_sector = df_all['AI분류업종'].mode()[0] if 'AI분류업종' in df_all and not df_all['AI분류업종'].isna().all() else "—"

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">누적 매물</div>
            <div class="kpi-value">{len(df_all)}<span class="kpi-unit">건</span></div>
            <div class="kpi-delta">↑ 실시간 업데이트</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">평균 월세</div>
            <div class="kpi-value">{int(avg_rent):,}<span class="kpi-unit">만원</span></div>
            <div class="kpi-delta">전체 지역 평균</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">평균 수익률</div>
            <div class="kpi-value">{avg_yield:.1f}<span class="kpi-unit">%</span></div>
            <div class="kpi-delta {'kpi-delta' if avg_yield >= 4.5 else 'kpi-delta neg'}">목표 4.5% 기준</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">주요 업종</div>
            <div class="kpi-value" style="font-size:1.3rem;">{top_sector}</div>
            <div class="kpi-delta">최다 수집 업종</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# 모드 A: 데이터 수집기
# ═══════════════════════════════════════════════════════
if "데이터 수집" in app_mode:
    st.markdown('<div class="section-title">신규 매물 데이터 수집</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:13px; color:#4A4870; margin-bottom:1.5rem;">매물 텍스트를 붙여넣으면 AI가 핵심 데이터를 자동 추출하고 수익성을 분석합니다.</p>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        input_region = st.text_input("수집 지역", placeholder="예: 송파구 잠실동", value="송파구")
        raw_text = st.text_area(
            "매물 텍스트 붙여넣기",
            height=260,
            placeholder="네이버 부동산, 직방, 상가정보 등에서 복사한 매물 설명을 여기에 붙여넣으세요.\n\n예시:\n위치: 강남구 역삼동 테헤란로\n면적: 25평\n보증금: 5,000만원 / 월세: 350만원\n권리금: 3,000만원\n..."
        )
        btn_extract = st.button("AI 분석 및 저장", type="primary", use_container_width=True)

    with col_right:
        if st.session_state.last_extracted:
            d = st.session_state.last_extracted
            st.markdown('<div class="section-title" style="margin-top:0;">방금 추출된 데이터</div>', unsafe_allow_html=True)

            prof = calc_profitability(
                d.get('월세_만원'), d.get('면적_평'), d.get('권장분양가_만원')
            )
            yield_color = "#4ADE80" if prof.get('수익률', 0) >= 4.5 else "#F87171"

            st.markdown(f"""
            <div class="profit-card">
                <div class="profit-title">📍 {d.get('상호명','—')} · {d.get('AI분류업종','—')}</div>
                <div class="profit-row">
                    <span>주소</span><span class="profit-num">{d.get('주소','—')}</span>
                </div>
                <div class="profit-row">
                    <span>면적</span><span class="profit-num">{fmt_num(d.get('면적_평'))}평</span>
                </div>
                <div class="profit-row">
                    <span>월세 / 보증금</span>
                    <span class="profit-num">{fmt_num(d.get('월세_만원'))}만 / {fmt_num(d.get('보증금_만원'))}만</span>
                </div>
                <div class="profit-row">
                    <span>권리금</span><span class="profit-num">{fmt_num(d.get('총권리금_만원'))}만원</span>
                </div>
                <div class="profit-row">
                    <span>권장 임대료</span><span class="profit-num">{fmt_num(d.get('권장임대료_만원'))}만원</span>
                </div>
                <div class="profit-row">
                    <span>권장 분양가</span><span class="profit-num">{fmt_num(d.get('권장분양가_만원'))}만원</span>
                </div>
                <div class="profit-row" style="margin-top:4px;">
                    <span style="font-weight:600; color:#C4C0FF;">예상 수익률</span>
                    <span class="profit-num profit-highlight" style="color:{yield_color};">
                        {prof.get('수익률','—')}%
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="md-card" style="margin-top:12px;">
                <div class="md-name">AI MD 솔루션</div>
                <div class="md-solution">{d.get('MD솔루션','—')}</div>
                <div style="margin-top:10px; font-size:12px; color:#4A4870;">키워드: {d.get('키워드','—')}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:#13131F; border:1px dashed rgba(255,255,255,0.1); border-radius:14px;
                        padding:40px; text-align:center; height:340px; display:flex; flex-direction:column;
                        align-items:center; justify-content:center;'>
                <div style='font-size:32px; margin-bottom:12px; opacity:0.3;'>◈</div>
                <div style='font-size:13px; color:#3A3860;'>좌측에 매물 텍스트를 입력하면<br>AI 분석 결과가 여기에 표시됩니다.</div>
            </div>
            """, unsafe_allow_html=True)

    # 추출 실행
    if btn_extract and raw_text.strip():
        with st.spinner("AI 분석 중..."):
            prompt = EXTRACTION_PROMPT.format(region=input_region, text=raw_text[:3000])
            try:
                resp = model.generate_content(prompt)
                data = safe_json(resp.text)
                if data:
                    data['지역그룹'] = input_region
                    data['수집일시'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    # 누락된 칼럼 채우기
                    for c in COLS:
                        if c not in data:
                            data[c] = None

                    new_row = pd.DataFrame([data])
                    st.session_state.md_data = pd.concat(
                        [st.session_state.md_data, new_row], ignore_index=True
                    )
                    st.session_state.last_extracted = data
                    to_gsheet(data)
                    st.success(f"✓ '{data.get('상호명','매물')}' 분석 완료 — DB에 저장되었습니다.")
                    st.rerun()
                else:
                    st.error("JSON 파싱 실패. 텍스트를 더 명확하게 입력해 주세요.")
            except Exception as e:
                st.error(f"API 오류: {e}")
    elif btn_extract:
        st.warning("매물 텍스트를 입력해 주세요.")


# ═══════════════════════════════════════════════════════
# 모드 B: 상권 분석
# ═══════════════════════════════════════════════════════
elif "상권 분석" in app_mode:
    st.markdown('<div class="section-title">상권 분석 및 MD 추천</div>', unsafe_allow_html=True)

    if df_all.empty:
        st.warning("아직 수집된 데이터가 없습니다. '데이터 수집' 탭에서 먼저 매물을 입력해 주세요.")
        st.stop()

    # 필터
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    with col_f1:
        regions = ["전체"] + sorted(df_all['지역그룹'].dropna().unique().tolist())
        sel_region = st.selectbox("지역 선택", regions)
    with col_f2:
        sectors = ["전체"] + sorted(df_all['AI분류업종'].dropna().unique().tolist())
        sel_sector = st.selectbox("업종 필터", sectors)
    with col_f3:
        st.markdown("<br>", unsafe_allow_html=True)
        do_ai = st.button("AI 상권 분석", type="primary")

    # 필터 적용
    df = df_all.copy()
    if sel_region != "전체":
        df = df[df['지역그룹'] == sel_region]
    if sel_sector != "전체":
        df = df[df['AI분류업종'] == sel_sector]

    st.markdown(f'<p style="font-size:12px; color:#3A3860; margin:0.5rem 0 1rem;">{len(df)}건 조회</p>', unsafe_allow_html=True)

    # 차트
    tab1, tab2, tab3 = st.tabs(["📈  임대료 분포", "💡  수익률 분석", "📋  전체 데이터"])

    with tab1:
        col_c1, col_c2 = st.columns(2, gap="large")
        with col_c1:
            if not df.empty and '월세_만원' in df and df['월세_만원'].notna().any():
                fig = px.box(
                    df.dropna(subset=['AI분류업종', '월세_만원']),
                    x="AI분류업종", y="월세_만원", color="AI분류업종",
                    title="업종별 월세 분포"
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#6B68A0', size=12),
                    title_font=dict(color='#FFFFFF', size=14),
                    showlegend=False,
                    margin=dict(l=0, r=0, t=40, b=0),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                )
                st.plotly_chart(fig, use_container_width=True)
        with col_c2:
            if not df.empty and '면적_평' in df and '월세_만원' in df:
                df_plot = df.dropna(subset=['면적_평', '월세_만원'])
                if not df_plot.empty:
                    fig2 = px.scatter(
                        df_plot, x="면적_평", y="월세_만원",
                        color="AI분류업종", size_max=15,
                        title="면적 vs 월세 분포",
                        hover_data=['상호명', '지역그룹']
                    )
                    fig2.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#6B68A0', size=12),
                        title_font=dict(color='#FFFFFF', size=14),
                        margin=dict(l=0, r=0, t=40, b=0),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                    )
                    st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        if not df.empty and '예상수익률_pct' in df and df['예상수익률_pct'].notna().any():
            col_y1, col_y2 = st.columns(2, gap="large")
            with col_y1:
                df_yield = df.dropna(subset=['예상수익률_pct', 'AI분류업종'])
                fig3 = px.bar(
                    df_yield.groupby('AI분류업종')['예상수익률_pct'].mean().reset_index(),
                    x='AI분류업종', y='예상수익률_pct',
                    title='업종별 평균 수익률 (%)',
                    color='예상수익률_pct',
                    color_continuous_scale=[[0,'#3A1A8A'],[0.5,'#7A5AF8'],[1,'#A78BFA']]
                )
                fig3.add_hline(y=4.5, line_dash="dot", line_color="#4ADE80",
                               annotation_text="목표 4.5%", annotation_font_color="#4ADE80")
                fig3.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#6B68A0', size=12),
                    title_font=dict(color='#FFFFFF', size=14),
                    showlegend=False,
                    coloraxis_showscale=False,
                    margin=dict(l=0, r=0, t=40, b=0),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                )
                st.plotly_chart(fig3, use_container_width=True)
            with col_y2:
                df_yield2 = df.dropna(subset=['권장분양가_만원', '예상수익률_pct', '상호명'])
                if not df_yield2.empty:
                    fig4 = px.scatter(
                        df_yield2, x='권장분양가_만원', y='예상수익률_pct',
                        text='상호명', title='분양가 vs 수익률',
                        color='예상수익률_pct',
                        color_continuous_scale=[[0,'#F87171'],[0.5,'#FBBF24'],[1,'#4ADE80']]
                    )
                    fig4.add_hline(y=4.5, line_dash="dot", line_color="#4ADE80")
                    fig4.update_traces(textposition='top center', textfont=dict(size=10, color='#6B68A0'))
                    fig4.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#6B68A0', size=12),
                        title_font=dict(color='#FFFFFF', size=14),
                        coloraxis_showscale=False,
                        margin=dict(l=0, r=0, t=40, b=0),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                    )
                    st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("수익률 데이터가 아직 없습니다.")

    with tab3:
        display_df = df.copy()
        display_df.index = range(1, len(display_df) + 1)
        st.dataframe(display_df, use_container_width=True, height=400)

    # AI 상권 분석
    if do_ai and not df.empty:
        with st.spinner("AI 상권 분석 중 (약 10초)..."):
            avg_rent = df['월세_만원'].mean() if df['월세_만원'].notna().any() else 0
            avg_dep = df['보증금_만원'].mean() if df['보증금_만원'].notna().any() else 0
            top_sec = df['AI분류업종'].value_counts().head(3).index.tolist() if '월세_만원' in df else []
            prompt = MD_RECOMMEND_PROMPT.format(
                region=sel_region,
                avg_rent=f"{avg_rent:.0f}",
                avg_deposit=f"{avg_dep:.0f}",
                top_sectors=", ".join(top_sec),
                count=len(df)
            )
            try:
                resp = model.generate_content(prompt)
                rec = safe_json(resp.text)
                if rec:
                    st.markdown('<div class="section-title">AI 상권 분석 결과</div>', unsafe_allow_html=True)
                    grade_color = {"A":"#4ADE80","B":"#A78BFA","C":"#FBBF24","D":"#F87171"}.get(rec.get("상권등급","C"), "#6B68A0")
                    col_g1, col_g2 = st.columns([1, 3])
                    with col_g1:
                        st.markdown(f"""
                        <div style='text-align:center; background:#13131F; border:1px solid rgba(255,255,255,0.08);
                                    border-radius:16px; padding:30px;'>
                            <div style='font-size:56px; font-family:Syne,sans-serif; font-weight:800; color:{grade_color};'>
                                {rec.get('상권등급','—')}
                            </div>
                            <div style='font-size:12px; color:#3A3860; margin-top:8px;'>상권 등급</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_g2:
                        st.markdown(f"""
                        <div class='profit-card'>
                            <div class='profit-title'>등급 분석</div>
                            <p style='font-size:13px; color:#8885B0; margin-bottom:12px;'>{rec.get('등급이유','—')}</p>
                            <div class='profit-row'><span>기회</span><span class='profit-num'>{rec.get('기회','—')}</span></div>
                            <div class='profit-row'><span>리스크</span><span class='profit-num' style='color:#F87171;'>{rec.get('리스크','—')}</span></div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown('<div class="section-title" style="margin-top:1.5rem;">추천 MD 업종</div>', unsafe_allow_html=True)
                    md_cols = st.columns(3, gap="medium")
                    for i, col in enumerate(md_cols, 1):
                        key = f"추천MD_{i}"
                        if key in rec:
                            m = rec[key]
                            with col:
                                st.markdown(f"""
                                <div class='md-card'>
                                    <div class='md-card-header'>
                                        <div class='md-tag'>{['1순위','2순위','3순위'][i-1]}</div>
                                        <div style='font-size:12px; color:#4ADE80;'>
                                            권장임대료 {fmt_num(m.get('권장임대료'))}만원
                                        </div>
                                    </div>
                                    <div class='md-name'>{m.get('업종','—')}</div>
                                    <div class='md-solution'>{m.get('이유','—')}</div>
                                </div>
                                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"분석 오류: {e}")


# ═══════════════════════════════════════════════════════
# 모드 C: 수익성 계산기
# ═══════════════════════════════════════════════════════
elif "수익성 계산기" in app_mode:
    st.markdown('<div class="section-title">분양가 수익성 시뮬레이터</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:13px; color:#4A4870; margin-bottom:1.5rem;">임대 조건을 입력하면 적정 분양가와 수익률을 즉시 계산합니다.</p>', unsafe_allow_html=True)

    col_inp, col_out = st.columns([1, 1], gap="large")

    with col_inp:
        area = st.number_input("면적 (평)", min_value=1, max_value=500, value=20, step=1)
        monthly_rent = st.number_input("예상 월세 (만원)", min_value=0, max_value=10000, value=300, step=10)
        deposit = st.number_input("보증금 (만원)", min_value=0, max_value=100000, value=3000, step=100)
        premium = st.number_input("권리금 (만원)", min_value=0, max_value=50000, value=0, step=100)
        target_yield = st.slider("목표 수익률 (%)", min_value=2.0, max_value=10.0, value=4.5, step=0.1)

    with col_out:
        # 수익환원법 기반 계산
        annual_rent = monthly_rent * 12
        # 분양가 = 연간임대료 / 목표수익률
        recommended_price = int(annual_rent / (target_yield / 100)) if target_yield > 0 else 0
        # 실제 수익률 (입력된 분양가 기준 — 여기선 권장 분양가로 계산)
        actual_yield = target_yield  # 권장가 기준이라 동일
        rent_per_pyeong = monthly_rent / area if area > 0 else 0
        payback = recommended_price / annual_rent if annual_rent > 0 else 0

        st.markdown(f"""
        <div class="profit-card" style="margin-top:0;">
            <div class="profit-title">수익성 분석 결과</div>
            <div class="profit-row">
                <span>면적당 임대료</span>
                <span class="profit-num">{rent_per_pyeong:.1f}만원/평</span>
            </div>
            <div class="profit-row">
                <span>연간 임대수익</span>
                <span class="profit-num">{annual_rent:,}만원</span>
            </div>
            <div class="profit-row">
                <span>보증금 운용수익 (연 2%)</span>
                <span class="profit-num">{int(deposit * 0.02):,}만원</span>
            </div>
            <div class="profit-row">
                <span>총 연간 수익</span>
                <span class="profit-num">{int(annual_rent + deposit * 0.02):,}만원</span>
            </div>
            <div class="profit-row" style="padding-top:12px; margin-top:4px; border-top:1px solid rgba(122,90,248,0.2);">
                <span style="font-weight:600; color:#C4C0FF; font-size:15px;">권장 분양가</span>
                <span class="profit-num profit-highlight">{recommended_price:,}만원</span>
            </div>
            <div class="profit-row">
                <span>권리금 포함 총 투자금</span>
                <span class="profit-num">{recommended_price + premium:,}만원</span>
            </div>
            <div class="profit-row">
                <span>투자 회수 기간</span>
                <span class="profit-num">{payback:.1f}년</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 수익률 게이지
        gauge_val = min(target_yield / 10, 1.0)
        gauge_color = "#4ADE80" if target_yield >= 4.5 else "#FBBF24" if target_yield >= 3.0 else "#F87171"
        st.markdown(f"""
        <div style='background:#13131F; border:1px solid rgba(255,255,255,0.07); border-radius:14px;
                    padding:20px; margin-top:12px; text-align:center;'>
            <div style='font-size:11px; color:#3A3860; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:8px;'>
                목표 수익률
            </div>
            <div style='font-family:Syne,sans-serif; font-size:3rem; font-weight:800; color:{gauge_color};'>
                {target_yield:.1f}%
            </div>
            <div style='background:#1A1A2E; border-radius:6px; height:6px; margin-top:12px;'>
                <div style='background:{gauge_color}; width:{int(gauge_val*100)}%; height:6px; border-radius:6px;
                            transition:width 0.4s ease;'></div>
            </div>
            <div style='display:flex; justify-content:space-between; font-size:11px; color:#3A3860; margin-top:4px;'>
                <span>0%</span><span>목표 4.5%</span><span>10%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 비교 시나리오 차트
    st.markdown('<div class="section-title">시나리오 비교</div>', unsafe_allow_html=True)
    yields = [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
    prices = [int(annual_rent / (y / 100)) for y in yields]
    fig_s = go.Figure()
    fig_s.add_trace(go.Bar(
        x=[f"{y}%" for y in yields],
        y=prices,
        marker_color=['#F87171' if y < 4.5 else '#4ADE80' for y in yields],
        text=[f"{p:,}만원" for p in prices],
        textposition='outside',
        textfont=dict(color='#6B68A0', size=11)
    ))
    fig_s.update_layout(
        title="수익률별 권장 분양가",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#6B68A0', size=12),
        title_font=dict(color='#FFFFFF', size=14),
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        showlegend=False
    )
    st.plotly_chart(fig_s, use_container_width=True)
