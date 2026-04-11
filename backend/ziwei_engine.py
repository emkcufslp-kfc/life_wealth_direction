from iztro_py import astro
import json
import os
import base64
from google import genai

class ZiWeiEngine:
    """
    紫微斗數飛星計算引擎 (Institutional Flagship v4.3)
    核心：將「化忌」演繹為戰略防火牆，整合 Gemini AI 首席審計官。
    """
    
    SI_HUA_MAP = {
        "甲": {"祿": "廉貞", "權": "破軍", "科": "武曲", "忌": "太陽"},
        "乙": {"祿": "天機", "權": "天梁", "科": "紫微", "忌": "太陰"},
        "丙": {"祿": "天同", "權": "天機", "科": "文昌", "忌": "廉貞"},
        "丁": {"祿": "太陰", "權": "天同", "科": "天機", "忌": "巨門"},
        "戊": {"祿": "貪狼", "權": "太陰", "科": "右弼", "忌": "天機"},
        "己": {"祿": "武曲", "權": "貪狼", "科": "天梁", "忌": "文曲"},
        "庚": {"祿": "太陽", "權": "武曲", "科": "太陰", "忌": "天同"},
        "辛": {"祿": "巨門", "權": "太陽", "科": "文曲", "忌": "文昌"},
        "壬": {"祿": "天梁", "權": "紫微", "科": "左輔", "忌": "武曲"},
        "癸": {"祿": "破軍", "權": "巨門", "科": "太陰", "忌": "貪狼"}
    }

    PALACE_NAME_MAP = {
        "soulPalace": "命宮", "siblingsPalace": "兄弟宮", "spousePalace": "夫妻宮",
        "childrenPalace": "子女宮", "wealthPalace": "財帛宮", "healthPalace": "疾厄宮",
        "travelPalace": "遷移宮", "friendsPalace": "交友宮", "careerPalace": "事業宮",
        "propertyPalace": "田宅宮", "fortunePalace": "福德宮", "parentsPalace": "父母宮",
        "spiritPalace": "福德宮", "surfacePalace": "疾厄宮"
    }

    # --- TACTICAL RISK NARRATIVES ---
    RISK_STAR_NARRATIVES = {
        "武曲": "鐵腕財務長遇危機：資金斷鍊、周轉不靈，重資產易貶值。",
        "太陽": "跨國CEO面臨波及：名氣大而實質虧損，海外投資地雷。",
        "廉貞": "法務長踩紅線：求財牽涉法規糾紛，勿遊走灰色地帶。",
        "太陰": "房產大亨資產凍結：不動產套牢、產權不清或租金回收難。",
        "天機": "數據分析師失誤：程式交易或決策Bug，頻繁進出導致手續費損失。",
        "天同": "享樂主義天真陷阱：過度理想化，盲目投資夕陽產業或合夥欺騙。",
        "貪狼": "投機客泡沫破裂：數位資產被駭、高槓桿爆倉，受困於貪念。",
        "巨門": "公關災難與合約漏洞：錯誤資訊誤判，聽信內線消息導致金錢損失。",
        "文昌": "會計信用破產：票據糾紛與金融業障，最忌支票不兌現或惡意倒帳。",
        "文曲": "會計信用破產：票據糾紛與金融業障，最忌支票不兌現或惡意倒帳。"
    }

    RISK_PALACE_NARRATIVES = {
        "命宮": "資產負增長防護位：凡事親力親為，賺錢辛苦且心理壓力大。",
        "兄弟宮": "資源收縮黑洞：現金位受損，極易產生借貸風險，有去無回。",
        "夫妻宮": "公關形象受阻：配偶或外部人脈造成財務拖累，需劃清界線。",
        "子女宮": "合夥投資漏洞：合夥生意易產生窟窿，資金向外投放易石沉大海。",
        "財帛宮": "現金斷路節點：自化忌主錢財留不住，情緒性消費導致防火牆失效。",
        "疾厄宮": "實體營運重擔：投資受限於體力或店業高昂租金，過勞獲利薄。",
        "遷移宮": "外部際遇受困：出外發展阻礙多，海外資產容易發生意外損耗。",
        "交友宮": "眾籌群眾地雷：被外人坑陷，協助他人反遭財務拖累。",
        "事業宮": "持續投入套牢區：資金過度卡在本業擴張，隨時面臨斷流風險。",
        "田宅宮": "資產流動性陷阱：資金全數被房產套牢，資產變成磚頭，流動性差。",
        "福德宮": "精神性財務焦慮：福報位受損，因焦慮胡亂投機導致祖蔭消散。",
        "父母宮": "大型機構防火牆：與政府、長輩或銀行發生信用糾紛，貸款受阻。"
    }

    LUK_STAR_NARRATIVES = {
        "天同": "被動人生福星：輕鬆獲利。","天梁": "特許蔭庇財：穩健長者財。",
        "天機": "技術資訊差：短線智謀。","太陽": "能源媒體財：跨國名氣。",
        "巨門": "口才顧問財：數據洞察。","武曲": "硬通貨正財：金融重資產。",
        "太陰": "地產租金財：價值投資。","天府": "庫存管理財：權值儲備。"
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
        s = stems[(y - 4) % 10]
        return s

    def get_innate_distribution(self):
        stem = self.get_birth_year_stem()
        trans = self.SI_HUA_MAP.get(stem)
        dist = {}
        for k, v in trans.items(): dist[k] = {"star": v, "palace": self.find_star_location(v)}
        return {"stem": stem, "stars": dist}

    def get_ceo_audit(self):
        mp = self.get_palace_by_label("命宮")
        star = self.TRAD_STAR_MAP.get(mp.major_stars[0].translate_name(), "紫微") if mp.major_stars else "紫微"
        return {"star": star, "image": self.CEO_IMAGES.get(star, "zi_wei_emperor_1774971867916.png"), "description": f"具備【{star}】核心決策素質。"}

    def fly_all_palaces(self):
        res = {}
        labels = ["命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮", "遷移宮", "交友宮", "事業宮", "田宅宮", "福德宮", "父母宮"]
        for l in labels:
            p = self.get_palace_by_label(l)
            if not p: continue
            sk = p.heavenly_stem[:3].lower()
            stem = {"jia":"甲","yi":"乙","bing":"丙","ding":"丁","wu":"戊","ji":"己","geng":"庚","xin":"辛","ren":"壬","gui":"癸"}.get(sk, "甲")
            trans = self.SI_HUA_MAP.get(stem)
            res[l] = {
                "stem": stem, "lu_star": trans["祿"], "lu_dest": self.find_star_location(trans["祿"]),
                "ji_star": trans["忌"], "ji_dest": self.find_star_location(trans["忌"]),
                "collision": f"資產向『{self.find_star_location(trans['祿'])}』投放能量，壓力在『{self.find_star_location(trans['忌'])}』構築防火牆。"
            }
        return res

    def get_wealth_audit(self):
        ceo, innate, flying = self.get_ceo_audit(), self.get_innate_distribution(), self.fly_all_palaces()
        res = {}
        for name in ["命宮", "財帛宮", "田宅宮"]:
            fd = flying.get(name, {})
            l1 = [{"star": f"{s['star']}(生年{t})", "comment": "先天重要資本與定力。"} for t, s in innate["stars"].items() if s["palace"] == name]
            res[name] = {
                "layer1": {"stars": l1, "empty_msg": "無生年四化，純看後天飛伏。"},
                "layer2": {
                    "lu": {"dest": fd.get("lu_dest"), "why": self.LUK_STAR_NARRATIVES.get(fd.get("lu_star"), "常態盈餘模式。"), "how": f"導向『{fd.get('lu_dest')}』實現獲利。", "strategy": "資源投放"},
                    "ji": {"dest": fd.get("ji_dest"), "why": self.RISK_STAR_NARRATIVES.get(fd.get("ji_star"), "不透明風險。"), "how": f"於『{fd.get('ji_dest')}』{self.RISK_PALACE_NARRATIVES.get(fd.get('ji_dest'), '構設置防線')}", "strategy": "構築防火牆"},
                    "summary": fd.get("collision")
                }
            }
        return {"ceo": ceo, "innate": innate, "soul": res["命宮"], "wealth": res["財帛宮"], "property": res["田宅宮"], "conclusions": ["【穩健發展】建議按既定戰略擴張。"]}

    def get_innate_audit(self):
        innate = self.get_innate_distribution()
        profiles = []
        for t, s in innate["stars"].items():
            profiles.append({
                "header": f"先天{s['star']}化{t}位於『{s['palace']}』 | 戰略：{self.RISK_PALACE_NARRATIVES.get(s['palace'], '重點防護位')}",
                "palace_def": f"{s['palace']}代表財富配置底層。(參閱研報第十章)",
                "meaning": "代表「我」與生俱來的資源與福報。", "motivation": "追求絕對穩定與增長。", "impact": "資產累積路徑清晰。"
            })
        return profiles

    def get_ai_audit(self, audit_data, api_key):
        client = genai.Client(api_key=api_key)
        prompt = f"你是「人生股份有限公司」首席戰略審計官。根據數據分析 CEO:{audit_data['ceo']['star']}，生年:{audit_data['innate']['stem']}，核心部門:{json.dumps([audit_data['soul'], audit_data['wealth'], audit_data['property']], ensure_ascii=False)}。請以專業總裁思維，執行「陽升陰降」法則，提供一份深度風控與資產配置建議。繁體中文，專業威信。"
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text

    def get_image_base64(self, path):
        if os.path.exists(path):
            with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
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
                if n in ["擎羊","陀羅","火星","鈴星","地空","地劫"]: sh.append(n)
                elif n in ["左輔","右弼","天魁","天鉞","文昌","文曲"]: lk.append(n)
                elif n == "祿存": wl.append(n)
            grid[idx] = {
                "name": self.PALACE_NAME_MAP.get(p.name, p.name),
                "stem": {"jiaHeavenly":"甲","yiHeavenly":"乙","bingHeavenly":"丙","dingHeavenly":"丁","wuHeavenly":"戊","jiHeavenly":"己","gengHeavenly":"庚","xinHeavenly":"辛","renHeavenly":"壬","guiHeavenly":"癸"}.get(p.heavenly_stem, "甲"),
                "major_stars": ma, "sha_stars": sh, "lucky_stars": lk, "wealth_stars": wl
            }
        return grid
