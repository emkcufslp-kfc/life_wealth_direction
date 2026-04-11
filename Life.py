import streamlit as st
import datetime
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.join(os.getcwd(), "backend"))
from ziwei_engine import ZiWeiEngine

# --- 1. 系統設定與視覺化 UI ---
st.set_page_config(
    page_title="紫微財務風控系統 - Life Inc.", 
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Outfit:wght@400;700&display=swap');
    
    :root {
        --glass-bg: rgba(30, 41, 59, 0.7);
        --glass-border: rgba(148, 163, 184, 0.1);
        --primary: #6366f1;
        --secondary: #fbbf24;
        --danger: #ef4444;
        --success: #22c55e;
        --info: #38bdf8;
    }

    .main { background-color: #0f172a; }
    
    /* Header styling */
    .stHeading h1 { font-family: 'Outfit', sans-serif; font-weight: 800; color: #f8fafc; }
    
    /* CEO Card styling */
    .ceo-card {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 24px;
        transition: transform 0.3s ease;
    }
    .ceo-card:hover { transform: translateY(-5px); border-color: var(--primary); }
    .ceo-img { border-radius: 12px; border: 2px solid var(--primary); box-shadow: 0 0 20px rgba(99, 102, 241, 0.2); }
    .ceo-title { font-size: 1.5rem; font-weight: 700; color: var(--secondary); margin-bottom: 8px; }
    .ceo-desc { color: #cbd5e1; font-size: 1rem; line-height: 1.6; }

    /* Conclusion Alert */
    .stAlert { border-radius: 12px; border: none; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

    /* Astrolabe Grid */
    .palace-box {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 15px; /* Softer rounded corners */
        padding: 12px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        min-height: 155px;
        position: relative;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .palace-box:hover { 
        border-color: var(--primary); 
        background-color: #1e1b4b; 
        z-index: 10; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* Grid Boundary Line */
    .unified-grid-container {
        position: relative;
        border-radius: 20px;
        padding: 5px;
        background-color: #4f46e5;
        display: grid;
        grid-template: repeat(4, 1fr) / repeat(4, 1fr);
        gap: 2px;
        box-shadow: 0 0 50px rgba(79, 70, 229, 0.3);
    }
</style>
""", unsafe_allow_html=True)

st.title("🧭 紫微財務風控：格局與風險審計系統")
st.markdown("本系統整合《飛星及欽天派財運解析》，自動完成從化祿獲利導航到化忌風險防火牆的深度審計。")
st.sidebar.caption("系統版本: v1.0.4-TwoLayer (Updated)")

# --- 2. Sidebar Navigation & Global References ---
st.sidebar.title("🗂️ 系統導航")
menu = st.sidebar.radio(
    "選擇功能模組",
    ["🚀 核心財務審計", "📜 十干四化對照表"],
    index=0
)

# --- 3. 渲染命盤函數 (Clickable Grid) ---
def render_astrolabe_grid(grid_data, audit, focused_trans=None, birth_info=None):
    def draw_palace_cell(idx):
        p = grid_data[idx]
        is_lu = p['name'] == audit['wealth']['lu_dest']
        is_ji = (p['name'] == audit['wealth']['ji_dest']) or ('命宮' in p['name'] and 'ji' in audit['ceo'].get('star', '')) # Simple heuristic for focus
        
        # Soul Palace (Red) vs Wealth Palace (Green) logic from image
        border_color = "#334155"
        if p['name'] == '命宮': border_color = "#ef4444" # Soul = Red
        elif p['name'] == '財帛宮': border_color = "#22c55e" # Wealth = Green
        elif is_lu: border_color = "#22c55e"
        elif is_ji: border_color = "#ef4444"
            
        # Star Processing Helper with Si Hua Check
        def process_stars(star_list, cat_color):
            processed = []
            innate_info = audit.get('innate', {}).get('stars', {})
            innate_colors = {"祿": "#22c55e", "權": "#fbbf24", "科": "#38bdf8", "忌": "#ef4444"}
            
            for star in star_list:
                # Clean name for matching
                clean_star = star.strip().replace(" ", "")
                star_text = star
                
                # 1. Check for Innate (Birth-year) Si Hua - Static
                for t_type, s_data in innate_info.items():
                    target_star = s_data['star'].strip().replace(" ", "")
                    # Direct match or containment
                    if target_star in clean_star or clean_star in target_star:
                        if s_data['palace'] == p['name']:
                            color = innate_colors.get(t_type, "#cbd5e1")
                            star_text = f'<span style="color:{color}; font-weight:800; border-bottom:1px solid {color}">{star}(生年{t_type})</span>'
                
                # 2. Check for Relational (Palace-flying) Si Hua - Dynamic
                if focused_trans:
                    match = None
                    for ts_name, ts_data in focused_trans.items():
                        clean_ts = ts_name.strip().replace(" ", "")
                        if clean_ts in clean_star or clean_star in clean_ts:
                            match = ts_data
                            break
                    if match and match['dest'] == p['name']:
                        if match['type'] == '祿':
                            star_text = f'<span style="color:#22c55e">{star_text}(祿)</span>'
                        elif match['type'] == '忌':
                            star_text = f'<span style="color:#ef4444">{star_text}(忌)</span>'
                
                processed.append(star_text)
            
            # Special logic for Lu Cun (Dark Green)
            final_processed = []
            for s in processed:
                if "祿存" in s or "禄存" in s:
                    final_processed.append(f'<span style="color:#006400; font-weight: 900;">{s}</span>')
                else:
                    final_processed.append(s)
            
            return f'<div style="font-size: 0.8rem; color: {cat_color}; font-weight: 700; margin-top: 4px;">{" ".join(final_processed)}</div>'

        major_html = process_stars(p["major_stars"], "#fbbf24")
        lucky_html = process_stars(p.get("lucky_stars", []), "#4ade80")
        wealth_html = process_stars(p.get("wealth_stars", []), "#006400")
        sha_html = process_stars(p.get("sha_stars", []), "#ef4444")
        minor_html = process_stars(p["minor_stars"], "#94a3b8")

        # Unified Card Block (Request #2 Fix: Everything inside the box)
        st.markdown(f"""
            <div style="border: 1.5px solid {border_color}; background-color: #0f172a; border-radius: 12px; padding: 12px; min-height: 180px; display: flex; flex-direction: column;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 5px;">
                    <span style="font-weight: 800; color: #f8fafc; font-size: 1.1rem;">{p['name']}</span>
                    <span style="color: #818cf8; font-size: 0.8rem; font-weight: 600;">{p['stem']}{p.get('branch', '')}</span>
                </div>
                {major_html}
                {lucky_html}
                {wealth_html}
                {sha_html}
                {minor_html}
            </div>
        """, unsafe_allow_html=True)
        
        # Focus button - placed immediately below to maintain grid alignment
        if st.button("🎯 聚焦", key=f"btn_{idx}_{p['name']}", use_container_width=True):
            st.session_state.focused_p = p['name']
            st.rerun()

    # UI Grid Execution
    st.markdown('<div class="unified-grid-container">', unsafe_allow_html=True)
    
    # Grid Row Layout using custom columns for precision
    r0 = st.columns(4)
    with r0[0]: draw_palace_cell(5)
    with r0[1]: draw_palace_cell(6)
    with r0[2]: draw_palace_cell(7)
    with r0[3]: draw_palace_cell(8)
    
    col_l, col_c, col_r = st.columns([1, 2, 1])
    
    with col_l:
        draw_palace_cell(4)
        st.write("")
        draw_palace_cell(3)
        
    with col_c:
        hub_content = ""
        if st.session_state.get("focused_p"):
            p_name = st.session_state.focused_p
            all_flying = st.session_state.engine.fly_all_palaces()
            data = all_flying.get(p_name, {})
            hub_content += f'<div style="margin-top: 20px; width: 100%; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px;">'
            hub_content += f'<div style="font-size: 1.4rem; color: #22c55e; font-weight: 800; text-shadow: 0 0 10px rgba(34, 197, 94, 0.3);">{data["lu_star"]}化祿 ➔ {data["lu_dest"]}</div>'
            hub_content += f'<div style="font-size: 1.4rem; color: #ef4444; font-weight: 800; margin-top: 12px; text-shadow: 0 0 10px rgba(239, 68, 68, 0.3);">{data["ji_star"]}化忌 ➔ {data["ji_dest"]}</div>'
            hub_content += f'<div style="font-size: 0.95rem; color: #fbbf24; margin-top: 25px; line-height: 1.6; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 12px; border: 1px solid rgba(251, 191, 36, 0.1);">{data["collision"]}</div>'
            hub_content += f'</div>'

        st.markdown(f"""
<div style="background: radial-gradient(circle, #312e81 0%, #1e1b4b 100%); 
            border-radius: 20px; border: 2px solid #4f46e5; 
            min-height: 420px; display: flex; flex-direction: column; 
            align-items: center; justify-content: center; padding: 25px; 
            text-align: center; color: white; box-shadow: inset 0 0 30px rgba(79, 70, 229, 0.2);">
    <div style="font-size: 2.2rem; font-weight: 900; color: #fbbf24; margin-bottom: 5px; text-shadow: 0 0 15px rgba(251, 191, 36, 0.4);">{birth_info['date']}</div>
    <div style="font-size: 1.4rem; color: #cbd5e1; font-weight: 600; margin-bottom: 20px;">{birth_info['time']}</div>
    <div style="margin: 15px 0; border-top: 2px solid rgba(255,255,255,0.1); width: 150px;"></div>
    {hub_content}
</div>
""", unsafe_allow_html=True)
        
    with col_r:
        draw_palace_cell(9)
        st.write("")
        draw_palace_cell(10)

    r3 = st.columns(4)
    with r3[0]: draw_palace_cell(2)
    with r3[1]: draw_palace_cell(1)
    with r3[2]: draw_palace_cell(0)
    with r3[3]: draw_palace_cell(11)

    # --- Si Hua Arrow Overlay (SVG) ---
    if focused_trans:
        coords = {
            5: (12.5, 12.5), 6: (37.5, 12.5), 7: (62.5, 12.5), 8: (87.5, 12.5),
            4: (12.5, 37.5), 9: (87.5, 37.5),
            3: (12.5, 62.5), 10: (87.5, 62.5),
            2: (12.5, 87.5), 1: (37.5, 87.5), 0: (62.5, 87.5), 11: (87.5, 87.5)
        }
        
        p_name_to_idx = {p['name']: i for i, p in enumerate(grid_data)}
        arrows_svg = ""
        all_flying = st.session_state.engine.fly_all_palaces()
        f_name = st.session_state.focused_p
        data = all_flying.get(f_name, {})
        target_dest = {"祿": data["lu_dest"], "忌": data["ji_dest"]}
        colors = {"祿": "#22c55e", "忌": "#ef4444"}
        
        for t_type, d_name in target_dest.items():
            d_idx = p_name_to_idx.get(d_name)
            if d_idx is not None and d_idx in coords:
                end_x, end_y = coords[d_idx]
                arrows_svg += f'<line x1="50%" y1="50%" x2="{end_x}%" y2="{end_y}%" stroke="{colors[t_type]}" stroke-width="3" marker-end="url(#arrowhead-{t_type})" />'

        st.markdown(f"""
            <div style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:1000;">
                <svg width="100%" height="100%">
                    <defs>
                        <marker id="arrowhead-祿" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                            <polygon points="0 0, 10 3.5, 0 7" fill="#22c55e" />
                        </marker>
                        <marker id="arrowhead-忌" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                            <polygon points="0 0, 10 3.5, 0 7" fill="#ef4444" />
                        </marker>
                    </defs>
                    {arrows_svg}
                </svg>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. Main Menu Logic ---
if menu == "🚀 核心財務審計":
    st.sidebar.header("👤 執行長資料輸入")
    birth_date = st.sidebar.date_input(
        "出生日期", 
        datetime.date(1990, 1, 1),
        min_value=datetime.date(1927, 1, 1),
        max_value=datetime.date(2026, 12, 31)
    )
    time_branches = [
        "(23:00-01:00) 子時", "(01:00-03:00) 丑時", "(03:00-05:00) 寅時", "(05:00-07:00) 卯時",
        "(07:00-09:00) 辰時", "(09:00-11:00) 巳時", "(11:00-13:00) 午時", "(13:00-15:00) 未時",
        "(15:00-17:00) 申時", "(17:00-19:00) 酉時", "(19:00-21:00) 戌時", "(21:00-23:00) 亥時"
    ]
    birth_hour_raw = st.sidebar.selectbox("出生時辰", time_branches, index=5)
    birth_hour = time_branches.index(birth_hour_raw)
    gender = st.sidebar.radio("性別", ["男", "女"], index=0)
    is_lunar = st.sidebar.checkbox("是否為農曆日期", value=False)

    if st.sidebar.button("🚀 開始深度財務審計", use_container_width=True) or 'audit_data' in st.session_state:
        try:
            # Force re-calculation if 'innate' key is missing (ensures migration to new logic)
            force_recalc = 'audit_data' in st.session_state and 'innate' not in st.session_state.audit_data
            
            if 'engine' not in st.session_state or st.sidebar.button("🔄 重新計算") or force_recalc:
                st.session_state.engine = ZiWeiEngine(birth_date.year, birth_date.month, birth_date.day, birth_hour, is_lunar, gender)
                st.session_state.audit_data = st.session_state.engine.get_wealth_audit()
                st.session_state.grid_data = st.session_state.engine.get_astrolabe_data()
                st.session_state.focused_p = None

            engine = st.session_state.engine
            audit = st.session_state.audit_data
            grid_data = st.session_state.grid_data
            
            # --- CEO Header ---
            st.markdown(f"""
            <div class="ceo-card">
                <img src="data:image/png;base64,{st.session_state.engine.get_image_base64(audit['ceo']['image'])}" width="120" class="ceo-img">
                <div>
                    <div class="ceo-title">🕵️‍♂️ 人生公司執行長：{audit['ceo']['star']}星坐命</div>
                    <div class="ceo-desc">{audit['ceo']['description']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.divider()

            col1, col2 = st.columns([2, 1])
            
            focused_p = st.session_state.get("focused_p")
            focused_trans = None
            if focused_p:
                focused_trans = engine.get_palace_transformations(focused_p)

            with col1:
                st.subheader("🏛️ 命盤獲利與風險分佈圖 (點擊宮位進行審計)")
                birth_info = {"date": birth_date.strftime("%Y-%m-%d"), "time": birth_hour_raw}
                render_astrolabe_grid(
                    grid_data, 
                    audit=audit,
                    focused_trans=focused_trans,
                    birth_info=birth_info
                )
                
            with col2:
                st.subheader("🏁 最終戰略結論")
                for msg in audit['strategic_conclusions']:
                    if "警報" in msg: st.error(msg)
                    elif "併購" in msg: st.info(msg)
                    elif "陽升陰降" in msg: st.success(msg)
                    else: st.warning(msg)
                
                st.divider()
                st.subheader("🎯 格局、天賦與意志力")
                p = audit['patterns']
                st.markdown(f"**核心天賦**: {p['talent']}")
                st.markdown(f"**意志力評估**: {p['willpower']}")
                st.info(f"**發展方向建議**: {p['direction']}")
                
                # --- [NEW] Innate Potential Map (Red Box) ---
                if 'innate' in audit:
                    st.markdown(f"""
                        <div style="padding: 20px; 
                                    background: rgba(239, 68, 68, 0.1); 
                                    border: 2px solid #ef4444; 
                                    border-radius: 15px; 
                                    margin-top: 15px; 
                                    margin-bottom: 25px;
                                    box-shadow: 0 0 15px rgba(239, 68, 68, 0.15);">
                            <h4 style="color: #ef4444; margin-bottom: 15px; font-size: 1.2rem; font-weight: 800; display: flex; align-items: center; gap: 8px;">
                                🎯 先天格局分布 (生年：{audit['innate']['stem']}干)
                            </h4>
                            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
                    """, unsafe_allow_html=True)
                    
                    innate_stars = audit['innate']['stars']
                    colors = {"祿": "#22c55e", "權": "#fbbf24", "科": "#38bdf8", "忌": "#ef4444"}
                    for t_type, s_data in innate_stars.items():
                        st.markdown(f"""
                            <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; border-left: 4px solid {colors[t_type]};">
                                <span style="color: {colors[t_type]}; font-weight: 800; font-size: 0.9rem;">{t_type}</span>
                                <div style="color: #f8fafc; font-weight: 600; font-size: 1rem;">{s_data['star']}</div>
                                <div style="color: #94a3b8; font-size: 0.8rem;">位於：{s_data['palace']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div><div style='color: #cbd5e1; font-size: 0.8rem; margin-top: 12px; font-style: italic;'>註：先天四化為出生時賦予的原始潛能與底氣</div></div>", unsafe_allow_html=True)
                
                # --- Pillar Summary Block (Updated Label) ---

            st.divider()
            
            # --- Strategic Audit Details ---
            st.subheader("🔍 財務部門深度審計報告")
            t1, t2, t3, t4 = st.tabs(["💸 業務部", "🏡 金庫部", "🛰️ 12宮連鎖", "🤖 AI CEO 策略審計"])
            
            with t1:
                w = audit['wealth']
                st.markdown(f"#### 🏦 業務部 (財帛宮) 審計報告")
                
                # --- Layer 1: Innate Setup ---
                st.subheader("🛠️ 第一層：先天構架 (Innate Setup)")
                st.info(f"**先天資源分佈**: {', '.join(w['innate_setup'])}")
                
                # --- Layer 2: Relational Flow ---
                st.subheader("🔄 第二層：對待關係 (Relational Flow)")
                c1, c2 = st.columns(2)
                with c1:
                    st.success(f"📈 **獲利導向 (祿)**: {w['lu_dest']}")
                    st.markdown(f"> **流向原因**: {w['lu_why']}")
                    st.markdown(f"💡 **戰略解法**: {w['lu_how']}")
                    st.markdown(f"✅ **最終戰略**: {w['lu_conclusion']}")
                with c2:
                    st.error(f"📉 **風險防火牆 (忌)**: {w['ji_dest']}")
                    st.markdown(f"> **壓力來源**: {w['ji_why']}")
                    st.markdown(f"💡 **戰略防護**: {w['ji_how']}")
                    st.markdown(f"⚠️ **最終戰略**: {w['ji_conclusion']}")
                st.divider()
                st.warning(f"**宮位對待動態**: {w['collision']}")

            with t2:
                pr = audit['property']
                st.markdown(f"#### 🏰 金庫部 (田宅宮) 審計報告")
                
                # --- Layer 1: Innate Setup ---
                st.subheader("🛠️ 第一層：先天構架 (Innate Setup)")
                st.info(f"**先天資產屬性**: {', '.join(pr['innate_setup'])}")
                
                # --- Layer 2: Relational Flow ---
                st.subheader("🔄 第二層：對待關係 (Relational Flow)")
                c1, c2 = st.columns(2)
                with c1:
                    st.success(f"🔒 **資產增值 (祿)**: {pr['lu_dest']}")
                    st.markdown(f"> **擴張原因**: {pr['lu_why']}")
                    st.markdown(f"💡 **戰略解法**: {pr['lu_how']}")
                    st.markdown(f"✅ **最終戰略**: {pr['lu_conclusion']}")
                with c2:
                    st.error(f"💸 **資產流失 (忌)**: {pr['ji_dest']}")
                    st.markdown(f"> **風險原因**: {pr['ji_why']}")
                    st.markdown(f"💡 **戰略防護**: {pr['ji_how']}")
                    st.markdown(f"⚠️ **最終戰略**: {pr['ji_conclusion']}")
                st.divider()
                st.warning(f"**資產對待動態**: {pr['collision']}")

            with t3:
                st.markdown("### 12宮位「祿忌沖照」動態分析")
                all_flying = engine.fly_all_palaces()
                for p_name, data in all_flying.items():
                    with st.expander(f"📌 {p_name} 飛星分析 (天干：{data['stem']})"):
                        st.markdown(f"**{data['lu_star']}化祿入：{data['lu_dest']} | {data['ji_star']}化忌入：{data['ji_dest']}**")
                        st.caption(data['collision'])

            with t4:
                st.markdown("### 🤖 執行長 AI 戰略決策支援")
                st.info("AI 將結合《飛星派》與《欽天派》邏輯，針對當前重點宮位進行跨國 CEO 級別的深度審計。")
                
                # Input for API Key if not in secrets
                api_key = st.secrets.get("GOOGLE_API_KEY", "")
                if not api_key:
                    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

                if st.button("🚀 啟動 AI 執行長深度審計", use_container_width=True):
                    if not api_key:
                        st.warning("請先輸入 API Key。")
                    else:
                        with st.spinner("🕵️‍♂️ AI 執行長正閱畢全盤數據，撰寫審計報告中..."):
                            report = engine.get_ai_audit(audit, focused_p, api_key)
                            
                            st.markdown(f"""
                            <div style="background: rgba(30, 41, 59, 0.7); 
                                        border: 1.5px solid #6366f1; 
                                        border-radius: 20px; 
                                        padding: 30px; 
                                        margin-top: 20px; 
                                        box-shadow: 0 0 30px rgba(99, 102, 241, 0.2);">
                                <div style="font-size: 1.5rem; font-weight: 800; color: #fbbf24; margin-bottom: 20px;">🤖 AI 執行長戰略審計報告</div>
                                <div style="color: #f8fafc; line-height: 1.8; font-family: 'Inter', sans-serif;">
                                    {report.replace('\n', '<br>')}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.download_button("📥 下載審計報告", report, file_name="AI_CEO_Audit.md")

        except Exception as e:
            st.error(f"系統偵測到異常：{e}")

    else:
        st.info("請在側邊欄輸入正確的出生參數。")

elif menu == "📖 財務圖解知識庫":
    st.header("📖 財務圖解知識庫 (戰略解析)")
    st.markdown("### **紫微斗數財富與風控戰略全集 (CEO 深度研報)**")
    st.divider()
    
    gallery_metadata = [
        {
            "title": "1. 財帛化忌入各主星：風險預警 (部門經理的投資地雷)",
            "desc": """
            當代表壓力與阻礙的「化忌」落在業務部（財帛宮）時，會引發專屬的地雷：
            - **武曲化忌**: 資金斷鍊、周轉不靈，最忌因財持械。
            - **太陽化忌**: 名氣大實質虧損，外匯與能源產業波動。
            - **廉貞化忌**: 法務部踩紅線，易面臨法律爭議或行政罰款。
            - **太陰化忌**: 房產大亨資產凍結，財產產權不清。
            - **天機化忌**: 數據錯誤、程式交易 Bug 或指標失效。
            """,
            "path": "assets/logic_5.jpg"
        },
        {
            "title": "2. 主星化祿分類：三大財富引擎 (最適投資標的)",
            "desc": """
            「化祿」降臨不同主星，代表了三種截然不同的獲利模式：
            1. **穩健服務類**: 天同 (民生休閒), 天梁 (醫藥特許)。
            2. **技術策略類**: 天機 (高頻交易), 太陽 (外匯媒體), 巨門 (法律顧問)。
            3. **金融財星類**: 武曲 (金屬貨幣), 太陰 (土地房產), 天府 (銀行倉儲)。
            """,
            "path": "assets/logic_1.jpg"
        },
        {
            "title": "3. 穩健與服務類：被動收入財",
            "desc": """
            這類星曜祿通常較悠閒，不適合高壓狼性操作：
            - **天同 (福星)**: 適合民生、休閒、餐飲、小額入股。賺享受人生的輕鬆財。
            - **天梁 (蔭星)**: 適合醫藥、特許產業或繼承遺產。賺庇蔭眾生的長者財。
            """,
            "path": "assets/logic_3.jpg"
        },
        {
            "title": "4. 金融財星類：主流與重資產標的",
            "desc": """
            這類星曜化祿時，與正統金融、實體硬資產直接相關：
            - **武曲 (正財星)**: 適合金融、五金、期貨與黃金等「硬通貨」。
            - **太陰 (田宅主)**: 適合房地產、土地、長線收租與民生必需品。
            - **天府 (庫星)**: 適合銀行股、權值股、穩健資產管理。
            """,
            "path": "assets/logic_4.jpg"
        },
        {
            "title": "5. 化祿入宮位置：內部引擎 (我宮發財)",
            "desc": """
            化祿落入「我宮」部門，是企業的最佳內部投資方向：
            - **命宮**: 投資個人品牌與技術資產。
            - **財帛宮**: 敢花敢賺，現金流轉速快。
            - **事業宮**: 以財生財，擴大經營或再投資利潤。
            - **田宅宮**: 最強守財格，適合價值投資與囤金。
            """,
            "path": "assets/logic_8.jpg"
        },
        {
            "title": "6. 化祿入宮位置：外部槓桿 (他宮發財)",
            "desc": """
            化祿落入「他宮」部門，代表資金應利用外部貴人：
            - **夫妻宮**: 配偶帶財，適合異性市場或公關活動。
            - **子女宮**: 新創合夥、外部投標或平台經濟。
            - **遷移宮**: 賺取海外財、外匯與跨國標的。
            - **交友宮**: 群眾募資、粉絲經濟與平台標的。
            """,
            "path": "assets/logic_6.jpg"
        },
        {
            "title": "7. 忌星入宮：內部耗損 (財務破洞在哪裡)",
            "desc": """
            化忌代表壓力與收斂，是必須嚴格設立防火牆的漏水點：
            - **命宮**: 凡事親力親為，賺的都是勞祿血汗錢。
            - **財帛宮**: 錢留不住，容易出現突發開支或斷路。
            - **事業宮**: 資金被事業套牢，周轉不靈。
            - **福德宮**: 因焦慮而胡亂投機，心態不穩導致破財。
            """,
            "path": "assets/logic_7.jpg"
        },
        {
            "title": "8. 忌星入宮：外部坑殺 (被環境拖累)",
            "desc": """
            化忌落入外人宮位，是必須截斷的風險血本：
            - **兄弟宮**: 現金位受損，極易產生借貸風險，切勿作保。
            - **子女宮**: 盲目跟風投資導致母公司資金鏈斷裂。
            - **遷移宮**: 海外與遠距風險，不宜投入陌生國際市場。
            - **交友宮**: 損友劫財，防範倒債與詐騙。
            """,
            "path": "assets/logic_2.jpg"
        },
        {
            "title": "9. 財務心態與風險全案 (CEO 的心育修練)",
            "desc": """
            「論財必須論福德」。心態決定了財富的最終歸宿：
            - **福德忌**: 絕對的大忌，代表內心匱乏與焦慮。
            - **戰略**: 必須建立「防火牆」，切斷情緒決策與現金流的聯繫。
            """,
            "path": "assets/logic_9.jpg"
        },
        {
            "title": "10. 完整板塊導航 (人生公司財富體系)",
            "desc": """
            本系統整合飛星與欽天派邏輯，建立完整的財務防火牆：
            - **CEO 格局**: 命宮與福德宮的核心意志。
            - **現金流管理**: 財帛宮的業務動能。
            - **金庫防護**: 田宅宮的資產鎖定。
            """,
            "path": "assets/logic_10.jpg"
        }
    ]
    
    for item in gallery_metadata:
        st.subheader(f"🖼️ {item['title']}")
        st.info(item['desc'])
        if os.path.exists(item['path']):
            st.image(item['path'], use_container_width=True)
        else:
            st.warning(f"檔案 {item['path']} 不存在。")
        st.divider()

elif menu == "📜 十干四化對照表":
    st.header("📜 十干四化對照表 (核心邏輯速查)")
    st.markdown("### **十天干飛星轉化規則 (傳統欽天派標準)**")
    st.divider()
    
    st.markdown("""
    | 天干 | 化祿 (祿) | 化權 (權) | 化科 (科) | 化忌 (忌) |
    | :--- | :--- | :--- | :--- | :--- |
    | **甲** | 廉貞 | 破軍 | 武曲 | 太陽 |
    | **乙** | 天機 | 天梁 | 紫微 | 太陰 |
    | **丙** | 天同 | 天機 | 文昌 | 廉貞 |
    | **丁** | 太陰 | 天同 | 天機 | 巨門 |
    | **戊** | 貪狼 | 太陰 | 右弼 | 天機 |
    | **己** | 武曲 | 貪狼 | 天梁 | 文曲 |
    | **庚** | 太陽 | 武曲 | 太陰 | 天同 |
    | **辛** | 巨門 | 太陽 | 文曲 | 文昌 |
    | **壬** | 天梁 | 紫微 | 左輔 | 武曲 |
    | **癸** | 破軍 | 巨門 | 太陰 | 貪狼 |
    """)
    st.info("💡 **操作建議**：在主畫面點擊宮位時，可參考此表確認各宮位發動的「祿忌」連鎖效應。")

st.divider()
st.caption("紫微財務風控系統 | 演算法：iztro-py | 邏輯架構：飛星 & 欽天派 | 繁體中文支援")