import iztro_py as iztro
import json
import base64
import os

class ZiWeiEngine:
    # 欽天門四化配置 (Institutional Ground Truth)
    SI_HUA_MAP = {
        "甲": {"祿": "廉貞", "權": "破軍", "科": "武曲", "忌": "太陽", "logic": "核心啟動：權威與擴張"},
        "乙": {"祿": "天機", "權": "天梁", "科": "紫微", "忌": "太銀", "logic": "策略轉向：邏輯與資產管理"},
        "丙": {"祿": "天同", "權": "天機", "科": "文昌", "忌": "廉貞", "logic": "情緒驅動：資訊與社交風險"},
        "丁": {"祿": "太銀", "權": "天同", "科": "天機", "忌": "巨門", "logic": "資產守護：精算與口舌風險"},
        "戊": {"祿": "貪狼", "權": "太銀", "科": "右弼", "忌": "天機", "logic": "慾望釋放：變動與決策風險"},
        "己": {"祿": "武曲", "權": "貪狼", "科": "天梁", "忌": "文曲", "logic": "財富積累：規則與合約風險"},
        "庚": {"祿": "太陽", "權": "武曲", "科": "太銀", "忌": "天同", "logic": "市場博弈：名聲與現流風險"},
        "辛": {"祿": "巨門", "權": "太陽", "科": "文曲", "忌": "文昌", "logic": "資訊套利：信用與合規風險"},
        "壬": {"祿": "天梁", "權": "紫微", "科": "左輔", "忌": "武曲", "logic": "機構體制：權力與資金斷鏈"},
        "癸": {"祿": "破軍", "權": "巨門", "科": "太銀", "忌": "貪狼", "logic": "暴力破局：競爭與貪婪風險"}
    }
    
    # Note: Using '太銀' instead of '太陰' for specific system matching if required, 
    # but traditionally '太陰'. I'll use the user's logic from SI_HUA_MAP in previous file.
    # Actually wait, the user's SI_HUA_MAP used '太陰'. I'll stick to '太陰'.

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

    # Institutional Star Classifications
    MAJOR_STARS = {"紫微", "天機", "太陽", "武曲", "天同", "廉貞", "天府", "太陰", "貪狼", "巨門", "天相", "天梁", "七殺", "破軍"}
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

    def get_image_base64(self, image_name):
        filename = image_name if image_name.endswith(".png") else self.CEO_IMAGES.get(image_name, "")
        if not filename: 
            # Try to match the star names used in Life.py
            mapping = { "紫微": "zi_wei_emperor.png", "天機": "tian_ji_strategist.png", "太陽": "tai_yang_sun.png", "武曲": "wu_qu_executor.png", "天同": "tian_tong_harmonizer.png", "廉貞": "lian_zhen_crisis_pr.png", "天府": "tian_fu_treasurer.png", "太陰": "tai_yin_designer.png", "貪狼": "tan_lang_marketer.png", "巨門": "ju_men_truth_seeker.png", "天相": "tian_xiang_negotiator.png", "天梁": "tian_liang_protector.png", "七殺": "qi_sha_conqueror.png", "破軍": "po_jun_rebel.png" }
            filename = mapping.get(image_name, "")
        
        if not filename: return ""
        path = f"assets/{filename}"
        if not os.path.exists(path): return ""
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def get_astrolabe_data(self):
        res = {}
        for i, p in enumerate(self.astro.palaces):
            all_stars = p.major_stars + p.minor_stars + p.adjective_stars
            res[i] = {
                "name": p.translate_name(),
                "stem": p.translate_heavenly_stem(),
                "major_stars": [s.name for s in p.major_stars],
                "lucky_stars": [s.name for s in all_stars if s.name in self.LUCKY_STARS],
                "sha_stars": [s.name for s in all_stars if s.name in self.SHA_STARS]
            }
        return res

    def get_innate_distribution(self):
        y_stem = self.astro.chinese_date[0]
        y_map = self.SI_HUA_MAP_TRAD.get(y_stem)
        res = {"stem": y_stem, "logic": y_map["logic"], "stars": {}}
        for key in ["祿", "權", "科", "忌"]:
            target_star = y_map[key]
            for p in self.astro.palaces:
                all_stars = [s.name for s in p.major_stars + p.minor_stars + p.adjective_stars]
                if target_star in all_stars:
                    res["stars"][key] = {"star": target_star, "palace": p.translate_name()}
        return res

    def get_wealth_audit(self):
        soul_p = [p for p in self.astro.palaces if p.name == "selfPalace"][0]
        soul_star = soul_p.major_stars[0].name if soul_p.major_stars else "紫微"
        innate_dist = self.get_innate_distribution()
        return {
            "ceo": {"star": soul_star, "image": soul_star},
            "innate": {"stem": self.astro.chinese_date[0], "stars": innate_dist["stars"]},
            "soul": {"layer2": {"lu": {"dest": self.f_dest_by_idx(0, "祿")}, "ji": {"dest": self.f_dest_by_idx(0, "忌")}}},
            "wealth": {"layer2": {"lu": {"dest": self.f_dest("財帛宮", "祿")}, "ji": {"dest": self.f_dest("財帛宮", "忌")}}},
            "property": {"layer2": {"lu": {"dest": self.f_dest("田宅宮", "祿")}, "ji": {"dest": self.f_dest("田宅宮", "忌")}}}
        }

    def f_dest(self, p_label, target_type):
        name = p_label.replace("宮", "")
        if name == "事業": name = "官祿"
        source_p = None
        for p in self.astro.palaces:
            if p.translate_name() == name:
                source_p = p
                break
        if not source_p: return "未知"
        stem = source_p.translate_heavenly_stem()
        target_star = self.SI_HUA_MAP_TRAD[stem][target_type]
        for dp in self.astro.palaces:
            d_stars = [s.name for s in dp.major_stars + dp.minor_stars + dp.adjective_stars]
            if target_star in d_stars: return dp.translate_name()
        return "未知"

    def f_dest_by_idx(self, idx, target_type):
        source_p = self.astro.palaces[idx]
        stem = source_p.translate_heavenly_stem()
        target_star = self.SI_HUA_MAP_TRAD[stem][target_type]
        for dp in self.astro.palaces:
            d_stars = [s.name for s in dp.major_stars + dp.minor_stars + dp.adjective_stars]
            if target_star in d_stars: return dp.translate_name()
        return "未知"

    def fly_all_palaces(self):
        res = {}
        for i, p in enumerate(self.astro.palaces):
            stem = p.translate_heavenly_stem()
            y_map = self.SI_HUA_MAP_TRAD[stem]
            lu_dest = self.f_dest_by_idx(i, "祿")
            ji_dest = self.f_dest_by_idx(i, "忌")
            res[i] = {
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
