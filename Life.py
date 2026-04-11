import streamlit as st
import datetime
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.join(os.getcwd(), "backend"))
from ziwei_engine import ZiWeiEngine

# --- 1. 系統設定 (Flagship v5.0 Restoration) ---
st.set_page_config(
    page_title="紫微財務風控系統", 
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Institutional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&family=Inter:wght@400;600;800&display=swap');
    
    :root {
        --paper-bg: #fdfbf7;
        --paper-card: #ffffff;
        --paper-border: #e2e8f0;
        --institutional-blue: #1e293b;
        --color-soul: #8b5cf6;
        --color-wealth: #059669;
        --color-property: #d97706;
    }

    .stApp { background-color: var(--paper-bg); color: var(--institutional-blue); }
    h1, h2, h3, h4, th, td, p { font-family: 'Noto Sans TC', sans-serif; color: var(--institutional-blue) !important; }
    
    .ceo-card {
        background: var(--paper-card); border: 2px solid var(--paper-border); border-radius: 20px; padding: 20px;
        margin-bottom: 25px; display: flex; align-items: center; gap: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    .palace-box {
        background: white; border-radius: 12px; padding: 12px; min-height: 155px;
        display: flex; flex-direction: column; border: 1px solid #e2e8f0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.01);
    }
    .palace-header { display: flex; justify-content: space-between; font-weight: 900; font-size: 1rem; }
    
    .center-clock {
        background: white; border-radius: 20px; border: 1px solid #e2e8f0;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center; height: 320px; padding: 20px; box-shadow: inset 0 2px 8px rgba(0,0,0,0.01);
    }
    
    .strategy-pill {
        background: #f0fdf4; border-left: 5px solid #16a34a; border-radius: 8px; 
        padding: 10px 15px; margin-bottom: 10px; font-size: 0.85rem; font-weight: 700; color: #166534;
    }
    
    .innate-box {
        border: 2px solid #dc2626; border-radius: 15px; padding: 20px; margin-top: 15px;
        background: white; box-shadow: 0 4px 10px rgba(220,38,38,0.05);
    }
</style>
""", unsafe_allow_html=True)

st.title("🧭 紫微財務風控系統：Global Flow Audit")

# --- Sidebar ---
st.sidebar.title("🗂️ 系統導航")
menu = st.sidebar.radio("功能模組", ["🚀 核心財務審計", "📜 研報概覽"], index=0)

if menu == "🚀 核心財務審計":
    b_date = st.sidebar.date_input("出生日期", datetime.date(1971, 11, 18))
    times = ["子時", "丑時", "寅時", "卯時", "辰時", "巳時", "午時", "未時", "申時", "酉時", "戌時", "亥時"]
    b_hour_raw = st.sidebar.selectbox("時辰", times, index=2)
    b_hour, gender, is_lunar = times.index(b_hour_raw), st.sidebar.radio("性別", ["男", "女"]), st.sidebar.checkbox("農曆")

    # Force Re-initialization if needed
    if st.sidebar.button("🔄 重置並重新審計"):
        st.session_state.engine = ZiWeiEngine(b_date.year, b_date.month, b_date.day, b_hour, is_lunar, gender)
        st.session_state.audit_data = st.session_state.engine.get_wealth_audit()
        st.session_state.grid_data = st.session_state.engine.get_astrolabe_data()
        st.rerun()

    if 'audit_data' not in st.session_state:
        st.session_state.engine = ZiWeiEngine(b_date.year, b_date.month, b_date.day, b_hour, is_lunar, gender)
        st.session_state.audit_data = st.session_state.engine.get_wealth_audit()
        st.session_state.grid_data = st.session_state.engine.get_astrolabe_data()

    audit = st.session_state.audit_data
    grid = st.session_state.grid_data

    # CEO Header
    st.markdown(f"""<div class="ceo-card">
        <img src="data:image/png;base64,{st.session_state.engine.get_image_base64(audit["ceo"]["image"])}" width="85">
        <div><div style="font-size:1.6rem; font-weight:900;">⚖️ 首席執行官 (CEO)：{audit["ceo"]["star"]}</div><div>{audit["ceo"]["description"]}</div></div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        def draw_box(idx):
            p = grid[idx]
            tc = "#8b5cf6" if p['name']=='命宮' else ("#059669" if p['name']=='財帛宮' else ("#d97706" if p['name']=='田宅宮' else "#1e293b"))
            bc = tc if p['name'] in ['命宮','財帛宮','田宅宮'] else "#e2e8f0"
            st.markdown(f'<div class="palace-box" style="border-top:5px solid {bc};"><div class="palace-header" style="color:{tc};"><span>{p["name"]}</span> <span>{p["stem"]}</span></div><div style="color:#d97706; font-weight:800; margin-top:5px;">{" ".join(p["major_stars"])}</div><div style="color:#15803d; font-size:0.8rem; font-weight:700;">{" ".join(p["lucky_stars"])} {" ".join(p["wealth_stars"])}</div><div style="color:#dc2626; font-size:0.8rem; font-weight:700;">{" ".join(p["sha_stars"])}</div></div>', unsafe_allow_html=True)
            if st.button("🔎 鎖定", key=f"lk_{idx}", use_container_width=True): pass

        # --- 4x4 RING LAYOUT ---
        # Top Row
        r1 = st.columns(4)
        for i, idx in enumerate([5, 6, 7, 8]):
            with r1[i]: draw_box(idx)
        
        # Middle
        st.write("")
        mr2 = st.columns([1, 2, 1])
        with mr2[0]: draw_box(4); st.write(""); draw_box(3)
        with mr2[1]: st.markdown(f'<div class="center-clock"><h1>{b_date.strftime("%Y-%m-%d")}</h1><p style="font-size:1.5rem; font-weight:700; color:#64748b;">{b_hour_raw}</p></div>', unsafe_allow_html=True)
        with mr2[2]: draw_box(9); st.write(""); draw_box(10)
        
        # Bottom
        st.write("")
        r4 = st.columns(4)
        for i, idx in enumerate([2, 1, 0, 11]):
            with r4[i]: draw_box(idx)

    with c2:
        st.subheader("🏁 首席審計總結")
        for msg in audit['conclusions']: st.markdown(f'<div class="strategy-pill">{msg}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="innate-box"><h4 style="color:#dc2626; margin-top:0; border-bottom:1px solid #fecaca; padding-bottom:10px;">🎯 先天資本 (年生：{audit["innate"]["stem"]})</h4>', unsafe_allow_html=True)
        for t, d in audit['innate']['stars'].items(): st.markdown(f"**{t}**：{d['star']} ➔ {d['palace']}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("🔍 財務部門深度審計報告")
    t1, t2, t3, tx, t4, t5, t6 = st.tabs(["決策部", "業務部", "金庫部", "先天格局", "12宮連鎖", "文庫指南", "AI 策略室"])
    
    def render_dept_audit(title, d):
        st.markdown(f"### 🛡️ {title} 營運預警")
        cl, cr = st.columns(2)
        with cl:
            st.success(f"📈 資源投放 ➔ {d['layer2']['lu']['dest']}\n\n**{d['layer2']['lu']['why']}**\n\n💡 {d['layer2']['lu']['how']}")
        with cr:
            st.error(f"🛡️ 戰略防火牆 ➔ {d['layer2']['ji']['dest']}\n\n**{d['layer2']['ji']['why']}**\n\n⚠️ {d['layer2']['ji']['how']}")

    with t1: render_dept_audit("命宮", audit['soul'])
    with t2: render_dept_audit("財帛宮", audit['wealth'])
    with t3: render_dept_audit("田宅宮", audit['property'])
    with tx:
        for p in st.session_state.engine.get_innate_audit():
            st.markdown(f'<div style="background:white; border:1px solid #e2e8f0; border-radius:12px; margin-bottom:15px; overflow:hidden;"><div style="background:#1e293b; color:white; padding:10px 20px; font-weight:700;">{p["header"]}</div><div style="padding:15px;"><div style="font-weight:700; border-bottom:1px solid #f1f5f9; padding-bottom:8px; margin-bottom:8px;">{p["palace_def"]}</div><div>* 深層意義：{p["meaning"]}</div><div>* 心理動機：{p["motivation"]}</div><div>* 具體影響：{p["impact"]}</div></div></div>', unsafe_allow_html=True)
    with t4:
        st.info("全宮位聯鎖動能分析")
        for p_n, p_d in st.session_state.engine.fly_all_palaces().items():
            with st.expander(f"{p_n} 流向 ➔ {p_d['lu_dest']} / {p_d['ji_dest']}"): st.markdown(f"**{p_d['collision']}**")
    with t5:
        cols = st.columns(2)
        for i in range(10): 
            with cols[i%2]: st.image(f"assets/logic_{i+1}.jpg", use_container_width=True)
    with t6:
        st.markdown("### 🤖 首席戰略審計官 (AI Gemini)")
        ak = st.secrets.get("GOOGLE_API_KEY", "") or st.sidebar.text_input("Gemini API Key", type="password")
        if st.button("🚀 執行 AI 深度戰略審計"):
            if ak:
                with st.spinner("戰略整合中..."):
                    if not hasattr(st.session_state.engine, 'get_ai_audit'): 
                        st.session_state.engine = ZiWeiEngine(b_date.year, b_date.month, b_date.day, b_hour, is_lunar, gender)
                    res = st.session_state.engine.get_ai_audit(audit, api_key=ak)
                    st.markdown(f'<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:15px; padding:25px; line-height:1.8;">{res}</div>', unsafe_allow_html=True)
            else: st.warning("請輸入 API Key")