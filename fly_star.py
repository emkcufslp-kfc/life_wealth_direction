class ZiWeiSystem:
    """
    Zi Wei Dou Shu Chain Flying Star (連鎖飛化) Diagnosis Engine.
    Based on the 【紫微斗數·全域飛化診斷 SOP】.
    
    This engine decomposes transformation into a 3-step matrix:
    1. Source (發射站): The 'Why' - intention or hazard.
    2. Carrier (能量載體): The 'How' - star DNA and means of action.
    3. Impact (落點效應): The 'Result' - direct impact and the 'Clash' (沖) effect.
    """

    def __init__(self):
        # --- Table A: 發射站 (Source Decoder) ---
        # Defines the root cause of the flying star movement.
        # Lu (祿) represents the proactive intent or talent.
        # Ji (忌) represents the inherent debt, obsession, or potential hazard.
        self.source_rules = {
            "命宮": {"lu": "我主動追求、天賦展現", "ji": "我執著、看不開、自我虧損"},
            "兄弟宮": {"lu": "現金流動、兄弟助力、床位/健康氣位", "ji": "現金卡住、借貸糾紛、身體隱疾"},
            "夫妻宮": {"lu": "配偶幫助、異性緣、在外形象", "ji": "感情債、配偶拖累、婚變風險"},
            "子女宮": {"lu": "合夥順利、投資獲利、晚輩緣、桃花", "ji": "合夥破局、投資虧損、桃花劫、意外"},
            "財帛宮": {"lu": "賺錢行為、錢財流向、賺錢機會", "ji": "財務缺口、錯誤決策、因錢傷感"},
            "疾厄宮": {"lu": "身體本質、潛意識、店面人氣", "ji": "身體病變、心結難解、店面營運差"},
            "遷移宮": {"lu": "出外遇貴人、社會名聲、意外運", "ji": "出外不順、車禍風險、人際孤立"},
            "交友宮": {"lu": "眾生緣、客戶支持、人脈變現", "ji": "小人陷害、損友拖累、人情壓力"},
            "官祿宮": {"lu": "工作模式、運氣擴張、升遷快", "ji": "工作過勞、官司是非、營運危機"},
            "田宅宮": {"lu": "家運興隆、資產增值、財庫儲存", "ji": "家宅不寧、財庫破洞、變賣祖產"},
            "福德宮": {"lu": "精神滿足、興趣獲利、祖德", "ji": "精神焦慮、情緒失控、因興趣敗家"},
            "父母宮": {"lu": "長輩提攜、文書合約、信用良好", "ji": "文書失誤、官非罰單、信用破產"}
        }

        # --- Table B: 能量載體 (Star DNA Matrix) ---
        # Maps the Heavenly Stem of the source palace to the specific Star Transformations.
        # Provides the 'Means' of profit (Lu) and 'Risk Points' (Ji).
        self.stem_rules = {
            "甲": {
                "lu_star": "廉貞", "lu_mean": "精密規劃、桃花人緣、電子科技",
                "ji_star": "太陽", "ji_mean": "男人惹禍、死要面子、公關危機"
            },
            "乙": {
                "lu_star": "天機", "lu_mean": "智慧企劃、頻繁變動、轉手機務",
                "ji_star": "太陰", "ji_mean": "女人受累、房產虧損、情緒憂鬱"
            },
            "丙": {
                "lu_star": "天同", "lu_mean": "服務協調、餐飲享樂、享福財",
                "ji_star": "廉貞", "ji_mean": "血光之災、官司刑罰、行政疏失"
            },
            "丁": {
                "lu_star": "太陰", "lu_mean": "細膩佈局、女性市場、房產財",
                "ji_star": "巨門", "ji_mean": "口舌是非、暗處吃虧、詐欺債務"
            },
            "戊": {
                "lu_star": "貪狼", "lu_mean": "交際應酬、投機偏財、博弈獲利",
                "ji_star": "天機", "ji_mean": "神經衰弱、判斷失誤、鑽牛角尖"
            },
            "己": {
                "lu_star": "武曲", "lu_mean": "實力執行、金融操作、重工業",
                "ji_star": "文曲", "ji_mean": "合約陷阱、支票跳票、文書詐騙"
            },
            "庚": {
                "lu_star": "太陽", "lu_mean": "名氣擴散、公益事業、男性貴人",
                "ji_star": "天同", "ji_mean": "無福消受、心力交瘁、泌尿代謝問題"
            },
            "辛": {
                "lu_star": "巨門", "lu_mean": "口才傳播、專業技術、醫藥法律",
                "ji_star": "文昌", "ji_mean": "文書無效、違約罰單、法規變動"
            },
            "壬": {
                "lu_star": "天梁", "lu_mean": "長輩蔭庇、繼承、保險醫療",
                "ji_star": "武曲", "ji_mean": "資金斷鏈、破產被劫、金屬傷害"
            },
            "癸": {
                "lu_star": "破軍", "lu_mean": "創新突破、破壞建設、流行時尚",
                "ji_star": "貪狼", "ji_mean": "桃花糾紛、縱慾過度、因色敗家"
            }
        }

        # --- Table C: 落點效應 (Impact Matrix) ---
        # Defines the final destination result. 
        # Crucially includes the 'Clash' (沖) effect where the opposite palace is damaged by the Ji star.
        self.palace_order = [
            "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
            "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮"
        ]
       
        self.target_rules = {
            "命宮": {"lu_effect": "資源主動對我好，得利明顯", "ji_effect": "責任壓在身上，心煩意亂", "clash": "遷移宮"},
            "兄弟宮": {"lu_effect": "增加現金流，庫存增值", "ji_effect": "現金卡住，兄弟受累", "clash": "交友宮"},
            "夫妻宮": {"lu_effect": "事業幫助配偶，異性緣增強", "ji_effect": "配偶干擾事業，感情負擔", "clash": "官祿宮"},
            "子女宮": {"lu_effect": "合夥投資順利，桃花多", "ji_effect": "合夥拆夥，子女離心", "clash": "田宅宮"},
            "財帛宮": {"lu_effect": "現金進帳順利，轉速快", "ji_effect": "破財，資金周轉困難", "clash": "福德宮"},
            "疾厄宮": {"lu_effect": "心情愉快，身體好，店面旺", "ji_effect": "身體不適，情緒卡點", "clash": "父母宮"},
            "遷移宮": {"lu_effect": "出外遇貴人，社會評價優", "ji_effect": "在外處處碰壁，意外風險", "clash": "命宮"},
            "交友宮": {"lu_effect": "人脈廣，客戶主動上門", "ji_effect": "朋友欠錢，小人陷害", "clash": "兄弟宮"},
            "官祿宮": {"lu_effect": "工作順利，權力地位提升", "ji_effect": "工作失誤多，容易換工作", "clash": "夫妻宮"},
            "田宅宮": {"lu_effect": "資產增值，家庭和諧，入庫", "ji_effect": "庫存流失，家宅不寧", "clash": "子女宮"},
            "福德宮": {"lu_effect": "精神滿足，財源穩定", "ji_effect": "精神焦慮，大破財(沖財)", "clash": "財帛宮"},
            "父母宮": {"lu_effect": "長輩提攜，文書順利，信用增", "ji_effect": "文書出錯，被長輩責罵", "clash": "疾厄宮"}
        }

    def get_clash_palace(self, target_palace_name):
        """Helper to find the opposite (Clash) palace using the 180-degree rule."""
        try:
            # Handle potential mapping issues
            name = target_palace_name.replace("宮", "") + "宮"
            idx = self.palace_order.index(name)
            clash_idx = (idx + 6) % 12
            return self.palace_order[clash_idx]
        except Exception:
            return "對宮"

    def diagnose_chain(self, source_palace, stem, lu_target_palace, ji_target_palace):
        """
        Generates a comprehensive diagnostic report following the 3-step SOP.
        Returns a dict structured for UI rendering.
        """
        # 1. Validate Core Inputs
        src_name = source_palace.replace("宮", "") + "宮"
        if src_name not in self.source_rules or stem not in self.stem_rules:
            return {"error": f"Invalid inputs: {source_palace}/{stem}"}

        src_data = self.source_rules[src_name]
        stem_data = self.stem_rules[stem]
        
        # 2. Map Destinations (Harden names)
        lu_target = lu_target_palace.replace("宮", "") + "宮"
        ji_target = ji_target_palace.replace("宮", "") + "宮"
        
        lu_impact = self.target_rules.get(lu_target, {})
        ji_impact = self.target_rules.get(ji_target, {})
        
        # Calculate Clash (沖)
        ji_clash_palace = self.get_clash_palace(ji_target)

        # 3. Construct the Modular Diagnosis
        return {
            "source": {
                "name": src_name,
                "stem": stem,
                "msg": f"起因：{src_data['lu']} (祿因) / {src_data['ji']} (忌果)"
            },
            "lu_chain": {
                "star": f"{stem_data['lu_star']}化祿",
                "means": stem_data['lu_mean'],
                "dest": lu_target,
                "effect": lu_impact.get("lu_effect", "現象不明")
            },
            "ji_chain": {
                "star": f"{stem_data['ji_star']}化忌",
                "hazard": stem_data['ji_mean'],
                "dest": ji_target,
                "effect": ji_impact.get("ji_effect", "現象不明"),
                "clash": ji_clash_palace,
                "clash_msg": f"⚠️ 嚴重警報：此忌沖擊『{ji_clash_palace}』，需防範相關範疇崩盤。"
            },
            "advice": f"建議利用『{stem_data['lu_star']}』的{stem_data['lu_mean']}來擴張，但務必截斷『{ji_target}』的{stem_data['ji_mean']}，特別是要保住『{ji_clash_palace}』的底線。"
        }