import streamlit as st
import datetime
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.join(os.getcwd(), "backend"))
from ziwei_engine import ZiWeiEngine

# --- 1. 系統設定 (Institutional Flagship v6.10 - Accuracy Upgrade) ---
st.set_page_config(
    page_title="紫微財務風控系統 - Institutional Auditor", 
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Robust Session State Initialization
if 'focus_idx' not in st.session_state: st.session_state.focus_idx = 0
if 'audit_init' not in st.session_state: st.session_state.audit_init = False

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
        background: transparent; border: none;
        padding: 15px; text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: white; border-radius: 8px 8px 0 0; padding: 10px 20px; border: 1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ 紫微財務風控系統：Institutional Flagship (v6.50-GOLD)")

# --- Sidebar ---
st.sidebar.title("🗂️ 系統導航")
menu = st.sidebar.radio("模組地圖", ["🚀 核心財務審計", "📚 戰略文庫", "📜 研報概覽"], index=0)

# --- Helper: Strategic Library ---
def render_strategic_library():
    st.subheader("📚 專業財富策略存檔")
    try:
        if not os.path.exists("assets/Logic.md"):
            st.error("⚠️ 戰略文庫文件 (Logic.md) 遺失，請檢查 assets 目錄。")
            return
        with open("assets/Logic.md", "r", encoding="utf-8") as f: content = f.read()
        import re
        # Harden regex to catch variants like 'logic_1.jpg:', 'logic_2.jpg', 'logic_5.jpg '
        sections = re.split(r'(logic_\d\.jpg[:\s]*)', content)
        for i in range(1, len(sections), 2):
            img_marker = sections[i]
            img_name = img_marker.replace(":", "").strip()
            text_content = sections[i+1].strip() if i+1 < len(sections) else ""
            
            col_img, col_txt = st.columns([1, 1.5])
            with col_img: 
                img_data = st.session_state.engine.get_image_base64(img_name)
                if img_data:
                    st.image(img_data, use_container_width=True)
                else:
                    st.warning(f"⚠️ 資源載入失敗: {img_name}")
            with col_txt: st.markdown(text_content)
            st.divider()
    except Exception as e:
        st.error(f"⚠️ 載入庫房時發生錯誤: {e}")

if menu == "🚀 核心財務審計":
    b_date = st.sidebar.date_input("出生日期", datetime.date(1971, 11, 18))
    times = ["子時", "丑時", "寅時", "卯時", "辰時", "巳時", "午時", "未時", "申時", "酉時", "戌時", "亥時"]
    b_hour_raw = st.sidebar.selectbox("時辰", times, index=2)
    b_hour, gender, is_lunar = times.index(b_hour_raw), st.sidebar.radio("性別", ["男", "女"]), st.sidebar.checkbox("農曆")

    # Audit Engine Initialization
    if st.sidebar.button("🔄 重置全系統審計") or not st.session_state.audit_init:
        st.session_state.engine = ZiWeiEngine(b_date.year, b_date.month, b_date.day, b_hour, is_lunar, gender)
        st.session_state.audit_data = st.session_state.engine.get_wealth_audit()
        st.session_state.grid_data = st.session_state.engine.get_astrolabe_data()
        st.session_state.fly_data = st.session_state.engine.fly_all_palaces()
        st.session_state.audit_init = True

    audit = st.session_state.audit_data
    grid = st.session_state.grid_data
    fly_data = st.session_state.fly_data

    st.markdown(f"""<div class="ceo-card">
        <img src="{st.session_state.engine.get_image_base64(audit["ceo"]["image"])}" width="80" style="border-radius:10px; border:2px solid #6366f1;">
        <div><div style="font-size:1.6rem; font-weight:900;">⚖️ 執行長 (CEO)：{audit["ceo"]["star"]}</div><div>具備核心決策素質。</div></div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([2.5, 1])
    with c1:
        st.markdown('<div class="grid-container">', unsafe_allow_html=True)
        # Palace Box Drawing Logic
        def draw_palace_box(idx):
            p = grid[idx]
            is_focused = (st.session_state.focus_idx == idx)
            border_c = "#6366f1" if is_focused else "#334155"
            # Fixed Branch Name Mapping (子=0, 丑=1, ...)
            branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
            b_name = branches[idx]
            
            st.markdown(f"""
            <div class="palace-box" style="border-top: 4px solid {border_c};">
                <div class="palace-header">
                    <span style="color:white !important;">{p["name"]} ({b_name})</span>
                    <span style="color:#818cf8 !important;">{p["stem"]}</span>
                </div>
                <div style="color:#fbbf24; font-weight:900; margin-top:8px; font-size:1rem;">{" ".join(p["major_stars"])}</div>
                <div style="color:#10b981; font-size:0.8rem; font-weight:700;">{" ".join(p["lucky_stars"])}</div>
                <div style="color:#ef4444; font-size:0.8rem; font-weight:700;">{" ".join(p["sha_stars"])}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🎯 宮位四化", key=f"fbtn_{idx}"):
                st.session_state.focus_idx = idx
                st.rerun()

        r1 = st.columns(4)
        for i, idx in enumerate([5,6,7,8]): 
            with r1[i]: draw_palace_box(idx)
        
        st.write(""); mr = st.columns([1, 2, 1])
        with mr[0]: draw_palace_box(4); st.write(""); draw_palace_box(3)
        with mr[1]:
            # --- CENTRAL COMMAND CLUSTER (v6.10 Index-Based Accuracy) ---
            focus_p = grid[st.session_state.focus_idx]
            # Precise Lookup by Index (0-11)
            focus_fly = fly_data[st.session_state.focus_idx]
            
            rep_star = focus_fly['lu_star'] if focus_fly['lu_star'] in st.session_state.engine.CEO_IMAGES else (focus_p['major_stars'][0] if focus_p['major_stars'] else "紫微")
            rep_img = st.session_state.engine.get_image_base64(rep_star)
            
            st.markdown('<div class="decision-center">', unsafe_allow_html=True)
            if rep_img:
                st.image(rep_img, width=140)
            st.markdown(f"""
            <h1 style="color:var(--inst-blue) !important; font-size:2.4rem; margin-bottom:2px;">{focus_p['name']}</h1>
            <p style="color:#94a3b8 !important; font-size:1.1rem; font-weight:600; margin-bottom:15px;">{b_date.strftime('%Y-%m-%d')} · {b_hour_raw}</p>
            <div style="flex-direction: column; display:flex; align-items:center; gap:12px; margin-bottom:15px;">
                <div style="color:#10b981 !important; font-size:1.8rem; font-weight:900; background:rgba(16,185,129,0.05); padding:5px 20px; border-radius:10px;">
                    <span style="color:#10b981 !important;">{focus_fly.get('lu_star', '化祿')} ➔ {focus_fly.get('lu_dest', '未知')}</span>
                    <div style="font-size:0.8rem; font-weight:600; color:#10b981;">手段：{focus_fly.get('lu_means', '請重置審計')}</div>
                </div>
                <div style="color:#ef4444 !important; font-size:1.8rem; font-weight:900; background:rgba(239,68,68,0.05); padding:5px 20px; border-radius:10px;">
                    <span style="color:#ef4444 !important;">{focus_fly.get('ji_star', '化忌')} ➔ {focus_fly.get('ji_dest', '未知')}</span>
                    <div style="font-size:0.8rem; font-weight:600; color:#ef4444;">風險：{focus_fly.get('ji_hazard', '請重置審計')}</div>
                </div>
            </div>
            <div style="background:rgba(99,102,241,0.1); border-radius:10px; padding:10px 15px; border-left:4px solid #6366f1;">
                <p style="color:#818cf8 !important; font-size:0.95rem; font-weight:700; margin:0;">📜 核心邏輯：{focus_fly.get('source_msg', '請點擊重置按鈕更新數據')}</p>
            </div>
            </div>""", unsafe_allow_html=True)
            
        with mr[2]: draw_palace_box(9); st.write(""); draw_palace_box(10)
        
        st.write(""); r4 = st.columns(4)
        for i, idx in enumerate([2,1,0,11]): 
            with r4[i]: draw_palace_box(idx)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.subheader("🏁 首席審計診斷")
        st.markdown(f'<div style="background:white; border:1px solid #ef4444; border-radius:15px; padding:20px; font-size:0.9rem;"><h4 style="color:#ef4444 !important; margin-top:0;">🎯 先天資本 (年生：{audit["innate"]["stem"]})</h4>', unsafe_allow_html=True)
        for t, d in audit['innate']['stars'].items(): 
            p_display = st.session_state.engine.PALACE_NAME_MAP.get(d['palace'], d['palace'])
            st.markdown(f"**{t}**：<span style='color:#d97706; font-weight:800;'>{d['star']}</span> ➔ {p_display}", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    # --- RESTORED AUDIT TABS ---
    st.divider()
    t1, t2, t3, tx, t4, t5 = st.tabs(["🏎️ 決策部", "💸 業務部", "🏰 金庫部", "🎯 先天格局", "🛰️ 12宮連鎖", "📚 文庫指南"])
    
    # Mapping Dept Data by Index to avoid name conflicts
    with t1: 
        st.markdown("### 🏎️ 決策部 (命宮) 核心戰略解析")
        prof_html = ""
        for p in audit['soul']['profiles']:
            prof_html += f'<p><b>{p["star"]}</b> - {p["desc"]}</p>'
        
        st.markdown(f"""
        <div style="background:white; border-left:5px solid #6366f1; border-radius:12px; padding:20px; margin-bottom:20px;">
            <h4 style="color:#6366f1 !important; margin-top:0;">🌟 核心主星才能 (The CEO Profile)</h4>
            {prof_html}
        </div>
        
        <div style="background:rgba(251,191,36,0.05); border:1px dashed #fbbf24; border-radius:12px; padding:20px;">
            <h4 style="color:#d97706 !important; margin-top:0;">🛡️ 專家戰略註記 (Strategy Note)</h4>
            <p>命宮主導了您的決策基調與整體氣質。結合目前宮位配置，這套核心主星組合決定了您在理財與事業上的底層決策邏輯。</p>
            <p><b>專家筆記：</b> 現金流流向核心（星曜化祿 ➔ {audit['soul']['layer2']['lu']['dest']}），建議利用主星的天賦優勢，將外部資源轉化為長期穩定的戰略資產。</p>
        </div>
        """, unsafe_allow_html=True)
    with t2: 
        st.markdown("### 💸 業務部 (財帛宮) 核心戰略解析")
        prof_html = ""
        for p in audit['wealth']['profiles']:
            prof_html += f'<p><b>{p["star"]}</b> - {p["desc"]}</p>'
            
        st.markdown(f"""
        <div style="background:white; border-left:5px solid #10b981; border-radius:12px; padding:20px; margin-bottom:20px;">
            <h4 style="color:#10b981 !important; margin-top:0;">🌟 業務部核心能手 (The Business Profile)</h4>
            {prof_html}
        </div>
        
        <div style="background:rgba(16,185,129,0.05); border:1px dashed #10b981; border-radius:12px; padding:20px;">
            <h4 style="color:#059669 !important; margin-top:0;">🛡️ 財富戰略與專家註記 (Wealth Strategy)</h4>
            <p>財帛宮具備強大的求財能量。此宮位的主星反映了您最擅長的盈利模式與市場開拓能力。</p>
            <p><b>專家筆記：</b> 現金流流向核心（星曜化祿 ➔ {audit['wealth']['layer2']['lu']['dest']}），建議根據主星屬性執行對應的市場策略，利用變革或穩定來獲取紅利。</p>
        </div>
        """, unsafe_allow_html=True)
    with t3: 
        st.markdown("### 🏰 金庫部 (田宅宮) 核心戰略解析")
        prof_html = ""
        for p in audit['property']['profiles']:
            prof_html += f'<p><b>{p["star"]}</b> - {p["desc"]}</p>'
            
        st.markdown(f"""
        <div style="background:white; border-left:5px solid #3b82f6; border-radius:12px; padding:20px; margin-bottom:20px;">
            <h4 style="color:#3b82f6 !important; margin-top:0;">🌟 金庫部核心守衛 (The Treasurer Profile)</h4>
            {prof_html}
        </div>
        
        <div style="background:rgba(59,130,246,0.05); border:1px dashed #3b82f6; border-radius:12px; padding:20px;">
            <h4 style="color:#1d4ed8 !important; margin-top:0;">🛡️ 資產防禦與專家註記 (Treasury Strategy)</h4>
            <p>此宮位代表了企業的總財庫。主星坐守的情況，決定了資產結構的穩定程度。應根據主星特性，在實體資產與風險投資之間取得平衡。</p>
            <p><b>專家筆記：</b> 現金流流向核心（星曜化祿 ➔ {audit['property']['layer2']['lu']['dest']}），建議將利潤轉化為符合主星特質的資產形態，利用穩健的防禦力來抵禦外界波動。</p>
        </div>
        """, unsafe_allow_html=True)
    with tx:
        st.markdown("### 🎯 先天格局 (Innate Matrix) 全維度戰略審計")
        st.info("💡 此表分析您與生俱來的能量分配。化祿代表獲利機遇，化忌代表風險盲點。")
        for p in st.session_state.engine.get_innate_audit():
            st.markdown(f"""
            <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; margin-bottom:20px; padding:25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                <h4 style="color:#1e3a8a !important; margin-top:0; border-bottom:2px solid #f1f5f9; padding-bottom:10px;">{p["header"]}</h4>
                <p style="color:#475569; font-weight:600; font-size:1rem;">{p["palace_def"]}</p>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin-top:15px;">
                    <div style="background:#f8fafc; padding:15px; border-radius:8px; border-left:4px solid #6366f1;">
                        <small style="color:#6366f1; font-weight:bold; text-transform:uppercase;">核心策略 (SOP)</small><br>
                        <span style="color:#1e293b; font-size:0.95rem;">{p["meaning"]}</span>
                    </div>
                    <div style="background:#fff7ed; padding:15px; border-radius:8px; border-left:4px solid #f59e0b;">
                        <small style="color:#f59e0b; font-weight:bold; text-transform:uppercase;">具體影響 (Impact)</small><br>
                        <span style="color:#1e293b; font-size:0.95rem;">{p["impact"]}</span>
                    </div>
                </div>
                <div style="margin-top:15px; background:rgba(99,102,241,0.05); padding:10px; border-radius:6px; font-size:0.9rem; color:#4338ca;">
                    <b>📍 專家決策建議：</b> {p["sop"]}
                </div>
            </div>""", unsafe_allow_html=True)
    with t4:
        st.markdown("### 🛰️ 偵察部 (12宮連鎖) 戰略路徑全域審計")
        st.info("💡 此模組透過『發射站 ➔ 能量載體 ➔ 落點效應』三位一體邏輯，鎖定企業內部的獲利動能與風險破洞。")
        
        for p_idx, p_d in fly_data.items():
            # Build HTML list for warnings
            warnings_list = "".join([f"<li>{w}</li>" for w in p_d.get('warnings', [])])
            # Build badges for prescriptions
            presc_badges = "".join([f'<span style="background:#d1fae5; color:#065f46; padding:4px 12px; border-radius:4px; font-size:0.85rem; font-weight:700;">{p}</span>' for p in p_d.get('prescription', [])])
            
            st.markdown(f"""
<div style="background:white; border:1px solid #e2e8f0; border-radius:15px; padding:25px; margin-bottom:20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
    <!-- Header -->
    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #f1f5f9; padding-bottom:12px; margin-bottom:15px;">
        <h3 style="margin:0; color:#1e293b; font-weight:900;">🏢 {p_d.get('name', '未知')} ({p_d.get('stem', '?')}干)</h3>
        <span style="background:#f1f5f9; color:#64748b; padding:4px 12px; border-radius:20px; font-size:0.8rem; font-weight:700;">Audit Cluster #{p_idx+1}</span>
    </div>

    <!-- Path & Intent -->
    <div style="margin-bottom:15px;">
        <div style="color:#64748b; font-size:0.85rem; font-weight:700; text-transform:uppercase;">🛰️ 戰略路徑 (Path)</div>
        <div style="color:#1e293b; font-size:1.1rem; font-weight:800; margin:5px 0;">{p_d.get('path', 'N/A')}</div>
        <div style="background:rgba(99,102,241,0.08); padding:8px 12px; border-radius:6px; color:#4338ca; font-size:0.95rem; font-weight:700; border-left:4px solid #6366f1;">
            🚀 關鍵意涵：{p_d.get('intent', 'N/A')}
        </div>
    </div>

    <!-- Warnings -->
    <div style="background:#fffcf0; border:1px solid #fef3c7; border-radius:8px; padding:15px; margin-bottom:15px;">
        <div style="color:#92400e; font-weight:800; font-size:0.85rem; margin-bottom:8px;">⚠️ 預警警號 (Warning Signals)</div>
        <ul style="margin:0; padding-left:20px; color:#92400e; font-size:0.9rem; line-height:1.6;">
            {warnings_list}
        </ul>
    </div>

    <!-- Diagnosis -->
    <div style="background:rgba(71,85,105,0.05); border-left:5px solid #475569; padding:15px; border-radius:4px; margin-bottom:15px;">
        <div style="color:#475569; font-weight:800; font-size:0.85rem; margin-bottom:5px;">📍 專家綜合診斷 (Expert Diagnosis)</div>
        <div style="color:#1e293b; font-size:1rem; font-weight:700; line-height:1.4;">{p_d.get('diagnosis', 'N/A')}</div>
    </div>

    <!-- Prescription -->
    <div style="background:rgba(16,185,129,0.03); border:1px solid rgba(16,185,129,0.1); border-radius:8px; padding:15px;">
        <div style="color:#065f46; font-weight:800; font-size:0.85rem; margin-bottom:8px;">💡 處方箋 (Prescription)</div>
        <div style="display:flex; flex-wrap:wrap; gap:10px;">
            {presc_badges}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
    with t5:
        render_strategic_library()

if menu == "📚 戰略文庫":
    render_strategic_library()

if menu == "📜 研報概覽":
    st.subheader("紫微財務戰略研究報告")
    with open("紫微斗數財運四化解析.md", "r", encoding="utf-8") as f: st.markdown(f.read())