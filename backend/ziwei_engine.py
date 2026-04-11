from iztro_py import astro
import json
import os
import base64
from google import genai

class ZiWeiEngine:
    """
    紫微斗數飛星計算引擎 (專業財務審計版 - Flagship Ver)
    修正宮位命名與網格映射，確保與 Streamlit Cloud 完全同步
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
        "spiritPalace": "福德宮", "surfacePalace": "疾厄宮"  # JSON variants
    }

    TRAD_STAR_MAP = {
        "太阳": "太陽", "太阴": "太陰", "天机": "天機", "廉贞": "廉貞", "贪狼": "貪狼", 
        "巨门": "巨門", "武曲": "武曲", "天同": "天同", "破军": "破軍", "天梁": "天梁", 
        "紫微": "紫微", "天府": "天府", "天相": "天相", "七杀": "七殺", "文昌": "文昌", 
        "文曲": "文曲", "左辅": "左輔", "右弼": "右弼", "禄存": "祿存", "祿存": "祿存",
        "擎羊": "擎羊", "陀罗": "陀羅", "火星": "火星", "铃星": "鈴星", "地空": "地空", "地劫": "地劫"
    }

    CEO_IMAGES = {
        "紫微": "zi_wei_emperor_1774971867916.png", "天機": "tian_ji_strategist_1774971903938.png",
        "太陽": "tai_yang_sun_1774971982538.png", "武曲": "wu_qu_executor_1774972069586.png",
        "天同": "tian_tong_harmonizer_1774972148960.png", "廉貞": "lian_zhen_crisis_pr_1774972254175.png",
        "天府": "tian_fu_treasurer_1774972278010.png", "太陰": "tai_yin_designer_1774972301368.png",
        "貪狼": "tan_lang_marketer_1774972333552.png", "巨門": "ju_men_truth_seeker_1774972355775.png",
        "天相": "tian_xiang_negotiator_justice_1774972456284.png", "天梁": "tian_liang_protector_advisor_1774972484778.png",
        "七殺": "qi_sha_conqueror_combatant_1774972505956.png", "破軍": "po_jun_rebel_disruptor_1774972529713.png"
    }

    INNATE_RICH_DATABASE = {
        "命宮": {
            "palace_def": "命宮代表自我、性格與承載力，是財富的總指揮部 1。",
            "meaning": "代表「我」與生俱來的資源與福報。這種人不需要向外乞求緣分，緣分會自動向其靠攏 3。",
            "motivation": "一種深根蒂固的「生命信任感」。更願意展現親和力，構成一生的幸運底色 1。",
            "impact": "聰明、有才華且不吝嗇。在財富獲取上多屬「自立格」，能靠個人魅力輕鬆上手 2。"
        },
        "兄弟宮": {
            "palace_def": "兄弟宮是財帛宮的田宅位，象徵現鈔蓄水池，也代表母親與手足 1。",
            "meaning": "代表現金流動性極強且財庫充盈。與母親關係的和諧度直接影響現金周轉能力 1。",
            "motivation": "追求物質上的流動與分享。對母親的全然接納，能引動此宮的化祿能量 1。",
            "impact": "易得手足、母系長輩或同儕的經濟支持。適合從事需高度現金流動的行業 1。"
        },
        "夫妻宮": {
            "palace_def": "夫妻宮是官祿宮的遷移位，代表事業對外的公眾形象與際遇 2。",
            "meaning": "表有婚配因緣，且對感情充滿期待。婚後通常會帶動事業與財運提升 3。",
            "motivation": "崇尚自由戀愛，希望在親密關係中獲得情感的潤澤與物資共享 3。",
            "impact": "配偶性格感性多情，且對命主有實質助益。適合透過配偶人脈拓展事業 3。"
        },
        "子女宮": {
            "palace_def": "子女宮代表晚輩、下屬、合夥事業，也是對外的桃花位 2。",
            "meaning": "主子息緣厚，子女聰明帶財。也象徵命主本人的才華能外顯，不藏拙 3。",
            "motivation": "渴望透過「繁衍」或「教導」來延續自我價值，對生命充滿創造性衝動。",
            "impact": "適合從事合夥生意。化祿照田宅宮，主居家環境氣場宏大、明亮 3。"
        },
        "財帛宮": {
            "palace_def": "財帛宮是財富最直接的展現位，反映賺錢的姿態與理財觀 1。",
            "meaning": "賺錢不僅是生存需要，更是一種「生活情趣」。其財源多元且來財輕鬆 3。",
            "motivation": "透過物質交換與獲取來確認自我價值。具有容人之心，講究雙贏 3。",
            "impact": "會賺錢但也易因「輕財」導致控制力不佳。與配偶在金錢使用上易達成共識 3。"
        },
        "疾厄宮": {
            "palace_def": "疾厄宮代表潛意識、肉體與私下的真實自我 3。",
            "meaning": "心懷寬廣、樂觀幽默。代表優越的工作環境與穩定的職涯 3。",
            "motivation": "追求「身體的絕對舒適」與「心靈的零壓力」。",
            "impact": "幼年多災病但能逢凶化吉 3。化祿照父母宮，考運不俗，利於大企業生存 3。"
        },
        "遷移宮": {
            "palace_def": "遷移宮代表出門在外運勢、公眾形象與際遇 2。",
            "meaning": "社交能力極強，外緣極佳。在外受人肯定，形象圓融親和 3。",
            "motivation": "追求「廣度」勝於「深度」的人際連結，老來運勢更好 3。",
            "impact": "適合變動性強的工作（如業務、公關、旅遊）。家庭財政受配偶影響大 3。"
        },
        "交友宮": {
            "palace_def": "交友宮掌管與平輩、群眾、部屬的互動關係 2。",
            "meaning": "朋友多且新緣不斷，對朋友有情義，樂於在群體中尋求存在感 3。",
            "motivation": "重視「眾生相」，渴望在人際互動中達成和諧與共榮 3。",
            "impact": "適合服務業，能得老闆賞識 3。往來對象多為汲汲營營於金錢之人 3。"
        },
        "事業宮": {
            "palace_def": "事業宮代表職場的和諧、工作態度與發展潛能 2。",
            "meaning": "工作環境人緣好，發展機會多。化祿照夫妻宮，主感情和諧 3。",
            "motivation": "工作中追求「愉悅感」與「和諧人際」，而非單純權力競爭 3。",
            "impact": "忙碌但效率可能不講究。學習態度聰明但易分心讀感興趣的閒書 3。"
        },
        "田宅宮": {
            "palace_def": "田宅宮是財富的最後堡壘，代表房產、家庭氛圍與安全感 2。",
            "meaning": "具備自立置產能力，家庭氛圍和睦。是一個典型的「有財庫」格局 3。",
            "motivation": "追求「落葉歸根」與絕對物資根基 3。對家庭有天然責任感 1。",
            "impact": "適合不動產相關行業或開設店面 3。對生活質量要求極高 3。"
        },
        "福德宮": {
            "palace_def": "福德宮代表福報、精神世界、祖德與潛意識財運 2。",
            "meaning": "心態健康、領悟力高。這類人有福報，懂得生活享受 3。",
            "motivation": "追求「靈魂的寧靜」與「精神的富足」 1。",
            "impact": "化祿照財帛宮，代表常有暗財或偏財。祖上有德，能遇難呈祥 3。"
        },
        "父母宮": {
            "palace_def": "父母宮代表父母、長輩、主管，也代表外貌與遺傳 2。",
            "meaning": "長輩緣深，聰明機敏，能得師長疼惜。在公門或大企業中具優勢 3。",
            "motivation": "渴望獲得主流價值觀與威權體系認可，善於表達自我 3。",
            "impact": "腦筋靈活能舉一反三。通常具備良好的遺傳基因與第一印象 3。"
        }
    }

    DEPARTMENTAL_DNA = {
        "命宮": {
            "wealth": "命主具備敏銳商業嗅覺，主動尋求生財之道，求財相對順利。",
            "property": "重視家庭與實體資產，一生致力購置房產，靠努力白手起家。"
        },
        "兄弟宮": {
            "wealth": "手足或摯友提供資金協助，透過內部集資或合夥輕鬆獲利。",
            "property": "家族間資金往來和睦，共同投資房產或從利潤中累積實體家產。"
        },
        "夫妻宮": {
            "wealth": "配偶給予財務大支持，婚後配偶運勢帶動命主實質現金收入。",
            "property": "配偶顧家，婚後家運興旺。配偶帶來嫁妝或協助購置房產。"
        },
        "子女宮": {
            "wealth": "晚輩下屬能幫命主賺錢。適合投資新興產業、娛樂或教育業。",
            "property": "「子帶財來」，生子後家運大開。用於開設分店或投資實業。"
        },
        "疾厄宮": {
            "wealth": "靠勞力或身體條件輕鬆賺錢。工作環境舒適，付出有對等回報。",
            "property": "工作場所能創造極大效益。重視居家品質與豪華視覺空間。"
        },
        "遷移宮": {
            "wealth": "出外逢貴人，適合海外市場或透過強大人脈關係賺取現金。",
            "property": "離鄉後能順處建立家業。透過品牌影響力帶動資產增值。"
        },
        "交友宮": {
            "wealth": "擁有廣大客戶群支援。朋友就是財富，適合眾籌或零售服務。",
            "property": "朋友客戶協助成家立業，或獲得房地產投資的一手內線。"
        },
        "事業宮": {
            "wealth": "本職表現佳，順利加薪分紅。事業擴張與財富累積呈正循環。",
            "property": "適合「廠店合一」。事業利潤全數轉化為實體不動產累積。"
        },
        "福德宮": {
            "wealth": "憑興趣、靈感或特殊才華賺錢。來財輕鬆，心想事成之福報。",
            "property": "祖德蔭庇，易獲遺產或贈與。住在置產房中感精神滿足。"
        },
        "父母宮": {
            "wealth": "獲長輩、政府或金融機構資金援助。適合政府標案獲取獲利。",
            "property": "繼承家族不動產，或透過銀行貸款獲得極佳利率順利買房。"
        }
    }

    def __init__(self, year, month, day, hour_index, is_lunar=False, gender="男"):
        date_str = f"{year}-{month:02d}-{day:02d}"
        if is_lunar: self.chart = astro.by_lunar(year, month, day, hour_index, False, gender)
        else: self.chart = astro.by_solar(date_str, hour_index, gender)
        self.palaces = self.chart.palaces

    def get_palace_by_label(self, label):
        for p in self.palaces:
            curr = self.PALACE_NAME_MAP.get(p.name, p.name)
            if curr == label: return p
        return None

    def find_star_location(self, target_trad):
        for p in self.palaces:
            all_s = [s.translate_name() for s in p.major_stars + p.minor_stars + p.adjective_stars]
            norm = [self.TRAD_STAR_MAP.get(s, s) for s in all_s]
            if target_trad in norm: return self.PALACE_NAME_MAP.get(p.name, p.name)
        return "未知宮位"

    def get_birth_year_stem(self):
        stems = "甲乙丙丁戊己庚辛壬癸"
        try: year = int(self.chart.solar_date.split("-")[0])
        except: year = 1971
        idx = (year - 4) % 10
        stem = stems[idx]
        if stem in self.chart.chinese_date: return stem
        return stem

    def get_innate_distribution(self):
        stem = self.get_birth_year_stem()
        trans = self.SI_HUA_MAP.get(stem)
        dist = {}
        for k, v in trans.items(): dist[k] = {"star": v, "palace": self.find_star_location(v)}
        return {"stem": stem, "stars": dist}

    def get_ceo_audit(self):
        mp = self.get_palace_by_label("命宮")
        star = mp.major_stars[0].translate_name() if mp.major_stars else "紫微"
        trad = self.TRAD_STAR_MAP.get(star, star)
        return {"star": trad, "image": self.CEO_IMAGES.get(trad, "zi_wei_emperor_1774971867916.png"), "description": f"具備【{trad}】核心決策素質。"}

    def fly_all_palaces(self):
        res = {}
        labels = ["命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮", "遷移宮", "交友宮", "事業宮", "田宅宮", "福德宮", "父母宮"]
        for l in labels:
            p = self.get_palace_by_label(l)
            if not p: continue
            stem = {"jia":"甲","yi":"乙","bing":"丙","ding":"丁","wu":"戊","ji":"己","geng":"庚","xin":"辛","ren":"壬","gui":"癸"}.get(p.heavenly_stem[:3].lower(), "甲")
            trans = self.SI_HUA_MAP.get(stem)
            res[l] = {
                "stem": stem, "lu_star": trans["祿"], "lu_dest": self.find_star_location(trans["祿"]),
                "ji_star": trans["忌"], "ji_dest": self.find_star_location(trans["忌"]),
                "collision": f"能量向『{self.find_star_location(trans['祿'])}』擴張，壓力在『{self.find_star_location(trans['忌'])}』收斂。"
            }
        return res

    def get_wealth_audit(self):
        ceo, innate, flying = self.get_ceo_audit(), self.get_innate_distribution(), self.fly_all_palaces()
        res = {}
        for name in ["命宮", "財帛宮", "田宅宮"]:
            fd = flying.get(name, {})
            l1 = []
            for t, s in innate["stars"].items():
                if s["palace"] == name:
                    rich = self.INNATE_RICH_DATABASE.get(name, {})
                    l1.append({"star": f"{s['star']}(生年{t})", "comment": rich.get("meaning", "重要先天基因")})
            
            # Simple logic for department audit
            res[name] = {
                "layer1": {"stars": l1, "empty_msg": "無生年四化，純看後天對待。"},
                "layer2": {
                    "lu": {"dest": fd.get("lu_dest"), "why": "資源挹注 [App-C10]", "how": "積極擴張戰果。", "strategy": "資源挹注"},
                    "ji": {"dest": fd.get("ji_dest"), "why": "風險收斂 [App-C10]", "how": "設立防火牆。", "strategy": "防火牆"},
                    "summary": fd.get("collision")
                }
            }
        return {"ceo": ceo, "innate": innate, "soul": res["命宮"], "wealth": res["財帛宮"], "property": res["田宅宮"], "conclusions": ["【穩健發展】建議按既定戰略擴張。"]}

    def get_innate_audit(self):
        innate = self.get_innate_distribution()
        profiles = []
        for t, s in innate["stars"].items():
            rich = self.INNATE_RICH_DATABASE.get(s["palace"], {
                "palace_def": f"{s['palace']}地位。", "meaning": "先天緣分在此。", 
                "motivation": "尋求穩定。", "impact": "生命潛力。"
            })
            dna = self.DEPARTMENTAL_DNA.get(s["palace"], {"wealth": "潛在財運。", "property": "潛在資產。"})
            header = f"先天{s['star']}化{t}位於『{s['palace']}』({s['palace']}) | {dna['wealth']} | {dna['property']}"
            profiles.append({
                "header": header, "palace_def": rich["palace_def"],
                "meaning": rich["meaning"], "motivation": rich["motivation"], "impact": rich["impact"]
            })
        return profiles

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
