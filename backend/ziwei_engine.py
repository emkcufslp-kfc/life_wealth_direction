import iztro_py as iztro
import json
import base64
import os

class ZiWeiEngine:
    # 欽天門四化配置 (Institutional Ground Truth)
    SI_HUA_MAP = {
        "甲": {"祿": "廉貞", "權": "破軍", "科": "武曲", "忌": "太陽", "logic": "核心啟動：權威與擴張"},
        "乙": {"祿": "天機", "權": "天梁", "科": "紫微", "忌": "太陰", "logic": "策略轉向：邏輯與資產管理"},
        "丙": {"祿": "天同", "權": "天機", "科": "文昌", "忌": "廉貞", "logic": "情緒驅動：資訊與社交風險"},
        "丁": {"祿": "太陰", "權": "天同", "科": "天機", "忌": "巨門", "logic": "資產守護：精算與口舌風險"},
        "戊": {"祿": "貪狼", "權": "太陰", "科": "右弼", "忌": "天機", "logic": "慾望釋放：變動與決策風險"},
        "己": {"祿": "武曲", "權": "貪狼", "科": "天梁", "忌": "文曲", "logic": "財富積累：規則與合約風險"},
        "庚": {"祿": "太陽", "權": "武曲", "科": "太陰", "忌": "天同", "logic": "市場博弈：名聲與現流風險"},
        "辛": {"祿": "巨門", "權": "太陽", "科": "文曲", "忌": "文昌", "logic": "資訊套利：信用與合規風險"},
        "壬": {"祿": "天梁", "權": "紫微", "科": "左輔", "忌": "武曲", "logic": "機構體制：權力與資金斷鏈"},
        "癸": {"祿": "破軍", "權": "巨門", "科": "太陰", "忌": "貪狼", "logic": "暴力破局：競爭與貪婪風險"}
    }

    PALACE_NAME_MAP = {
        "命宮": "命宮", "兄弟": "兄弟宮", "夫妻": "夫妻宮", "子女": "子女宮",
        "財帛": "財帛宮", "疾厄": "疾厄宮", "遷移": "遷移宮", "交友": "交友宮",
        "事業": "事業宮", "田宅": "田宅宮", "福德": "福德宮", "父母": "父母宮",
        "官祿": "事業宮"
    }

    TRAD_STAR_MAP = {
        "紫微": "紫微", "天機": "天機", "太陽": "太陽", "武曲": "武曲", "天同": "天同", "廉貞": "廉貞",
        "天府": "天府", "太陰": "太陰", "貪狼": "貪狼", "巨門": "巨門", "天相": "天相", "天梁": "天梁",
        "七殺": "七殺", "破軍": "破軍", "文昌": "文昌", "文曲": "文曲", "左輔": "左輔", "右弼": "右弼",
        "祿存": "祿存"
    }

    def __init__(self, year, month, day, hour, is_lunar=False, gender="男"):
        self.gender_str = '男' if gender in ["男", "male"] else '女'
        solar_date = f"{year}-{month}-{day}"
        if is_lunar:
            self.astro = iztro.by_lunar(solar_date, hour, self.gender_str)
        else:
            self.astro = iztro.by_solar(solar_date, hour, self.gender_str)

    def get_image_base64(self, star_name):
        # Fallback to a placeholder if image not found
        path = f"assets/{star_name}.png"
        if not os.path.exists(path):
            return "" # Return empty or a default base64
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def get_palace_by_label(self, label):
        target = label.replace("宮", "")
        if target == "事業": target = "官祿"
        for p in self.astro.palaces:
            if p.name == target:
                return p
        return None

    def get_innate_distribution(self):
        y_stem = self.astro.chinese_date[0]
        y_map = self.SI_HUA_MAP.get(y_stem)
        res = {"stem": y_stem, "logic": y_map["logic"], "stars": {}}
        for key in ["祿", "權", "科", "忌"]:
            target_star = y_map[key]
            for p in self.astro.palaces:
                all_stars = [s.name for s in p.major_stars + p.minor_stars + p.adjective_stars]
                if target_star in all_stars:
                    res["stars"][key] = {"star": target_star, "palace": self.PALACE_NAME_MAP.get(p.name, p.name+"宮")}
        return res

    def get_wealth_audit(self):
        # Simplified for dashboard requirements
        soul_p = self.astro.not_empty_palaces()[0] # Method call required
        soul_star = soul_p.major_stars[0].name if soul_p.major_stars else "紫微"
        return {
            "ceo": {"star": soul_star, "image": soul_star},
            "innate": self.get_innate_audit()
        }

    def get_astrolabe_data(self):
        res = {}
        for p in self.astro.palaces:
            p_label = self.PALACE_NAME_MAP.get(p.name, p.name + "宮")
            res[p_label] = {
                "stars": [s.name for s in p.major_stars + p.minor_stars + p.adjective_stars],
                "temple": ""
            }
        return res

    def get_innate_audit(self):
        dist = self.get_innate_distribution()
        
        LU_SOP = {
            "命宮": {"m": "Alpha 核心：你本身就是最強的生財工具。", "i": "優先投資「個人品牌」與「專業認證」。你的腦袋就是印鈔機。"},
            "兄弟宮": {"m": "高頻現金流：重視資金周轉率。", "i": "適合利差交易 (Carry Trade) 或現金拆借。保持資產高流動性。"},
            "夫妻宮": {"m": "關係槓桿：借力使力，靠關係獲利。", "i": "鎖定異性消費領域或參考伴侶投資建議。合作共贏。"},
            "子女宮": {"m": "對外擴張位：風險投資 (VC) 與撒網佈局。", "i": "適合新創項目或合夥生意。這是一種向外播種獲利的策略。"},
            "財帛宮": {"m": "流動性玩家：追求高周轉率的獲利模式。", "i": "操作高流動性標的（外匯、熱門股），忌諱資產套牢。"},
            "疾厄宮": {"m": "深位穩健財：實體產權與重資產運營。", "i": "佈局連鎖店面、健康產業或具備實體運營場域的資產。"},
            "遷移宮": {"m": "全球套利：賺取遠方財與資訊差。", "i": "佈局海外市場、外匯與跨境商務。錢在遠方，不在家。"},
            "交友宮": {"m": "平台經濟：靠群眾心理與流量獲利。", "i": "發展社群電商或利用大數據挖掘大眾需求。流量即財富。"},
            "官祿宮": {"m": "複利效應：盈餘轉增資，擴大資本投入。", "i": "進行垂直整合或設備升級。賺來的錢用於強化本業競爭力。"},
            "田宅宮": {"m": "庫位鎖定：資產積累的馬拉松終點站。", "i": "投資不動產、長線存股或黃金。錢進去就出不來，階梯式增長。"},
            "福德宮": {"m": "直覺福報財：隨機獲利與情緒驅動。", "i": "佈局收藏品、藝術品或隨市場情緒波動的標的。不宜全倉。"},
            "父母宮": {"m": "體制與信用：依附國家或大型機構的債信獲利。", "i": "標售案、特許行業或政府支持的藍籌股。獲利受體制保護。"}
        }

        JI_SOP = {
            "stars": {
                "文昌": {"m": "信用違約風險：文書與法律合約存在結構性缺陷。", "i": "執行 KYC (Know Your Contract)。所有簽名合約必須經過二次審計與合規複核。"},
                "文曲": {"m": "文書口才風險：合約漏洞 or 口舌糾紛。", "i": "確保所有溝通留存文字證據，避開非標準化合約標的。"},
                "武曲": {"m": "資金斷鏈風險：現金流受損與信用違約。", "i": "保留 6-12 個月現金儲備，嚴禁過度槓桿，避開銀行/金融股。"},
                "太陰": {"m": "地產套牢風險：不動產變現力差（凍產）。", "i": "避開海外房產。涉及女性合夥人時，合約需經第三方審核。"},
                "天機": {"m": "模型失效風險：量化策略失靈或邏輯過度擬合。", "i": "暫停程式交易，回歸簡單配置。別相信過度複雜的獲利模型。"},
                "巨門": {"m": "資訊不對稱風險：資訊差導致的決策失誤。", "i": "交叉驗證訊息源。嚴禁『聽說明牌』，避開資訊不透明的產業。"},
                "廉貞": {"m": "法律紅線風險：行政處罰與官非隱患。", "i": "嚴守合規性 (Compliance)。避開監管不明的灰色地帶產業。"},
                "貪狼": {"m": "投機陷阱風險：貪婪爆倉與虛擬資產遭駭。", "i": "嚴禁短線高倍槓桿。化忌時偏財運為負值，守成為主。"},
                "太陽": {"m": "名實不符風險：匯率損失與死撐虧損標的（Sunk Cost）。", "i": "嚴格止損 (Stop Loss)。放棄『我會贏回來』的心理偏誤。"},
                "天同": {"m": "理想化陷阱：投資夕陽產業或過度感性創業。", "i": "當你覺得計畫『很美好』時通常不賺錢。回歸冷酷的財務數據分析。"}
            },
            "palaces": {
                "命宮": {"m": "心理陷阱位：親力親為導致規模化受阻。", "i": "適度授權，別因為過度保守而錯過時代洪流的機會。"},
                "財帛宮": {"m": "流動性缺口：口袋漏水，資金進出頻繁且不留存。", "i": "建立自動儲蓄機制，限制非預期消費 (OpEx 控管)。"},
                "官祿宮": {"m": "資本密集陷阱：資金套牢在重資產營運中。", "i": "追求『輕資產模式』。嚴控設備與存貨投資比率。"},
                "田宅宮": {"m": "資產僵化位：房奴風險，現金流被困在磚頭。", "i": "注意資產變現天數 (Time to Exit)。別讓不動產壓死流動性。"},
                "疾厄宮": {"m": "固定成本陷阱：營運場所與健康資產的耗損。", "i": "優化工作流程，降低固定 OpEx。健康即資產，別因財失命。"},
                "福德宮": {"m": "情緒交易位：主觀誤判與情緒失控 (Tilt)。", "i": "嚴禁在市場狂熱時進場。避開任何『直覺型』主觀投資。"},
                "父母宮": {"m": "合規與信用位：體制財的風險溢出。", "i": "重視合約與法律合規。在與大型機構合作時，必須嚴查信用背書。"}
            }
        }

        meanings = {
            "祿": {"m": "代表圓滿、資源集結、福報與增加。", "i": "主要財富流向位，建議以此宮位為戰略核心。"},
            "權": {"m": "代表權力、主導、技術與競爭力。", "i": "專業技能展現位，適合在此宮位執行攻勢策略。"},
            "科": {"m": "代表名聲、條理、斯文與貴人相助。", "i": "品牌價值與信譽位，適合長期穩健經營。"},
            "忌": {"m": "代表欠債、執著、風險、變數與壓力。", "i": "重災區與防火牆位，嚴禁在此宮位進行高槓桿操作。"}
        }
        res = []
        for t, d in dist["stars"].items():
            m = meanings[t]["m"]
            i = meanings[t]["i"]
            if t == "祿":
                sop = LU_SOP.get(d["palace"])
                if sop: m, i = sop["m"], sop["i"]
            elif t == "忌":
                star_sop = JI_SOP["stars"].get(d["star"])
                pal_sop = JI_SOP["palaces"].get(d["palace"])
                if star_sop: 
                    m = star_sop["m"]
                    i = star_sop.get("i")
                if pal_sop:
                    if not star_sop: m = pal_sop["m"]
                    i = f"{i} | {pal_sop['i']}" if i else pal_sop["i"]
            
            res.append({
                "header": f"【生年化{t} ➔ {d['star']} ({d['palace']})】",
                "palace_def": f"這顆星曜在此宮位代表您一生中最核心的『{t}』之氣，具有天生的決定性影響。",
                "meaning": m,
                "impact": i
            })
        return res

    def f_dest(self, p_label, target_type):
        p = self.get_palace_by_label(p_label)
        if not p: return "未知"
        sk = p.heavenly_stem[:3].lower()
        stem = {"jia":"甲","yi":"乙","bing":"丙","ding":"丁","wu":"戊","ji":"己","geng":"庚","xin":"辛","ren":"壬","gui":"癸"}.get(sk, "甲")
        target_star = self.SI_HUA_MAP[stem][target_type]
        for dp in self.astro.palaces:
            d_stars = [s.name for s in dp.major_stars + dp.minor_stars + dp.adjective_stars]
            if target_star in d_stars: 
                return self.PALACE_NAME_MAP.get(dp.name, dp.name + "宮")
        return "未知"

    def get_collision_diagnostic(self, p_label, lu_dest, ji_dest, innate_dist):
        """
        Institutional Chain Narrative Engine (v6.39)
        Derived directly from 化祿 SOP & 化忌 SOP Expert Summaries
        """
        ROLE_MAP = {
            "命宮": {"role": "Alpha核心", "lu": "核心主控", "ji": "心理陷阱", "l_exec": "投資個人 IP 與專業認證", "j_exec": "適度授權並隔離情緒"},
            "兄弟宮": {"role": "現流儲備", "lu": "資金周轉", "ji": "流動性風險", "l_exec": "執行利差交易或現金拆借", "j_exec": "預留 6-12 個月現金頭寸"},
            "夫妻宮": {"role": "關係槓桿", "lu": "跨業合夥", "ji": "人際風險", "l_exec": "參考伴侶意見或佈局異性市場", "j_exec": "執行 KYC 並嚴查合約細節"},
            "子女宮": {"role": "外部擴張", "lu": "合夥佈局", "ji": "過度擴張", "l_exec": "執行天使投資或新創撒網策略", "j_exec": "嚴格止損，防範合夥漏財"},
            "財帛宮": {"role": "獲利交易", "lu": "高頻獲利", "ji": "流動缺口", "l_exec": "操作高流動性標的(Scalping)", "j_exec": "建立自動儲蓄機制限制消費"},
            "疾厄宮": {"role": "實體營運", "lu": "實體產權", "ji": "固定成本", "l_exec": "配置連鎖店面或重資產運營", "j_exec": "優化工作流程減少 OpEx 耗損"},
            "遷移宮": {"role": "外部市場", "lu": "全球套利", "ji": "變動風險", "l_exec": "賺取遠方財與資訊差(佈局海外)", "j_exec": "嚴格執行止損，防範匯率損失"},
            "交友宮": {"role": "平台流量", "lu": "流量獲利", "ji": "資訊不對稱", "l_exec": "利用群眾心理發展社群電商", "j_exec": "二次核實源頭訊息，防範明牌陷阱"},
            "官祿宮": {"role": "複利本業", "lu": "資本支出", "ji": "重資產陷阱", "l_exec": "盈餘轉增資，強化垂直整合力", "j_exec": "追求輕資產模式，嚴控 CAPEX"},
            "事業宮": {"role": "複利本業", "lu": "資本支出", "ji": "重資產陷阱", "l_exec": "盈餘轉增資，強化垂直整合力", "j_exec": "追求輕資產模式，嚴控 CAPEX"},
            "田宅宮": {"role": "馬拉松終點", "lu": "庫位鎖定", "ji": "資產僵化", "l_exec": "將獲利鎖定房產/長線存股/黃金", "j_exec": "注意變現天數，防止現金流抽筋"},
            "福德宮": {"role": "心理資產", "lu": "直覺獲利", "ji": "情緒回報", "l_exec": "配置收藏品/藝術品等直覺標的", "j_exec": "減少盯盤頻率，防範主觀誤判(Tilt)"},
            "父母宮": {"role": "體制信用", "lu": "特許權益", "ji": "合規風險", "l_exec": "依負大機構信用獲取標售案/藍籌", "j_exec": "嚴守合規，嚴查信用背書與 KYC"}
        }
        
        s = ROLE_MAP.get(p_label, {"role": "核心單元", "lu": "資源流動", "ji": "結構壓力", "l_exec": "按部就班", "j_exec": "基礎風控"})
        l = ROLE_MAP.get(lu_dest, {"role": "目標資產"})
        j = ROLE_MAP.get(ji_dest, {"role": "風險緩衝"})
        
        rel = f"【關係】：由『{p_label}』({s['role']}) 對外輸出能量，將獲利鏈條延伸至 {lu_dest}。"
        what_how = f"【策略】：利用進攻端的『{s['lu']}』模式建立 Alpha；並同步轉移『{s['ji']}』的結構性壓力至 {ji_dest}。"
        
        conc_base = f"【結論】：這是您的『理財馬拉松』配速策略。建議執行『{s['l_exec']}』以提升配速（祿）；同時落實『{j.get('j_exec', '建立專屬防火牆')}』以穩定心率（忌），防止資產中途抽筋。"
        
        birth_lu_p = innate_dist["stars"]["祿"]["palace"]
        birth_ji_p = innate_dist["stars"]["忌"]["palace"]
        warn_text = ""
        if lu_dest == birth_ji_p: warn_text = " ⚠️ 先天死穴：獲利流向先天忌位，猶如在崩塌區建金庫，應暫停擴張。"
        if ji_dest == birth_lu_p: warn_text = " ❗ 能量抵銷：風險傳導衝擊先天祿位，防止辛苦錢遭蠶食。"

        return f"{rel} {what_how} {conc_base}{warn_text}"

    def fly_all_palaces(self):
        res = {}
        target_p = ["命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮", "遷移宮", "交友宮", "事業宮", "田宅宮", "福德宮", "父母宮"]
        for p_label in target_p:
            res[p_label] = {"lu": self.f_dest(p_label, "祿"), "ji": self.f_dest(p_label, "忌")}
        return res

    def detect_flow_collisions(self):
        innate = self.get_innate_distribution()
        chain = self.fly_all_palaces()
        innate_lu_p = innate["stars"]["祿"]["palace"]
        innate_ji_p = innate["stars"]["忌"]["palace"]
        collisions = []
        for src, dests in chain.items():
            if dests["lu"] == innate_ji_p:
                collisions.append(f"{src} 祿入先天忌 ({innate_ji_p})：利潤流向黑洞，需嚴防虧損。")
            if dests["ji"] == innate_lu_p:
                collisions.append(f"{src} 忌入先天祿 ({innate_lu_p})：風險衝擊財源，防範利潤遭蠶食。")
        return collisions
