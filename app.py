import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import math
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from supabase import create_client, Client

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="KT Estate MD Optimizer",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="auto"
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

html, body, .stApp { font-family: 'DM Sans', sans-serif !important; background-color: #F8F9FA !important; color: #1E293B !important; }
#MainMenu, footer { display: none !important; }
.main .block-container { padding: 1rem 2.5rem 3rem !important; max-width: 1400px !important; margin-top: 2rem !important; }
[data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; }
[data-testid="stSidebar"] * { color: #334155 !important; }
[data-testid="stSidebar"] .stRadio > div { gap: 2px !important; }
[data-testid="stSidebar"] .stRadio label { font-family: 'DM Sans', sans-serif !important; font-size: 14px !important; font-weight: 500 !important; color: #334155 !important; padding: 9px 14px !important; border-radius: 8px !important; transition: background 0.15s !important; }
[data-testid="stSidebar"] .stRadio label:hover { background: #F1F5F9 !important; }
.hero-sub { font-size: 11px; font-weight: 600; color: #6366F1; letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 6px; }
.hero-header { font-family: 'DM Sans', sans-serif; font-size: 2.4rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.1; color: #0F172A; margin-bottom: 0; }
.hero-header .md-word { font-weight: 400; color: #4F46E5; }
.hero-badge { display: inline-flex; align-items: center; gap: 6px; background: #DCFCE7; border: 1px solid #BBF7D0; color: #16A34A; font-size: 11px; font-weight: 600; padding: 4px 12px; border-radius: 100px; letter-spacing: 0.05em; }
.kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin: 1.4rem 0; }
.kpi-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 18px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); transition: border-color .2s, box-shadow .2s; }
.kpi-card:hover { border-color: #818CF8; box-shadow: 0 4px 20px rgba(99,102,241,.08); }
.kpi-label { font-size: 10px; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: #64748B; margin-bottom: 8px; }
.kpi-value { font-family: 'DM Sans',sans-serif; font-size: 1.9rem; font-weight: 700; color: #0F172A; line-height: 1; }
.kpi-unit  { font-size: 13px; color: #64748B; margin-left: 3px; font-weight: 400; }
.kpi-delta { font-size: 11px; margin-top: 7px; color: #16A34A; font-weight: 500; }
.kpi-delta.neg { color: #DC2626; }
.section-title { font-family: 'DM Sans', sans-serif; font-size: 1.1rem; font-weight: 700; color: #0F172A; letter-spacing: 0; margin: 1.6rem 0 .7rem; display: flex; align-items: center; gap: 10px; }
.section-title::after { content:''; flex:1; height:1px; background: #E2E8F0; }
.page-sub { font-size: 13px; color: #64748B; margin-bottom: 1.4rem; font-weight: 400; }
.white-card, .profit-card, .md-card { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:20px 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
.md-card { padding:16px 18px; margin-bottom:8px; border-radius:12px; transition:all .2s; }
.md-card:hover { border-color:#818CF8; box-shadow:0 4px 16px rgba(99,102,241,.08); }
.profit-title { font-size:11px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:#4F46E5; margin-bottom:14px; }
.profit-row { display:flex; justify-content:space-between; align-items:center; padding:7px 0; border-bottom:1px solid #F1F5F9; font-size:13px; color:#475569; font-weight:400; }
.profit-row:last-child { border-bottom:none; }
.profit-num { font-weight:600; color:#0F172A; font-family:'DM Sans',sans-serif; }
.profit-highlight { color:#16A34A !important; font-size:14px !important; font-weight:700 !important; }
.md-card-header { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; }
.md-tag { font-size:10px; font-weight:700; letter-spacing:.07em; padding:3px 10px; border-radius:100px; background:#EEF2FF; color:#4F46E5; border:1px solid #C7D2FE; }
.md-name { font-size:14px; font-weight:700; color:#0F172A; margin-bottom:4px; }
.md-solution { font-size:12px; color:#475569; line-height:1.65; border-top:1px solid #F1F5F9; padding-top:9px; margin-top:5px; }
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input { background:#FFFFFF !important; border:1.5px solid #CBD5E1 !important; border-radius:9px !important; color:#0F172A !important; font-family:'DM Sans',sans-serif !important; font-size:14px !important; }
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus, .stNumberInput>div>div>input:focus { border-color:#4F46E5 !important; box-shadow:0 0 0 3px rgba(79,70,229,.1) !important; }
.stTextInput label, .stTextArea label, .stNumberInput label, .stSlider label, .stSelectbox label { color:#475569 !important; font-size:11px !important; font-weight:700 !important; letter-spacing:.08em !important; text-transform:uppercase !important; font-family:'DM Sans',sans-serif !important; }
.stButton>button { background:linear-gradient(135deg,#6366F1 0%,#4F46E5 100%) !important; color:#FFFFFF !important; border:none !important; border-radius:9px !important; font-family:'DM Sans',sans-serif !important; font-size:14px !important; font-weight:600 !important; padding:10px 22px !important; transition:all .18s !important; letter-spacing:.01em !important; }
.stButton>button:hover { transform:translateY(-1px) !important; box-shadow:0 8px 24px rgba(79,70,229,.3) !important; }
.sidebar-tagline { font-family:'DM Sans',sans-serif; font-size:12px; font-weight:800; color:#0F172A; letter-spacing:.12em; text-transform:uppercase; }
.sector-row { display:flex; justify-content:space-between; align-items:center; padding:5px 0; border-bottom:1px solid #F1F5F9; font-size:12px; font-family:'DM Sans',sans-serif; color:#475569; }
.sector-row:last-child { border-bottom:none; }
.sector-cnt { font-weight:700; color:#64748B; font-size:13px; }
.sector-total { font-size:12px; font-weight:700; color:#4F46E5; padding-top:6px; border-top:1px solid #C7D2FE; margin-top:4px; font-family:'DM Sans',sans-serif; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 핵심 유틸리티 (에러 방지용)
# ─────────────────────────────────────────────
def clean_num(val):
    """문자열에 섞인 콤마를 제거하고 안전하게 실수로 변환 (NaN 방지)"""
    if val is None or val == "": return 0.0
    try:
        v = float(str(val).replace(",", ""))
        return 0.0 if math.isnan(v) else v
    except (ValueError, TypeError):
        return 0.0

def safe_json(text: str) -> dict:
    """LLM이 뱉은 마크다운 잔재를 안전하게 제거 (에러 수정 완료)"""
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        return {}

def fmt(v, sfx=""):
    """숫자를 천 단위 콤마 포맷으로 변경"""
    if v is None or v == "": return "—"
    try:
        return f"{int(float(v)):,}{sfx}"
    except Exception:
        return str(v)

def calc_profit(rent, deposit, price):
    """보증금을 차감한 실투자금 기준 수익률 계산"""
    r = clean_num(rent)
    d = clean_num(deposit)
    p = clean_num(price)
    
    if r <= 0 or p <= 0:
        return {"수익률": 0.0, "회수기간": 0.0}
        
    annual = r * 12
    invest = p - d # 실투자금 = 분양가 - 보증금
    
    if invest <= 0:
        return {"수익률": 0.0, "회수기간": 0.0}
        
    return {
        "수익률": round((annual / invest) * 100, 2),
        "회수기간": round(invest / annual, 1) if annual > 0 else 0
    }

CHART_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#64748B', size=11, family='DM Sans'),
    title_font=dict(color='#0F172A', size=13, family='DM Sans'),
    margin=dict(l=0, r=0, t=36, b=0),
    xaxis=dict(gridcolor='rgba(0,0,0,0.05)', tickfont=dict(color='#64748B', family='DM Sans')),
    yaxis=dict(gridcolor='rgba(0,0,0,0.05)', tickfont=dict(color='#64748B', family='DM Sans')),
)
PALETTE = ["#4F46E5","#818CF8","#C7D2FE","#A78BFA","#DDD6FE"]

# ─────────────────────────────────────────────
# Supabase 연동 로직
# ─────────────────────────────────────────────
@st.cache_resource
def init_supabase() -> Client:
    try:
        url = st.secrets["supabase"]["URL"]
        key = st.secrets["supabase"]["KEY"]
        return create_client(url, key)
    except Exception:
        return None

supabase = init_supabase()
sb_live = supabase is not None

def insert_to_supabase(data: dict) -> bool:
    if not sb_live:
        return False
    try:
        clean_data = {k: v for k, v in data.items() if v is not None}
        response = supabase.table('md_properties').insert(clean_data).execute()
        return len(response.data) > 0 if hasattr(response, 'data') else False
    except Exception as e:
        st.error(f"Supabase DB 저장 실패: {e}")
        return False

@st.cache_data(ttl=60)
def fetch_from_supabase():
    """앱 시작 시 과거 DB 데이터 불러오기"""
    if sb_live:
        try:
            response = supabase.table('md_properties').select('*').execute()
            if response.data:
                return pd.DataFrame(response.data)
        except Exception:
            pass
    return pd.DataFrame()

# ─────────────────────────────────────────────
# 세션 & API 설정
# ─────────────────────────────────────────────
COLS = ['지역그룹','상호명','주소','AI분류업종','면적_평','보증금_만원',
        '월세_만원','총권리금_만원','키워드','MD솔루션',
        '권장임대료_만원','권장분양가_만원','예상수익률_pct','수집일시']

if 'md_data' not in st.session_state or st.session_state.md_data.empty:
    db_data = fetch_from_supabase()
    st.session_state.md_data = db_data if not db_data.empty else pd.DataFrame(columns=COLS)

if 'last_extracted' not in st.session_state:
    st.session_state.last_extracted = None

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')
except KeyError:
    st.error("⚠ GEMINI_API_KEY가 설정되지 않았습니다.")
    st.stop()

EXTRACTION_PROMPT = """
당신은 부동산·상업시설 MD 전문가입니다.
아래 매물 텍스트에서 정보를 추출하여 JSON만 반환하세요.
지역힌트: {region}
매물텍스트: {text}

반환형식(JSON만, 없는 항목은 null):
{{
  "상호명":"...","주소":"...",
  "AI분류업종":"F&B|패션|뷰티|라이프스타일|서비스|의료|교육|기타 중 1개",
  "면적_평":숫자,"보증금_만원":숫자,"월세_만원":숫자,"총권리금_만원":숫자,
  "키워드":"핵심키워드3개 쉼표구분",
  "MD솔루션":"이 상권에 적합한 업종과 이유(2~3문장)",
  "권장임대료_만원":숫자,"권장분양가_만원":숫자,"예상수익률_pct":숫자
}}
"""

MD_RECOMMEND_PROMPT = """
부동산 MD 전문가로서 아래 데이터를 분석하고 JSON만 반환하세요.
지역:{region} / 평균월세:{avg_rent}만원 / 평균보증금:{avg_deposit}만원
주요업종:{top_sectors} / 건수:{count}건

{{
  "상권등급":"A|B|C|D","등급이유":"...",
  "추천MD_1":{{"업종":"...","이유":"...","권장임대료":숫자}},
  "추천MD_2":{{"업종":"...","이유":"...","권장임대료":숫자}},
  "추천MD_3":{{"업종":"...","이유":"...","권장임대료":숫자}},
  "리스크":"...","기회":"..."
}}
"""

# ═══════════════════════════════════════════════════════
# 사이드바
# ═══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-tagline">◈ MD Optimizer · v2.0</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    app_mode = st.radio("mode", ["📥  데이터 수집", "🏷  MD 추천", "💰  수익성 계산기"], label_visibility="collapsed")
    st.markdown("<br><hr>", unsafe_allow_html=True)

    df_all = st.session_state.md_data
    total  = len(df_all)
    st.markdown("<div style='font-size:10px;color:#64748B;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;'>누적 데이터</div>", unsafe_allow_html=True)

    if total == 0:
        st.markdown("<div style='font-size:1.6rem;font-weight:800;color:#0F172A;'>0<span style='font-size:12px;color:#64748B;margin-left:4px;'>건</span></div>", unsafe_allow_html=True)
    else:
        if 'AI분류업종' in df_all.columns:
            sc = df_all['AI분류업종'].dropna().value_counts()
            rows = "".join(f"<div class='sector-row'><span>{s}</span><span class='sector-cnt'>{c}건</span></div>" for s, c in sc.items())
            rows += f"<div class='sector-total'>총 {total}건</div>"
            st.markdown(f"<div style='margin-top:4px;'>{rows}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    dot_c   = "#16A34A" if sb_live else "#DC2626"
    dot_t   = "Supabase 연결됨" if sb_live else "DB 연결 실패"
    st.markdown(f"<div style='display:flex;align-items:center;gap:7px;font-size:12px;font-weight:600;color:#475569;'><span style='width:8px;height:8px;border-radius:50%;background:{dot_c};display:inline-block;'></span>{dot_t}</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# 히어로 헤더 & KPI (수익률 계산 최적화)
# ═══════════════════════════════════════════════════════
c_h1, c_h2 = st.columns([3, 1])
with c_h1:
    st.markdown('<div class="hero-sub">Commercial Real Estate Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-header">상업시설 <span class="md-word">MD</span> 최적화 플랫폼</div>', unsafe_allow_html=True)
with c_h2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    badge_txt = "🟢 Supabase 연동" if sb_live else "🔴 DB 연결 안됨"
    st.markdown(f'<div class="hero-badge">{badge_txt}</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if not df_all.empty:
    def _safe_mean(col):
        if col in df_all.columns:
            s = pd.to_numeric(df_all[col], errors='coerce').dropna()
            s = s[s > 0]
            return s.mean() if not s.empty else 0
        return 0

    avg_rent  = _safe_mean('월세_만원')
    avg_yield = _safe_mean('예상수익률_pct')
    top_sec   = df_all['AI분류업종'].mode()[0] if 'AI분류업종' in df_all and not df_all['AI분류업종'].isna().all() else "—"
    dcls      = "kpi-delta" if avg_yield >= 4.5 else "kpi-delta neg"

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">누적 매물</div>
        <div class="kpi-value">{len(df_all)}<span class="kpi-unit">건</span></div>
        <div class="kpi-delta">↑ DB 실시간 연동</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">평균 월세</div>
        <div class="kpi-value">{int(avg_rent):,}<span class="kpi-unit">만원</span></div>
        <div class="kpi-delta">전체 지역 평균</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">평균 수익률</div>
        <div class="kpi-value">{avg_yield:.1f}<span class="kpi-unit">%</span></div>
        <div class="{dcls}">목표 4.5% 기준</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">주요 업종</div>
        <div class="kpi-value" style="font-size:1.4rem;">{top_sec}</div>
        <div class="kpi-delta">최다 수집 업종</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# 모드 A: 데이터 수집 (안전한 계산 및 저장)
# ═══════════════════════════════════════════════════════
if "데이터 수집" in app_mode:
    st.markdown('<div class="section-title">신규 매물 데이터 수집</div>', unsafe_allow_html=True)
    
    col_L, col_R = st.columns([1, 1], gap="large")

    with col_L:
        input_region = st.text_input("수집 지역", placeholder="예: 송파구 잠실동", value="송파구")
        raw_text = st.text_area("매물 텍스트 붙여넣기", height=240)
        btn_extract = st.button("AI 분석 및 저장", type="primary", use_container_width=True)

    with col_R:
        result_ph = st.empty()

        if not btn_extract:
            if st.session_state.last_extracted:
                d = st.session_state.last_extracted
                pr = calc_profit(d.get('월세_만원', 0), d.get('보증금_만원', 0), d.get('권장분양가_만원', 0))
                yc = "#16A34A" if pr.get('수익률', 0) >= 4.5 else "#DC2626"
                
                result_ph.markdown(f"""
                <div class="profit-card">
                  <div class="profit-title">📍 {d.get('상호명','—')} · {d.get('AI분류업종','—')}</div>
                  <div class="profit-row"><span>주소</span><span class="profit-num">{d.get('주소','—')}</span></div>
                  <div class="profit-row"><span>면적</span><span class="profit-num">{fmt(d.get('면적_평'))}평</span></div>
                  <div class="profit-row"><span>월세 / 보증금</span><span class="profit-num">{fmt(d.get('월세_만원'))}만 / {fmt(d.get('보증금_만원'))}만</span></div>
                  <div class="profit-row"><span>권리금</span><span class="profit-num">{fmt(d.get('총권리금_만원'))}만원</span></div>
                  <div class="profit-row"><span>권장 분양가</span><span class="profit-num">{fmt(d.get('권장분양가_만원'))}만원</span></div>
                  <div class="profit-row">
                    <span style="font-weight:700;color:#0F172A;">실투자 수익률</span>
                    <span class="profit-highlight" style="color:{yc};">{pr.get('수익률','—')}%</span>
                  </div>
                </div>
                <div class="md-card" style="margin-top:10px;">
                  <div class="md-name">AI MD 솔루션</div>
                  <div class="md-solution">{d.get('MD솔루션','—')}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                result_ph.info("좌측에 매물 텍스트를 입력하면 분석 결과가 여기에 표시됩니다.")

        if btn_extract and raw_text.strip():
            result_ph.markdown("""<div style='text-align:center;padding:50px;'>AI 분석 중... 잠시만 기다려주세요.</div>""", unsafe_allow_html=True)
            try:
                resp = model.generate_content(EXTRACTION_PROMPT.format(region=input_region, text=raw_text[:3000]))
                data = safe_json(resp.text)
                
                if data:
                    data['지역그룹'] = input_region
                    data['수집일시'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    # 철저한 숫자형 변환 및 계산 (DB 에러 원천 차단)
                    r = clean_num(data.get('월세_만원'))
                    d = clean_num(data.get('보증금_만원'))
                    p = clean_num(data.get('권장분양가_만원'))
                    
                # 권장 분양가가 없으면 업종별 타겟 수익률(Cap Rate)로 역산
                    if p <= 0 and r > 0:
                        sector = data.get('AI분류업종', '')
                        if '의료' in sector or '교육' in sector:
                            cap_rate = 0.040  # 우량 업종은 4.0%로 계산 (가치 높음)
                        elif 'F&B' in sector:
                            cap_rate = 0.052  # F&B는 리스크 반영 5.2%
                        elif '패션' in sector or '뷰티' in sector:
                            cap_rate = 0.048  # 리테일 4.8%
                        else:
                            cap_rate = 0.045  # 기본 4.5%
                            
                        p = int((r * 12) / cap_rate) + d
                        
                    calcs = calc_profit(r, d, p)
                    
                    # 변환된 깨끗한 데이터를 덮어쓰기
                    data['월세_만원'] = r
                    data['보증금_만원'] = d
                    data['권장분양가_만원'] = p
                    data['예상수익률_pct'] = calcs.get('수익률', 0.0)

                    for c in COLS:
                        if c not in data:
                            data[c] = None

                    st.session_state.md_data = pd.concat([st.session_state.md_data, pd.DataFrame([data])], ignore_index=True)
                    st.session_state.last_extracted = data
                    
                    # Supabase에 데이터 쏘기
                    saved = insert_to_supabase(data)
                    msg = "Supabase DB 저장 완료 ✓" if saved else "DB 전송 실패 (일시적 오류)"
                    st.success(f"✓ 분석 완료 — {msg}")
                    st.rerun()
                else:
                    st.error("JSON 파싱 실패.")
            except Exception as e:
                st.error(f"API 오류: {e}")

# ═══════════════════════════════════════════════════════
# 모드 B: MD 추천
# ═══════════════════════════════════════════════════════
elif "MD 추천" in app_mode:
    st.markdown('<div class="section-title">MD 추천 및 상권 분석</div>', unsafe_allow_html=True)

    if df_all.empty:
        st.warning("아직 수집된 데이터가 없습니다.")
        st.stop()

    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        sel_reg = st.selectbox("지역 선택", ["전체"] + sorted(df_all['지역그룹'].dropna().unique().tolist()))
    with c2:
        sel_sec = st.selectbox("업종 필터", ["전체"] + sorted(df_all['AI분류업종'].dropna().unique().tolist()))
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        do_ai = st.button("AI MD 분석", type="primary")

    df = df_all.copy()
    if sel_reg != "전체": df = df[df['지역그룹'] == sel_reg]
    if sel_sec != "전체": df = df[df['AI분류업종'] == sel_sec]
    for col in ['월세_만원','보증금_만원','면적_평','권장분양가_만원','예상수익률_pct']:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')
# [NEW] 평당 임대료 파생 변수 생성 (이 줄이 반드시 차트 그리기 전에 들어가야 해!)
    df['평당임대료_만원'] = df.apply(
        lambda x: x['월세_만원'] / x['면적_평'] if pd.notna(x['면적_평']) and x['면적_평'] > 0 else 0, 
        axis=1
    )

    st.markdown(f'<p class="page-sub">{len(df)}건 조회</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈  임대료 분포", "💡  수익률 분석", "📋  전체 데이터"])

    with tab1:
        ca, cb = st.columns(2, gap="large")
        with ca:
            df_b = df[df['평당임대료_만원'] > 0].dropna(subset=['AI분류업종'])
            if not df_b.empty:
                fig = px.box(df_b, x="AI분류업종", y="평당임대료_만원", color="AI분류업종", 
                             title="업종별 평당 임대료 분포", color_discrete_sequence=PALETTE)
                fig.update_layout(**CHART_LAYOUT, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        with cb:
            df_s = df[df['평당임대료_만원'] > 0].dropna(subset=['면적_평'])
            if not df_s.empty:
                fig2 = px.scatter(df_s, x="면적_평", y="평당임대료_만원", color="AI분류업종", 
                                  title="면적 vs 평당 임대료", hover_data=['상호명', '월세_만원'], color_discrete_sequence=PALETTE)
                # 평균 평당가 기준선 추가
                fig2.add_hline(y=df_s['평당임대료_만원'].mean(), line_dash="dot", line_color="#94A3B8", 
                               annotation_text="평균 평당가", annotation_font_color="#64748B")
                fig2.update_layout(**CHART_LAYOUT)
                st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        df_y = df.dropna(subset=['예상수익률_pct','AI분류업종'])
        if not df_y.empty:
            cc, cd = st.columns(2, gap="large")
            with cc:
                grp = df_y.groupby('AI분류업종')['예상수익률_pct'].mean().reset_index()
                fig3 = px.bar(grp, x='AI분류업종', y='예상수익률_pct', title='업종별 평균 수익률', color='예상수익률_pct', color_continuous_scale=[[0,'#818CF8'],[.5,'#4F46E5'],[1,'#312E81']])
                fig3.add_hline(y=4.5, line_dash="dot", line_color="#16A34A", annotation_text="목표 4.5%", annotation_font_color="#16A34A")
                fig3.update_layout(**CHART_LAYOUT, showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig3, use_container_width=True)
            with cd:
                df_p = df.dropna(subset=['권장분양가_만원','예상수익률_pct'])
                if not df_p.empty:
                    fig4 = px.scatter(df_p, x='권장분양가_만원', y='예상수익률_pct', text='상호명', title='분양가 vs 수익률', color='예상수익률_pct', color_continuous_scale=[[0,'#DC2626'],[.5,'#F59E0B'],[1,'#16A34A']])
                    fig4.add_hline(y=4.5, line_dash="dot", line_color="#16A34A")
                    fig4.update_traces(textposition='top center', textfont=dict(size=9, color='#475569', family='DM Sans'))
                    fig4.update_layout(**CHART_LAYOUT, coloraxis_showscale=False)
                    st.plotly_chart(fig4, use_container_width=True)

    with tab3:
        disp = df.copy()
        disp.index = range(1, len(disp)+1)
        st.dataframe(disp, use_container_width=True, height=400)

    if do_ai and not df.empty:
        ai_ph = st.empty()
        ai_ph.markdown("""<div style='text-align:center;padding:50px;'>AI MD 분석 중... 잠시만 기다려주세요.</div>""", unsafe_allow_html=True)
        try:
            tops = df['AI분류업종'].value_counts().head(3).index.tolist() if 'AI분류업종' in df else []
            resp = model.generate_content(MD_RECOMMEND_PROMPT.format(
                region=sel_reg, avg_rent=f"{df['월세_만원'].mean():.0f}", avg_deposit=f"{df['보증금_만원'].mean():.0f}",
                top_sectors=", ".join(tops), count=len(df)
            ))
            rec = safe_json(resp.text)
            ai_ph.empty()
            if rec:
                st.markdown('<div class="section-title">AI MD 분석 결과</div>', unsafe_allow_html=True)
                gc = {"A":"#16A34A","B":"#4F46E5","C":"#F59E0B","D":"#DC2626"}.get(rec.get("상권등급","C"), "#64748B")
                cg1, cg2 = st.columns([1, 3])
                with cg1:
                    st.markdown(f"""
                    <div class="white-card" style="text-align:center;padding:28px;">
                      <div style='font-family:DM Sans,sans-serif;font-size:3.2rem;font-weight:800;color:{gc};'>{rec.get('상권등급','—')}</div>
                      <div style='font-size:11px;color:#64748B;margin-top:6px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;'>상권 등급</div>
                    </div>
                    """, unsafe_allow_html=True)
                with cg2:
                    st.markdown(f"""
                    <div class="profit-card">
                      <div class="profit-title">등급 분석</div>
                      <p style='font-size:13px;color:#475569;margin-bottom:12px;'>{rec.get('등급이유','—')}</p>
                      <div class="profit-row"><span>기회</span><span class="profit-num" style="color:#16A34A;">{rec.get('기회','—')}</span></div>
                      <div class="profit-row"><span>리스크</span><span class="profit-num" style="color:#DC2626;">{rec.get('리스크','—')}</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown('<div class="section-title" style="margin-top:1.4rem;">추천 MD 업종</div>', unsafe_allow_html=True)
                md_cols = st.columns(3, gap="medium")
                for i, col in enumerate(md_cols, 1):
                    m = rec.get(f"추천MD_{i}", {})
                    if m:
                        with col:
                            st.markdown(f"""
                            <div class="md-card">
                              <div class="md-card-header">
                                <div class="md-tag">{['1순위','2순위','3순위'][i-1]}</div>
                                <div style='font-size:12px;color:#16A34A;font-weight:700;'>{fmt(m.get('권장임대료'))}만원</div>
                              </div>
                              <div class="md-name">{m.get('업종','—')}</div>
                              <div class="md-solution">{m.get('이유','—')}</div>
                            </div>
                            """, unsafe_allow_html=True)
        except Exception as e:
            ai_ph.empty()
            st.error(f"분석 오류: {e}")

# ═══════════════════════════════════════════════════════
# 모드 C: 수익성 계산기
# ═══════════════════════════════════════════════════════
elif "수익성 계산기" in app_mode:
    st.markdown('<div class="section-title">분양가 수익성 시뮬레이터</div>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">임대 조건을 입력하면 보증금을 반영한 실투자금 기준 적정 분양가를 계산합니다.</p>', unsafe_allow_html=True)

    ci, co = st.columns([1, 1], gap="large")

    with ci:
        area         = st.number_input("면적 (평)", min_value=1, max_value=500, value=20, step=1)
        monthly_rent = st.number_input("예상 월세 (만원)", min_value=0, max_value=10000, value=300, step=10)
        deposit      = st.number_input("보증금 (만원)", min_value=0, max_value=100000, value=3000, step=100)
        premium      = st.number_input("권리금 (만원)", min_value=0, max_value=50000, value=0, step=100)
        target_yield = st.slider("목표 수익률 (%)", min_value=2.0, max_value=10.0, value=4.5, step=0.1)

    with co:
        annual   = monthly_rent * 12
        rec_p    = int((annual / (target_yield / 100)) + deposit) if target_yield > 0 else 0
        rent_pp  = monthly_rent / area if area > 0 else 0
        
        invest_amt = rec_p - deposit if rec_p > deposit else 0
        payback  = invest_amt / annual if annual > 0 else 0
        dep_y    = int(deposit * 0.02)

        st.markdown(f"""
        <div class="profit-card" style="margin-top:0;">
          <div class="profit-title">수익성 분석 결과</div>
          <div class="profit-row"><span>평당 임대료</span><span class="profit-num">{rent_pp:.1f}만원/평</span></div>
          <div class="profit-row"><span>연간 임대수익</span><span class="profit-num">{annual:,}만원</span></div>
          <div class="profit-row"><span>보증금 운용수익 (연 2%)</span><span class="profit-num">{dep_y:,}만원</span></div>
          <div class="profit-row"><span>순수 실투자금 (분양가 - 보증금)</span><span class="profit-num">{invest_amt:,}만원</span></div>
          <div class="profit-row" style="padding-top:10px;margin-top:4px;border-top:2px solid #E2E8F0;">
            <span style="font-weight:800;color:#0F172A;font-size:14px;font-family:DM Sans,sans-serif;">적정 권장 분양가</span>
            <span class="profit-highlight">{rec_p:,}만원</span>
          </div>
          <div class="profit-row"><span>권리금 포함 총 투자 예산</span><span class="profit-num">{rec_p + premium:,}만원</span></div>
          <div class="profit-row"><span>투자 회수 기간 (실투자금 기준)</span><span class="profit-num">{payback:.1f}년</span></div>
        </div>
        """, unsafe_allow_html=True)

        gauge_val = min(target_yield / 10, 1.0)
        g_color   = "#16A34A" if target_yield >= 4.5 else "#F59E0B" if target_yield >= 3.0 else "#DC2626"
        st.markdown(f"""
        <div class="white-card" style="text-align:center;margin-top:12px;">
          <div style='font-size:11px;font-weight:700;color:#64748B;letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px;'>목표 수익률</div>
          <div style='font-family:DM Sans,sans-serif;font-size:2.8rem;font-weight:800;color:{g_color};'>{target_yield:.1f}%</div>
          <div style='background:#F1F5F9;border-radius:6px;height:6px;margin-top:14px;'>
            <div style='background:{g_color};width:{int(gauge_val*100)}%;height:6px;border-radius:6px;transition:width .3s;'></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">수익률 시나리오 비교</div>', unsafe_allow_html=True)
    yields = [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
    prices = [int((annual / (y / 100)) + deposit) for y in yields]
    
    fig_s  = go.Figure(go.Bar(
        x=[f"{y}%" for y in yields], y=prices,
        marker_color=["#DC2626" if y < 4.5 else "#4F46E5" for y in yields],
        text=[f"{p:,}만" for p in prices], textposition='outside',
        textfont=dict(color='#475569', size=11, family='DM Sans', weight='bold')
    ))
    fig_s.update_layout(title="수익률별 적정 분양가 (보증금 포함)", **CHART_LAYOUT, showlegend=False)
    st.plotly_chart(fig_s, use_container_width=True)
