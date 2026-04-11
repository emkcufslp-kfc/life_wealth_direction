from iztro_py import astro
import json
import os
import base64
import google.generativeai as genai

class ZiWeiEngine:
    """
    紫微斗數飛星計算引擎 (專業財務審計版)
    整合《紫微斗數財運四化解析》Part 1 (靜態) & Part 2 (動態)
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
        "surfacePalace": "父母宮", "spiritPalace": "福德宮" # Technical aliases
    }

    # CEO Image Mapping (Star -> Filename)
    CEO_IMAGES = {
        "紫微": "zi_wei_emperor_1774971867916.png",
        "天機": "tian_ji_strategist_1774971903938.png",
        "太陽": "tai_yang_sun_1774971982538.png",
        "武曲": "wu_qu_executor_1774972069586.png",
        "天同": "tian_tong_harmonizer_1774972148960.png",
        "廉貞": "lian_zhen_crisis_pr_1774972254175.png",
        "天府": "tian_fu_treasurer_1774972278010.png",
        "太陰": "tai_yin_designer_1774972301368.png",
        "貪狼": "tan_lang_marketer_1774972333552.png",
        "巨門": "ju_men_truth_seeker_1774972355775.png",
        "天相": "tian_xiang_negotiator_justice_1774972456284.png",
        "天梁": "tian_liang_protector_advisor_1774972484778.png",
        "七殺": "qi_sha_conqueror_combatant_1774972505956.png",
        "破軍": "po_jun_rebel_disruptor_1774972529713.png"
    }

    # === [Part 1] Library Interpretations (Static) ===
    LU_INTERPRETATION = {
        "命宮": "命主天生具備敏銳商業嗅覺，主動尋求生財之道，求財相對順利。",
        "兄弟宮": "【內部資金】兄弟或摯友提供資金協助，現金流調度靈活。",
        "夫妻宮": "【配偶財】配偶給予財務支持，或婚後配偶運勢帶動現金收入。",
        "子女宮": "【投資擴張】晚輩或下屬助益，適合投資新興產業或娛樂教育事業。",
        "疾厄宮": "【勞力獲利】靠體力、技術或實體工廠穩定賺錢，重視居家/工作品質。",
        "遷移宮": "【遠方財】適合海外市場、公關形象，在外地逢貴人得財。",
        "交友宮": "【人脈財】粉絲與客戶群廣大，適合平台經濟、電商或現金零售業。",
        "事業宮": "【本業分紅】事業營運良性循環，加薪分紅順利，以財生財。",
        "田宅宮": "【最強守財】家運興隆，資金穩入庫，適合購買不動產或長線價值投資。",
        "福德宮": "【福報財】靠興趣、靈感或特殊才華獲利，心情愉快則財運更佳。",
        "父母宮": "【政策財】得長輩、政府標案或銀行融資支援，資金來源高端。",
        "財帛宮": "【高轉速】敢花敢賺，現金流轉速度快，適合高流動性投資。"
    }

    JI_INTERPRETATION = {
        "命宮": "對金錢極度執著（守財奴），但易因決策失誤導致破財流失。",
        "兄弟宮": "【金融黑洞】嚴禁金錢借貸或合夥，易因債務導致大失血。",
        "夫妻宮": "【伴侶損財】配偶花費大或因婚姻變動導致財產大宗流失。",
        "子女宮": "【盲目燒錢】在子女教育或合夥項目上不斷投入卻難見收益，現金流斷裂。",
        "疾厄宮": "【過勞代價】因健康問題支出龐大，或因實體店面高昂租金被拖垮。",
        "遷移宮": "【外地風險】出外求財阻礙多，易遭詐騙或在海外市場遭受重大挫折。",
        "交友宮": "【損友劫財】因朋友牽連背負債務，不宜聽信內線消息或跟風投資。",
        "事業宮": "【營運瓶頸】管理成本過高，資金被事業嚴重套牢，易產生產權糾紛。",
        "田宅宮": "【金庫破洞】房貸壓力沈重，或因抵押家產填補虧空，金庫見底。",
        "福德宮": "【無福享用】腦波弱，情緒性消費嚴重，來錢快去得更快，陷入債難還困局。",
        "父母宮": "【稅務法規】易受官司、行政罰款或長輩債務牽連，必須破財消災。",
        "財帛宮": "【留不住錢】典型自化忌，情緒性開支或突發支出導致資金斷路。"
    }

    # === [Part 2] Dynamic Logic: Self-Transformation & Collision ===
    SELF_TRANS_LU = "【自化祿】業務部天生體質樂觀，求財手腕圓融，屬於天賜財源。"
    SELF_TRANS_QUAN = "【自化權】投資紀律嚴明，具備強大掌控力，適合高階經理人或定時定額。"
    SELF_TRANS_KE = "【自化科】智慧理財典範，靠專業分析、著作權或諮詢服務獲取智慧財產。"
    SELF_TRANS_JI = "【自化忌】理財習性先天不良，應採取『陽升陰降』，若本宮化祿入田宅則應『有錢買房』。"

    def __init__(self, year, month, day, hour_index, is_lunar=False, gender="男"):
        date_str = f"{year}-{month:02d}-{day:02d}"
        if is_lunar:
            self.chart = astro.by_lunar(year, month, day, hour_index, False, gender)
        else:
            self.chart = astro.by_solar(date_str, hour_index, gender)
        self.palaces = self.chart.palaces

    def get_palace_by_label(self, label):
        for p in self.palaces:
            curr_label = self.PALACE_NAME_MAP.get(p.name)
            if not curr_label:
                try: curr_label = p.translate_name()
                except: pass
            if curr_label == label:
                return p
        return None

    def find_star_location(self, target_trad_name):
        # Normalization mapping for simplified -> traditional
        trad_mapping = {"太阳":"太陽", "太阴":"太陰", "天机":"天機", "廉贞":"廉貞", "贪狼":"貪狼", "巨门":"巨門", "文昌":"文昌", "文曲":"文曲", "武曲":"武曲", "天同":"天同", "破军":"破軍", "天梁":"天梁", "紫微":"紫微", "天府":"天府", "天相":"天相", "七杀":"七殺"}
        for p in self.palaces:
            all_stars = [s.translate_name() for s in p.major_stars + p.minor_stars + p.adjective_stars]
            normalized_stars = [trad_mapping.get(s, s) for s in all_stars]
            if target_trad_name in normalized_stars:
                return self.PALACE_NAME_MAP.get(p.name, p.name)
        return "未知宮位"

    def get_collision_logic(self, source_p, lu_dest, ji_dest):
        """
        [Part 2] 祿忌沖照動態邏輯
        """
        palace_order = ["命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮", "遷移宮", "交友宮", "事業宮", "田宅宮", "福德宮", "父母宮"]
        try:
            p1_idx = palace_order.index(lu_dest)
            p2_idx = palace_order.index(ji_dest)
            
            # Opposite palace check (Distance = 6)
            is_opposite = abs(p1_idx - p2_idx) == 6
            is_same = p1_idx == p2_idx
            
            if is_same:
                return f"【祿忌同宮】資源與壓力在『{lu_dest}』交織。代表此部門雖然獲利豐厚，但內部矛盾極大，處於『高營收、高風險』的震盪狀態。"
            elif is_opposite:
                return f"【祿忌沖照】祿在『{lu_dest}』、忌在對宮『{ji_dest}』。形成『拉扯效應』：這代表您在獲利的同時，對宮產生了絕對的空缺感，必須隨時防範『後院失火』的危機。"
            else:
                return f"【動態分布】獲利導向『{lu_dest}』，但風險潛伏於『{ji_dest}』。建議利用『{lu_dest}』的盈餘來填補『{ji_dest}』的漏洞。"
        except:
            return "四化動態平衡中。"

    def get_ceo_audit(self):
        """
        [Section: Company CEO] Character mapping and Mindset Audit
        """
        soul_p = self.get_palace_by_label("命宮")
        main_star = soul_p.major_stars[0].translate_name() if soul_p.major_stars else "紫微"
        trad_mapping = {"太阳":"太陽", "太阴":"太陰", "天机":"天機", "廉贞":"廉貞", "贪狼":"貪狼", "巨门":"巨門", "武曲":"武曲", "天同":"天同", "破军":"破軍", "天梁":"天梁", "紫微":"紫微", "天府":"天府", "天相":"天相", "七杀":"七殺"}
        main_star_trad = trad_mapping.get(main_star, main_star)
        
        ceo_image = self.CEO_IMAGES.get(main_star_trad, "zi_wei_emperor_1774971867916.png")
        
        # Willpower/Talent logic based on CEO Main Star
        mindset_db = {
            "紫微": "【格局：帝王格】天生具備強大領導力與格調。意志力堅定，發展方向應鎖定高端市場。",
            "天機": "【格局：智多星】擅長數據分析與策略佈局。天賦在於靈活變通，意志力受情緒波動影響。",
            "武曲": "【格局：正財長】極度務實與強大執行力。意志力鋼鐵般堅硬，適合實體金融與主流硬貨幣。",
            "太陽": "【格局：跨國CEO】博愛且具備公眾影響力。發光發熱，適合海外市場與能源/媒體產業。",
            "太陰": "【格局：設計大師】細膩、沈穩、重視家庭。天才的理財嗅覺，適合房地產與長線複利。",
            "貪狼": "【格局：市場開發】充滿欲望、交際手腕強。天賦在於發現新興機會，意志力在誘惑面前需磨練。",
            "巨門": "【格局：研究型長】深挖細部資訊差。意志力在於追求真相，發展方向為諮詢、法律、研究。",
            "廉貞": "【格局：風控長】敏銳的危機感與紀律。最忌違法，天賦在於處理複雜的人事與合規。",
            "天同": "【格局：和諧師】追求穩定與舒適。意志力偏弱，但福報深厚，適合輕資產、民生服務業。",
            "天府": "【格局：國庫管理】沈穩守成、累積資產。意志力保守，天賦在於資產配置與風險規避。",
            "破軍": "【格局：開拓先鋒】敢於打破舊有格局。意志力極強，適合高風險高收益的新創。"
        }
        
        return {
            "star": main_star_trad,
            "image": ceo_image,
            "description": mindset_db.get(main_star_trad, "整體格局深藏不露，具備全方位CEO潛能。")
        }

    def fly_all_palaces(self):
        """
        [Part 2] Full 12-Palace Dynamic Analysis
        """
        results = {}
        palace_labels = ["命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮", "遷移宮", "交友宮", "事業宮", "田宅宮", "福德宮", "父母宮"]
        for label in palace_labels:
            p = self.get_palace_by_label(label)
            if not p: continue
            stem = {"jiaHeavenly":"甲", "yiHeavenly":"乙", "bingHeavenly":"丙", "dingHeavenly":"丁", 
                    "wuHeavenly":"戊", "jiHeavenly":"己", "gengHeavenly":"庚", "xinHeavenly":"辛", 
                    "renHeavenly":"壬", "guiHeavenly":"癸"}.get(p.heavenly_stem, "甲")
            transforms = self.SI_HUA_MAP.get(stem)
            
            lu_dest = self.find_star_location(transforms["祿"])
            ji_dest = self.find_star_location(transforms["忌"])
            
            results[label] = {
                "stem": stem,
                "lu_star": transforms["祿"],
                "lu_dest": lu_dest,
                "ji_star": transforms["忌"],
                "ji_dest": ji_dest,
                "collision": self.get_collision_logic(label, lu_dest, ji_dest)
            }
        return results

    def get_palace_transformations(self, source_label):
        """
        獲取特定宮位飛出的四化標的 (祿、忌)
        """
        p = self.get_palace_by_label(source_label)
        if not p: return None
        
        stem = {"jiaHeavenly":"甲", "yiHeavenly":"乙", "bingHeavenly":"丙", "dingHeavenly":"丁", 
                "wuHeavenly":"戊", "jiHeavenly":"己", "gengHeavenly":"庚", "xinHeavenly":"辛", 
                "renHeavenly":"壬", "guiHeavenly":"癸"}.get(p.heavenly_stem, "甲")
        transforms = self.SI_HUA_MAP.get(stem)
        
        return {
            transforms["祿"]: {"type": "祿", "dest": self.find_star_location(transforms["祿"])},
            transforms["忌"]: {"type": "忌", "dest": self.find_star_location(transforms["忌"])}
        }

    def get_key_si_hua_summary(self):
        """
        [Request #4] Get key transformations for: 命宮, 財帛宮, 田宅宮, 福德宮
        """
        all_flying = self.fly_all_palaces()
        target_palaces = ["命宮", "財帛宮", "田宅宮", "福德宮"]
        summary = {}
        for p_name in target_palaces:
            data = all_flying.get(p_name)
            if data:
                summary[p_name] = {
                    "lu": f"{data['lu_star']} ➔ {data['lu_dest']}",
                    "ji": f"{data['ji_star']} ➔ {data['ji_dest']}"
                }
        return summary

    def get_wealth_audit(self):
        # 1. 執行長與格局審計 (CEO Audit)
        ceo_data = self.get_ceo_audit()
        
        # 2. 全宮位動態飛星 (Part 2)
        all_flying = self.fly_all_palaces()
        
        # 3. 核心部門審計 (Part 1 - Wealth/Property)
        wealth_data = all_flying.get("財帛宮", {})
        self_trans = []
        if wealth_data.get("lu_dest") == "財帛宮": self_trans.append(self.SELF_TRANS_LU)
        if wealth_data.get("ji_dest") == "財帛宮": self_trans.append(self.SELF_TRANS_JI)

        # Audit Object
        audit = {
            "ceo": ceo_data,
            "patterns": {
                "talent": ceo_data["description"],
                "direction": "根據『命宮』飛星軌跡：" + (all_flying.get("命宮", {}).get("collision", "執行力均衡。")),
                "willpower": "CEO 自帶格局意志分析：穩定。" if "權" in ceo_data["description"] else "意志富有韌性。"
            },
            "wealth": {
                "source": "財帛宮",
                "lu_dest": wealth_data.get("lu_dest"),
                "lu_why": f"此為財帛宮宮干『{wealth_data.get('stem')}』使『{wealth_data.get('lu_star')}』化祿入『{wealth_data.get('lu_dest')}』，代表資源與機會的主動流向。",
                "lu_how": self.get_audit_how("祿", wealth_data.get("lu_dest")),
                "lu_conclusion": f"戰略模式：{self.get_audit_conclusion('祿', wealth_data.get('lu_dest'))}",
                "ji_dest": wealth_data.get("ji_dest"),
                "ji_why": f"此為財帛宮宮干『{wealth_data.get('stem')}』使『{wealth_data.get('ji_star')}』化忌入『{wealth_data.get('ji_dest')}』，代表壓力與阻礙的收斂點。",
                "ji_how": self.get_audit_how("忌", wealth_data.get("ji_dest")),
                "ji_conclusion": f"風控目標：{self.get_audit_conclusion('忌', wealth_data.get('ji_dest'))}",
                "self_trans": self_trans,
                "collision": wealth_data.get("collision")
            },
            "property": {
                "source": "田宅宮",
                "lu_dest": all_flying.get("田宅宮", {}).get("lu_dest"),
                "lu_why": f"此為田宅宮宮干『{all_flying.get('田宅宮', {}).get('stem')}』使『{all_flying.get('田宅宮', {}).get('lu_star')}』化祿入『{all_flying.get('田宅宮', {}).get('lu_dest')}』，代表資產保值與擴張的底氣。",
                "lu_how": self.get_audit_how("祿", all_flying.get("田宅宮", {}).get("lu_dest")),
                "lu_conclusion": f"守成方向：{self.get_audit_conclusion('祿', all_flying.get('田宅宮', {}).get('lu_dest'))}",
                "ji_dest": all_flying.get("田宅宮", {}).get("ji_dest"),
                "ji_why": f"此為田宅宮宮干『{all_flying.get('田宅宮', {}).get('stem')}』使『{all_flying.get('田宅宮', {}).get('ji_star')}』化忌入『{all_flying.get('田宅宮', {}).get('ji_dest')}』，代表潛在的漏水點與守財壓力。",
                "ji_how": self.get_audit_how("忌", all_flying.get("田宅宮", {}).get("ji_dest")),
                "ji_conclusion": f"資產防護：{self.get_audit_conclusion('忌', all_flying.get('田宅宮', {}).get('ji_dest'))}",
                "collision": all_flying.get("田宅宮", {}).get("collision")
            },
            "strategic_conclusions": self.get_strategic_conclusions(all_flying)
        }
        return audit

    def get_audit_how(self, trans_type, dest):
        if trans_type == "祿":
            mapping = {
                "財帛宮": "適合短線周轉，保持高流動性。隨時調整投資組合。",
                "田宅宮": "有錢就換成磚頭。鎖住現金，轉化為實體資產或黃金。",
                "交友宮": "專攻口碑行銷與廣大客戶群，透過讓利與服務帶動業績。",
                "事業宮": "持續再投資於本業。擴大經營規模，開發垂直整合機會。",
                "命宮": "建立個人品牌。投資於自身能力與影響力，以人帶財。",
                "子女宮": "投資新創事業、新技術或教育培訓。透過向外擴大版圖獲利。"
            }
            return mapping.get(dest, "順應市場趨勢，積極主動佈局。")
        else:
            mapping = {
                "財帛宮": "小心突發性消費與情緒性理財。嚴格設立止損點。",
                "田宅宮": "防範金庫破洞，避免變賣家產支應短利。注意房產產權。",
                "交友宮": "切勿與人有大額金錢借貸，小心損友劫財或合夥紛爭。",
                "命宮": "防止守財奴心理導致決策僵化。警惕過度保守錯失機運。",
                "父母宮": "注意契約文書與政府稅務。嚴格簽署合規文件。",
                "疾厄宮": "小心過勞導致的醫療支出。防止體力透支影響財運。"
            }
            return mapping.get(dest, "設立財務防火牆，定期進行風險審計。")

    def get_audit_conclusion(self, trans_type, dest):
        if trans_type == "祿":
            mapping = {
                "財帛宮": "現金流即是生命線，周轉速度決定勝負。",
                "田宅宮": "金庫穩固則天下平，不動產是最後的堡壘。",
                "交友宮": "人脈即財脈，粉絲經濟與社群影響力是核心。",
                "事業宮": "深挖護城河，本業競爭力才是最強資產。",
                "命宮": "執行長(CEO)本身就是公司最值錢的智慧財產。"
            }
            return mapping.get(dest, "在變動中尋求最大化的資源溢出效應。")
        else:
            mapping = {
                "財帛宮": "守住錢財即是獲利，情緒控制是第一要務。",
                "田宅宮": "警惕過度槓桿，保住核心底氣勝過一切。",
                "交友宮": "合規與誠信是防火牆，遠離債務糾葛。"
            }
            return mapping.get(dest, "保守控管風險，防止局部破產引發鏈式反應。")

    def get_strategic_conclusions(self, all_flying):
        conclusions = []
        fortune = all_flying.get("福德宮", {})
        if fortune.get("ji_dest") in ["命宮", "財帛宮", "田宅宮"]:
            conclusions.append("【企業文化警報】執行長精神內耗嚴重，福德忌沖命/財，易因焦慮致使決策崩潰。")
        
        spouse = all_flying.get("夫妻宮", {})
        if spouse.get("lu_dest") in ["財帛宮", "福德宮"]:
            conclusions.append("【關鍵併購】伴侶化祿入財/福，是人生最強策略合夥人，能大幅抵銷財務損失執行長的精神內耗。")
            
        wealth = all_flying.get("財帛宮", {})
        if wealth.get("lu_dest") == "田宅宮":
            conclusions.append("【陽升陰降】目前呈現典型『有錢就買房』格局，實體資產能有效鎖住流動性風險。")
        
        if not conclusions:
            conclusions.append("【穩健擴張】當前人生公司各項財務指標運行於標準軌道，建議優化本業現金流。")
            
        return conclusions

    def get_ai_audit(self, audit_data, focused_palace=None, api_key=None):
        """
        [NEW] 使用 Gemini 3 Flash 進行 AI 執行長深度審計
        """
        if not api_key:
            return "❌ 未偵測到 API Key。請在 Streamlit Secrets 或設定中配置 GOOGLE_API_KEY。"

        try:
            genai.configure(api_key=api_key)
            # Using 'gemini-1.5-flash-latest' for better stability and free tier access
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # 構造上下文 (從知識庫文件中提取的核心邏輯)
            context = """
            您是一位專業的紫微斗數大師與「人生公司」首席審計執行長。
            您的邏輯來自於「飛星派」與「欽天派」的財務風控體系。
            
            核心哲學：
            1. 人生 12 宮位是公司的不同部門（命宮為 CEO，財帛為業務，田宅為金庫，福德為企業文化）。
            2. 財富不僅在於賺（化祿），更在於守（田宅）與心態（福德）。
            3. 「陽升陰降」邏輯：利用化祿的優勢去彌補化忌的黑洞。
            
            星性參考：
            - 紫微：統籌全局 / 天機：預測趨勢 / 太陽：公眾影響 / 武曲：精算風險
            - 天同：營造和諧 / 廉貞：危機公關 / 天府：穩健守成 / 太陰：關注細節
            - 貪狼：挖掘欲望 / 巨門：深度剖析 / 天相：協調利益 / 天梁：庇蔭傳承
            - 七殺：鎖定目標 / 破軍：打破常規
            """
            
            # 構造問題
            focus_text = f"目前重點審計宮位：{focused_palace}" if focused_palace else "進行全公司整體財務健康審計"
            prompt = f"""
            {context}
            
            根據以下命盤數據進行深度審計：
            執行長主星：{audit_data['ceo']['star']}
            特質描述：{audit_data['ceo']['description']}
            
            財務部門數據：
            - 業務部(財帛)化祿入：{audit_data['wealth']['lu_dest']} | 化忌入：{audit_data['wealth']['ji_dest']}
            - 金庫部(田宅)化祿入：{audit_data['property']['lu_dest']} | 化忌入：{audit_data['property']['ji_dest']}
            
            {focus_text}
            
            請提供以下內容（使用繁體中文，語氣需專業且具備 CEO 戰略高度）：
            1. 🔍 關係結論：總結此宮位飛星對公司的主要影響。
            2. 📊 深度效應：分析主星特質在該飛星路徑下的動態變化。
            3. 🛡️ 戰略解法：提供 2-3 條具體的「陽升陰降」的操作建議，幫助 CEO 化解風險。
            """
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ AI 審計過程發生錯誤：{str(e)}"

    def get_image_base64(self, file_path):
        """
        將本地圖片轉換為 Base64 字串以供 HTML 渲染
        """
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                data = f.read()
                return base64.b64encode(data).decode()
        return ""

    def get_astrolabe_data(self):
        BRANCH_MAP = {"ziEarthly":0, "chouEarthly":1, "yinEarthly":2, "maoEarthly":3, "chenEarthly":4, "siEarthly":5, "wuEarthly":6, "weiEarthly":7, "shenEarthly":8, "youEarthly":9, "xuEarthly":10, "haiEarthly":11}
        BRANCH_NAME_MAP = {"ziEarthly":"子","chouEarthly":"丑","yinEarthly":"寅","maoEarthly":"卯","chenEarthly":"辰","siEarthly":"巳","wuEarthly":"午","weiEarthly":"未","shenEarthly":"申","youEarthly":"酉","xuEarthly":"戌","haiEarthly":"亥"}
        STEM_MAP = {"jiaHeavenly":"甲","yiHeavenly":"乙","bingHeavenly":"丙","dingHeavenly":"丁","wuHeavenly":"戊","jiHeavenly":"己","gengHeavenly":"庚","xinHeavenly":"辛","renHeavenly":"壬","guiHeavenly":"癸"}
        TRAD_STARS = {
            "紫微":"紫微","天机":"天機","太阳":"太陽","武曲":"武曲","天同":"天同","廉贞":"廉貞",
            "天府":"天府","太阴":"太陰","贪狼":"貪狼","巨门":"巨門","天相":"天相","天梁":"天梁",
            "七杀":"七殺","破军":"破軍","左辅":"左輔","右弼":"右弼","文昌":"文昌","文曲":"文曲",
            "擎羊":"擎羊","陀罗":"陀羅","火星":"火星","铃星":"鈴星","地空":"地空","地劫":"地劫",
            "天魁":"天魁","天钺":"天鉞","祿存":"祿存","禄存":"祿存"
        }
        
        grid = [None] * 12
        for p in self.palaces:
            idx = BRANCH_MAP.get(p.earthly_branch)
            label = self.PALACE_NAME_MAP.get(p.name, p.name)
            major = [TRAD_STARS.get(s.translate_name(), s.translate_name()) for s in p.major_stars]
            all_other = p.minor_stars + p.adjective_stars
            sha_stars_list = ["擎羊", "陀羅", "火星", "鈴星", "地空", "地劫"]
            lucky_stars_list = ["左輔", "右弼", "天魁", "天鉞", "文昌", "文曲"]
            wealth_stars_list = ["祿存"]
            sha_found = []
            lucky_found = []
            wealth_found = []
            minor_found = []
            
            for s in all_other:
                name = TRAD_STARS.get(s.translate_name(), s.translate_name())
                if name in sha_stars_list:
                    sha_found.append(name)
                elif name in lucky_stars_list:
                    lucky_found.append(name)
                elif name in wealth_stars_list:
                    wealth_found.append(name)
                else:
                    if name not in minor_found and name not in major:
                        minor_found.append(name)

            grid[idx] = {
                "name": label,
                "stem": STEM_MAP.get(p.heavenly_stem, p.heavenly_stem),
                "branch": BRANCH_NAME_MAP.get(p.earthly_branch, ""),
                "major_stars": major,
                "minor_stars": minor_found,
                "sha_stars": sha_found,
                "lucky_stars": lucky_found,
                "wealth_stars": wealth_found
            }
        return grid
