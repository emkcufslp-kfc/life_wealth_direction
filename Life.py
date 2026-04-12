import streamlit as st
import datetime
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.join(os.getcwd(), "backend"))
from ziwei_engine import ZiWeiEngine

# --- 1. 系統設定 (Institutional Flagship v5.6 - Final Production Refinement) ---
st.set_page_config(
    page_title="紫微財務風控系統 - Strategy Archive", 
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
    
    .logic-section {
        background: white; border-radius: 20px; border: 1px solid #e2e8f0; padding: 35px; margin-bottom: 40px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }
    .logic-title {
        font-size: 1.6rem; font-weight: 900; color: #1e293b; margin-bottom: 25px;
        border-right: 8px solid #6366f1; padding-right: 15px; display: inline-block;
    }
    .logic-text { font-size: 1rem; line-height: 1.9; color: #334155; }
</style>
""", unsafe_allow_html=True)

st.title("🧭 紫微財務風控系統：Strategy Archive")

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

        r1 = st.columns(4)
        for i, idx in enumerate([5,6,7,8]): 
            with r1[i]: draw_box(idx)
        st.write(""); mr = st.columns([1, 2, 1])
        with mr[0]: draw_box(4); st.write(""); draw_box(3)
        with mr[1]: st.markdown(f'<div style="text-align:center; height:320px; padding:100px 0;"><h1>{b_date.strftime("%Y-%m-%d")}</h1><p>{b_hour_raw}</p></div>', unsafe_allow_html=True)
        with mr[2]: draw_box(9); st.write(""); draw_box(10)
        st.write(""); r4 = st.columns(4)
        for i, idx in enumerate([2,1,0,11]): 
            with r4[i]: draw_box(idx)

    with c2:
        st.subheader("🏁 首席審計總結")
        st.info("【穩健發展】建議按既定戰略擴張。")
        st.markdown(f'<div style="border:2px solid #dc2626; border-radius:15px; padding:20px; background:white;"><h4 style="color:#dc2626; margin-top:0;">🎯 先天資本 (年生：{audit["innate"]["stem"]})</h4>', unsafe_allow_html=True)
        for t, d in audit['innate']['stars'].items(): st.markdown(f"**{t}**：{d['star']} ➔ {d['palace']}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    t1, t2, t3, tx, t4, t5, t6 = st.tabs(["🏎️ 決策部", "💸 業務部", "🏰 金庫部", "🎯 先天格局", "🛰️ 12宮連鎖", "📚 文庫指南", "🤖 AI 策略室"])
    
    with t1:
        st.markdown(f"### 🛡️ 命宮 營運報表")
        cl, cr = st.columns(2)
        with cl: st.success(f"📈 資源投放 ➔ {audit['soul']['layer2']['lu']['dest']}\n\n**流向導向位。**")
        with cr: st.error(f"🛡️ 戰略防火牆 ➔ {audit['soul']['layer2']['ji']['dest']}\n\n**風險防禦位。**")
    with t2:
        st.markdown(f"### 🛡️ 財帛宮 營運報表")
        cl, cr = st.columns(2)
        with cl: st.success(f"📈 資源投放 ➔ {audit['wealth']['layer2']['lu']['dest']}\n\n**流向導向位。**")
        with cr: st.error(f"🛡️ 戰略防火牆 ➔ {audit['wealth']['layer2']['ji']['dest']}\n\n**風險防禦位。**")
    with t3:
        st.markdown(f"### 🛡️ 田宅宮 營運報表")
        cl, cr = st.columns(2)
        with cl: st.success(f"📈 資源投放 ➔ {audit['property']['layer2']['lu']['dest']}\n\n**流向導向位。**")
        with cr: st.error(f"🛡️ 戰略防火牆 ➔ {audit['property']['layer2']['ji']['dest']}\n\n**風險防禦位。**")
    with tx:
        for p in st.session_state.engine.get_innate_audit():
            st.markdown(f'<div style="background:white; border:1px solid #e2e8f0; border-radius:12px; margin-bottom:15px; overflow:hidden;"><div style="background:#1e293b; color:white; padding:10px 20px; font-weight:700;">{p["header"]}</div><div style="padding:20px;">{p["palace_def"]}<br><br>* **深層意義**：{p["meaning"]}<br>* **具體影響**：{p["impact"]}</div></div>', unsafe_allow_html=True)
    with t4:
        for p_n, p_d in st.session_state.engine.fly_all_palaces().items():
            with st.expander(f"{p_n} 流向 ➔ {p_d['lu_dest']} / {p_d['ji_dest']}"): st.write(p_d['collision'])
    
    with t5:
        # Logic Mapping Data 1-8
        logics = [
            ("Logic 01: 腦袋與資訊財引擎", "logic_1.jpg", """這張圖表將傳統的紫微斗數星曜（當它們化祿時）與現代的投資策略及產業進行了結合。核心邏輯是：這三顆星不靠體力活發財，而是靠「腦袋」、「資訊差」或「名氣」來賺錢。
            1. **天機星**：高頻交易、量化模型、軟體程式、短線技術。
            2. **太陽星**：藍籌股、太陽能、媒體產業、海外投資。
            3. **巨門星**：深度分析、法律諮詢、深挖資訊差。"""),
            ("Logic 02: 宮位化忌風險黑洞", "logic_2.jpg", """深入解析「化忌」落在不同宮位時的財務漏洞與心態風險。
            1. **兄弟宮**：現金流黑洞，嚴禁借貸。
            2. **夫妻宮**：感情連累財務，建議財務獨立。
            3. **子女宮**：投資合夥禁區，錢存不住。
            4. **遷移宮**：外地求財壓力大，匯率風險。
            5. **交友宮**：眾人劫財，切勿跟風募資。
            6. **父母宮**：法律合約雷區，稅務與官司。"""),
            ("Logic 03: 佛系穩健被動收益", "logic_3.jpg", """天同與天梁化祿：不爭之財，細水長流。
            1. **天同星**：民生餐飲、休閒產業、穩健分紅。
            2. **天梁星**：醫藥長照、保險、特許、繼承。
            *戰略：拒絕高槓桿，佈局租金與股息。*"""),
            ("Logic 04: 正統主流重資產財星", "logic_4.jpg", """武曲、太陰、天府：靠實力與規模說話。
            1. **武曲星**：硬通貨(黃金/期貨)、主流金融。
            2. **太陰星**：不動產、土地、長線收租。
            3. **天府星**：大型權值股、資產管理、倉儲。"""),
            ("Logic 05: 財帛化忌：九大主星地雷", "logic_5.jpg", """財帛化忌落入主星時的針對性防禦。
            - 武曲: 資金斷鍊 / 廉貞: 法律紅線 / 太陽: 海外虧損
            - 貪狼: 泡沫破裂 / 天機: 指標失效 / 太陰: 房產套牢
            - 巨門: 合約漏洞 / 天同: 夕陽產業 / 昌曲: 信用破產"""),
            ("Logic 06: 化祿入他宮：外部槓桿", "logic_6.jpg", """錢從哪裡來？錢該往哪裡投？
            1. **兄弟宮**：現金周轉位。 / **夫妻宮**：異性助力財。
            2. **子女宮**：合夥新創投資。 / **遷移宮**：跨國外幣機會。
            3. **交友宮**：平台與大眾財。 / **父母宮**：政府機構特許。"""),
            ("Logic 07: 忌星入我宮：自我損耗", "logic_7.jpg", """財務心態與內部洩壓點分析。
            1. **命宮**：辛苦血汗錢。 / **財帛宮**：突發支出漏水。
            2. **官祿宮**：資本過度套牢。 / **田宅宮**：資產固化淪為房奴。
            3. **疾厄宮**：健康成本。 / **福德宮**：焦慮主觀誤判。"""),
            ("Logic 08: 祿星入我宮：核心獲利位", "logic_8.jpg", """不同位置的致富「手感」與獲利方向。
            1. **命宮**：個人品牌變現。 / **財帛宮**：高轉速短線交易。
            2. **官祿宮**：以財生財再投資。 / **田宅宮**：最強守財不動產。
            3. **疾厄宮**：穩健實體加盟。 / **福德宮**：直覺與偏財福報。""")
        ]

        for title, img_path, desc in logics:
            with st.container():
                st.markdown(f'<div class="logic-section"><div class="logic-title">🏗️ {title}</div>', unsafe_allow_html=True)
                ic, tc = st.columns([1, 1.2])
                with ic: st.image(f"assets/{img_path}", use_container_width=True)
                with tc: st.markdown(f'<div class="logic-text">{desc.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    with t6:
        st.markdown("### 🤖 首席戰略審計官 (AI Gemini Pro)")
        ak = st.secrets.get("GOOGLE_API_KEY", "") or st.sidebar.text_input("Gemini API Key", type="password")
        if st.button("🚀 啟動專業深度審計"):
            if ak:
                with st.spinner("審查數據中..."):
                    res = st.session_state.engine.get_ai_audit(audit, api_key=ak)
                    st.markdown(f'<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:15px; padding:25px; line-height:1.8;">{res}</div>', unsafe_allow_html=True)
            else: st.warning("請輸入 API Key")

if menu == "📜 研報概覽":
    st.subheader("紫微財務戰略研究報告")
    with open("紫微斗數財運四化解析.md", "r", encoding="utf-8") as f: st.markdown(f.read())