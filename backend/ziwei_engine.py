import iztro_py as iztro
import json
import base64
import os
from pathlib import Path

class ZiWeiEngine:
    VERSION_ID = "v6.34-DYNAMIC-AUDIT"
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

    # Institutional Star Profiles (HK Comic Style Strategic Narratives)
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
        "巨門": "深度剖析、精準表達、邏輯辯論、直指核心。法律/調查報導抽絲剝繭龐雜資訊，透過嚴密邏輯揭露真相贏得辯論。",
        "天相": "協調利益、維護正義、輔助決策、優化外觀。跨國談判作為絕對中立橋樑協調矛盾，以高品味提升品牌形象。",
        "天梁": "庇蔭他人、傳承經驗、排解糾紛、制定紀律。醫療照護/顧問在緊急狀態保持冷靜，依經驗制定計畫成為精神支柱。",
        "七殺": "鎖定目標、承擔高風險、獨當一面、不畏權威。新創企業拓展在荒野市場中單槍匹馬殺出重圍，迅速奪下市佔率。",
        "破軍": "打破常規、顛覆體制、破而後立、徹底重組。破壞性產品設計淘汰僵化系統，開發顛覆市場常理的全新破壞性解法。"
    }

    # Earthly Branch Ordering (0 = 子, 1 = 丑 ... 11 = 亥)
    BRANCH_ORDER = {
        "ziEarthly": 0, "chouEarthly": 1, "yinEarthly": 2, "maoEarthly": 3,
        "chenEarthly": 4, "siEarthly": 5, "wuEarthly": 6, "weiEarthly": 7,
        "shenEarthly": 8, "youEarthly": 9, "xuEarthly": 10, "haiEarthly": 11
    }

    LUCKY_STARS = {"文昌", "文曲", "左輔", "右弼", "天魁", "天鉞", "祿存", "天馬"}
    SHA_STARS = {"擎羊", "陀羅", "火星", "鈴星", "地空", "地劫"}

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
        # Allow .png, .jpg, .jpeg extensions directly
        is_direct_file = any(image_name.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"])
        filename = image_name if is_direct_file else self.CEO_IMAGES.get(image_name, "")
        
        if not filename: return ""
        path = self.ASSETS_DIR / filename
        if not path.exists(): return ""
        
        # Determine mime type
        ext = path.suffix.lower()
        mime = "image/png"
        if ext in [".jpg", ".jpeg"]: mime = "image/jpeg"
        
        with open(path, "rb") as f:
            b64_str = base64.b64encode(f.read()).decode()
            return f"data:{mime};base64,{b64_str}"

    def get_astrolabe_data(self):
        """Returns astrolabe data indexed by Earthly Branch (0-11)."""
        res = {}
        for p in self.astro.palaces:
            b_idx = self._get_branch_idx(p)
            all_stars = p.major_stars + p.minor_stars + p.adjective_stars
            major_names = [self._translate(s) for s in p.major_stars]
            lucky_names = [self._translate(s) for s in all_stars if self._translate(s) in self.LUCKY_STARS]
            sha_names = [self._translate(s) for s in all_stars if self._translate(s) in self.SHA_STARS]
            
            res[b_idx] = {
                "name": p.translate_name(),
                "stem": p.translate_heavenly_stem(),
                "major_stars": major_names,
                "lucky_stars": lucky_names,
                "sha_stars": sha_names,
                "lucky_stars_ext": lucky_names,
                "sha_stars_ext": sha_names
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
                    res["stars"][key] = {"star": target_star, "palace": p.translate_name()}
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
        """Calculates flying star destination starting from a specific branch index."""
        source_p = next(p for p in self.astro.palaces if self._get_branch_idx(p) == b_idx)
        stem = source_p.translate_heavenly_stem()
        target_star = self.SI_HUA_MAP_TRAD[stem][target_type]
        for dp in self.astro.palaces:
            d_stars = [self._translate(s) for s in dp.major_stars + dp.minor_stars + dp.adjective_stars]
            if target_star in d_stars: return dp.translate_name()
        return "未知"

    def fly_all_palaces(self):
        """Returns flying star data indexed by Earthly Branch (0-11)."""
        res = {}
        for p in self.astro.palaces:
            b_idx = self._get_branch_idx(p)
            stem = p.translate_heavenly_stem()
            y_map = self.SI_HUA_MAP_TRAD[stem]
            lu_dest = self.f_dest_by_branch(b_idx, "祿")
            ji_dest = self.f_dest_by_branch(b_idx, "忌")
            res[b_idx] = {
                "name": p.translate_name(), "stem": stem,
                "lu_star": y_map["祿"], "ji_star": y_map["忌"],
                "lu_dest": lu_dest, "ji_dest": ji_dest,
                "logic": y_map["logic"],
                "collision": f"獲利鏈條延伸至 {lu_dest}，同步防範 {ji_dest} 的風險傳導。"
            }
        return res

    def get_innate_audit(self):
        dist = self.get_innate_distribution()["stars"]
        res = []
        for t, d in dist.items():
            res.append({
                "header": f"【生年化{t} ➔ {d['star']} ({d['palace']})】",
                "palace_def": f"這顆星曜在此宮位代表您一生中最核心的『{t}』之氣。",
                "meaning": "資源啟動位" if t == "祿" else "風險結點位",
                "impact": "聚焦此位獲利" if t == "祿" else "守護此位風控"
            })
        return res
