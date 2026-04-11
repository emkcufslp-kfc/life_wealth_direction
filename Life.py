import streamlit as st
import datetime
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.join(os.getcwd(), "backend"))
from ziwei_engine import ZiWeiEngine

# --- 1. 系統設定與視覺化 UI ---
st.set_page_config(
    page_title="紫微財務風控系統 - Institutional Flagship", 
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Institutional CSS (Refined Warm Paper Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Noto+Sans+TC:wght@400;700;900&family=Outfit:wght@400;700;900&display=swap');
    
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
    .ceo-img { border-radius: 12px; border: 1px solid var(--paper-border); transition: transform 0.3s ease; }
    .ceo-img:hover { transform: scale(1.05); }
    
    .unified-grid-container {
        display: grid; grid-template-columns: repeat(4, 1fr); grid-template-rows: repeat(4, 1fr);
        gap: 12px; background: #eeede9; padding: 12px; border-radius: 20px;
    }
    .palace-box {
        background: white; border-radius: 15px; padding: 15px; min-height: 160px;
        display: flex; flex-direction: column; border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .palace-header { display: flex; justify-content: space-between; font-weight: 900; font-size: 1.1rem; }
    
    .center-clock {
        grid-column: 2 / span 2; grid-row: 2 / span 2;
        background: white; border-radius: 18px; border: 1.5px solid #e2e8f0;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center; padding: 30px; box-shadow: inset 0 2px 10px rgba(0,0,0,0.02);
    }
    
    .strategy-bubble {
        background: #f0fdf4; border-left: 5px solid #16a34a; border-radius: 8px; 
        padding: 12px 15px; margin-bottom: 12px; font-size: 0.9rem; font-weight: 700; color: #166534;
    }
    .innate-red-box {
        border: 2.5px solid #dc2626; border-radius: 15px; padding: 20px; margin-top: 15px;
        background: rgba(220, 38, 38, 0.01);
    }
    .innate-red-header {
        color: #dc2626; font-weight: 900; font-size: 1.2rem; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;
    }
    
    .innate-profile-card {
        background: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; padding: 0; margin-bottom: 30px;
        overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    }
    .innate-banner {
        background: #1e293b; color: #ffffff !important; padding: 15px 25px; font-weight: 700; font-size: 1.1rem;
        border-bottom: 4px solid #6366f1; letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧭 紫微財務風控系統：Global Flow Audit")

# --- Sidebar ---
st.sidebar.title("🗂️ 系統導航")
menu = st.sidebar.radio("模組地圖", ["🚀 核心財務審計", "📜 研報對照表"], index=0)

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
            <img src="data:image/png;base64,{st.session_state.engine.get_image_base64(audit["ceo"]["image"])}" width="100" class="ceo-img">
            <div>
                <div style="font-size:1.7rem; font-weight:900; color:var(--institutional-blue); margin-bottom:5px;">⚖️ 執行長報告：{audit["ceo"]["star"]}</div>
                <div style="font-size:1rem; color:#475569; letter-spacing:0.5px;">{audit["ceo"]["description"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c_grid, c_summary = st.columns([2, 1])
        with c_grid:
            def draw_box(idx):
                p = grid[idx]
                theme_color = "#8b5cf6" if p['name'] == '命宮' else ("#059669" if p['name'] == '財帛宮' else ("#d97706" if p['name'] == '田宅宮' else "#1e293b"))
                border_color = theme_color if p['name'] in ['命宮', '財帛宮', '田宅宮'] else "#e2e8f0"
                bg_color = (theme_color + "05") if p['name'] in ['命宮', '財帛宮', '田宅宮'] else "white"
                
                st.markdown(f"""
                <div class="palace-box" style="border-top: 5px solid {border_color}; background-color: {bg_color};">
                    <div class="palace-header" style="color: {theme_color};">
                        <span>{p['name']}</span> <span>{p['stem']}</span>
                    </div>
                    <div style="color:#d97706; font-size:1rem; font-weight:800; margin-top:8px;">{" ".join(p['major_stars'])}</div>
                    <div style="color:#15803d; font-size:0.85rem; font-weight:700;">{" ".join(p['wealth_stars'])} {" ".join(p['lucky_stars'])}</div>
                    <div style="color:#dc2626; font-size:0.85rem; font-weight:700;">{" ".join(p['sha_stars'])}</div>
                    <div style="margin-top:auto; padding-top:10px;">
                        <button style="width:100%; font-size:0.75rem; border-radius:6px; border:1px solid #e2e8f0; background:white; cursor:pointer; color:#64748b;">🔎 鎖定部門</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<div class="unified-grid-container">', unsafe_allow_html=True)
            r1 = st.columns(4)
            with r1[0]: draw_box(5)
            with r1[1]: draw_box(6)
            with r1[2]: draw_box(7)
            with r1[3]: draw_box(8)

            mid_grid = st.columns([1, 2, 1])
            with mid_grid[0]: draw_box(4); st.write(""); draw_box(3)
            with mid_grid[1]: 
                st.markdown(f'<div class="center-clock" style="height:355px;"><h1 style="font-size:3.5rem; margin:0;">{b_date.strftime("%Y-%m")}<br>{b_date.strftime("%d")}</h1><p style="font-size:1.2rem; color:#64748b; font-weight:700;">{b_hour_raw}</p></div>', unsafe_allow_html=True)
            with mid_grid[2]: draw_box(9); st.write(""); draw_box(10)

            r4 = st.columns(4)
            with r4[0]: draw_box(2)
            with r4[1]: draw_box(1)
            with r4[2]: draw_box(0)
            with r4[3]: draw_box(11)
            st.markdown('</div>', unsafe_allow_html=True)

        with c_summary:
            st.subheader("※ 戰略總論 (Summary)")
            for msg in audit['conclusions']:
                st.markdown(f'<div class="strategy-bubble">{msg}</div>', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="innate-red-box">
                <div class="innate-red-header">🎯 先天資本 (年生：{audit['innate']['stem']})</div>
                <div style="font-size:1rem; line-height:2; font-weight:700; color:#334155;">
            """, unsafe_allow_html=True)
            for t, d in audit['innate']['stars'].items():
                st.markdown(f"**{t}**：{d['star']} ➔ {d['palace']}")
            st.markdown("</div></div>", unsafe_allow_html=True)

        st.divider()
        st.subheader("🔍 財務部門深度審計報告 (Dept Audit)")
        t1, t2, t3, tx, t4, t5, t6 = st.tabs(["🏎️ 執行長部", "💸 業務部", "🏰 金庫部", "🎯 先天格局", "🛰️ 12宮連鎖", "📚 參考文庫", "🤖 AI 策略室"])
        
        def render_dept_audit(p_name, d):
            st.markdown(f"### 🛡️ {p_name} 審計細節")
            st.markdown("#### **第一層：先天構架**")
            if d['layer1']['stars']:
                for s in d['layer1']['stars']: st.info(f"**{s['star']}**: {s['comment']}")
            else: st.caption(d['layer1']['empty_msg'])
            st.markdown("#### **第二層：對待關係**")
            cl, cr = st.columns(2)
            with cl: st.success(f"📈 挹注 ➔ {d['layer2']['lu']['dest']}\n\n**{d['layer2']['lu']['why']}**\n\n💡 {d['layer2']['lu']['how']}\n\n✅ {d['layer2']['lu']['strategy']}")
            with cr: st.error(f"🛡️ 風險 ➔ {d['layer2']['ji']['dest']}\n\n**{d['layer2']['ji']['why']}**\n\n⚖️ {d['layer2']['ji']['how']}\n\n⚠️ {d['layer2']['ji']['strategy']}")

        with t1: render_dept_audit("命宮", audit['soul'])
        with t2: render_dept_audit("財帛宮", audit['wealth'])
        with t3: render_dept_audit("田宅宮", audit['property'])
        with tx:
            st.markdown("### 🎯 先天格局深度解析 (Psych Profile)")
            profiles = st.session_state.engine.get_innate_audit()
            for p in profiles:
                st.markdown(f"""
                <div class="innate-profile-card">
                    <div class="innate-banner">{p['header']}</div>
                    <div class="innate-body">
                        <div class="palace-def-line">{p['palace_def']}</div>
                        <div class="bullet-item"><div style="font-weight:900; min-width:100px;">* 深層意義：</div><div style="color:#475569;">{p['meaning']}</div></div>
                        <div class="bullet-item"><div style="font-weight:900; min-width:100px;">* 心理動機：</div><div style="color:#475569;">{p['motivation']}</div></div>
                        <div class="bullet-item"><div style="font-weight:900; min-width:100px;">* 具體影響：</div><div style="color:#475569;">{p['impact']}</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        with t4:
            st.markdown("### 🛰️ 全宮位聯鎖審計 (Flying Stars)")
            f_all = st.session_state.engine.fly_all_palaces()
            for p_n, p_d in f_all.items():
                with st.expander(f"{p_n} 流向 ➔ {p_d['lu_dest']} / {p_d['ji_dest']}"): st.markdown(f"**{p_d['collision']}**")
        with t5:
            st.markdown("### 📚 財富策略知識庫")
            cols = st.columns(2)
            for i in range(10):
                with cols[i % 2]:
                    st.image(f"assets/logic_{i+1}.jpg", use_container_width=True)
                    st.divider()
        with t6: st.info("AI 深度戰略審計整合中...")