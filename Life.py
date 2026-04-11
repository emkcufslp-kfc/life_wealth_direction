import streamlit as st
import datetime
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.join(os.getcwd(), "backend"))
from ziwei_engine import ZiWeiEngine

# --- 1. 系統設定與視覺化 UI ---
st.set_page_config(
    page_title="紫微財務風控系統 - Flagship Audit", 
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
        --slate-900: #0f172a;
        --slate-700: #334155;
    }

    .stApp { background-color: var(--paper-bg); color: var(--slate-900); }
    h1, h2, h3, h4, th, td, p { color: var(--slate-900) !important; }
    
    .ceo-card {
        background: var(--paper-card); border: 1px solid var(--paper-border); border-radius: 12px; padding: 20px;
        margin-bottom: 24px; display: flex; align-items: center; gap: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .ceo-img { border-radius: 8px; border: 1px solid var(--paper-border); }
    
    .unified-grid-container {
        display: grid; grid-template-columns: repeat(4, 1fr); grid-template-rows: repeat(4, 1fr);
        gap: 8px; background: #e2e8f0; padding: 8px; border-radius: 12px;
    }
    .palace-box {
        background: white; border-radius: 8px; padding: 10px; min-height: 140px;
        display: flex; flex-direction: column; border: 1px solid #dee2e6;
    }
    .center-clock {
        grid-column: 2 / span 2; grid-row: 2 / span 2;
        background: white; border-radius: 12px; border: 1px solid #e2e8f0;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center; padding: 20px;
    }
    
    .dashboard-card {
        background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px; margin-bottom: 12px;
    }
    .innate-red-box {
        border: 2px solid #dc2626; border-radius: 12px; padding: 15px; margin-top: 10px;
    }
    
    .innate-profile-card {
        background: #ffffff; border: 1px solid #e2e8f0; border-radius: 15px; padding: 0; margin-bottom: 25px;
        overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
    }
    .innate-banner {
        background: #1e293b; color: #ffffff !important; padding: 12px 20px; font-weight: 700; font-size: 1rem;
        border-bottom: 3px solid #6366f1;
    }
    .innate-body { padding: 20px; }
    .palace-def-line { font-weight: 700; font-size: 1rem; color: #1e293b; margin-bottom: 12px; border-bottom: 1px solid #edf2f7; padding-bottom: 8px; }
    .bullet-item { display: flex; gap: 10px; margin-bottom: 8px; }
    .bullet-tag { font-weight: 800; color: #1e293b; min-width: 90px; }
    .bullet-text { color: #4a5568; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

st.title("🧭 紫微財務風控系統：Global Flow Audit")

# --- Sidebar ---
st.sidebar.title("🗂️ 系統導航")
menu = st.sidebar.radio("功能模組", ["🚀 核心財務審計", "📜 四化對照表"], index=0)

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
        st.markdown(f"""
        <div class="ceo-card">
            <img src="data:image/png;base64,{st.session_state.engine.get_image_base64(audit["ceo"]["image"])}" width="80" class="ceo-img">
            <div>
                <div style="font-size:1.4rem; font-weight:800; color:#1e293b;">🕵️ 執行長：{audit["ceo"]["star"]}</div>
                <div style="font-size:0.9rem; color:#475569;">{audit["ceo"]["description"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([2, 1])
        with c1:
            # TRUE RING LAYOUT (4x4)
            def draw_box(idx):
                p = grid[idx]
                bc = "#6366f1" if p['name'] == '命宮' else ("#16a34a" if p['name'] == '財帛宮' else ("#d97706" if p['name'] == '田宅宮' else "#dee2e6"))
                st.markdown(f"""
                <div class="palace-box" style="border-top: 4px solid {bc};">
                    <div style="display:flex; justify-content:space-between; font-weight:800; font-size:0.95rem; color:#1e293b;">
                        <span>{p['name']}</span> <span style="color:#6366f1;">{p['stem']}</span>
                    </div>
                    <div style="color:#d97706; font-size:0.85rem; font-weight:700; margin-top:4px;">{" ".join(p['major_stars'])}</div>
                    <div style="color:#15803d; font-size:0.75rem;">{" ".join(p['wealth_stars'])} {" ".join(p['lucky_stars'])}</div>
                    <div style="color:#b91c1c; font-size:0.75rem;">{" ".join(p['sha_stars'])}</div>
                    <div style="margin-top:auto;">
                        <button style="width:100%; font-size:0.7rem; border-radius:4px; border:1px solid #e2e8f0; background:none; cursor:pointer;">🔎 鎖定</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Grid Container
            st.markdown('<div class="unified-grid-container">', unsafe_allow_html=True)
            # Row 1 (Index 5, 6, 7, 8)
            r1 = st.columns(4)
            with r1[0]: draw_box(5)
            with r1[1]: draw_box(6)
            with r1[2]: draw_box(7)
            with r1[3]: draw_box(8)

            # Row 2 & 3 (Middle)
            st.markdown('<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top:8px;">', unsafe_allow_html=True)
            mr2 = st.columns([1, 2, 1])
            with mr2[0]: draw_box(4); st.write(""); draw_box(3)
            with mr2[1]: 
                st.markdown(f'<div class="center-clock" style="height:310px;"><h2>{b_date.strftime("%Y-%m-%d")}</h2><p>{b_hour_raw}</p></div>', unsafe_allow_html=True)
            with mr2[2]: draw_box(9); st.write(""); draw_box(10)
            st.markdown('</div>', unsafe_allow_html=True)

            # Row 4 (Index 2, 1, 0, 11)
            st.markdown('<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top:8px;">', unsafe_allow_html=True)
            r4 = st.columns(4)
            with r4[0]: draw_box(2)
            with r4[1]: draw_box(1)
            with r4[2]: draw_box(0)
            with r4[3]: draw_box(11)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.subheader("※ 戰略總論")
            for msg in audit['conclusions']:
                st.markdown(f'<div style="background:#f0fdf4; border-radius:8px; padding:12px; margin-bottom:10px; font-size:0.85rem; color:#166534;">{msg}</div>', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="innate-red-box">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                    <span style="font-size:1.2rem;">🎯</span>
                    <span style="font-weight:800; font-size:1.1rem; color:#1e293b;">先天資本 (年生：{audit['innate']['stem']})</span>
                </div>
                <div style="font-size:0.9rem; line-height:1.8;">
            """, unsafe_allow_html=True)
            for t, d in audit['innate']['stars'].items():
                st.markdown(f"**{t}**：{d['star']} ➔ {d['palace']}")
            st.markdown("</div></div>", unsafe_allow_html=True)

        st.divider()
        st.subheader("🔍 財務部門深度審計報告")
        t1, t2, t3, tx, t4, t5, t6 = st.tabs(["🏎️ 執行長部", "💸 業務部", "🏰 金庫部", "🎯 先天格局", "🛰️ 12宮連鎖", "📚 參考知識庫", "🤖 AI 策略室"])
        
        def render_dept(p_name, d_data):
            st.markdown(f"### 🛡️ {p_name}")
            st.markdown("#### **第一層：先天構架**")
            if d_data['layer1']['stars']:
                for s in d_data['layer1']['stars']: st.info(f"**{s['star']}**: {s['comment']}")
            else: st.caption(d_data['layer1']['empty_msg'])
            st.markdown("#### **第二層：對待關係**")
            cl, cr = st.columns(2)
            with cl: st.success(f"📈 挹注 ➔ {d_data['layer2']['lu']['dest']}\n\n**{d_data['layer2']['lu']['why']}**\n\n💡 {d_data['layer2']['lu']['how']}\n\n✅ {d_data['layer2']['lu']['strategy']}")
            with cr: st.error(f"🛡️ 風險 ➔ {d_data['layer2']['ji']['dest']}\n\n**{d_data['layer2']['ji']['why']}**\n\n⚖️ {d_data['layer2']['ji']['how']}\n\n⚠️ {d_data['layer2']['ji']['strategy']}")

        with t1: render_dept("命宮", audit['soul'])
        with t2: render_dept("財帛宮", audit['wealth'])
        with t3: render_dept("田宅宮", audit['property'])
        with tx:
            st.markdown("### 🎯 先天格局深度解析")
            profiles = st.session_state.engine.get_innate_audit()
            for p in profiles:
                st.markdown(f"""
                <div class="innate-profile-card">
                    <div class="innate-banner">{p['header']}</div>
                    <div class="innate-body">
                        <div class="palace-def-line">{p['palace_def']}</div>
                        <div class="bullet-item"><div class="bullet-tag">* **深層意義：**</div><div class="bullet-text">{p['meaning']}</div></div>
                        <div class="bullet-item"><div class="bullet-tag">* **心理動機：**</div><div class="bullet-text">{p['motivation']}</div></div>
                        <div class="bullet-item"><div class="bullet-tag">* **具體影響：**</div><div class="bullet-text">{p['impact']}</div></div>
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
                "武曲化忌：鐵腕財務長遇危機。防資金斷鍊、周轉不靈。", "太陽化忌：跨國CEO面臨波及。小心外匯虧損、海外地雷。", "廉貞化忌：法務長踩紅線。求財易涉法務、行政罰金。", "太陰化忌：房產大亨資產凍結。防不動產套牢、租金回收難。", "天機化忌：數據分析師失誤。策略/交易Bug。頻繁進出損失。", "天同化忌：享樂天真陷阱。防盲目合夥欺騙、夕陽產業。", "貪狼化忌：投機客泡沫破裂。防詐騙、高槓桿爆倉、被駭風險。", "巨門化忌：公關災難。防流言誤判、合約漏洞。勿聽信內線。", "文昌/文曲化忌：信用破產。防票據糾紛、支票不兌現。", "Wealth Engines (Lu)：穩健/技術/金融三大引擎。"
            ]
            cols = st.columns(2)
            for i in range(10):
                with cols[i % 2]:
                    path = f"assets/logic_{i+1}.jpg"
                    if os.path.exists(path): st.image(path, caption=f"Chart {i+1}")
                    else: st.warning(f"Missing Chart {i+1}")
                    st.info(descriptions[i])
        with t6:
            st.info("AI 深度戰略審計整合中...")