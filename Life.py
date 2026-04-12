import streamlit as st
import datetime
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.join(os.getcwd(), "backend"))
from ziwei_engine import ZiWeiEngine

# --- 1. 系統設定 (Institutional Flagship v6.0 - Dark Neon Focus) ---
st.set_page_config(
    page_title="紫微財務風控系統 - Dark Neon Focus", 
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Neon Institutional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&family=Inter:wght@400;600;800&display=swap');
    
    :root {
        --dark-bg: #0f172a;
        --card-bg: #1e293b;
        --accent-indigo: #6366f1;
        --star-major: #fbbf24;
        --star-lucky: #10b981;
        --star-sha: #ef4444;
        --text-white: #f8fafc;
    }

    .stApp { background-color: var(--dark-bg); color: var(--text-white); }
    h1, h2, h3, h4, p, span { font-family: 'Noto Sans TC', sans-serif; color: var(--text-white) !important; }
    
    /* Palace Box Styling */
    .palace-box {
        background: var(--card-bg); border-radius: 12px; padding: 15px; min-height: 185px;
        display: flex; flex-direction: column; border: 1px solid #334155;
        transition: transform 0.2s, border-color 0.2s;
    }
    .palace-box:hover { border-color: var(--accent-indigo); transform: translateY(-2px); }
    .palace-header { display: flex; justify-content: space-between; font-weight: 900; font-size: 1.1rem; }
    .palace-stem { color: #818cf8 !important; font-size: 0.9rem; }
    
    /* Central Decision Cluster */
    .decision-center {
        background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%);
        border: 2px solid var(--accent-indigo); border-radius: 20px;
        padding: 30px; text-align: center; height: 100%;
        box-shadow: 0 0 25px rgba(99, 102, 241, 0.2);
    }
    .status-badge {
        background: rgba(255,255,255,0.05); border: 1px solid #334155; border-radius: 10px;
        padding: 15px; margin-top: 25px; font-size: 0.95rem; line-height: 1.6;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%; border-radius: 8px; border: 1px solid #334155; background: rgba(255,255,255,0.03);
        color: #94a3b8; font-size: 0.8rem; height: 32px; transition: all 0.2s;
    }
    .stButton>button:hover { border-color: var(--accent-indigo); color: white; background: rgba(99, 102, 241, 0.1); }
</style>
""", unsafe_allow_html=True)

st.title("🌌 紫微財務風控系統：Institutional v6.0")

# --- State Management ---
if 'focus_idx' not in st.session_state:
    st.session_state.focus_idx = 0  # Default to Life Palace (命宮)

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

    # Layout: Grid + Side Panel
    c1, c2 = st.columns([2.5, 1])
    
    with c1:
        def draw_box(idx):
            p = grid[idx]
            is_focused = (st.session_state.focus_idx == idx)
            border_color = "#6366f1" if is_focused else "#334155"
            
            st.markdown(f"""
            <div class="palace-box" style="border-top: 3px solid {border_color};">
                <div class="palace-header">
                    <span>{p["name"]}</span>
                    <span class="palace-stem">{p["stem"]}</span>
                </div>
                <div style="color:#fbbf24; font-weight:800; margin-top:8px; font-size:1rem;">{" ".join(p["major_stars"])}</div>
                <div style="color:#10b981; font-size:0.85rem; font-weight:600; margin-top:4px;">{" ".join(p["lucky_stars"])}</div>
                <div style="color:#ef4444; font-size:0.85rem; font-weight:600;">{" ".join(p["sha_stars"])}</div>
                <div style="flex-grow:1;"></div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🎯 宮位四化", key=f"focus_{idx}"):
                st.session_state.focus_idx = idx
                st.rerun()

        # 4x4 Ring Grid
        r1 = st.columns(4)
        for i, idx in enumerate([5,6,7,8]): 
            with r1[i]: draw_box(idx)
        
        st.write("")
        mr = st.columns([1, 2, 1])
        with mr[0]: draw_box(4); st.write(""); draw_box(3)
        
        # --- Central Decision Cluster ---
        with mr[1]:
            focus_p = grid[st.session_state.focus_idx]
            focus_fly = fly_data[focus_p['name']]
            
            st.markdown(f"""
            <div class="decision-center">
                <h1 style="color:#fbbf24 !important; font-size:2.8rem; margin-bottom:0;">{b_date.year}</h1>
                <p style="color:#94a3b8 !important; font-size:1.1rem; margin-bottom:30px;">{b_date.strftime("%m-%d")} ({b_hour_raw}) {focus_p['name']}</p>
                
                <h2 style="color:#10b981 !important; font-size:1.6rem; margin-bottom:10px;">{focus_fly['lu_dest']}</h2>
                <h2 style="color:#ef4444 !important; font-size:1.6rem; margin-bottom:30px;">{focus_fly['ji_dest']}</h2>
                
                <div class="status-badge">
                    <span style="color:#fbbf24 !important; font-weight:900;">【動態分布】</span>
                    獲利導向「{focus_fly['lu_dest'].split(' ')[-1]}」，但風險潛伏於「{focus_fly['ji_dest'].split(' ')[-1]}」。
                    建議利用「{focus_fly['lu_dest'].split(' ')[-1]}」的盈餘來填補「{focus_fly['ji_dest'].split(' ')[-1]}」的漏洞。
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with mr[2]: draw_box(9); st.write(""); draw_box(10)
        
        st.write("")
        r4 = st.columns(4)
        for i, idx in enumerate([2,1,0,11]): 
            with r4[i]: draw_box(idx)

    with c2:
        st.subheader("🏁 首席審計診斷")
        st.info("【策略提示】點擊宮位「聚焦」以查看部門四化流向。")
        st.markdown(f"""
        <div style="background:#1e293b; border:1px solid #ef4444; border-radius:15px; padding:20px;">
            <h4 style="color:#ef4444 !important; margin-top:0;">🎯 先天資本 (年生：{audit["innate"]["stem"]})</h4>
        """, unsafe_allow_html=True)
        for t, d in audit['innate']['stars'].items(): 
            st.markdown(f"**{t}**：<span style='color:#fbbf24'>{d['star']}</span> ➔ {d['palace']}", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("")
        st.markdown("### 🤖 AI 智能建議")
        ak = st.secrets.get("GOOGLE_API_KEY", "") or st.sidebar.text_input("Gemini API Key", type="password")
        if st.button("🚀 執行 AI 戰略分析"):
            if ak:
                with st.spinner("戰略模擬中..."):
                    res = st.session_state.engine.get_ai_audit(audit, api_key=ak)
                    st.markdown(f'<div style="background:rgba(255,255,255,0.05); border:1px solid #334155; border-radius:10px; padding:15px; font-size:0.9rem;">{res}</div>', unsafe_allow_html=True)
            else: st.warning("請輸入 API Key")

if menu == "📚 戰略文庫":
    st.subheader("📚 專業財富策略存檔")
    with open("assets/Logic.md", "r", encoding="utf-8") as f:
        st.markdown(f.read())

if menu == "📜 研報概覽":
    st.subheader("紫微財務戰略研究報告")
    with open("紫微斗數財運四化解析.md", "r", encoding="utf-8") as f: 
        st.markdown(f.read())