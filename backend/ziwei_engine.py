from iztro_py import astro
import json
import os
import base64
import google.generativeai as genai

class ZiWeiEngine:
    """
    紫微斗數飛星計算引擎 (Institutional Flagship v5.3)
    核心：深度整合「欽天派、飛星派、紫雲先生」專業理財框架與 Gemini AI。
    """
    
    # Qin Tian Men (欽天門) - Institutional Ground Truth Table
    SI_HUA_MAP = {
        "甲": {"祿": "廉貞", "權": "破軍", "科": "武曲", "忌": "太陽", "logic": "陽木：先天之氣啟動，首重秩序與突破"},
        "乙": {"祿": "天機", "權": "天梁", "科": "紫微", "忌": "太陰", "logic": "陰木：靈動變通，蔭庇與帝威的轉化"},
        "丙": {"祿": "天同", "權": "天機", "科": "文昌", "忌": "廉貞", "logic": "陽火：情感生發，智慧掌控，文書彰顯"},
        "丁": {"祿": "太陰", "權": "天同", "科": "天機", "忌": "巨門", "logic": "陰火：內斂之福，機謀轉化，口舌收斂"},
        "戊": {"祿": "貪狼", "權": "太陰", "科": "右弼", "忌": "天機", "logic": "陽土：欲望驅動，女性權柄，貴人暗助"},
        "己": {"祿": "武曲", "權": "貪狼", "科": "天梁", "忌": "文曲", "logic": "陰土：財富累積，競爭執行，清譽科名"},
        "庚": {"祿": "太陽", "權": "武曲", "科": "太陰", "忌": "天同", "logic": "陽金：名聲顯赫，財權結合，陰柔調和"},
        "辛": {"祿": "巨門", "權": "太陽", "科": "文曲", "忌": "文昌", "logic": "陰金：口才生財，權威擴張，才藝顯名"},
        "壬": {"祿": "天梁", "權": "紫微", "科": "左輔", "忌": "武曲", "logic": "陽水：資源下放，帝座威權，平輩助力"},
        "癸": {"祿": "破軍", "權": "巨門", "科": "太陰", "忌": "貪狼", "logic": "陰水：變動更新，言語服眾，收斂歸藏"}
    }

    PALACE_NAME_MAP = {
        "soulPalace": "命宮", "siblingsPalace": "兄弟宮", "spousePalace": "夫妻宮",
        "childrenPalace": "子女宮", "wealthPalace": "財帛宮", "healthPalace": "疾厄宮",
        "travelPalace": "遷移宮", "friendsPalace": "交友宮", "careerPalace": "事業宮",
        "propertyPalace": "田宅宮", "fortunePalace": "福德宮", "parentsPalace": "父母宮",
        "spiritPalace": "福德宮", "surfacePalace": "遷移宮", "mentalPalace": "福德宮"
    }

    TRAD_STAR_MAP = {"太阳":"太陽","太阴":"太陰","天机":"天機","廉贞":"廉貞","贪狼":"貪狼","巨门":"巨門","武曲":"武曲","天同":"天同","破军":"破軍","天梁":"天梁","紫微":"紫微","天府":"天府","天相":"天相","七杀":"七殺","文昌":"文昌","文曲":"文曲","左辅":"左輔","右弼":"右弼","禄存":"祿存","擎羊":"擎羊","陀罗":"陀羅","火星":"火星","铃星":"鈴星","地空":"地空","地劫":"地劫"}

    CEO_IMAGES = {
        "紫微": "zi_wei_emperor_1774971867916.png", "天機": "tian_ji_strategist_1774971903938.png",
        "太陽": "tai_yang_sun_1774971982538.png", "武曲": "wu_qu_executor_1774972069586.png",
        "天同": "tian_tong_harmonizer_1774972148960.png", "廉貞": "lian_zhen_crisis_pr_1774972254175.png",
        "天府": "tian_fu_treasurer_1774972278010.png", "太陰": "tai_yin_designer_1774972301368.png",
        "貪狼": "tan_lang_marketer_1774972333552.png", "巨門": "ju_men_truth_seeker_1774972355775.png",
        "天相": "tian_xiang_negotiator_justice_1774972456284.png", "天梁": "tian_liang_protector_advisor_1774972484778.png",
        "七殺": "qi_sha_conqueror_combatant_1774972505956.png", "破軍": "po_jun_rebel_disruptor_1774972529713.png"
    }

    def __init__(self, year, month, day, hour_index, is_lunar=False, gender="男"):
        date_str = f"{year}-{month:02d}-{day:02d}"
        if is_lunar: self.chart = astro.by_lunar(year, month, day, hour_index, False, gender)
        else: self.chart = astro.by_solar(date_str, hour_index, gender)
        self.palaces = self.chart.palaces
        self.gender = gender

    def get_palace_by_label(self, label):
        for p in self.palaces:
            if self.PALACE_NAME_MAP.get(p.name, p.name) == label: return p
        return None

    def find_star_location(self, target_trad):
        for p in self.palaces:
            all_s = [self.TRAD_STAR_MAP.get(s.translate_name(), s.translate_name()) for s in p.major_stars + p.minor_stars + p.adjective_stars]
            if target_trad in all_s: return self.PALACE_NAME_MAP.get(p.name, p.name)
        return "未知宮位"

    def get_birth_year_stem(self):
        stems = "甲乙丙丁戊己庚辛壬癸"
        y = int(self.chart.solar_date.split("-")[0])
        return stems[(y - 4) % 10]

    def get_innate_distribution(self):
        stem = self.get_birth_year_stem()
        trans = self.SI_HUA_MAP.get(stem)
        dist = {}
        for k, v in trans.items():
            if k == "logic": continue
            dist[k] = {"star": v, "palace": self.find_star_location(v)}
        return {"stem": stem, "stars": dist}

    def get_innate_audit(self):
        dist = self.get_innate_distribution()
        
        # 化祿 SOP Institutional Mapping (v6.25)
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

        # 化忌 SOP Institutional Mapping (v6.26)
        JI_SOP = {
            "stars": {
                "文昌": {"m": "信用違約風險：文書與法律合約存在結構性缺陷。", "i": "執行 KYC (Know Your Contract)。所有簽名合約必須經過二次審計與合規複核。"},
                "文曲": {"m": "文書口才風險：合約漏洞或口舌糾紛。", "i": "確保所有溝通留存文字證據，避開非標準化合約標的。"},
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
                "財帛宮": {"m": "流動性缺口：口袋漏水，資金進出頻繁且不留存。", "i": "建立自動儲蓄機制，限制非預期消費（OpEx 控管）。"},
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
            # Apply SOP logic for LU/JI if available
            m = meanings[t]["m"]
            i = meanings[t]["i"]
            if t == "祿":
                sop = LU_SOP.get(d["palace"])
                if sop: m, i = sop["m"], sop["i"]
            elif t == "忌":
                star_sop = JI_SOP["stars"].get(d["star"])
                pal_sop = JI_SOP["palaces"].get(d["palace"])
                # Combine star risk with palace context if both exist
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

    def detect_self_transformation(self, palace_label):
        p = self.get_palace_by_label(palace_label)
        if not p: return []
        sk = p.heavenly_stem[:3].lower()
        stem = {"jia":"甲","yi":"乙","bing":"丙","ding":"丁","wu":"戊","ji":"己","geng":"庚","xin":"辛","ren":"壬","gui":"癸"}.get(sk, "甲")
        trans = self.SI_HUA_MAP.get(stem)
        all_s = [self.TRAD_STAR_MAP.get(s.translate_name(), s.translate_name()) for s in p.major_stars + p.minor_stars + p.adjective_stars]
        results = []
        for k, s_target in trans.items():
            if k == "logic": continue
            if s_target in all_s: results.append(f"自化{k}({s_target})")
        return results

    def get_collision_diagnostic(self, p_label, lu_dest, ji_dest, innate_dist):
        """核心碰撞診斷邏輯：分析飛星流向與生年主星的互動"""
        rules = []
        birth_lu_p = innate_dist["stars"]["祿"]["palace"]
        birth_ji_p = innate_dist["stars"]["忌"]["palace"]
        
        if lu_dest == birth_ji_p: rules.append("祿入沖忌: 資源投入以補先天之缺，轉危為安之象。")
        if ji_dest == birth_lu_p: rules.append("忌入沖祿: 先吉後兇，防備資源遭風險位沖抵。")
        
        self_trans = self.detect_self_transformation(p_label)
        if self_trans: rules.append(f"宮位自化: {','.join(self_trans)}，能量外流須防損耗。")
        
        if not rules: rules.append("流向平穩: 按部就班，穩定經營。")
        return " | ".join(rules)

    def fly_all_palaces(self):
        res = {}
        # We index by 0-11 (ziEarthly, chouEarthly, etc.) to ensure uniqueness
        B_MAP = {"ziEarthly":0,"chouEarthly":1,"yinEarthly":2,"maoEarthly":3,"chenEarthly":4,"siEarthly":5,"wuEarthly":6,"weiEarthly":7,"shenEarthly":8,"youEarthly":9,"xuEarthly":10,"haiEarthly":11}
        innate = self.get_innate_distribution()
        
        for p in self.palaces:
            idx = B_MAP.get(p.earthly_branch)
            p_name = self.PALACE_NAME_MAP.get(p.name, p.name)
            # Use full-string mapping for robustness
            S_MAP = {"jiaHeavenly":"甲","yiHeavenly":"乙","bingHeavenly":"丙","dingHeavenly":"丁","wuHeavenly":"戊","jiHeavenly":"己","gengHeavenly":"庚","xinHeavenly":"辛","renHeavenly":"壬","guiHeavenly":"癸"}
            stem = S_MAP.get(p.heavenly_stem, "甲")
            trans = self.SI_HUA_MAP.get(stem)
            lu_dest = self.find_star_location(trans["祿"])
            ji_dest = self.find_star_location(trans["忌"])
            
            res[idx] = { 
                "name": p_name,
                "stem": stem, 
                "lu_star": trans["祿"], 
                "lu_dest": lu_dest, 
                "ji_star": trans["忌"], 
                "ji_dest": ji_dest, 
                "logic": trans["logic"],
                "self": self.detect_self_transformation(p_name),
                "collision": self.get_collision_diagnostic(p_name, lu_dest, ji_dest, innate)
            }
        return res

    def get_wealth_audit(self):
        mp = self.get_palace_by_label("命宮")
        ceo_star = self.TRAD_STAR_MAP.get(mp.major_stars[0].translate_name(), "紫微") if mp.major_stars else "紫微"
        innate, flying = self.get_innate_distribution(), self.fly_all_palaces()
        res = {}
        for name in ["命宮", "財帛宮", "田宅宮"]:
            fd = flying.get(name, {})
            l1 = [{"star": f"{s['star']}(生年{t})", "comment": "核心資本。"} for t, s in innate["stars"].items() if s["palace"] == name]
            res[name] = { "layer1": {"stars": l1}, "layer2": {"lu": {"dest": fd.get("lu_dest")}, "ji": {"dest": fd.get("ji_dest")}, "self": fd.get("self", [])} }
        return {"ceo": {"star": ceo_star, "image": self.CEO_IMAGES.get(ceo_star, "zi_wei_emperor.png")}, "innate": innate, "soul": res["命宮"], "wealth": res["財帛宮"], "property": res["田宅宮"], "flying": flying}

    def get_ai_audit(self, audit_data, api_key):
        genai.configure(api_key=api_key)
        # Construct Detailed AI Context
        ctx = f"""
        【審計對象資訊】
        - 性別：{self.gender}
        - 出生日期：{self.chart.solar_date} (國曆)
        - 農曆日期：{self.chart.chinese_date}
        - 執行長 (CEO)：{audit_data['ceo']['star']}
        
        【先天財富基因 (Birth DNA)】
        - 生年干：{audit_data['innate']['stem']}
        - 生年四化明確位：
          * 祿：{audit_data['innate']['stars']['祿']['star']} ➔ {audit_data['innate']['stars']['祿']['palace']}
          * 權：{audit_data['innate']['stars']['權']['star']} ➔ {audit_data['innate']['stars']['權']['palace']}
          * 科：{audit_data['innate']['stars']['科']['star']} ➔ {audit_data['innate']['stars']['科']['palace']}
          * 忌：{audit_data['innate']['stars']['忌']['star']} ➔ {audit_data['innate']['stars']['忌']['palace']}
        """
        
        prompt = f"""
        你是一位精通「欽天四化派」、「飛星派」及「紫雲先生理論」的首席審計官。
        請根據數據執行財務審計：{ctx}
        """
        
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(prompt)
            return resp.text
        except Exception as e:
            return f"AI 審計暫時無法連線: {str(e)}"

    def get_image_base64(self, path):
        # Resolve path: try relative to current, then check assets/
        paths_to_check = [path, os.path.join("assets", path), os.path.join("backend/assets", path)]
        for p in paths_to_check:
            if os.path.exists(p):
                with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
        return ""

    def get_astrolabe_data(self):
        grid = [None] * 12
        B_MAP = {"ziEarthly":0,"chouEarthly":1,"yinEarthly":2,"maoEarthly":3,"chenEarthly":4,"siEarthly":5,"wuEarthly":6,"weiEarthly":7,"shenEarthly":8,"youEarthly":9,"xuEarthly":10,"haiEarthly":11}
        for p in self.palaces:
            idx = B_MAP.get(p.earthly_branch)
            ma = [self.TRAD_STAR_MAP.get(s.translate_name(), s.translate_name()) for s in p.major_stars]
            sh, lk, wl = [], [], []
            for s in p.minor_stars + p.adjective_stars:
                n = self.TRAD_STAR_MAP.get(s.translate_name(), s.translate_name())
                if n in ["左輔","右弼","天魁","天鉞","文昌","文曲"]: lk.append(n)
                elif n in ["擎羊","陀羅","火星","鈴星","地空","地劫"]: sh.append(n)
                elif n == "祿存": wl.append(n)
            grid[idx] = {
                "name": self.PALACE_NAME_MAP.get(p.name, p.name),
                "stem": {"jiaHeavenly":"甲","yiHeavenly":"乙","bingHeavenly":"丙","dingHeavenly":"丁","wuHeavenly":"戊","jiHeavenly":"己","gengHeavenly":"庚","xinHeavenly":"辛","renHeavenly":"壬","guiHeavenly":"癸"}.get(p.heavenly_stem, "甲"),
                "major_stars": ma, "sha_stars": sh, "lucky_stars": lk, "wealth_stars": wl
            }
        return grid
