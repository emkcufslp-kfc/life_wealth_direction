import streamlit as st
import datetime
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.join(os.getcwd(), "backend"))
from ziwei_engine import ZiWeiEngine

# --- 1. 系統設定與視覺化 UI (Flagship v4.2 - Final Audit suite) ---
st.set_page_config(
    page_title="紫微財務風控系統 - Institutional Auditor", 
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Institutional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Noto+Sans+TC:wght@400;700;900&display=swap');
    
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
        background: var(--paper-card); border: 1.5px solid var(--paper-border); border-radius: 20px; padding: 25px;
        margin-bottom: 24px; display: flex; align-items: center; gap: 25px;
        box-shadow: 0 4px 15px -1px rgba(0, 0, 0, 0.03);
    }
    
    .unified-grid-container {
        display: grid; grid-template-columns: repeat(4, 1fr); grid-template-rows: repeat(4, 1fr);
        gap: 12px; background: #eeede9; padding: 12px; border-radius: 20px;
    }
    
    .palace-box {
        background: white; border-radius: 15px; padding: 15px; min-height: 160px;
        display: flex; flex-direction: column; border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧭 紫微財務風控系統：Institutional Auditor")

# --- Sidebar ---
st.sidebar.title("🗂️ 系統導覽")
menu = st.sidebar.radio("功能模組", ["🚀 核心財務審計", "📜 研報對照表"], index=0)

if menu == "🚀 核心財務審計":
    b_date = st.sidebar.date_input("出生日期", datetime.date(1971, 11, 18))
    times = ["子時", "丑時", "寅時", "卯時", "辰時", "巳時", "午時", "未時", "申時", "酉時", "戌時", "亥時"]
    b_hour_raw = st.sidebar.selectbox("時辰", times, index=2)
    b_hour, gender, is_lunar = times.index(b_hour_raw), st.sidebar.radio("性別", ["男", "女"]), st.sidebar.checkbox("農曆")

    if st.sidebar.button("🚀 啟動審計") or 'audit_data' in st.session_state:
        if 'engine' not in st.session_state or st.sidebar.button("🔄 重算"):
            st.session_state.engine = ZiWeiEngine(b_date.year, b_date.month, b_date.day, b_hour, is_lunar, gender)
            st.session_state.audit_data = st.session_state.engine.get_wealth_audit()
            st.session_state.grid_data = st.session_state.engine.get_astrolabe_data()

        audit = st.session_state.audit_data
        grid = st.session_state.grid_data

        # CEO Header
        st.markdown(f"""<div class="ceo-card">
            <img src="data:image/png;base64,{st.session_state.engine.get_image_base64(audit["ceo"]["image"])}" width="80">
            <div><div style="font-size:1.6rem; font-weight:900;">👮 首席執行官 (CEO)：{audit["ceo"]["star"]}</div><div>{audit["ceo"]["description"]}</div></div>
        </div>""", unsafe_allow_html=True)

        c_grid, c_summary = st.columns([2, 1])
        with c_grid:
            st.markdown('<div class="unified-grid-container">', unsafe_allow_html=True)
            def draw_box(idx):
                p = grid[idx]
                tc = "#8b5cf6" if p['name']=='命宮' else ("#059669" if p['name']=='財帛宮' else ("#d97706" if p['name']=='田宅宮' else "#1e293b"))
                st.markdown(f'<div class="palace-box" style="border-top:5px solid {tc};"><div style="display:flex; justify-content:space-between; font-weight:900; color:{tc};"><span>{p["name"]}</span> <span>{p["stem"]}</span></div><div style="color:#d97706; font-weight:800; margin-top:5px;">{" ".join(p["major_stars"])}</div><div style="color:#15803d; font-size:0.8rem;">{" ".join(p["wealth_stars"])} {" ".join(p["lucky_stars"])}</div><div style="color:#dc2626; font-size:0.8rem;">{" ".join(p["sha_stars"])}</div></div>', unsafe_allow_html=True)
            
            # (Grid Ring Layout)
            r1=st.columns(4); [draw_box(i) for i in [5,6,7,8]]
            m=st.columns([1,2,1]); [draw_box(i) for i in [4,3]]; st.markdown(f'<div style="text-align:center; padding:20px;"><h2>{b_date.strftime("%Y-%m-%d")}</h2><p>{b_hour_raw}</p></div>', unsafe_allow_html=True); [draw_box(i) for i in [9,10]]
            r4=st.columns(4); [draw_box(i) for i in [2,1,0,11]]
            st.markdown('</div>', unsafe_allow_html=True)

        with c_summary:
            st.subheader("🏁 首席審計總結")
            for msg in audit['conclusions']: st.success(msg)
            st.markdown(f'<div style="border:2.5px solid #dc2626; border-radius:15px; padding:20px; background:rgba(220,38,38,0.02);"><h4 style="color:#dc2626; margin-top:0;">🎯 先天資本 (年生：{audit["innate"]["stem"]})</h4>', unsafe_allow_html=True)
            for t, d in audit['innate']['stars'].items(): st.markdown(f"**{t}**：{d['star']} ➔ {d['palace']}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        st.subheader("🔍 財務部門深度審計報告")
        t1, t2, t3, tx, t4, t5, t6 = st.tabs(["🏎️ 決策部", "💸 業務部", "🏰 金庫部", "🎯 先天格局", "🛰️ 12宮連鎖", "📚 文庫指南", "🤖 AI 策略室"])
        
        def render_audit_card(title, data):
            st.markdown(f"### 🛡️ {title} 審計細節")
            st.markdown("#### **第一層：先天基因軌跡 (Innate DNA)**")
            if data['layer1']['stars']:
                for s in data['layer1']['stars']: st.info(f"**{s['star']}**: {s['comment']}")
            else: st.caption(data['layer1']['empty_msg'])
            st.markdown("#### **第二層：飛星資源動能 (Global Flow)**")
            cl, cr = st.columns(2)
            with cl: st.success(f"📈 資源投放 ➔ {data['layer2']['lu']['dest']}\n\n**{data['layer2']['lu']['why']}**\n\n💡 {data['layer2']['lu']['how']}")
            with cr: st.error(f"🛡️ 戰略防火牆 ➔ {data['layer2']['ji']['dest']}\n\n**{data['layer2']['ji']['why']}**\n\n⚠️ {data['layer2']['ji']['how']}")

        with t1: render_audit_card("命宮", audit['soul'])
        with t2: render_audit_card("財帛宮", audit['wealth'])
        with t3: render_audit_card("田宅宮", audit['property'])
        with tx:
            st.markdown("### 🎯 先天格局深度解析")
            for p in st.session_state.engine.get_innate_audit():
                st.markdown(f'<div style="background:white; border:1px solid #e2e8f0; border-radius:15px; overflow:hidden; margin-bottom:20px;"><div style="background:#1e293b; color:white; padding:12px 20px; font-weight:700;">{p["header"]}</div><div style="padding:20px;"><div style="font-weight:700; border-bottom:1px solid #f1f5f9; padding-bottom:10px; margin-bottom:10px;">{p["palace_def"]}</div><div>* **深層意義：** {p["meaning"]}</div><div>* **心理動機：** {p["motivation"]}</div><div>* **具體影響：** {p["impact"]}</div></div></div>', unsafe_allow_html=True)
        with t4:
            for p_n, p_d in st.session_state.engine.fly_all_palaces().items():
                with st.expander(f"{p_n} 動能流向 ➔ {p_d['lu_dest']} / {p_d['ji_dest']}"): st.markdown(f"**戰略指引：{p_d['collision']}**")
        with t5:
            cols = st.columns(2)
            for i in range(10): 
                with cols[i%2]: st.image(f"assets/logic_{i+1}.jpg", use_container_width=True)
        with t6:
            st.markdown("### 🤖 首席戰略審計官 (AI Gemini)")
            ak = st.secrets.get("GOOGLE_API_KEY", "") or st.sidebar.text_input("Gemini API Key", type="password")
            if st.button("🚀 執行 AI 深度戰略審計"):
                if ak: 
                    with st.spinner("戰略盤整中，請稍候..."):
                        res = st.session_state.engine.get_ai_audit(audit, api_key=ak)
                        st.markdown(f'<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:15px; padding:25px; line-height:1.8;">{res}</div>', unsafe_allow_html=True)
                else: st.warning("請於側邊欄輸入 API Key 以啟動 AI 審計。")