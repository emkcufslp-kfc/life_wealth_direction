import streamlit as st
import datetime
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.join(os.getcwd(), "backend"))
from ziwei_engine import ZiWeiEngine

# --- 1. 系統設定 (Institutional Flagship v5.7 - Unabridged Strategy Archive) ---
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
        --institutional-blue: #1e293b;
    }

    .stApp { background-color: var(--paper-bg); color: var(--institutional-blue); }
    h1, h2, h3, h4, th, td, p, li { font-family: 'Noto Sans TC', sans-serif; color: var(--institutional-blue) !important; }
    
    .ceo-card {
        background: white; border: 1.5px solid #e2e8f0; border-radius: 20px; padding: 25px;
        margin-bottom: 24px; display: flex; align-items: center; gap: 25px;
    }
    
    .palace-box {
        background: white; border-radius: 12px; padding: 12px; min-height: 155px;
        display: flex; flex-direction: column; border: 1px solid #e2e8f0;
    }
    
    .logic-container {
        background: white; border-radius: 20px; border: 1px solid #e2e8f0; padding: 40px; margin-bottom: 45px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
    }
    .logic-header {
        font-size: 1.8rem; font-weight: 900; color: #1e293b; margin-bottom: 30px;
        border-left: 10px solid #6366f1; padding-left: 20px;
    }
    .unabridged-text { font-size: 1.05rem; line-height: 2.0; color: #334155; }
</style>
""", unsafe_allow_html=True)

st.title("🧭 紫微財務風控系統：Institutional Archive (Unabridged)")

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

    st.markdown(f"""<div class="ceo-card">
        <img src="data:image/png;base64,{st.session_state.engine.get_image_base64(audit["ceo"]["image"])}" width="80">
        <div><div style="font-size:1.6rem; font-weight:900;">⚖️ 執行長 (CEO)：{audit["ceo"]["star"]}</div><div>具備核心決策素質。</div></div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        def draw_box(idx):
            p = grid[idx]
            tc = "#8b5cf6" if p['name']=='命宮' else ("#059669" if p['name']=='財帛宮' else ("#d97706" if p['name']=='田宅宮' else "#1e293b"))
            st.markdown(f'<div class="palace-box" style="border-top:5px solid {tc};"><div style="display:flex; justify-content:space-between; font-weight:900;"><span>{p["name"]}</span> <span>{p["stem"]}</span></div><div style="color:#d97706; font-weight:800; margin-top:5px;">{" ".join(p["major_stars"])}</div><div style="color:#15803d; font-size:0.8rem; font-weight:700;">{" ".join(p["lucky_stars"])}</div><div style="color:#dc2626; font-size:0.8rem; font-weight:700;">{" ".join(p["sha_stars"])}</div></div>', unsafe_allow_html=True)
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
    
    with t1:
        st.markdown(f"### 🛡️ 命宮 營運報表")
        cl, cr = st.columns(2)
        with cl: st.success(f"📈 資源投放 ➔ {audit['soul']['layer2']['lu']['dest']}")
        with cr: st.error(f"🛡️ 戰略防火牆 ➔ {audit['soul']['layer2']['ji']['dest']}")
    with t2:
        st.markdown(f"### 🛡️ 財帛宮 營運報表")
        cl, cr = st.columns(2)
        with cl: st.success(f"📈 資源投放 ➔ {audit['wealth']['layer2']['lu']['dest']}")
        with cr: st.error(f"🛡️ 戰略防火牆 ➔ {audit['wealth']['layer2']['ji']['dest']}")
    with t3:
        st.markdown(f"### 🛡️ 田宅宮 營運報表")
        cl, cr = st.columns(2)
        with cl: st.success(f"📈 資源投放 ➔ {audit['property']['layer2']['lu']['dest']}")
        with cr: st.error(f"🛡️ 戰略防火牆 ➔ {audit['property']['layer2']['ji']['dest']}")
    with tx:
        for p in st.session_state.engine.get_innate_audit():
            st.markdown(f'<div style="background:white; border:1px solid #e2e8f0; border-radius:12px; margin-bottom:15px; padding:20px;">{p["header"]}<br><br>{p["palace_def"]}</div>', unsafe_allow_html=True)
    with t4:
        for p_n, p_d in st.session_state.engine.fly_all_palaces().items():
            with st.expander(f"{p_n} 流向 ➔ {p_d['lu_dest']} / {p_d['ji_dest']}"): st.write(p_d['collision'])
    
    with t5:
        st.markdown("### 📚 財富策略知識庫 (Unabridged Logic.md)")
        
        # Unabridged Data from Logic.md
        unabridged_logics = [
            ("Logic 01: 腦袋與資訊財引擎 (天機、太陽、巨門)", "logic_1.jpg", """這張圖表將傳統的紫微斗數星曜（當它們化祿時）與現代的投資策略及產業進行了結合。核心邏輯是：這三顆星不靠體力活發財，而是靠「腦袋」、「資訊差」或「名氣」來賺錢。

以下是詳細的拆解與分析：
1. **天機星**：變動與邏輯（靠「快」與「準」）
   - 核心思維：利用演算法或技術分析，在市場波動中賺取短線利潤。
   - 適合工具：高頻交易與量化模型、軟體程式、運輸、短線技術面。
2. **太陽星**：名聲與能源（靠「光」與「遠」）
   - 核心思維：投資那些大家都看得見、有口碑、且具備國際規模的標的。
   - 適合工具：藍籌股、太陽能、媒體產業、海外投資（外幣）。
3. **巨門星**：研究與口才（靠「挖」與「說」）
   - 核心思維：透過深度挖掘別人看不見的細節，或者利用專業知識獲利。
   - 適合工具：深度分析報告、法律與諮詢、「深挖」資訊差。"""),
            
            ("Logic 02: 宮位化忌風險黑洞 (他宮篇)", "logic_2.jpg", """深入解析「化忌」落在不同宮位時，對財務管理與風險心態的具體影響。
1. **兄弟宮**：現金流的「黑洞」。現金部位感不足。建議嚴禁借錢給他人，存錢要用「物理性隔絕」。
2. **夫妻宮**：感情帶動的「判斷失誤」。財務風險在於情緒化決策。建議財務獨立。
3. **子女宮**：投資與合夥的「禁區」。容易在外盲目投資，或合夥生意虧損。避開不熟悉合夥。
4. **遷移宮**：外地財運的「阻力」。匯率與海外市場風險。不適合進軍陌生海外市場。
5. **交友宮**：眾人與損友的「劫財」。容易遇到倒債詐騙。絕對不要跟風投資。
6. **父母宮**：文書與體制的「雷區」。法律訴訟與合約漏洞。簽署合約要非常謹慎。"""),

            ("Logic 03: 佛系穩健被動收益 (天同、天梁)", "logic_3.jpg", """天同與天梁化祿：步調慢、壓力小、細水長流。
1. **天同星**：享受生活的「福星」。賺享受人生的輕鬆財。適合民生餐飲、休閒、小額入股、穩定利息。
2. **天梁星**：遮風避雨的「蔭星」。靠「資歷」和「規則」獲利。適合醫藥長照、保險、特許、繼承。
*理財建議：拒絕高槓桿與高壓，佈局租金、股息與授權費。*"""),

            ("Logic 04: 正統主流重資產財星 (武曲、太陰、天府)", "logic_4.jpg", """正統三財星：靠「實力」與「資產規模」說話。
1. **武曲星**：鋼鐵意志的「正財星」。適合金融銀行、五金金屬、期貨黃金、硬通貨。
2. **太陰星**：溫潤如水的「田宅主」。財富是靠「養」出來的。適合房地產土地、長線收租、女性消費、民生必需。
3. **天府星**：深不見底的「庫星」。規模化經營穩健收益。適合銀行股國庫券、大型權值股、資產管理、倉儲。"""),

            ("Logic 05: 財帛化忌：九大主星風險預警", "logic_5.jpg", """根據你的命盤，避開那些會讓你賠錢的「雷區」。
- **武曲化忌**：資金斷鏈與財引衝突。
- **太陰化忌**：房地產套牢與租金回收難。
- **貪狼化忌**：最忌「貪心」與高槓桿泡沫。
- **廉貞化忌**：法律紅線與行政處罰。
- **天機化忌**：策略錯誤與程式Bug。
- **巨門化忌**：合約漏洞與流言損失。
- **太陽化忌**：匯率虧損與面子破財。
- **天同化忌**：夕陽產業與天真陷阱。
- **昌曲化忌**：支票不兌現與信用破產。"""),

            ("Logic 06: 化祿入他宮：外部獲利槓桿", "logic_6.jpg", """錢該往哪裡投？
1. **兄弟宮**：現金流。適合短期周轉。
2. **夫妻宮**：配偶名義投資或異性市場。
3. **子女宮**：新創投資與教育培訓合夥。
4. **遷移宮**：遠方財與跨國外匯。
5. **交友宮**：平台經濟與大眾大數據財。
6. **父母宮**：政府標案與特許行業、藍籌股。"""),

            ("Logic 07: 忌星入我宮：財務心態與損耗", "logic_7.jpg", """財務破洞與執著點剖析。
1. **命宮**：賺辛苦血汗錢。不信他人。
2. **財帛宮**：自化忌，情緒性消費支出。
3. **官祿宮**：資金完全被事業套牢周轉不靈。
4. **田宅宮**：房奴傾向，淪為資產磚頭。
5. **疾厄宮**：固定成本高，體力勞力依賴。
6. **福德宮**：焦慮投機失利，主觀誤判。"""),

            ("Logic 08: 祿星入我宮：核心戰略獲利位", "logic_8.jpg", """不同位置的獲利「手感」。
1. **命宮**：投資自己，個人品牌變現。
2. **財帛宮**：高轉速短線交易，重視變現。
3. **官祿宮**：以財生財規模化再投資。
4. **田宅宮**：最強守財房產價值投資。
5. **疾厄宮**：穩紮穩打實體店面連鎖。
6. **福德宮**：直覺與福報興趣收藏。
*總結：祿在田宅別玩短線，祿在命宮專注自我身價。*""")
        ]

        for title, img, desc in unabridged_logics:
            with st.container():
                st.markdown(f'<div class="logic-container"><div class="logic-header">🏗️ {title}</div>', unsafe_allow_html=True)
                il, rl = st.columns([1, 1.5])
                with il: st.image(f"assets/{img}", use_container_width=True)
                with rl: st.markdown(f'<div class="unabridged-text">{desc.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    with t6:
        st.markdown("### 🤖 首席戰略審計官 (AI Gemini Pro)")
        ak = st.secrets.get("GOOGLE_API_KEY", "") or st.sidebar.text_input("Gemini API Key", type="password")
        if st.button("🚀 啟動專業深度審計"):
            if ak:
                with st.spinner("專業數據分析中..."):
                    res = st.session_state.engine.get_ai_audit(audit, api_key=ak)
                    st.markdown(f'<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:15px; padding:25px; line-height:1.8;">{res}</div>', unsafe_allow_html=True)
            else: st.warning("請輸入 API Key")

if menu == "📜 研報概覽":
    st.subheader("紫微財務戰略研究報告")
    with open("紫微斗數財運四化解析.md", "r", encoding="utf-8") as f: st.markdown(f.read())