from iztro_py import astro
import json
import os
import base64
from google import genai

class ZiWeiEngine:
    """
    紫微斗數飛星計算引擎 (專業財務審計版 - 旗艦溫潤紙本)
    整合《先天格局與財富格局》與《財運四化解析》
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
        "propertyPalace": "田宅宮", "fortunePalace": "福德宮", "parentsPalace": "父母宮"
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

    # === [Appendix Logic] Chapter 10 Terminology ===
    RISK_WARNINGS = {
        "武曲-忌": "武曲化忌（鐵腕財務長遇危機）：小心資金斷鍊、周轉不靈。實體資產與金融銀行類投資易貶值。",
        "太陽-忌": "太陽化忌（跨國CEO面臨波及）：小心外匯虧損、海外波及與能源產業波動。賺了面子賠了底子。",
        "廉貞-忌": "廉貞化忌（法務長踩紅線）：求財過程易牽扯合規與法務問題。最忌遊走灰色地帶。",
        "太陰-忌": "太陰化忌（房產大亨資產凍結）：小心房地產套牢、租金回收困難。最忌財務糾紛。",
        "天機-忌": "天機化忌（數據分析師的失誤）：小心策略錯誤、程式交易Bug。最忌頻繁短線進出。",
        "天同-忌": "天同化忌（享樂主義的天真陷阱）：小心盲目投資夕陽產業或因輕信朋友落入合夥欺騙。",
        "貪狼-忌": "貪狼化忌（投機客泡沫破裂）：小心詐騙陷阱、高槓桿爆倉。嚴防數位資產被駭。",
        "巨門-忌": "巨門化忌（公關災難）：小心錯誤資訊判斷。最忌聽信內線消息或合約漏洞。",
        "文曲-忌": "會計信用破產：極端危險。代表票據糾紛與金融業障問題，最忌支票不兌現。",
        "文昌-忌": "契約法律漏洞：嚴防簽約風險，支票不兌現，面臨惡意倒帳。"
    }

    WEALTH_ENGINES = {
        "天同-祿": "穩健與服務類 (被動收入財)：賺享受人生的輕鬆財。",
        "天梁-祿": "穩健與服務類 (被動收入財)：賺庇蔭眾生的長者財。",
        "天機-祿": "技術與策略類 (資訊財)：適合高頻交易、軟體程式與短線操作。",
        "太陽-祿": "技術與策略類 (名聲財)：適合知名藍籌企業股、跨國外匯投資。",
        "巨門-祿": "技術與策略類 (資訊財)：適合法律相關、諮詢顧問業，深挖資訊差。",
        "武曲-祿": "金融財星類 (重資產)：適合正統金融、銀行與黃金等硬通貨。",
        "太陰-祿": "金融財星類 (實體資產)：適合房地產、長線收租與民生必需品。",
        "天府-祿": "金融財星類 (庫星)：適合銀行股、大型權值股與倉儲業。"
    }

    # === [Layer 1] High-Depth Innate Setup Database ===
    # Source: 先天格局與財富格局.md (lines 76-170)
    INNATE_RICH_DATABASE = {
        "命宮": {
            "palace_def": "命宮代表自我、性格與承載力，是財富的總指揮部 1。",
            "meaning": "代表「我」與生俱來的資源與福報。這種人不需要向外乞求緣分，緣分會自動向其靠攏 3。",
            "motivation": "一種深根蒂固的「生命信任感」。因為覺得世界是友善的，所以更願意展現親和力，構成一生的幸運底色 1。",
            "impact": "聰明、有才華且不吝嗇。在財富獲取上多屬「自立格」，能靠個人魅力或天賦輕鬆上手 2。"
        },
        "兄弟宮": {
            "palace_def": "兄弟宮是財帛宮的田宅位，象徵現鈔蓄水池，也代表母親與手足 1。",
            "meaning": "化祿在此宮，代表現金流動性極強，且財庫充盈。與母親關係的和諧度直接影響現金周轉能力 1。",
            "motivation": "追求物質上的流動與分享。對母親的全然接納，能引動此宮的化祿能量，使財源滾滾而來 1。",
            "impact": "易得手足、母系長輩或同儕的經濟支持。適合從事需要高度現金流動的行業 1。"
        },
        "夫妻宮": {
            "palace_def": "夫妻宮是官祿宮的遷移位，代表事業對外的公眾形象與際遇 2。",
            "meaning": "表有婚配因緣，且對感情充滿期待。婚後通常會帶動事業與財運的提升 3。",
            "motivation": "崇尚自由戀愛，希望在親密關係中獲得情感的潤澤與物資的共享 3。",
            "impact": "配偶性格感性多情，且對命主有實質助益。適合透過配偶的人脈或資源來拓展事業 3。"
        },
        "子女宮": {
            "palace_def": "子女宮代表晚輩、下屬、合夥事業，也是對外的桃花位 2。",
            "meaning": "主子息緣厚，子女聰明帶財而來。同時也象徵命主本人的才華能外顯，不藏拙 3。",
            "motivation": "渴望透過「繁衍」或「教導」來延續自我價值，對生命充滿創造性的衝動。",
            "impact": "適合從事合夥生意，且能得力下屬助益 3。化祿照田宅宮，主居家環境氣場宏大、明亮 3。"
        },
        "財帛宮": {
            "palace_def": "財帛宮是財富最直接的展現位，反映賺錢的姿態與理財觀 1。",
            "meaning": "賺錢不僅是生存需要，更是一種「生活情趣」。其財源多元，且來財過程相對輕鬆 3。",
            "motivation": "透過物質交換與獲取來確認自我價值，具有容人之心，在交易中講究雙贏 3。",
            "impact": "很會賺錢但也容易因「輕財」導致對金錢控制力不佳。與配偶在金錢使用上較易達成共識 3。"
        },
        "疾厄宮": {
            "palace_def": "疾厄宮是命宮的陰面，代表潛意識、肉體與私下的真實自我 3。",
            "meaning": "心懷寬廣、樂觀幽默，是一個好相處的人。代表優越的工作環境與穩定的職涯 3。",
            "motivation": "追求「身體的絕對舒適」與「心靈的零壓力」。",
            "impact": "幼年多災病但能逢凶化吉 3。化祿照父母宮，代表考運不俗，利於在大型企業生存 3。"
        },
        "遷移宮": {
            "palace_def": "遷移宮代表出門在外的運勢、公眾形象與際遇 2。",
            "meaning": "社交能力極強，外緣極佳，易得貴人相助。在外受人肯定，形象圓融親和 3。",
            "motivation": "追求「廣度」勝於「深度」的人際連結，老來運勢更好 3。",
            "impact": "適合變動性強的工作（如業務、公關、旅遊） 3。家庭財政上往往受配偶理財影響較大 3。"
        },
        "交友宮": {
            "palace_def": "交友宮掌管與平輩、群眾、部屬的互動關係 2。",
            "meaning": "朋友多且新緣不斷，對朋友有情義，樂於在群體中尋求存在感 3。",
            "motivation": "重視「眾生相」，渴望在人際互動中達成和諧與共榮 3。",
            "impact": "適合服務業，能得老闆或主管的賞識 3。往來對象多為汲汲營營於金錢之人 3。"
        },
        "事業宮": {
            "palace_def": "事業宮代表職場的和諧、工作態度與發展潛能 2。",
            "meaning": "工作環境人緣好，發展機會多，適合自立門戶。化祿照夫妻宮，主感情和諧 3。",
            "motivation": "在工作中追求「愉悅感」與「和諧的人際關係」，而非單純的權力競爭 3。",
            "impact": "忙碌但可能效率不講究。學習態度聰明但易分心去讀自己喜歡的「閒書」 3。"
        },
        "田宅宮": {
            "palace_def": "田宅宮是財富的最後堡壘，代表房產、家庭氛圍與安全感 2。",
            "meaning": "具備自立置產的能力，家庭氛圍和睦。這是一個典型的「有財庫」格局 3。",
            "motivation": "追求「落葉歸根」與絕對的物資根基 3。對家庭有一種天然的責任感與依附感 1。",
            "impact": "適合從事不動產相關行業或開設店面 3。對生活質量有極高要求，且享受慾望不低 3。"
        },
        "福德宮": {
            "palace_def": "福德宮代表福報、精神世界、祖德與潛意識財運 2。",
            "meaning": "心態健康、情緒佳，領悟力高。這類人有福報，懂得生活享受，不會虧待自己 3。",
            "motivation": "追求「靈魂的寧靜」與「精神的富足」 1。",
            "impact": "化祿照財帛宮，代表常有暗財或偏財，來財輕鬆。祖上有德，遇到困難常能遇難呈祥 3。"
        },
        "父母宮": {
            "palace_def": "父母宮代表父母、長輩、主管，也代表外貌與遺傳 2。",
            "meaning": "長輩緣深，聰明機敏，能得師長或上司的疼惜與助益。在公門或大企業中極具優勢 3。",
            "motivation": "渴望獲得主流價值觀與威權體系的認可，善於表達自我 3。",
            "impact": "腦筋靈活不讀死書，能舉一反三。通常具備良好的遺傳基因與第一印象 3。"
        }
    }

    DEPARTMENTal_DNA = {
        "命宮": {
            "wealth": "命主天生具備敏銳的商業嗅覺，對賺錢充滿熱情，會主動尋求生財之道，求財過程相對順利。",
            "property": "命主極度重視家庭與實體資產，一生致力於購買房地產，家庭觀念極重，能靠自身努力白手起家置產。"
        },
        "兄弟宮": {
            "wealth": "兄弟姊妹或摯友能提供資金協助，或透過與人合夥、內部集資而輕鬆獲利，現金流調度靈活。",
            "property": "家族兄弟間有資金往來且和睦，能共同投資房地產獲利，或從合夥事業的利潤中累積龐大的實體家產。"
        },
        "夫妻宮": {
            "wealth": "配偶給予財務上的極大支持，花配偶的錢不心痛，或婚後配偶的運勢帶動命主的實質現金收入。",
            "property": "配偶顧家，婚後家運興旺。配偶可能帶來嫁妝，或憑藉配偶的精打細算協助購入房產，家庭氣氛和樂。"
        },
        "子女宮": {
            "wealth": "晚輩、下屬或學生能幫命主賺錢。極度適合投資新興產業，或從事與娛樂、教育相關的事業而獲取現金。",
            "property": "俗稱「子帶財來」，生小孩後家運大開，購置房產。也代表將公司盈餘用於開設分店或投資實業廠房。"
        },
        "疾厄宮": {
            "wealth": "命主靠著勞力、身體美貌或體力活動能輕鬆賺錢。工作環境令人感到舒適，付出勞力即有對等豐厚回報。",
            "property": "工作場所或工廠能創造極大效益。命主喜歡將家裡佈置得非常豪華舒適，極度重視居家品質與生活空間。"
        },
        "遷移宮": {
            "wealth": "出外逢貴人，適合離開家鄉發展。在外地或透過強大的公眾人際關係、海外市場賺取大筆現金。",
            "property": "離鄉背井後能順利在外地建立家業並置產。透過強大的公眾形象或品牌影響力，帶動公司整體資產的升值。"
        },
        "交友宮": {
            "wealth": "擁有廣大的客戶群與粉絲支持，朋友就是財富。非常適合從事群眾募資、直銷或現金零售服務業。",
            "property": "朋友或客戶會協助命主成家立業，或透過廣大的人脈網絡獲得第一手房地產投資的內線消息而順利買房。"
        },
        "事業宮": {
            "wealth": "工作表現極佳，透過本職工作順利加薪、獲得豐厚分紅。事業的擴張與財富的累積呈現正相關的良性循環。",
            "property": "適合「廠店合一」或將公司設立在自家。工作與事業帶來的豐厚利潤，最終全數轉化為不動產累積。"
        },
        "福德宮": {
            "wealth": "憑藉興趣、靈感、良好的心理素質或特殊才華賺錢。來財輕鬆，心想事成，擁有令人羨慕的「福報財」。",
            "property": "祖上積德，容易獲得遺產或長輩贈與的不動產。心態安穩，住在自己購置的房子裡能感到極大的精神滿足。"
        },
        "父母宮": {
            "wealth": "容易獲得長輩、政府機關或金融機構的直接資金援助。適合從事公職或與政府標案相關的生意獲利。",
            "property": "順利繼承父母或家族的不動產，或是透過向銀行貸款（父母宮為文書與借貸位）獲得極佳利率而順利購買房地產。"
        }
    }

    def __init__(self, year, month, day, hour_index, is_lunar=False, gender="男"):
        date_str = f"{year}-{month:02d}-{day:02d}"
        if is_lunar: self.chart = astro.by_lunar(year, month, day, hour_index, False, gender)
        else: self.chart = astro.by_solar(date_str, hour_index, gender)
        self.palaces = self.chart.palaces

    def get_palace_by_label(self, label):
        for p in self.palaces:
            curr = self.PALACE_NAME_MAP.get(p.name)
            if not curr:
                try: curr = p.translate_name()
                except: pass
            if curr == label: return p
        return None

    def find_star_location(self, target_trad):
        trad_map = {"太阳":"太陽", "太阴":"太陰", "天机":"天機", "廉贞":"廉貞", "贪狼":"貪狼", "巨门":"巨門", "文昌":"文昌", "文曲":"文曲", "武曲":"武曲", "天同":"天同", "破军":"破軍", "天梁":"天梁", "紫微":"紫微", "天府":"天府", "天相":"天相", "七杀":"七殺"}
        for p in self.palaces:
            all_s = [s.translate_name() for s in p.major_stars + p.minor_stars + p.adjective_stars]
            norm = [trad_map.get(s, s) for s in all_s]
            if target_trad in norm: return self.PALACE_NAME_MAP.get(p.name, p.name)
        return "未知宮位"

    def get_birth_year_stem(self):
        stems = "甲乙丙丁戊己庚辛壬癸"
        try: year = int(self.chart.solar_date.split("-")[0])
        except: year = 1971
        idx = (year - 4) % 10
        stem = stems[idx]
        if stem in self.chart.chinese_date: return stem
        prev = stems[(idx-1)%10]
        return prev if prev in self.chart.chinese_date else stem

    def get_innate_distribution(self):
        stem = self.get_birth_year_stem()
        trans = self.SI_HUA_MAP.get(stem)
        dist = {}
        for k, v in trans.items(): dist[k] = {"star": v, "palace": self.find_star_location(v)}
        return {"stem": stem, "stars": dist}

    def get_ceo_audit(self):
        p = self.get_palace_by_label("命宮")
        star = p.major_stars[0].translate_name() if p.major_stars else "紫微"
        trad = {"太阳":"太陽", "太阴":"太陰", "天机":"天機", "廉贞":"廉貞", "贪狼":"貪狼", "巨门":"巨門", "武曲":"武曲", "天同":"天同", "破军":"破軍", "天梁":"天梁", "紫微":"紫微", "天府":"天府", "天相":"天相", "七杀":"七殺"}.get(star, star)
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
                "collision": self.get_collision_logic(l, self.find_star_location(trans["祿"]), self.find_star_location(trans["忌"]))
            }
        return res

    def get_collision_logic(self, source, lu, ji):
        if lu == ji: return f"【祿忌同宮】壓力與機遇在『{lu}』交織。高風險高收益。"
        return f"【能量流動】資源向『{lu}』擴張，壓力在『{ji}』收斂。"

    def get_audit_how(self, trans_type, source, dest):
        if trans_type == "祿":
            if dest == "財帛宮" and source in self.DEPARTMENTal_DNA:
                return {"why": "部門資源挹助 [App-C10]", "how": self.DEPARTMENTal_DNA[source]["wealth"], "strategy": "資源挹注格"}
            if dest == "田宅宮" and source in self.DEPARTMENTal_DNA:
                return {"why": "資產守護格局 [App-C10]", "how": self.DEPARTMENTal_DNA[source]["property"], "strategy": "金庫底氣格"}
            return {"why": f"{source} 資源流向 {dest}", "how": "積極在變動中尋求最大化資源溢出點。", "strategy": "擴張引擎"}
        else:
            p = self.get_palace_by_label(source)
            stem = p.heavenly_stem[0] if p else "甲"
            star = self.SI_HUA_MAP.get(stem, self.SI_HUA_MAP["甲"])["忌"]
            key = f"{star}-忌"
            if key in self.RISK_WARNINGS:
                return {"why": self.RISK_WARNINGS[key], "how": "設立防火牆，嚴防風險擴散。", "strategy": "風險預警"}
            return {"why": f"{source} 壓力收斂於 {dest}", "how": "保住核心資產，嚴控現金流漏水點。", "strategy": "防火牆"}

    def get_wealth_audit(self):
        ceo, innate, flying = self.get_ceo_audit(), self.get_innate_distribution(), self.fly_all_palaces()
        res = {}
        for name in ["命宮", "財帛宮", "田宅宮"]:
            fd = flying.get(name, {})
            l1 = []
            for t, s in innate["stars"].items():
                if s["palace"] == name:
                    rich = self.INNATE_RICH_DATABASE.get(name, {})
                    l1.append({"star": f"{s['star']}(生年{t})", "key": name, "comment": rich.get("meaning", "重要先天基因")})
            
            lu_l = self.get_audit_how("祿", name, fd.get("lu_dest"))
            ji_l = self.get_audit_how("忌", name, fd.get("ji_dest"))
            res[name] = {
                "layer1": {"stars": l1, "empty_msg": "此宮位無生年四化，純看後天對待。"},
                "layer2": {
                    "lu": {"dest": fd.get("lu_dest"), "why": lu_l["why"], "how": lu_l["how"], "strategy": lu_l["strategy"]},
                    "ji": {"dest": fd.get("ji_dest"), "why": ji_l["why"], "how": ji_l["how"], "strategy": ji_l["strategy"]},
                    "summary": fd.get("collision")
                }
            }
        return {"ceo": ceo, "innate": innate, "soul": res["命宮"], "wealth": res["財帛宮"], "property": res["田宅宮"], "conclusions": ["【穩健發展】建議按既定戰略擴張。"]}

    def get_innate_audit(self):
        innate = self.get_innate_distribution()
        profiles = []
        for t, s in innate["stars"].items():
            rich = self.INNATE_RICH_DATABASE.get(s["palace"], {
                "palace_def": f"{s['palace']}角色位。", "meaning": "先天緣分在此紮根。", 
                "motivation": "尋求穩定與成長。", "impact": "帶來潛在生命動力。"
            })
            dna = self.DEPARTMENTal_DNA.get(s["palace"], {"wealth": "對財運有潛在作用。", "property": "對資產有潛在作用。"})
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
        T_STARS= {"紫微":"紫微","天机":"天機","太阳":"太陽","武曲":"武曲","天同":"天同","廉贞":"廉貞","天府":"天府","太阴":"太陰","贪狼":"貪狼","巨门":"巨門","天相":"天相","天梁":"天梁","七杀":"七殺","破军":"破軍","左辅":"左輔","右弼":"右弼","文昌":"文昌","文曲":"文曲","禄存":"祿存","祿存":"祿存","擎羊":"擎羊","陀罗":"陀羅","火星":"火星","铃星":"鈴星","地空":"地空","地劫":"地劫"}
        for p in self.palaces:
            idx = B_MAP.get(p.earthly_branch)
            grid[idx] = {
                "name": self.PALACE_NAME_MAP.get(p.name, p.name),
                "stem": {"jiaHeavenly":"甲","yiHeavenly":"乙","bingHeavenly":"丙","dingHeavenly":"丁","wuHeavenly":"戊","jiHeavenly":"己","gengHeavenly":"庚","xinHeavenly":"辛","renHeavenly":"壬","guiHeavenly":"癸"}.get(p.heavenly_stem, "甲"),
                "major_stars": [T_STARS.get(s.translate_name(), s.translate_name()) for s in p.major_stars],
                "minor_stars": [T_STARS.get(s.translate_name(), s.translate_name()) for s in p.minor_stars if s.translate_name() not in ["左輔","右弼","天魁","天鉞","文昌","文曲","祿存","擎羊","陀羅","火星","鈴星","地空","地劫"]],
                "sha_stars": [T_STARS.get(s.translate_name(), s.translate_name()) for s in p.minor_stars + p.adjective_stars if T_STARS.get(s.translate_name()) in ["擎羊","陀羅","火星","鈴星","地空","地劫"]],
                "lucky_stars": [T_STARS.get(s.translate_name(), s.translate_name()) for s in p.minor_stars + p.adjective_stars if T_STARS.get(s.translate_name()) in ["左輔","右弼","天魁","天鉞","文昌","文曲"]],
                "wealth_stars": ["祿存"] if any(s.translate_name() == "祿存" for s in p.minor_stars + p.adjective_stars) else []
            }
        return grid
