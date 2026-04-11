import streamlit as st
import datetime
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.join(os.getcwd(), "backend"))
from ziwei_engine import ZiWeiEngine

# --- 1. 系統設定與視覺化 UI ---
st.set_page_config(
    page_title="紫微財務風控系統 - Institutional Audit", 
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Institutional CSS (Warm Paper Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Outfit:wght@400;700&display=swap');
    
    :root {
        --paper-bg: #fdfbf7;
        --paper-card: #ffffff;
        --paper-border: #e2e8f0;
        --institutional-blue: #1e293b;
        --primary: #6366f1;
        --secondary: #fbbf24;
        --success: #15803d;
        --danger: #b91c1c;
        --slate-900: #0f172a;
        --slate-700: #334155;
    }

    .stApp { background-color: var(--paper-bg); color: var(--slate-900); }
    h1, h2, h3, h4, th, td, p { color: var(--slate-900) !important; }
    .stHeading h1 { font-family: 'Outfit', sans-serif; font-weight: 800; color: var(--institutional-blue) !important; }
    
    .ceo-card {
        background: var(--paper-card); border: 1px solid var(--paper-border); border-radius: 15px; padding: 24px;
        margin-bottom: 24px; display: flex; align-items: center; gap: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .ceo-img { border-radius: 12px; border: 2px solid var(--paper-border); }
    
    .palace-content-box {
        background-color: var(--paper-card) !important; border-radius: 12px; padding: 12px; min-height: 180px;
        display: flex; flex-direction: column; border: 1.5px solid var(--paper-border);
    }
    
    .innate-profile-card {
        background: #ffffff; border: 1px solid #e2e8f0; border-radius: 15px; padding: 0; margin-bottom: 25px;
        overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
    }
    .innate-banner {
        background: #1e293b; color: #ffffff !important; padding: 15px 25px; font-weight: 700; font-size: 1.1rem;
        border-bottom: 3px solid #6366f1;
    }
    .innate-body { padding: 25px; }
    .palace-def-text { font-size: 1.1rem; color: #1e293b; font-weight: 600; margin-bottom: 15px; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; }
    .insight-bullet { margin-bottom: 12px; display: flex; gap: 12px; }
    .bullet-label { font-weight: 800; color: #1e293b; min-width: 100px; display: flex; align-items: center; }
    .bullet-content { color: #475569; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

st.title("🧭 紫微財務風控系統：Global Flow Audit")

# --- Sidebar ---
st.sidebar.title("🗂️ 系統導航")
menu = st.sidebar.radio("選擇功能模組", ["🚀 核心財務審計", "📜 十干四化對照表"], index=0)

# --- Functions ---
def render_grid(grid_data, audit, info):
    def draw_cell(idx):
        p = grid_data[idx]
        border = "#6366f1" if p['name'] == '命宮' else ("#16a34a" if p['name'] == '財帛宮' else ("#d97706" if p['name'] == '田宅宮' else "#e2e8f0"))
        st.markdown(f"""
            <div class="palace-content-box" style="border-color: {border};">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-weight: 800; color: #1e293b;">{p['name']}</span>
                    <span style="color: #6366f1; font-weight: 700;">{p['stem']}</span>
                </div>
                <div style="font-size: 0.82rem; color: #d97706; font-weight: 600; margin-top: 5px;">{" ".join(p["major_stars"])}</div>
                <div style="font-size: 0.75rem; color: #15803d;">{" ".join(p["wealth_stars"])} {" ".join(p["lucky_stars"])}</div>
                <div style="font-size: 0.75rem; color: #b91c1c;">{" ".join(p["sha_stars"])}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🔎 鎖定", key=f"foc_{idx}", use_container_width=True):
            st.session_state.focused_p = p['name']
            st.rerun()

    c1, c2, c3 = st.columns([1, 2, 1])
    with c1: draw_cell(5); draw_cell(4); draw_cell(3); draw_cell(2)
    with c2:
        st.markdown(f'<div style="background:white; border-radius:20px; border:2px solid #e2e8f0; min-height:420px; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;"><h3>{info["date"]}</h3><p>{info["time"]}</p></div>', unsafe_allow_html=True)
        st.columns(2)[0].write(""); st.columns(2)[1].write("")
        st.columns(2)[0].write(""); st.columns(2)[1].write("")
    with c3: draw_cell(9); draw_cell(10); draw_cell(11); draw_cell(0)
    st.columns(4)[0].write(""); st.columns(4)[1].write(""); st.columns(4)[2].write(""); st.columns(4)[3].write("")
    r_cols = st.columns(4)
    for i, idx in enumerate([6, 7, 8, 1]):
        with r_cols[i]: draw_cell(idx)

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
        st.markdown(f'<div class="ceo-card"><img src="data:image/png;base64,{st.session_state.engine.get_image_base64(audit["ceo"]["image"])}" width="100" class="ceo-img"><div><div style="font-size:1.5rem; font-weight:700;">🕵️ 執行長：{audit["ceo"]["star"]}</div><div>{audit["ceo"]["description"]}</div></div></div>', unsafe_allow_html=True)
        
        c_main1, c_main2 = st.columns([2, 1])
        with c_main1: render_grid(st.session_state.grid_data, audit=audit, info={"date": b_date.strftime("%Y-%m-%d"), "time": b_hour_raw})
        with c_main2:
            st.subheader("🏁 戰略總論")
            for msg in audit['conclusions']: st.success(msg)
            st.markdown(f'<div style="padding:15px; border:2.5px solid #dc2626; border-radius:12px;"><h4 style="color:#dc2626; margin-top:0;">🎯 先天資本 (年生：{audit["innate"]["stem"]})</h4>', unsafe_allow_html=True)
            for t, d in audit['innate']['stars'].items():
                st.markdown(f'**{t}**：{d["star"]} ➔ {d["palace"]}')
            st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        st.subheader("🔍 部門深度審計報告")
        # Exact tab order as requested
        t1, t2, t3, tx, t4, t5, t6 = st.tabs(["🏎️ 執行長部", "💸 業務部", "🏰 金庫部", "🎯 先天格局", "🛰️ 12宮連鎖", "📚 參考知識庫", "🤖 AI 策略室"])
        
        def render_dept_card(name, d):
            st.markdown(f"### 🛡️ {name}")
            st.markdown("#### **第一層：先天構架**")
            if d['layer1']['stars']:
                for s in d['layer1']['stars']: st.info(f"**{s['star']}**: {s['key']} | {s['comment']}")
            else: st.caption(d['layer1']['empty_msg'])
            st.markdown("#### **第二層：對待關係**")
            cl, cr = st.columns(2)
            with cl: st.success(f"📈 挹注 ➔ {d['layer2']['lu']['dest']}\n\n**{d['layer2']['lu']['why']}**\n\n💡 {d['layer2']['lu']['how']}\n\n✅ {d['layer2']['lu']['strategy']}")
            with cr: st.error(f"🛡️ 風險 ➔ {d['layer2']['ji']['dest']}\n\n**{d['layer2']['ji']['why']}**\n\n⚖️ {d['layer2']['ji']['how']}\n\n⚠️ {d['layer2']['ji']['strategy']}")

        with t1: render_dept_card("命宮", audit['soul'])
        with t2: render_dept_card("財帛宮", audit['wealth'])
        with t3: render_dept_card("田宅宮", audit['property'])
        with tx:
            st.markdown("### 🎯 先天格局深度解析")
            profiles = st.session_state.engine.get_innate_audit()
            for p in profiles:
                st.markdown(f"""
                <div class="innate-profile-card">
                    <div class="innate-banner">{p['header']}</div>
                    <div class="innate-body">
                        <div class="palace-def-text">{p['palace_def']}</div>
                        <div class="insight-bullet">
                            <div class="bullet-label">* **深層意義：**</div>
                            <div class="bullet-content">{p['meaning']}</div>
                        </div>
                        <div class="insight-bullet">
                            <div class="bullet-label">* **心理動機：**</div>
                            <div class="bullet-content">{p['motivation']}</div>
                        </div>
                        <div class="insight-bullet">
                            <div class="bullet-label">* **具體影響：**</div>
                            <div class="bullet-content">{p['impact']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        with t4:
            st.markdown("### 🛰️ 全宮位聯鎖審計")
            f_all = st.session_state.engine.fly_all_palaces()
            for p_n, p_d in f_all.items():
                with st.expander(f"{p_n} ➔ {p_d['lu_dest']} / {p_d['ji_dest']}"): st.write(p_d['collision'])
        with t5:
            st.markdown("### 📚 財富參考知識庫")
            descriptions = [
                "武曲化忌：鐵腕財務長遇危機。防資金斷鍊、周轉不靈。實業與銀行投資易貶值。",
                "太陽化忌：跨國CEO面臨波及。小心外匯虧損、海外市場地雷。名氣大實質虧損。",
                "廉貞化忌：法務長踩紅線。求財易涉法務、行政罰款或官司。勿遊灰色地帶。",
                "太陰化忌：房產大亨資產凍結。防不動產套牢、租金回收困難。女性合夥人糾紛。",
                "天機化忌：數據分析師失誤。策略/交易Bug。頻繁進出手續費損失。聰明反誤。",
                "天同化忌：享樂天真陷阱。防盲目合夥欺騙、夕陽產業投資。過度理想化。",
                "貪狼化忌：投機客泡沫破裂。防詐騙、高槓桿爆倉、虛擬貨幣駭客風險。",
                "巨門化忌：公關災難。防流言誤判、合約漏洞。絕不可輕信內線消息。",
                "文昌/文曲化忌：信用破產。極端危險。防票據糾紛、支票不兌現、惡意倒帳。",
                "Wealth Engines (Lu)：穩健/技術/金融三大財富引擎。對準標的，資源極大化。"
            ]
            cols = st.columns(2)
            for i in range(10):
                with cols[i % 2]:
                    path = f"assets/logic_{i+1}.jpg"
                    if os.path.exists(path): st.image(path, caption=f"Strategic Chart {i+1}")
                    st.info(descriptions[i])
        with t6:
            ak = st.secrets.get("GOOGLE_API_KEY", "") or st.sidebar.text_input("Gemini API Key", type="password")
            if st.button("🚀 執行 AI 深度戰略審計"):
                if ak: st.write(st.session_state.engine.get_ai_audit(audit, api_key=ak))
                else: st.warning("請提供 API Key")

st.divider()
st.caption("紫微財務風控系統 Premium v4 | Professional Innate Setup Architecture")