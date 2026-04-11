import streamlit as st
import datetime
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.join(os.getcwd(), "backend"))
from ziwei_engine import ZiWeiEngine

# --- 1. 系統設定 (Institutional Flagship v5.4 - Final Production) ---
st.set_page_config(
    page_title="紫微財務風控系統 - Institutional Auditor", 
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
    h1, h2, h3, h4, th, td, p, li { font-family: 'Noto Sans TC', sans-serif; color: var(--institutional-blue) !important; }
    
    .ceo-card {
        background: var(--paper-card); border: 1.5px solid var(--paper-border); border-radius: 20px; padding: 25px;
        margin-bottom: 24px; display: flex; align-items: center; gap: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    .palace-box {
        background: white; border-radius: 12px; padding: 12px; min-height: 155px;
        display: flex; flex-direction: column; border: 1px solid #e2e8f0;
    }
    .palace-header { display: flex; justify-content: space-between; font-weight: 900; font-size: 1rem; }
    
    .knowledge-card {
        background: white; border-radius: 20px; border: 1px solid #e2e8f0; padding: 25px; margin-bottom: 30px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    }
    .knowledge-header {
        font-size: 1.4rem; font-weight: 900; color: #1e293b; margin-bottom: 20px;
        border-bottom: 3px solid #6366f1; display: inline-block; padding-bottom: 5px;
    }
    .knowledge-body { font-size: 0.95rem; line-height: 1.8; color: #475569; }
</style>
""", unsafe_allow_html=True)

st.title("🧭 紫微財務風控系統：Institutional Flagship")

# --- Sidebar ---
st.sidebar.title("🗂️ 系統導航")
menu = st.sidebar.radio("模組地圖", ["🚀 核心財務審計", "📜 研報概覽"], index=0)

if menu == "🚀 核心財務審計":
    b_date = st.sidebar.date_input("出生日期", datetime.date(1971, 11, 18))
    times = ["子時", "丑時", "寅時", "卯時", "辰時", "巳時", "午時", "未時", "申時", "酉時", "戌時", "亥時"]
    b_hour_raw = st.sidebar.selectbox("時辰", times, index=2)
    b_hour, gender, is_lunar = times.index(b_hour_raw), st.sidebar.radio("性別", ["男", "女"]), st.sidebar.checkbox("農曆")

    if st.sidebar.button("🔄 重置全系統審計") or 'audit_data' not in st.session_state:
        st.session_state.engine = ZiWeiEngine(b_date.year, b_date.month, b_date.day, b_hour, is_lunar, gender)
        st.session_state.audit_data = st.session_state.engine.get_wealth_audit()
        st.session_state.grid_data = st.session_state.engine.get_astrolabe_data()

    audit = st.session_state.audit_data
    grid = st.session_state.grid_data

    # CEO Header
    st.markdown(f"""<div class="ceo-card">
        <img src="data:image/png;base64,{st.session_state.engine.get_image_base64(audit["ceo"]["image"])}" width="80">
        <div><div style="font-size:1.6rem; font-weight:900;">⚖️ 執行長 (CEO)：{audit["ceo"]["star"]}</div><div>具備核心決策素質。</div></div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        def draw_box(idx):
            p = grid[idx]
            tc = "#8b5cf6" if p['name']=='命宮' else ("#059669" if p['name']=='財帛宮' else ("#d97706" if p['name']=='田宅宮' else "#1e293b"))
            st.markdown(f'<div class="palace-box" style="border-top:5px solid {tc};"><div class="palace-header" style="color:{tc};"><span>{p["name"]}</span> <span>{p["stem"]}</span></div><div style="color:#d97706; font-weight:800; margin-top:5px;">{" ".join(p["major_stars"])}</div><div style="color:#15803d; font-size:0.8rem; font-weight:700;">{" ".join(p["lucky_stars"])} {" ".join(p["wealth_stars"])}</div><div style="color:#dc2626; font-size:0.8rem; font-weight:700;">{" ".join(p["sha_stars"])}</div></div>', unsafe_allow_html=True)

        r1 = st.columns(4); [with r1[i]: draw_box(idx) for i, idx in enumerate([5,6,7,8])]
        st.write(""); mr = st.columns([1, 2, 1])
        with mr[0]: draw_box(4); st.write(""); draw_box(3)
        with mr[1]: st.markdown(f'<div style="text-align:center; height:320px; padding:100px 0;"><h1>{b_date.strftime("%Y-%m-%d")}</h1><p>{b_hour_raw}</p></div>', unsafe_allow_html=True)
        with mr[2]: draw_box(9); st.write(""); draw_box(10)
        st.write(""); r4 = st.columns(4); [with r4[i]: draw_box(idx) for i, idx in enumerate([2,1,0,11])]

    with c2:
        st.subheader("🏁 首席審計總結")
        st.info("【穩健發展】建議按既定戰略擴張。")
        st.markdown(f'<div style="border:2px solid #dc2626; border-radius:15px; padding:20px; background:white;"><h4 style="color:#dc2626; margin-top:0;">🎯 先天資本 (年生：{audit["innate"]["stem"]})</h4>', unsafe_allow_html=True)
        for t, d in audit['innate']['stars'].items(): st.markdown(f"**{t}**：{d['star']} ➔ {d['palace']}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    t1, t2, t3, tx, t4, t5, t6 = st.tabs(["🏎️ 決策部", "💸 業務部", "🏰 金庫部", "🎯 先天格局", "🛰️ 12宮連鎖", "📚 文庫指南", "🤖 AI 策略室"])
    
    def render_dept(title, d):
        st.markdown(f"### 🛡️ {title} 營運報表")
        cl, cr = st.columns(2)
        with cl: st.success(f"📈 資源投放 ➔ {d['layer2']['lu']['dest']}\n\n**流向導向位。**")
        with cr: st.error(f"🛡️ 戰略防火牆 ➔ {d['layer2']['ji']['dest']}\n\n**風險防禦位。**")

    with t1: render_dept("命宮", audit['soul'])
    with t2: render_dept("財帛宮", audit['wealth'])
    with t3: render_dept("田宅宮", audit['property'])
    with tx:
        for p in st.session_state.engine.get_innate_audit():
            st.markdown(f'<div style="background:white; border:1px solid #e2e8f0; border-radius:12px; margin-bottom:15px; overflow:hidden;"><div style="background:#1e293b; color:white; padding:10px 20px; font-weight:700;">{p["header"]}</div><div style="padding:20px;">{p["palace_def"]}<br><br>* **深層意義**：{p["meaning"]}<br>* **具體影響**：{p["impact"]}</div></div>', unsafe_allow_html=True)
    with t4:
        for p_n, p_d in st.session_state.engine.fly_all_palaces().items():
            with st.expander(f"{p_n} 流向 ➔ {p_d['lu_dest']} / {p_d['ji_dest']}"): st.write(p_d['collision'])
    with t5:
        st.markdown("### 📚 財富策略知識庫 (附錄・第十章)")
        
        # Section 1: Risk Warnings
        with st.container():
            st.markdown('<div class="knowledge-card"><div class="knowledge-header">一、 財帛化忌：風險預警 (Dept Mine)</div>', unsafe_allow_html=True)
            k1c, k1i = st.columns([1, 1])
            with k1c: st.markdown("""
            * **武曲化忌**：小心資金斷鍊、周轉不靈。
            * **太陽化忌**：小心海外投資地雷、名氣大而實質虧損。
            * **廉貞化忌**：求財牽涉法規糾紛，勿遊走法律紅線。
            * **太陰化忌**：不動產套牢、產權不清或租金回收難。
            * **天機化忌**：策略錯誤或指標失效，頻繁進出手續費重。
            * **貪狼化忌**：投機泡沫破裂、數位資產被駭或爆倉。
            """); st.markdown('</div>', unsafe_allow_html=True)
            with k1i: st.image("assets/logic_1.jpg", use_container_width=True)
        
        # Section 2: Wealth Engines
        with st.container():
            st.markdown('<div class="knowledge-card"><div class="knowledge-header">二、 主星化祿：財富引擎 (Wealth Engines)</div>', unsafe_allow_html=True)
            k2c, k2i = st.columns([1, 1])
            with k2c: st.markdown("""
            * **穩健服務類**：天同(輕鬆財)、天梁(特許蔭庇財)。
            * **技術策略類**：天機(資訊差)、太陽(媒體財)、巨門(顧問財)。
            * **金融財星類**：武曲(正財金融)、太陰(地產收租)、天府(庫存儲備)。
            """); st.markdown('</div>', unsafe_allow_html=True)
            with k2i: st.image("assets/logic_5.jpg", use_container_width=True)

        # Section 3: Investment Strategy
        with st.container():
            st.markdown('<div class="knowledge-card"><div class="knowledge-header">三、 化祿入宮：投資方向 (Strategic Directions)</div>', unsafe_allow_html=True)
            k3c, k3i = st.columns([1, 1])
            with k3c: st.markdown("""
            * **內部引擎 (我宮)**：
                - **命宮**：個人品牌與增值。
                - **田宅宮**：最強守財，適合房貸存股。
                - **官祿宮**：以財生財，擴大再投資。
            * **外部槓桿 (他宮)**：
                - **遷移宮**：遠距與外匯際遇。
                - **交友宮**：大眾財與平台經濟。
            """); st.markdown('</div>', unsafe_allow_html=True)
            with k3i: st.image("assets/logic_7.jpg", use_container_width=True)
            
        # Section 4: Leaks
        with st.container():
            st.markdown('<div class="knowledge-card"><div class="knowledge-header">四、 忌星入宮：財務破洞 (Financial Leaks)</div>', unsafe_allow_html=True)
            k4c, k4i = st.columns([1, 1])
            with k4c: st.markdown("""
            * **田宅宮**：淪為房奴，資產流動性極差。
            * **兄弟宮**：現金位受損，嚴禁借貸。
            * **福德宮**：焦慮投機失利，因財煩惱。
            * **父母宮**：法律文書糾紛，注意合約漏洞。
            """); st.markdown('</div>', unsafe_allow_html=True)
            with k4i: st.image("assets/logic_10.jpg", use_container_width=True)

    with t6:
        st.markdown("### 🤖 首席戰略審計官 (AI Gemini Pro)")
        ak = st.secrets.get("GOOGLE_API_KEY", "") or st.sidebar.text_input("Gemini API Key", type="password")
        if st.button("🚀 啟動專業深度審計"):
            if ak:
                with st.spinner("專業審核中..."):
                    res = st.session_state.engine.get_ai_audit(audit, api_key=ak)
                    st.markdown(f'<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:15px; padding:25px; line-height:1.8;">{res}</div>', unsafe_allow_html=True)
            else: st.warning("請輸入 API Key")