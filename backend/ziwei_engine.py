# -*- coding: utf-8 -*-
import iztro_py as iztro
import json
import base64
import os
from pathlib import Path

class ZiWeiEngine:
    VERSION_ID = "v6.42-INSTITUTIONAL-HARDENED"
    ROOT_DIR = Path(__file__).parent.parent
    ASSETS_DIR = ROOT_DIR / "assets"
    
    # 欽天門四化配置 (Institutional Ground Truth)
    SI_HUA_MAP_TRAD = {
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

    # Absolute Internal-to-Traditional Star Mapping
    STAR_MAP = {
        "ziweiMaj": "紫微", "tianjiMaj": "天機", "taiyangMaj": "太陽", "wuquMaj": "武曲", 
        "tiantongMaj": "天同", "lianzhenMaj": "廉貞", "tianfuMaj": "天府", "taiyinMaj": "太陰", 
        "tanlangMaj": "貪狼", "jumenMaj": "巨門", "tianxiangMaj": "天相", "tianliangMaj": "天梁", 
        "qishaMaj": "七殺", "pojunMaj": "破軍", "wenchangMin": "文昌", "wenquMin": "文曲", 
        "zuofuMin": "左輔", "youbiMin": "右弼", "tiankuiMin": "天魁", "tianyueMin": "天鉞", 
        "lucunMin": "祿存", "tianmaMin": "天馬", "qingyangMin": "擎羊", "tuoluoMin": "陀羅", 
        "huoxingMin": "火星", "lingxingMin": "鈴星", "dikongMin": "地空", "dijieMin": "地劫"
    }

    # Institutional Star Profiles
    STAR_PROFILES = {
        "紫微": "統籌全局、建立規範、分配資源、引領方向。專案管理在混亂中建立清晰規範，帶領跨部門團隊達成目標。",
        "天機": "拆解複雜資訊、預測趨勢、策劃路徑、優化流程。數據分析開發精準預測模型，找出系統漏洞並提供最優解法。",
        "太陽": "溫暖他人、傳遞理念、照亮盲點、無私奉獻。教育心理學透過渲染力演說啟發潛能，建立高凝聚力社群。",
        "武曲": "果斷執行、精算風險、管理財務、捍衛成果。財務金融在極端壓力下做出精準投資決策，確保資源最大化。",
        "天同": "營造和諧、化解衝突、凝聚共識、傾聽需求。人力資源管理平衡各方矛盾利益，打造具心理安全感的企業文化。",
        "廉貞": "堅持目標、敏銳洞察、建立公關、掌控邊界。危機公關在公關危機時精準洞察大眾心理，以手腕力挽狂瀾。",
        "天府": "守成穩健、構築安全感、穩步擴張、風險控管。營運管理接手搖搖欲墜的專案，透過資源調度使其穩定獲利。",
        "太陰": "關注細節、感受情緒、營造美感、計畫長遠。空間/介面設計捕捉微小情感需求，設計兼具美感與無縫體驗的服務。",
        "貪狼": "建立連結、挖掘欲望、跨界融合、煽動情緒。數位行銷掌握市場潛在慾望，策劃跨界病毒行銷抓住大眾眼球。",
        "巨門": "深度剖析、精準表達、邏輯辯論、直指核心。法律/調查報導抽絲撥繭龐雜資訊，透過嚴密邏輯揭露真相贏得辯論。",
        "天相": "協調利益、維護正義、輔助決策、優化外觀。跨國談判作為絕對中立橋樑協調矛盾，以高品味提升品牌形象。",
        "天梁": "庇蔭他人、傳傳經驗、排解糾紛、制定紀律。醫療照護/顧問在緊急狀態保持冷靜，依經驗制定計畫成為精神支柱。",
        "七殺": "鎖定目標、承擔高風險、獨當一面、不畏權威。新創企業拓展在荒野市場中單槍匹馬殺出重圍，迅速奪下市佔率。",
        "破軍": "打破常規、顛覆體制、破而後立、徹底重組。破壞性產品設計淘汰僵化系統，開發顛覆市場常理的全新破壞性解法。"
    }

    # Earthly Branch Ordering
    BRANCH_ORDER = {
        "ziEarthly": 0, "chouEarthly": 1, "yinEarthly": 2, "maoEarthly": 3,
        "chenEarthly": 4, "siEarthly": 5, "wuEarthly": 6, "weiEarthly": 7,
        "shenEarthly": 8, "youEarthly": 9, "xuEarthly": 10, "haiEarthly": 11
    }

    LUCKY_STARS = {"文昌", "文曲", "左輔", "右弼", "天魁", "天鉞", "祿存", "天馬"}
    SHA_STARS = {"擎羊", "陀羅", "火星", "鈴星", "地空", "地劫"}

    STRATEGIC_SCENARIOS = {
        "soulPalace": {
            "祿": {"inner": "自我滿足、樂觀、有福氣、賺錢主動且輕鬆。", "outer": "待人厚道、廣結善緣、對伴侶/小孩大方。", "sop": "人緣型格，宜建立個人品牌與社交資產。"},
            "權": {"inner": "意志力強、主觀、掌控欲高、對事業積極。", "outer": "霸道、愛管閒事、容易與人發生摩擦。", "sop": "專業領袖型，需注意修飾言辭，避免傲慢。"},
            "科": {"inner": "斯文、講理、重視名聲、情緒平穩。", "outer": "君子之交、處事得體、與家人關係平淡和睦。", "sop": "儒將型，適合靠名聲與專業特許獲利。"},
            "忌": {"inner": "自卑、想不開、自我糾結、勞碌命。", "outer": "欠債格局。對伴侶/朋友執著卻招怨。", "sop": "執著型，必須學習「放下」，切莫自我透支。"}
        },
        "siblingsPalace": {
            "祿": {"inner": "手頭現金充裕、母親或兄弟資助我、家境好。", "outer": "兄弟人際好、母親樂於助人。", "sop": "現金流穩定。適合與親近友合夥。"},
            "權": {"inner": "掌控現金流、兄弟強勢、事業資金調度快。", "outer": "兄弟愛爭權、母親主觀強。", "sop": "槓桿型。注意資金流動性，防範兄弟爭產。"},
            "科": {"inner": "現金儲蓄穩健、手足間明理講禮。", "outer": "兄弟有名聲、關係平淡但有助力。", "sop": "儲蓄型。資金配置以低風險債券為主。"},
            "忌": {"inner": "現金庫破洞、兄弟拖累我、賺錢辛苦。", "outer": "兄弟災多、母親身體差、現金流斷裂。", "sop": "風險型。嚴禁借貸給他人，錢需物隔離。"}
        },
        "spousePalace": {
            "祿": {"inner": "伴侶帶財、婚姻助力大、事業得配偶幫忙。", "outer": "配偶人緣好、感情豐富、易有異性貴人。", "sop": "貴人型感情。宜與另一半共同創業或投資。"},
            "權": {"inner": "配偶能幹且掌控家政、婚姻中爭主導權。", "outer": "配偶在事業上強勢、對外表現欲強。", "sop": "摩擦型感情。需劃分財務與生活權力邊界。"},
            "科": {"inner": "感情細水長流、伴侶有涵養、家世清白。", "outer": "配偶有社會名聲、處事理智。", "sop": "平淡型感情。重視精神契合與文化生活。"},
            "忌": {"inner": "感情債、配偶損我、婚姻是沉重負擔。", "outer": "配偶多意外、感情路坎坷、易遭異性劫。", "sop": "業力型感情。不宜早婚，財務必須獨立。"}
        },
        "childrenPalace": {
            "祿": {"inner": "桃花帶財、合夥事業順利、晚輩孝順。", "outer": "小孩有福、合夥人好相處、性生活和諧。", "sop": "擴張型格局。適合新創投資與教育產業。"},
            "權": {"inner": "子孫有成就、強勢主導合夥項目。", "outer": "小孩霸道、合夥生意競爭激烈。", "sop": "霸權型投資。注意與合夥人的權利平衡。"},
            "科": {"inner": "小孩明理、合夥關係清白、投資有計畫。", "outer": "子女有名望、合夥標的穩健。", "sop": "計畫型投資。以分散風險的小額入股為主。"},
            "忌": {"inner": "投資必敗、合夥觸雷、小孩難管、敗家。", "outer": "小孩身體差、合夥人捲款、桃花劫破財。", "sop": "套牢型格局。終身拒絕非專業合夥與投機。"}
        },
        "wealthPalace": {
            "祿": {"inner": "賺錢極度輕鬆、自帶吸金體質、財源廣。", "outer": "對人大方、用錢買人脈、利潤分享。", "sop": "現金流之王。適合動態獲利與高頻套利。"},
            "權": {"inner": "追求高利潤、掌控財權、敢於重押操作。", "outer": "用錢壓人、商場競爭力極強。", "sop": "槓桿之王。注意風險控制，避免一次爆倉。"},
            "科": {"inner": "財務透明、平穩進帳、靠名聲或執照。", "outer": "理性理財、對金錢態度中庸。", "sop": "專業之財。適合藍籌股、定存與特許收入。"},
            "忌": {"inner": "守財奴、為錢辛苦、錢留不住、財庫破。", "outer": "因錢遭災、被騙、因財起糾紛、損友。", "sop": "錢財之黑洞。改用指數投資，嚴禁情緒交易。"}
        },
        "healthPalace": {
            "祿": {"inner": "心寬體胖、身體健康、宅居舒適。", "outer": "店面興旺、對外形象親切。", "sop": "享受型體質。適合房產收租與健康產業。"},
            "權": {"inner": "體質強悍、爆發力強、店面擴張。", "outer": "勞碌拼命、對外展現強大生命力。", "sop": "勞動力型。注意職業病預防，適合實體店經營。"},
            "科": {"inner": "病有良醫、遺傳好、精神層次高。", "outer": "店面裝修雅致、外在表現斯文。", "sop": "療癒型。適合從事身心靈 or 醫療保健行業。"},
            "忌": {"inner": "體弱、多暗疾、潛意識焦慮、自卑。", "outer": "店面虧損、身體意外受傷、工作場地出事。", "sop": "損耗型。強化保險規劃，避免過度勞累。"}
        },
        "surfacePalace": {
            "祿": {"inner": "出外遇貴人、際遇好、在大眾面前吃香。", "outer": "社會資源豐富、海外發展機遇多。", "sop": "社交型格局。宜離鄉求發展，賺大眾錢。"},
            "權": {"inner": "出外好勝、在外部環境展現競爭力。", "outer": "積極拓展海外版圖、掌控公眾輿論。", "sop": "競爭型格局。適合海外併購、外匯高頻操作。"},
            "科": {"inner": "外出平安、有聲望、給人理智的初印象。", "outer": "海外生活平順、社交圈層次高。", "sop": "形象型格局。靠名氣、學歷或執照在外立足. "},
            "忌": {"inner": "出外水土不服、外在大環境對我不利。", "outer": "海外投資慘賠、出外遭意外、大眾緣差。", "sop": "孤僻型格局。宜安分待在熟悉的環境中發展。"}
        },
        "friendsPalace": {
            "祿": {"inner": "朋友帶財、部屬得力、群眾支持度高。", "outer": "朋友有福、人際關係和諧、資源互助。", "sop": "平台型格局。適合經營流量、粉絲與中介。"},
            "權": {"inner": "朋友/下屬能幹、領導群眾、掌控人際圈。", "outer": "朋友強勢、社交圈多為權貴。", "sop": "領袖型人際。注意與部屬的利益分配。"},
            "科": {"inner": "君子之交、朋友多為專業人士。", "outer": "社交圈清流、人際往來重視禮儀。", "sop": "智庫型人際。適合建立高端諮詢或學者圈。"},
            "忌": {"inner": "損友劫財、部屬背叛、人際關係痛苦。", "outer": "遭詐騙、群眾暴力、被割韭菜、人脈斷。", "sop": "劫難型人際. 不聽明牌、不借錢、不當保人。"}
        },
        "careerPalace": {
            "祿": {"inner": "事業順遂、熱愛工作、容易升遷。", "outer": "工作帶旺家庭、事業對伴侶有益。", "sop": "順境型事業. 宜趁勝追擊，擴大業務版圖。"},
            "權": {"inner": "事業企圖心極大、職場競爭力強、升職快。", "outer": "掌控事業資源、在行業內有話語權。", "sop": "權力型事業. 適合在高壓、高競爭環境生存。"},
            "科": {"inner": "職場名聲好、靠專業立身、工作穩定。", "outer": "業務推展有計畫、事業流程標準化。", "sop": "專業型事業. 適合公職、顧問、審計與教學。"},
            "忌": {"inner": "事業瓶頸、工作勞而無功、套牢事業。", "outer": "失業風險、事業拖累家庭、職場官非。", "sop": "逆境型事業. 轉向輕資產模式，不輕易擴張。"}
        },
        "propertyPalace": {
            "祿": {"inner": "家產豐厚、居家豪華、財入庫能守。", "outer": "家族興旺、女性長輩有助力、祖產增值。", "sop": "財庫型格局. 不動產與黃金是你的守護神。"},
            "權": {"inner": "強勢置產、家中我說了算、家族擴張。", "outer": "房產不斷增值、家族事業掌控力強。", "sop": "霸主型資產. 適合房地產開發、高槓桿收房。"},
            "科": {"inner": "家教好、居家環境幽雅、資產平穩。", "outer": "家族聲望佳、房產產權清晰。", "sop": "文雅型資產. 房產配置以學區、穩健地段為主. "},
            "忌": {"inner": "房產套牢、家宅不寧、現金流枯竭、敗產。", "outer": "家道中落、房屋漏水糾紛、資產流動性死。", "sop": "破耗型資產. 保留足夠現金，慎防因家損財。"}
        },
        "spiritPalace": {
            "祿": {"inner": "精神愉悅、偏財運極佳、福報深厚。", "outer": "享受人生、與大眾共享福報、大方。", "sop": "福報型格局. 相信直覺，適合感性驅動投資。"},
            "權": {"inner": "意志強悍、主觀意識強、追求精神成就。", "outer": "掌控個人慾望、強迫自己達成目標。", "sop": "執念型格局. 馬拉松是你的救贖，意志即金錢。"},
            "科": {"inner": "修養極好、理性平衡、有高雅興趣。", "outer": "精神層次高、處事有分寸、受人尊敬。", "sop": "理智型格局. 適合宗教、藝術 or 哲學研究。"},
            "忌": {"inner": "焦慮症、想不開、精神虐待、損福報。", "outer": "極端偏激、因興趣大破財、潛意識創傷。", "sop": "業力型精神. 強制轉移注意力，嚴禁主觀重押。"}
        },
        "parentsPalace": {
            "祿": {"inner": "長輩疼愛、得體制內資源、父母有福。", "outer": "與政府關係好、易得銀行信貸、合約順。", "sop": "背景型格局. 適合賺體制內的錢、政府標案。"},
            "權": {"inner": "挑戰威權、對長輩強勢、想主導體制。", "outer": "長輩強勢、受制於嚴苛的法規。", "sop": "衝突型體質. 注意言行，避免觸碰法律紅線. "},
            "科": {"inner": "長輩緣佳、求學順遂、合約文書平順。", "outer": "父母有名望、信譽度極高、合規性好。", "sop": "信用型格局. 適合金融、保險、法律與考公。"},
            "忌": {"inner": "與長輩代溝、受體制打壓、文書官非。", "outer": "父母多難、銀行抽銀根、合約漏洞、罰單。", "sop": "文書型災難. 簽約必請律師，合法納稅。"}
        }
    }

    CEO_IMAGES = {
        "紫微": "zi_wei_emperor.png", "天機": "tian_ji_strategist.png", "太陽": "tai_yang_sun.png",
        "武曲": "wu_qu_executor.png", "天同": "tian_tong_harmonizer.png", "廉貞": "lian_zhen_crisis_pr.png",
        "天府": "tian_fu_treasurer.png", "太陰": "tai_yin_designer.png", "貪狼": "tan_lang_marketer.png",
        "巨門": "ju_men_truth_seeker.png", "天相": "tian_xiang_negotiator.png", "天梁": "tian_liang_protector.png",
        "七殺": "qi_sha_conqueror.png", "破軍": "po_jun_rebel.png"
    }

    def __init__(self, year, month, day, hour, is_lunar=False, gender="男"):
        self.gender_str = '男' if gender in ["男", "male"] else '女'
        solar_date = f"{year}-{month}-{day}"
        if is_lunar:
            self.astro = iztro.by_lunar(solar_date, hour, self.gender_str)
        else:
            self.astro = iztro.by_solar(solar_date, hour, self.gender_str)
        print(f"[{self.VERSION_ID}] ZiWeiEngine Initialized for {solar_date}")

    def _translate(self, star):
        return self.STAR_MAP.get(star.name, star.translate_name())

    def _get_branch_idx(self, p):
        return self.BRANCH_ORDER.get(p.earthly_branch, 0)

    def get_image_base64(self, image_name):
        """Unified image loader for star names and direct files (png/jpg)."""
        if not image_name: return ""
        
        # 1. Check if it's already a filename or a star name
        is_direct_file = any(image_name.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"])
        filename = image_name if is_direct_file else self.CEO_IMAGES.get(image_name, "")
        
        # 2. Path Resolution
        path = self.ASSETS_DIR / filename if filename else None
        
        # 3. Last Resort Fallback (search by star name in CEO_IMAGES if image_name had an extension but was a star)
        if not path or not path.exists():
            clean_name = image_name.split(".")[0]
            filename_alt = self.CEO_IMAGES.get(clean_name, "")
            if filename_alt:
                path = self.ASSETS_DIR / filename_alt
        
        if not path or not path.exists():
            print(f"[ERROR] Asset not found: {image_name} -> {filename}")
            return ""
        
        # 4. MIME determination
        ext = path.suffix.lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        
        try:
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                print(f"[DEBUG] Loaded Asset: {image_name} as {path.name} ({len(b64)} bytes)")
                return f"data:{mime};base64,{b64}"
        except Exception as e:
            print(f"[ERROR] Failed to load {path}: {e}")
            return ""

    def get_astrolabe_data(self):
        res = {}
        for p in self.astro.palaces:
            b_idx = self._get_branch_idx(p)
            all_stars = p.major_stars + p.minor_stars + p.adjective_stars
            major_names = [self._translate(s) for s in p.major_stars]
            lucky_names = [self._translate(s) for s in all_stars if self._translate(s) in self.LUCKY_STARS]
            sha_names = [self._translate(s) for s in all_stars if self._translate(s) in self.SHA_STARS]
            res[b_idx] = {
                "name": p.translate_name(), "stem": p.translate_heavenly_stem(),
                "major_stars": major_names, "lucky_stars": lucky_names, "sha_stars": sha_names,
                "lucky_stars_ext": lucky_names, "sha_stars_ext": sha_names
            }
        return res

    def get_innate_distribution(self):
        y_stem = self.astro.chinese_date[0]
        y_map = self.SI_HUA_MAP_TRAD.get(y_stem)
        res = {"stem": y_stem, "logic": y_map["logic"], "stars": {}}
        for key in ["祿", "權", "科", "忌"]:
            target_star = y_map[key]
            for p in self.astro.palaces:
                all_stars = [self._translate(s) for s in p.major_stars + p.minor_stars + p.adjective_stars]
                if target_star in all_stars:
                    res["stars"][key] = {"star": target_star, "palace": p.name}
        return res

    def get_wealth_audit(self):
        soul_p = [p for p in self.astro.palaces if p.name == "soulPalace"][0]
        soul_stars = [self._translate(s) for s in soul_p.major_stars] if soul_p.major_stars else ["紫微"]
        innate_dist = self.get_innate_distribution()
        soul_idx = self._get_branch_idx(soul_p)
        wealth_p = [p for p in self.astro.palaces if p.name == "wealthPalace"][0]
        wealth_stars = [self._translate(s) for s in wealth_p.major_stars] if wealth_p.major_stars else ["武曲"]
        wealth_idx = self._get_branch_idx(wealth_p)
        property_p = [p for p in self.astro.palaces if p.name == "propertyPalace"][0]
        property_stars = [self._translate(s) for s in property_p.major_stars] if property_p.major_stars else ["天府"]
        property_idx = self._get_branch_idx(property_p)
        
        return {
            "ceo": {"star": " / ".join(soul_stars), "image": soul_stars[0], "profiles": [{"star": s, "desc": self.STAR_PROFILES.get(s, "")} for s in soul_stars]},
            "innate": {"stem": self.astro.chinese_date[0], "stars": innate_dist["stars"]},
            "soul": {"stars": soul_stars, "profiles": [{"star": s, "desc": self.STAR_PROFILES.get(s, "")} for s in soul_stars], "layer2": {"lu": {"dest": self.f_dest_by_branch(soul_idx, "祿")}, "ji": {"dest": self.f_dest_by_branch(soul_idx, "忌")}}},
            "wealth": {"stars": wealth_stars, "profiles": [{"star": s, "desc": self.STAR_PROFILES.get(s, "")} for s in wealth_stars], "layer2": {"lu": {"dest": self.f_dest_by_branch(wealth_idx, "祿")}, "ji": {"dest": self.f_dest_by_branch(wealth_idx, "忌")}}},
            "property": {"stars": property_stars, "profiles": [{"star": s, "desc": self.STAR_PROFILES.get(s, "")} for s in property_stars], "layer2": {"lu": {"dest": self.f_dest_by_branch(property_idx, "祿")}, "ji": {"dest": self.f_dest_by_branch(property_idx, "忌")}}}
        }

    def f_dest_by_branch(self, b_idx, target_type):
        source_p = next(p for p in self.astro.palaces if self._get_branch_idx(p) == b_idx)
        stem = source_p.translate_heavenly_stem()
        target_star = self.SI_HUA_MAP_TRAD[stem][target_type]
        for dp in self.astro.palaces:
            d_stars = [self._translate(s) for s in dp.major_stars + dp.minor_stars + dp.adjective_stars]
            if target_star in d_stars: return dp.translate_name()
        return "未知"

    def fly_all_palaces(self):
        res = {}
        for p in self.astro.palaces:
            b_idx = self._get_branch_idx(p)
            stem = p.translate_heavenly_stem()
            y_map = self.SI_HUA_MAP_TRAD[stem]
            res[b_idx] = {
                "name": p.translate_name(), "stem": stem,
                "lu_star": y_map["祿"], "ji_star": y_map["忌"],
                "lu_dest": self.f_dest_by_branch(b_idx, "祿"),
                "ji_dest": self.f_dest_by_branch(b_idx, "忌"),
                "logic": y_map["logic"],
                "collision": f"獲利鏈條延伸至 {self.f_dest_by_branch(b_idx, '祿')}，同步防範 {self.f_dest_by_branch(b_idx, '忌')} 的風險傳導。"
            }
        return res

    def get_innate_audit(self):
        dist = self.get_innate_distribution()["stars"]
        res = []
        # Mapping from name back to display for header
        display_map = {
            "soulPalace": "命宮", "siblingsPalace": "兄弟宮", "spousePalace": "夫妻宮",
            "childrenPalace": "子女宮", "wealthPalace": "財帛宮", "healthPalace": "疾厄宮",
            "surfacePalace": "遷移宮", "friendsPalace": "交友宮", "careerPalace": "官祿宮",
            "propertyPalace": "田宅宮", "spiritPalace": "福德宮", "parentsPalace": "父母宮"
        }
        for t, d in dist.items():
            internal_p_name = d['palace']
            palace_display = display_map.get(internal_p_name, "未知宮位")
            star_name = d['star']
            
            # Scenario Lookup
            scenario = self.STRATEGIC_SCENARIOS.get(internal_p_name, {}).get(t, {})
            is_inner = internal_p_name in {"soulPalace", "wealthPalace", "healthPalace", "careerPalace", "propertyPalace", "spiritPalace"}
            
            meaning = scenario.get("sop", "待定策略位")
            impact = scenario.get("inner" if is_inner else "outer", "待定影響位")
            
            res.append({
                "header": f"【生年化{t} ➔ {star_name} ({palace_display})】",
                "palace_def": f"這顆星曜在此宮位代表您一生中最核心的『{t}』之氣。",
                "meaning": f"**深層意義**: {meaning}",
                "impact": f"**具體影響**: {impact}"
            })
        return res
