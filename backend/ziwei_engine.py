from iztro_py import astro
import json
import os
import base64
from google import genai
from google.genai import types

class ZiWeiEngine:
    """
    紫微斗數飛星計算引擎 (Institutional Flagship v5.3)
    核心：深度整合「欽天派、飛星派、紫雲先生」專業理財框架與 Gemini AI。
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
        for k, v in trans.items(): dist[k] = {"star": v, "palace": self.find_star_location(v)}
        return {"stem": stem, "stars": dist}

    def get_innate_audit(self):
        dist = self.get_innate_distribution()
        meanings = {
            "祿": {"m": "代表圓滿、資源集結、福報與增加。", "i": "主要財富流向位，建議以此宮位為戰略核心。"},
            "權": {"m": "代表權力、主導、技術與競爭力。", "i": "專業技能展現位，適合在此宮位執行攻勢策略。"},
            "科": {"m": "代表名聲、條理、斯文與貴人相助。", "i": "品牌價值與信譽位，適合長期穩健經營。"},
            "忌": {"m": "代表欠債、執著、風險、變數與壓力。", "i": "重災區與防火牆位，嚴禁在此宮位進行高槓桿操作。"}
        }
        res = []
        for t, d in dist["stars"].items():
            res.append({
                "header": f"【生年化{t} ➔ {d['star']} ({d['palace']})】",
                "palace_def": f"這顆星曜在此宮位代表您一生中最核心的『{t}』之氣，具有天生的決定性影響。",
                "meaning": meanings[t]["m"],
                "impact": meanings[t]["i"]
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
            if s_target in all_s: results.append(f"自化{k}({s_target})")
        return results

    def fly_all_palaces(self):
        res = {}
        labels = ["命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮", "遷移宮", "交友宮", "事業宮", "田宅宮", "福德宮", "父母宮"]
        for l in labels:
            p = self.get_palace_by_label(l)
            if not p: continue
            sk = p.heavenly_stem[:3].lower()
            stem = {"jia":"甲","yi":"乙","bing":"丙","ding":"丁","wu":"戊","ji":"己","geng":"庚","xin":"辛","ren":"壬","gui":"癸"}.get(sk, "甲")
            trans = self.SI_HUA_MAP.get(stem)
            res[l] = { "stem": stem, "lu_star": trans["祿"], "lu_dest": self.find_star_location(trans["祿"]), "ji_star": trans["忌"], "ji_dest": self.find_star_location(trans["忌"]), "self": self.detect_self_transformation(l) }
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
        client = genai.Client(api_key=api_key)
        # Construct Detailed AI Context based on '紫微專業提示詞.md'
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
        
        【核心財庫結構 (Wealth-Vault Triad)】
        - 財帛宮 (交易部)：飛祿➔{audit_data['wealth']['layer2']['lu']['dest']} / 飛忌➔{audit_data['wealth']['layer2']['ji']['dest']} / 自化:{audit_data['wealth']['layer2']['self']}
        - 田宅宮 (總財庫)：飛祿➔{audit_data['property']['layer2']['lu']['dest']} / 飛忌➔{audit_data['property']['layer2']['ji']['dest']} / 自化:{audit_data['property']['layer2']['self']}
        - 兄弟宮 (現金流)：飛祿➔{audit_data['flying']['兄弟宮']['lu_dest']} / 飛忌➔{audit_data['flying']['兄弟宮']['ji_dest']} / 自化:{audit_data['flying']['兄弟宮']['self']}
        
        【外擴投資與合夥 (Investment)】
        - 子女宮 (股票期貨部)：飛祿➔{audit_data['flying']['子女宮']['lu_dest']} / 飛忌➔{audit_data['flying']['子女宮']['ji_dest']} / 自化:{audit_data['flying']['子女宮']['self']}
        
        【理財心態與福報 (Mindset)】
        - 福德宮 (決策潛意識)：飛祿➔{audit_data['flying']['福德宮']['lu_dest']} / 飛忌➔{audit_data['flying']['福德宮']['ji_dest']} / 自化:{audit_data['flying']['福德宮']['self']}
        """

        prompt = f"""
        你是一位精通「欽天四化派」、「飛星派」及「紫雲先生理論」的「人生股份有限公司 (Life Inc.)」首席戰略審計官。
        請根據以下精確的命盤數據執行深度審計。**嚴禁使用模糊模擬，僅限使用提供的固定數據**。

        {ctx}

        🏗️ 財富解析核心邏輯：
        1. 祿隨忌走：分析生年祿(因)如何流向生年忌(果)，判斷財富終極歸宿。
        2. 三位一體：評估 財帛、田宅、兄弟 之間的互動關係。
        3. 自化洩能：分析自化對財運穩定性的負面影響。
        4. 紫雲投資論：分析子女宮是否適合股票期貨或合夥操作。

        最後，請給出三條具體的、可執行的「財富增長策略」。
        繁體中文，專業、威信、冷靜。
        """

        try:
            resp = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(safety_settings=[types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE")])
            )
            return resp.text
        except Exception:
            # Fallback to 1.5-flash
            resp = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
            return resp.text

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
