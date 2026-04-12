import streamlit as st
import datetime
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.join(os.getcwd(), "backend"))
from ziwei_engine import ZiWeiEngine

# --- 1. 系統設定 (Institutional Flagship v6.4 - Full Restoration) ---
st.set_page_config(
    page_title="紫微財務風控系統 - Institutional Auditor", 
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hybrid Institutional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&family=Inter:wght@400;600;800&display=swap');
    
    :root {
        --paper-bg: #fdfbf7;
        --white-card: #ffffff;
        --inst-blue: #1e293b;
        --grid-dark: #1e293b;
        --neon-indigo: #6366f1;
        --star-major: #fbbf24;
        --star-lucky: #10b981;
        --star-sha: #ef4444;
    }

    .stApp { background-color: var(--paper-bg); color: var(--inst-blue); }
    h1, h2, h3, h4, p, li { font-family: 'Noto Sans TC', sans-serif; color: var(--inst-blue) !important; }
    
    .ceo-card {
        background: var(--white-card); border: 1.5px solid #e2e8f0; border-radius: 20px; padding: 25px;
        margin-bottom: 24px; display: flex; align-items: center; gap: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    .grid-container {
        background: #0f172a; border-radius: 24px; padding: 20px; border: 2px solid #1e293b;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    .palace-box {
        background: #1e293b; border-radius: 12px; padding: 12px; min-height: 165px;
        display: flex; flex-direction: column; border: 1px solid #334155;
    }
    .palace-header { display: flex; justify-content: space-between; font-weight: 700; color: white !important; }
    .palace-header span { color: white !important; }
    
    .decision-center {
        background: #1e293b; border: 2.5px solid var(--neon-indigo); border-radius: 20px;
        padding: 25px; text-align: center; height: 100%;
    }
    .status-badge {
        background: rgba(255,255,255,0.03); border: 1px solid #334155; border-radius: 10px;
        padding: 12px; margin-top: 15px; font-size: 0.9rem; line-height: 1.6; color: #cbd5e1 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: white; border-radius: 8px 8px 0 0; padding: 10px 20px; border: 1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ 紫微財務風控系統：Institutional Flagship")

# --- State Management ---
if 'focus_idx' not in st.session_state: st.session_state.focus_idx = 0

# --- Sidebar ---
st.sidebar.title("🗂️ 系統導航")
menu = st.sidebar.radio("模組地圖", ["🚀 核心財務審計", "📚 戰略文庫", "📜 研報概覽"], index=0)

if menu == "🚀 核心財務審計":
    b_date = st.sidebar.date_input("出生日期", datetime.date(1971, 11, 18))
    times = ["子時", "丑時", "寅時", "卯時", "辰時", "巳時", "午時", "未時", "申時", "酉時", "戌時", "亥時"]
    b_hour_raw = st.sidebar.selectbox("時辰", times, index=2)
    b_hour, gender, is_lunar = times.index(b_hour_raw), st.sidebar.radio("性別", ["男", "女"]), st.sidebar.checkbox("農曆")

    if st.sidebar.button("🔄 重置全系統審計") or 'audit_data' not in st.session_state:
        st.session_state.engine = ZiWeiEngine(b_date.year, b_date.month, b_date.day, b_hour, is_lunar, gender)
        st.session_state.audit_data = st.session_state.engine.get_wealth_audit()
        st.session_state.grid_data = st.session_state.engine.get_astrolabe_data()
        st.session_state.fly_data = st.session_state.engine.fly_all_palaces()

    audit = st.session_state.audit_data
    grid = st.session_state.grid_data
    fly_data = st.session_state.fly_data

    st.markdown(f"""<div class="ceo-card">
        <img src="data:image/png;base64,{st.session_state.engine.get_image_base64(audit["ceo"]["image"])}" width="80">
        <div><div style="font-size:1.6rem; font-weight:900;">⚖️ 執行長 (CEO)：{audit["ceo"]["star"]}</div><div>具備核心決策素質。</div></div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([2.5, 1])
    with c1:
        st.markdown('<div class="grid-container">', unsafe_allow_html=True)
        def draw_box(idx):
            p = grid[idx]
            is_focused = (st.session_state.focus_idx == idx)
            border_c = "#6366f1" if is_focused else "#334155"
            st.markdown(f"""
            <div class="palace-box" style="border-top: 4px solid {border_c};">
                <div class="palace-header"><span>{p["name"]}</span><span style="color:#818cf8 !important;">{p["stem"]}</span></div>
                <div style="color:#fbbf24; font-weight:900; margin-top:8px;">{" ".join(p["major_stars"])}</div>
                <div style="color:#10b981; font-size:0.8rem; font-weight:700;">{" ".join(p["lucky_stars"])}</div>
                <div style="color:#ef4444; font-size:0.8rem; font-weight:700;">{" ".join(p["sha_stars"])}</div>
                <div style="flex-grow:1;"></div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🎯 宮位四化", key=f"focus_{idx}"):
                st.session_state.focus_idx = idx
                st.rerun()

        r1 = st.columns(4)
        for i, idx in enumerate([5,6,7,8]):
            with r1[i]: draw_box(idx)
        st.write(""); mr = st.columns([1, 2, 1])
        with mr[0]: draw_box(4); st.write(""); draw_box(3)
        with mr[1]:
            focus_p = grid[st.session_state.focus_idx]
            focus_fly = fly_data[focus_p['name']]
            st.markdown(f"""
<div class="decision-center">
<h1 style="color:#fbbf24 !important; font-size:2.8rem; margin-bottom:5px;">{b_date.year}</h1>
<p style="color:#94a3b8 !important; font-size:1rem; margin-bottom:25px;">{b_date.strftime("%m-%d")} ({b_hour_raw}) {focus_p['name']}</p>
<h2 style="color:#10b981 !important; font-size:1.5rem; margin-bottom:8px;">{focus_fly['lu_dest']}</h2>
<h2 style="color:#ef4444 !important; font-size:1.5rem; margin-bottom:20px;">{focus_fly['ji_dest']}</h2>
<div class="status-badge">
<span style="color:#fbbf24 !important; font-weight:900;">【動態分布】</span><br>
獲利導向「{focus_fly['lu_dest'].split(' ')[-1]}」，但風險潛伏於「{focus_fly['ji_dest'].split(' ')[-1]}」。
建議利用「{focus_fly['lu_dest'].split(' ')[-1]}」的盈餘填補漏洞。
</div></div>
""", unsafe_allow_html=True)
        with mr[2]: draw_box(9); st.write(""); draw_box(10)
        st.write(""); r4 = st.columns(4)
        for i, idx in enumerate([2,1,0,11]):
            with r4[i]: draw_box(idx)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.subheader("🏁 首席審計診斷")
        st.info("【策略提示】點按宮位「🎯 宮位四化」以查看動態流向。")
        st.markdown(f'<div style="background:white; border:1px solid #ef4444; border-radius:15px; padding:20px;"><h4 style="color:#ef4444 !important; margin-top:0;">🎯 先天資本 (年生：{audit["innate"]["stem"]})</h4>', unsafe_allow_html=True)
        for t, d in audit['innate']['stars'].items(): st.markdown(f"**{t}**：<span style='color:#d97706; font-weight:800;'>{d['star']}</span> ➔ {d['palace']}", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider(); st.markdown("### 🤖 AI 智能建議")
        ak = st.secrets.get("GOOGLE_API_KEY", "") or st.sidebar.text_input("Gemini API Key", type="password")
        if st.button("🚀 執行 AI 戰略分析"):
            if ak:
                with st.spinner("戰略模擬中..."):
                    st.session_state.ai_res = st.session_state.engine.get_ai_audit(audit, api_key=ak)
                    st.markdown(f'<div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:20px; font-size:0.95rem;">{st.session_state.ai_res}</div>', unsafe_allow_html=True)
            else: st.warning("請輸入 API Key")

    # --- RESTORED AUDIT TABS ---
    st.divider()
    t1, t2, t3, tx, t4, t5, t6 = st.tabs(["🏎️ 決策部", "💸 業務部", "🏰 金庫部", "🎯 先天格局", "🛰️ 12宮連鎖", "📚 文庫指南", "🤖 AI 策略室"])
    
    def render_dept(title, d):
        st.markdown(f"### 🛡️ {title} 營運報表")
        cl, cr = st.columns(2)
        with cl: st.success(f"📈 資源投放 ➔ {d['layer2']['lu']['dest']}\n\n**核心流向導向位。**")
        with cr: st.error(f"🛡️ 戰略防火牆 ➔ {d['layer2']['ji']['dest']}\n\n**核心風險防禦位。**")

    with t1: render_dept("命宮", audit['soul'])
    with t2: render_dept("財帛宮", audit['wealth'])
    with t3: render_dept("田宅宮", audit['property'])
    with tx:
        for p in st.session_state.engine.get_innate_audit():
            st.markdown(f'<div style="background:white; border:1px solid #e2e8f0; border-radius:12px; margin-bottom:15px; padding:20px;">{p["header"]}<br><br>{p["palace_def"]}<br><br>* **深層意義**：{p["meaning"]}<br>* **具體影響**：{p["impact"]}</div>', unsafe_allow_html=True)
    with t4:
        for p_n, p_d in st.session_state.engine.fly_all_palaces().items():
            with st.expander(f"{p_n} 流向 ➔ {p_d['lu_dest']} / {p_d['ji_dest']}"): st.write(p_d['collision'])
    with t5:
        with open("assets/Logic.md", "r", encoding="utf-8") as f: st.markdown(f.read())
    with t6:
        if 'ai_res' in st.session_state:
            st.markdown(f'<div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:20px; font-size:0.95rem;">{st.session_state.ai_res}</div>', unsafe_allow_html=True)
        else:
            st.info("請點擊側邊欄或上方按鈕執行 AI 戰略分析，結果將同步顯示於此。")

if menu == "📚 戰略文庫":
    st.subheader("📚 專業財富策略存檔")
    with open("assets/Logic.md", "r", encoding="utf-8") as f: st.markdown(f.read())

if menu == "📜 研報概覽":
    st.subheader("紫微財務戰略研究報告")
    with open("紫微斗數財運四化解析.md", "r", encoding="utf-8") as f: st.markdown(f.read())