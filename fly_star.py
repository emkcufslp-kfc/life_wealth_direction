class ZiWeiSystem:
    """
    Zi Wei Dou Shu Chain Flying Star (連鎖飛化) Strategic Audit Engine.
    Version: v6.50-INSTITUTIONAL-NARRATIVE
    
    This engine decomposes transformation into a professional 5-section narrative:
    1. 路徑 (Path): Visual sequence of the energy movement.
    2. 關鍵意涵 (Key Intent): The 'Why' from the Source station.
    3. 預警警號 (Warning Signals): Detailed phenomena based on Star DNA and Impact.
    4. 專家綜合診斷 (Expert Diagnosis): Catchy summary and energy flow analysis.
    5. 處方箋 (Prescription): Strategic actionable advice.
    """

    def __init__(self):
        # Table A: Source Definitions (The 'Why')
        self.source_rules = {
            "命宮": {"lu": "我主動追求、天賦展現", "ji": "我執著、看不開、自我虧損", "subject": "自己"},
            "兄弟宮": {"lu": "現金流動、兄弟助力", "ji": "現金卡住、借貸糾紛", "subject": "資金庫"},
            "夫妻宮": {"lu": "配偶幫助、異性緣", "ji": "感情債、配偶拖累", "subject": "感情位"},
            "子女宮": {"lu": "合夥順利、投資獲利", "ji": "合夥破局、投資虧損", "subject": "投資位"},
            "財帛宮": {"lu": "賺錢行為、現金流向", "ji": "財務缺口、決策失誤", "subject": "現金流"},
            "疾厄宮": {"lu": "身體本質、店面人氣", "ji": "身體病變、營運問題", "subject": "實體位"},
            "遷移宮": {"lu": "出外遇貴人、社會名聲", "ji": "出外不順、意外風險", "subject": "社會位"},
            "交友宮": {"lu": "眾生緣、人脈變現", "ji": "小人陷害、人情壓力", "subject": "人脈位"},
            "官祿宮": {"lu": "工作模式、運氣擴張", "ji": "工作過勞、營運危機", "subject": "事業部"},
            "田宅宮": {"lu": "家運興隆、資產增值", "ji": "家宅不寧、財庫破洞", "subject": "資產庫"},
            "福德宮": {"lu": "精神滿足、財源穩定", "ji": "精神焦慮、情緒失控", "subject": "心智位"},
            "父母宮": {"lu": "長輩提攜、文書合約", "ji": "文書失誤、信用破產", "subject": "法律位"}
        }

        # Table B: Star DNA (The 'How')
        self.stem_rules = {
            "甲": {
                "lu_star": "廉貞", "lu_mean": "精密規劃、電子科技", "ji_star": "太陽", "ji_mean": "公關危機、男性惹禍",
                "diag": "成也開創，敗也面子", "presc": ["避免過度擴張", "注意公關聲譽", "保護核心技術"]
            },
            "乙": {
                "lu_star": "天機", "lu_mean": "智慧企劃、轉手獲利", "ji_star": "太陰", "ji_mean": "房產虧損、女性拖累",
                "diag": "成也智慧，敗也情執", "presc": ["理財需抽離情緒", "防範資產套牢", "善用邏輯優勢"]
            },
            "丙": {
                "lu_star": "天同", "lu_mean": "服務協調、享福財", "ji_star": "廉貞", "ji_mean": "官司刑罰、行政疏失",
                "diag": "成也人緣，敗也官非", "presc": ["合規審查優於一切", "保持行政透明", "善用調解手段"]
            },
            "丁": {
                "lu_star": "太陰", "lu_mean": "房產財、細膩佈局", "ji_star": "巨門", "ji_mean": "口舌是非、暗處吃虧",
                "diag": "成也細節，敗也口舌", "presc": ["謹言慎行防背刺", "保護核心資產", "防範合約暗樁"]
            },
            "戊": {
                "lu_star": "貪狼", "lu_mean": "投機偏財、交際獲利", "ji_star": "天機", "ji_mean": "判斷失誤、鑽牛角尖",
                "diag": "成也應酬，敗也鑽牛角尖", "presc": ["適時止盈止損", "不要陷入單一邏輯", "保持思維靈活"]
            },
            "己": {
                "lu_star": "武曲", "lu_mean": "金融操作、實力執行", "ji_star": "文曲", "ji_mean": "合約陷阱、支票跳票",
                "diag": "成也實力，敗也合約", "presc": ["簽約必請法務檢查", "建立信用備忘錄", "防範金融文書詐欺"]
            },
            "庚": {
                "lu_star": "太陽", "lu_mean": "名氣擴散、海外機遇", "ji_star": "天同", "ji_mean": "無福消受、心力交瘁",
                "diag": "成也名氣，敗也無福", "presc": ["平衡工作與享受", "防範過勞風險", "控制擴張規模"]
            },
            "辛": {
                "lu_star": "巨門", "lu_mean": "口才傳播、專業技術", "ji_star": "文昌", "ji_mean": "文書無效、法規變動",
                "diag": "成也嘴巴，敗也白紙黑字", "presc": ["談判由你負責", "簽字必請律師", "現金結算為先"]
            },
            "壬": {
                "lu_star": "天梁", "lu_mean": "長輩蔭庇、繼承保險", "ji_star": "武曲", "ji_mean": "資金斷鏈、因錢傷感",
                "diag": "成也體制，敗也斷鏈", "presc": ["保留充足現金額度", "防範合資風險", "善用保險工具避險"]
            },
            "癸": {
                "lu_star": "破軍", "lu_mean": "創新突破、顛覆模式", "ji_star": "貪狼", "ji_mean": "桃花糾紛、因色敗家",
                "diag": "成也破局，敗也色難", "presc": ["建立人際邊界", "防範投機慾望", "專注於產業顛覆"]
            }
        }

        self.palace_order = [
            "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
            "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮"
        ]

        # Table C: Impact Logic
        self.target_rules = {
            "命宮": {"ji_warn": "責任壓在身上，心煩意亂", "clash": "遷移宮", "clash_impact": "在外處處碰壁，意外風險"},
            "兄弟宮": {"ji_warn": "現金卡住，兄弟受累", "clash": "交友宮", "clash_impact": "損友、人際關係崩壞、現金流中斷"},
            "夫妻宮": {"ji_warn": "配偶干擾事業，感情負擔", "clash": "官祿宮", "clash_impact": "影響工作運、事業不順"},
            "子女宮": {"ji_warn": "合夥拆夥，子女離心", "clash": "田宅宮", "clash_impact": "庫存流失、財庫破洞、家道不穩"},
            "財帛宮": {"ji_warn": "大破財，資金周轉困難", "clash": "福德宮", "clash_impact": "損財傷神、因錢財壓力焦慮"},
            "疾厄宮": {"ji_warn": "身體不適，情緒卡點", "clash": "父母宮", "clash_impact": "與長輩不和、文書法律糾紛"},
            "遷移宮": {"ji_warn": "在外處處碰壁，意外風險", "clash": "命宮", "clash_impact": "最凶。自我運勢崩盤、意外車禍"},
            "交友宮": {"ji_warn": "小人陷害，朋友欠錢", "clash": "兄弟宮", "clash_impact": "損財(兄弟是財庫)、朋友借錢不還"},
            "官祿宮": {"ji_warn": "工作過勞，營運危機", "clash": "夫妻宮", "clash_impact": "因工作忽略家庭導致婚姻糾紛"},
            "田宅宮": {"ji_warn": "家宅不寧，財庫破洞", "clash": "子女宮", "clash_impact": "子女離散、合夥拆夥、家變"},
            "福德宮": {"ji_warn": "精神焦慮，大破財(沖財)", "clash": "財帛宮", "clash_impact": "投資必敗、錯誤決策大損"},
            "父母宮": {"ji_warn": "文書出錯，官非罰單", "clash": "疾厄宮", "clash_impact": "身體受傷、官司纏身、情緒不穩"}
        }

    def get_clash_palace(self, target_palace_name):
        try:
            name = target_palace_name.replace("宮", "") + "宮"
            idx = self.palace_order.index(name)
            return self.palace_order[(idx + 6) % 12]
        except: return "對宮"

    def diagnose_chain(self, source_palace, stem, lu_target, ji_target):
        src_name = source_palace.replace("宮", "") + "宮"
        src_data = self.source_rules.get(src_name, {})
        stem_data = self.stem_rules.get(stem, {})
        
        lu_t = lu_target.replace("宮", "") + "宮"
        ji_t = ji_target.replace("宮", "") + "宮"
        ji_data = self.target_rules.get(ji_t, {})
        clash_palace = self.get_clash_palace(ji_t)

        path = f"【{src_name} ({stem})】 ➔ {stem_data['lu_star']}祿入 {lu_t} / {stem_data['ji_star']}忌入 {ji_t}"
        
        warnings = [
           f"{stem_data['ji_star']}化忌主『{stem_data['ji_mean']}』。",
           f"{ji_t}是『{src_data['subject']}』的變動位。{ji_data.get('ji_warn', '風險累積')}。",
           f"入{ji_t}會直接衝擊『{clash_palace}』：{ji_data.get('clash_impact', '影響深遠')}"
        ]

        diagnosis = f"這是一個『{stem_data['diag']}』的結構。能量流向：{stem}干讓你的{stem_data['lu_star']}變強（擴張至{lu_t}），但也讓{stem_data['ji_star']}變脆（衝擊{ji_t}）。"
        
        return {
            "path": path,
            "intent": f"供給鏈：{src_data['lu']} ➔ {lu_t}受益；風險鏈：{src_data['ji']} ➔ {ji_t}受損",
            "warnings": warnings,
            "diagnosis": diagnosis,
            "prescription": stem_data['presc']
        }