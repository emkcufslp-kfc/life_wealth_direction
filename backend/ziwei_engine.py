# -*- coding: utf-8 -*-
import iztro_py as iztro
import json
import base64
import os
from pathlib import Path

class ZiWeiEngine:
    VERSION_ID = "v6.43-INSTITUTIONAL-HARDENED"
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

    # Palace Name Mapping (Institutional Standard)
    PALACE_NAME_MAP = {
        "soulPalace": "命宮", "siblingsPalace": "兄弟宮", "spousePalace": "夫妻宮",
        "childrenPalace": "子女宮", "wealthPalace": "財帛宮", "healthPalace": "疾厄宮",
        "surfacePalace": "遷移宮", "friendsPalace": "交友宮", "careerPalace": "官祿宮",
        "propertyPalace": "田宅宮", "spiritPalace": "福德宮", "parentsPalace": "父母宮"
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
            "祿": {"inner": "自得其樂、自我滿足、樂觀有福。將愛與關注留給自己，建立個人品牌與社交資產。", "outer": "待人厚道、廣結善緣、對伴侶/小孩大方。宜透過名聲與專業特許獲利。", "sop": "人緣型格，宜建立個人品牌。能量的擴張點在於『自我完善』。"},
            "權": {"inner": "意志力強、極度主觀、追求掌控。將強壓能量作用於自身，展現領袖特質但也帶來壓力。", "outer": "霸道好勝、干涉伴侶、與人有磨。需注意修飾言辭，避免傲慢。", "sop": "專業領袖型。能量的擴張點在於『意志掌控』。"},
            "科": {"inner": "斯文講理、惜毛如金、情緒平穩。能量梳理得宜，給人理智初印象。", "outer": "君子之交、處事得體。靠名聲、學歷或執照立足。", "sop": "儒將型。能量的擴張點在於『名聲傳播』。"},
            "忌": {"inner": "執著、自尋煩惱、精神焦慮、對自己不滿。欠債格局，必須學習「放下」，切莫自我透支。", "outer": "對伴侶/朋友執著卻招怨。人生的業障點在於『自我糾結』。", "sop": "執著型時，內心負擔重。能量的黑洞在於『精神磨損』。解法是將關注點移向外部事物。"}
        },
        "siblingsPalace": {
            "祿": {"inner": "手頭現金充裕、現金庫穩健、家境好。能量向內部輸送，適合與人合夥。", "outer": "兄弟/母親疼愛我、手足人緣佳。透過親近友人的資源增長。", "sop": "現金流之庫。能量擴張在於『內部流動性』。"},
            "權": {"inner": "掌控現金流、資金調度極快。在資金分配上有絕對話語權。", "outer": "兄弟強勢、掌控家政、易生爭端。注意與手足間的利益分配。", "sop": "槓桿之庫。能量強壓在於『資金配置』。"},
            "科": {"inner": "現金儲蓄穩健、帳目清晰。能量梳理平順，重視資金安全。", "outer": "兄弟有名聲、關係平淡和睦。透過穩定的信用獲利。", "sop": "智庫之庫。能量梳理在於『守成穩健』。"},
            "忌": {"inner": "現金庫破洞、錢留不住、賺錢辛苦。嚴禁借貸給他人，錢需物隔離。", "outer": "兄弟拖累我、長輩多災。能量的黑洞在於『現金斷鏈』。", "sop": "風險之庫。能量黑洞在於『信貸危機』。注意與平輩間的財務邊界。"}
        },
        "spousePalace": {
            "祿": {"inner": "伴侶帶財、婚姻助力大、事業得配偶幫。將愉悅能量帶入感情，婚姻是資源輸送帶。", "outer": "配偶人緣好、感情豐富、易有異性貴人。宜與另一半共同創業。", "sop": "貴人型感情。能量擴張在於『親密連結』。"},
            "權": {"inner": "配偶能幹、掌控家政、婚姻競爭。配偶干涉我的事業，需劃分財務邊界。", "outer": "配偶在事業上強勢、對外表現欲強。需注意婚姻中的主導權摩擦。", "sop": "磨合型感情。能量強壓在於『權力分配』。"},
            "科": {"inner": "感情細水長流、伴侶明理講禮。重視精神契合與文化生活，關係平穩。", "outer": "配偶有聲望、處事理智。以名聲或專業特許作為婚姻紐帶。", "sop": "理智型感情。能量梳理在於『精神契合』。"},
            "忌": {"inner": "感情債、配偶損我、婚姻是沉重負擔。對伴侶執著卻招怨，財務必須獨立。", "outer": "配偶多意外、感情路坎坷。能量的黑洞在於『業力情感』。", "sop": "業力型感情。能量黑洞在於『執念沉重』。不宜早婚，需在心態成熟後再進入關係。"}
        },
        "childrenPalace": {
            "祿": {"inner": "合夥事業順利、資金擴張、晚輩孝順。能量向外發散，適合新創投資與教育業。", "outer": "桃花帶財、合夥人好相處。利用外部連結獲利，過程愉悅受惠。", "sop": "擴張型投資。能量擴張在於『外部合作』。"},
            "權": {"inner": "強勢主導合夥項目、子孫有成就。在外部競爭中展現霸氣，掌控投資標的。", "outer": "合夥生意競爭激烈、小孩霸道。注意與合夥人的權利平衡。", "sop": "競爭型投資. 能量強壓在於『專案壟斷』。"},
            "科": {"inner": "合夥關係清白、投資有計畫、晚輩明理。計畫性推展業務，重視規章制度。", "outer": "子女有名望、合夥標的穩健。以分散風險的小額入股為主。", "sop": "計畫型投資. 能量梳理在於『流程合規』。"},
            "忌": {"inner": "投資必敗、合夥觸雷、敗家子、敗產。能量黑洞在此，嚴禁非專業合夥與投機。", "outer": "小孩難教、因桃花劫破財。人生的業障點在於『盲目投資』。", "sop": "黑洞型投資. 能量黑洞在於『資金套牢』。終身拒絕非專業合夥與高頻投機。"}
        },
        "wealthPalace": {
            "祿": {"inner": "自帶吸金體質、賺錢輕鬆、財源廣。將愛與關注投入求財，現金流動向良好。", "outer": "對人大方、用錢買人脈、利潤分享。適合動態獲利與高頻套利。", "sop": "現金流之王. 能量擴張在於『賺錢手段』。"},
            "權": {"inner": "追求高利潤、掌控財權、敢於重押。財務高槓桿，在商場競爭力極強。", "outer": "用錢壓人、商場競爭白熱化。注意風險控制，避免一次爆倉。", "sop": "槓桿之王. 能量強壓在於『利潤獲取』。"},
            "科": {"inner": "理財平穩、正式收入、靠專業賺錢。理財態度理性中庸，帳目清晰透明。", "outer": "靠名聲賺錢、理財計畫完善。適合藍籌股、定存與特許收入。", "sop": "專業之財. 能量梳理在於『理財秩序』。"},
            "忌": {"inner": "守財奴、為錢辛苦、錢留不住、財庫破。為錢苦惱反被錢困，必須改用指數投資。", "outer": "因錢遭災、因財起糾紛、損友。能量的黑洞在於『金錢焦慮』。", "sop": "黑洞型財富. 能量黑洞在於『現金流失』。嚴禁情緒化交易，建議採用自動化理財。"}
        },
        "healthPalace": {
            "祿": {"inner": "樂觀發福、身體健康、宅居舒適。享受人生，能量在肉體與潛意識中愉悅擴張。", "outer": "店面興旺、對外形象親切. 適合從事房產收租與健康產業。", "sop": "享受型體質. 能量擴張在於『身體感官』。"},
            "權": {"inner": "生命力強悍、抗壓性高、勞碌拼命。將強壓能量作用於肉體，爆發力極強。", "outer": "店面擴張、展現強大影響力. 注意職業病預防，適合硬核勞動力。", "sop": "強健型體質. 能量強壓在於『抗壓能力』。"},
            "科": {"inner": "遇病有良醫、精神層次高、修養好。能量梳理得宜，給人平和穩定的初象。", "outer": "醫護朋友多、外在斯文。適合與醫療保健、身心靈產業連結。", "sop": "療癒型體質. 能量梳理在於『情緒調節』。"},
            "忌": {"inner": "體弱多病、潛意識創傷、重度焦慮. 黑洞在肉體中，強化保險規劃，嚴禁過勞。", "outer": "店面虧損、工作場地出事。人生的業障點在於『病灶纏身』。", "sop": "損耗型體質. 能量黑洞在於『能量透支』。加強預防醫學，避免長期高壓環境。"}
        },
        "surfacePalace": {
            "祿": {"inner": "出外遇貴人、際遇好、在大眾前吃香。在社會環境中擴張人緣，適合遠方財。", "outer": "社會資源豐富、海外機遇多。宜離鄉發展，建立廣泛的社交網。", "sop": "社交型格局. 能量擴張在於『外部機遇』。"},
            "權": {"inner": "在外好勝、展現競爭力、掌控輿論。強勢進軍外部市場，積極拓展板圖。", "outer": "海外併購、外匯高頻操作. 注意法律合規，避免過度擴張招忌。", "sop": "競爭型格局. 能量強壓在於『社會地位』。"},
            "科": {"inner": "在外平安有聲望、給人理智印象。靠名氣、學歷 or 執照在外立足，生活平順。", "outer": "海外生活優雅、社交圈層次高。重視外在形象與專業信用。", "sop": "形象型格局. 能量梳理在於『專業信用』。"},
            "忌": {"inner": "出外水土不服、海外投資慘賠。環境對我不利，能量黑洞在外部際遇中。", "outer": "海外災多、大眾緣差、遭意外。宜安分待在熟悉的環境中發展。", "sop": "孤僻型格局. 能量黑洞在於『外部受挫』。外出必備保險，且不輕易移居他鄉。"}
        },
        "friendsPalace": {
            "祿": {"inner": "朋友帶財、部屬得力、群眾支持。在人際交往中獲得愉悅，適合經營平台流量。", "outer": "朋友有福、資源互助、社交廣。利用外部連結獲利，建立利潤分成機制。", "sop": "平台型格局. 能量擴張在於『人際動能』。"},
            "權": {"inner": "朋友強勢能幹、領導群眾、掌控人脈。在社交圈中展現強大影響力，主導關係。", "outer": "社交圈多權貴、高壓管理群眾. 注意與部屬的利益分配與摩擦。", "sop": "領袖型人際. 能量強壓在於『群眾掌控』。"},
            "科": {"inner": "君子之交、朋友圈層次高、重視禮儀。能量梳理有序，適合建立高階諮詢圈。", "outer": "社交圈清流、人際往來合規. 靠口碑與專業人脈進行資源對接。", "sop": "智庫型人際. 能量梳理在於『人脈品質』。"},
            "忌": {"inner": "損友劫財、部屬背叛、人際痛苦。黑洞 in 人際關係中，嚴禁借錢給朋友或擔保。", "outer": "遭詐騙、群眾暴力、被割韭菜。人生的業障點在於『人情債務』。", "sop": "劫難型人際. 能量黑洞在於『人脈斷裂』。不聽明牌、不借錢、不當保人。"}
        },
        "careerPalace": {
            "祿": {"inner": "熱愛工作、事業順遂、極易變現。將核心動機投入事業，享受擴張的過程。", "outer": "事業帶旺家庭、對伴侶有益。適合多元化發展，擴大業務版圖。", "sop": "順境型事業. 能量擴張在於『業務開發』。"},
            "權": {"inner": "企圖心強、職場競爭力極高、掌控權。在專業領域內強勢爭奪資源，追求成就。", "outer": "掌控事業話語權、競爭對手強大. 適合在高壓、高競爭環境生存。", "sop": "權力型事業. 能量強壓在於『市場市佔』。"},
            "科": {"inner": "職場名聲好、靠專業立身、流程標準。注重名聲與合規，適合諮詢或教育產業。", "outer": "業務推展有計畫、合約平穩。靠執照、證照 or 專業形象獲利。", "sop": "專業型事業. 能量梳理在於『標準規章』。"},
            "忌": {"inner": "事業瓶頸、工作勞而無功、套牢事業。能量在此黑洞化，必須轉向輕資產模式發展。", "outer": "失業風險、事業拖累家庭、官非。人生的業障點在於『職涯波折』。", "sop": "逆境型事業. 能量黑洞在於『經營阻礙』。保持核心能力，避免陷入重資產陷阱。"}
        },
        "propertyPalace": {
            "祿": {"inner": "家產豐厚、居家豪華、財入庫能守。能量向庫房輸送，家庭是溫暖的避風港。", "outer": "家族興旺、德高望重、祖產增值。房產與黃金是你的守護神。", "sop": "財庫型格局. 能量擴張在於『資產歸宿』。"},
            "權": {"inner": "強勢置產、家中我說了算、霸占家產。高槓桿運作房地產，家族事業掌控力強。", "outer": "房產不斷增值、家族擴張迅速. 適合地產開發或大規模持房。", "sop": "霸主型資產. 能量強壓在於『資源壟斷』。"},
            "科": {"inner": "家教好、居家優雅、資產緩步增長。資產配置以穩健為主，房產產權清晰。", "outer": "家族聲望佳、資產傳承平順. 重視居家環境的衛生與文化氣息。", "sop": "文雅型資產. 能量梳理在於『資產傳播』。"},
            "忌": {"inner": "房產套牢、家宅不寧、現金被家掏空. 黑洞在此，慎防房屋漏水或產權糾紛敗產。", "outer": "家道中落、被迫搬家、敗祖德。人生的業障點在於『家運破敗』。", "sop": "破耗型資產. 能量黑洞在於『資產鎖死』。保留充足現金，慎防因家務事損及資產。"}
        },
        "spiritPalace": {
            "祿": {"inner": "精神愉悅、偏財極佳、福報深厚。相信直覺，將愛投入內在世界，享受人生。", "outer": "享受人生、大方好施、與眾共惠. 適合感性驅動投資，福報迴向自我。", "sop": "福報型格局. 能量擴張在於『精神享受』。"},
            "權": {"inner": "意志強悍、主觀性強、追求精神成就。透過強壓意志達成目標，意志即是金錢。", "outer": "追求排場、慾望極強、強迫自己. 注意精神緊繃引發的身心失調。", "sop": "執念型格局. 能量強壓在於『意志磨練』。"},
            "科": {"inner": "修養極好、理性平衡、重視精神層次。在複雜世界中保持梳理，適合藝術、哲學。", "outer": "處事分寸拿揶精準、受人尊敬. 重視精神糧食與文化愛好。", "sop": "理智型格局. 能量梳理在於『心智穩定』。"},
            "忌": {"inner": "精神黑洞、鑽牛角尖、重度焦慮症. 能量在此糾結，嚴禁主觀重押，忌諱極端。", "outer": "極端偏激、因嗜好大破財、想不開. 人生的業障點在於『潛意識創傷』。", "sop": "業力型精神. 能量黑洞在於『煩惱自尋』。尋其正面嗜好轉移注意力，嚴禁主觀執迷。"}
        },
        "parentsPalace": {
            "祿": {"inner": "長輩疼愛、體制內資源、合約順遂。將愉悅動機投入對上級的運作，獲利豐厚。", "outer": "得政府標案、信貸信譽好、父母強. 適合賺體制內的錢、銀行槓桿。", "sop": "背景型格局. 能量擴張在於『上層通路』。"},
            "權": {"inner": "挑戰威權、對長輩強勢、想主導體制。強勢與長官或規則競爭，謀求更高權限。", "outer": "受制於嚴苛法規、長輩強勢打壓. 注意言行，避免觸碰法律紅線。", "sop": "衝突型體質. 能量強壓在於『體制對抗』。"},
            "科": {"inner": "長輩緣佳、求學順遂、信譽度極高。靠合約、文書 or 專業執照獲得穩定發展。", "outer": "父母有名望、信譽保障、合規性佳. 適合金融、法律與特許行業。", "sop": "信用型格局. 能量梳理在於『合規誠信』。"},
            "忌": {"inner": "與長輩不合、體制打壓、文書官非。黑洞在文書與法律中，簽約必請律師。", "outer": "父母多難、銀行抽根、合約漏洞. 人生的業障點在於『長輩業力』。", "sop": "文書型災難. 能量黑洞在於『法律糾紛』。合約簽署前務必諮詢專業意見。"}
        }
    }

    CEO_IMAGES = {
        "紫微": "zi_wei_emperor.png", "天機": "tian_ji_strategist.png", "太陽": "tai_yang_sun.png",
        "武曲": "wu_qu_executor.png", "天同": "tian_tong_harmonizer.png", "廉貞": "lian_zhen_crisis_pr.png",
        "天府": "tian_fu_treasurer.png", "太陰": "tai_yin_designer.png", "貪狼": "tan_lang_marketer.png",
        "巨門": "ju_men_truth_seeker.png", "天相": "tian_xiang_negotiator.png", "天梁": "tian_liang_protector.png",
        "七殺": "qi_sha_conqueror.png", "破軍": "po_jun_rebel.png"
    }

    # --- Enhanced Flying Star Chain Rules (Based on SOP) ---
    SOURCE_RULES = {
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

    STEM_RULES = {
        "甲": {"lu_star": "廉貞", "lu_mean": "精密規劃、桃花人緣、電子科技", "ji_star": "太陽", "ji_mean": "男人惹禍、死要面子、公關危機"},
        "乙": {"lu_star": "天機", "lu_mean": "智慧企劃、頻繁變動、轉手機務", "ji_star": "太陰", "ji_mean": "女人受累、房產虧損、情緒憂鬱"},
        "丙": {"lu_star": "天同", "lu_mean": "服務協調、餐飲享樂、享福財", "ji_star": "廉貞", "ji_mean": "血光之災、官司刑罰、行政疏失"},
        "丁": {"lu_star": "太陰", "lu_mean": "細膩佈局、女性市場、房產財", "ji_star": "巨門", "ji_mean": "口舌是非、暗處吃虧、詐欺債務"},
        "戊": {"lu_star": "貪狼", "lu_mean": "交際應酬、投機偏財、博弈獲利", "ji_star": "天機", "ji_mean": "神經衰弱、判斷失誤、鑽牛角尖"},
        "己": {"lu_star": "武曲", "lu_mean": "實力執行、金融操作、重工業", "ji_star": "文曲", "ji_mean": "合約陷阱、支票跳票、文書詐騙"},
        "庚": {"lu_star": "太陽", "lu_mean": "名氣擴散、公益事業、男性貴人", "ji_star": "天同", "ji_mean": "無福消受、心力交瘁、泌尿代謝問題"},
        "辛": {"lu_star": "巨門", "lu_mean": "口才傳播、專業技術、醫藥法律", "ji_star": "文昌", "ji_mean": "文書無效、違約罰單、法規變動"},
        "壬": {"lu_star": "天梁", "lu_mean": "長輩蔭庇、繼承、保險醫療", "ji_star": "武曲", "ji_mean": "資金斷鏈、破產被劫、金屬傷害"},
        "癸": {"lu_star": "破軍", "lu_mean": "創新突破、破壞建設、流行時尚", "ji_star": "貪狼", "ji_mean": "桃花糾紛、縱慾過度、因色敗家"}
    }

    IMPACT_RULES = {
        "命宮": {"lu": "資源主動對我好，得利明顯", "ji": "責任壓在身上，心煩意亂"},
        "兄弟宮": {"lu": "增加現金流，庫存增值", "ji": "現金卡住，兄弟受累"},
        "夫妻宮": {"lu": "事業幫助配偶，異性緣增強", "ji": "配偶干擾事業，感情負擔"},
        "子女宮": {"lu": "合夥投資順利，桃花多", "ji": "合夥拆夥，子女離心"},
        "財帛宮": {"lu": "現金進帳順利，轉速快", "ji": "破財，資金周轉困難"},
        "疾厄宮": {"lu": "心情愉快，身體好，店面旺", "ji": "身體不適，情緒卡點"},
        "遷移宮": {"lu": "出外遇貴人，社會評價優", "ji": "在外處處碰壁，意外風險"},
        "交友宮": {"lu": "人脈廣，客戶主動上門", "ji": "朋友欠錢，小人陷害"},
        "官祿宮": {"lu": "工作順利，權力地位提升", "ji": "工作失誤多，容易換工作"},
        "田宅宮": {"lu": "資產增值，家庭和諧，入庫", "ji": "庫存流失，家宅不寧"},
        "福德宮": {"lu": "精神滿足，財源穩定", "ji": "精神焦慮，大破財(沖財)"},
        "父母宮": {"lu": "長輩提攜，文書順利，信用增", "ji": "文書出錯，被長輩責罵"}
    }

    PALACE_LIST_ORDER = ["命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮", "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮"]

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
        is_direct_file = any(image_name.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"])
        filename = image_name if is_direct_file else self.CEO_IMAGES.get(image_name, "")
        path = self.ASSETS_DIR / filename if filename else None
        if not path or not path.exists():
            clean_name = image_name.split(".")[0]
            filename_alt = self.CEO_IMAGES.get(clean_name, "")
            if filename_alt: path = self.ASSETS_DIR / filename_alt
        if not path or not path.exists(): return ""
        ext = path.suffix.lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        try:
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                return f"data:{mime};base64,{b64}"
        except Exception: return ""

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
                "major_stars": major_names, "lucky_stars": lucky_names, "sha_stars": sha_names
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
            if target_star in d_stars: 
                p_name_internal = dp.name
                return self.PALACE_NAME_MAP.get(p_name_internal, dp.translate_name())
        return "未知"

    def get_clash_palace(self, target_name):
        try:
            clean_name = target_name.replace("宮", "") + "宮"
            idx = self.PALACE_LIST_ORDER.index(clean_name)
            return self.PALACE_LIST_ORDER[(idx + 6) % 12]
        except: return "對宮"

    def fly_all_palaces(self):
        res = {}
        for p in self.astro.palaces:
            b_idx = self._get_branch_idx(p)
            p_name = p.translate_name()
            stem = p.translate_heavenly_stem()
            
            lu_dest = self.f_dest_by_branch(b_idx, "祿")
            ji_dest = self.f_dest_by_branch(b_idx, "忌")
            
            src_data = self.SOURCE_RULES.get(p_name, {"lu": "未知", "ji": "未知"})
            stem_data = self.STEM_RULES.get(stem, {"lu_star": "", "lu_mean": "", "ji_star": "", "ji_mean": ""})
            lu_imp = self.IMPACT_RULES.get(lu_dest, {"lu": "現象不明"})
            ji_imp = self.IMPACT_RULES.get(ji_dest, {"ji": "現象不明"})
            clash_palace = self.get_clash_palace(ji_dest)
            
            res[b_idx] = {
                "name": p_name, "stem": stem,
                "lu_star": stem_data["lu_star"], "ji_star": stem_data["ji_star"],
                "lu_dest": lu_dest, "ji_dest": ji_dest,
                "source_msg": f"起因：{src_data['lu']} (祿因) / {src_data['ji']} (忌果)",
                "lu_means": stem_data["lu_mean"], "lu_effect": lu_imp["lu"],
                "ji_hazard": stem_data["ji_mean"], "ji_effect": ji_imp["ji"],
                "clash": clash_palace, "advice": f"利用『{stem_data['lu_star']}』獲利，防範『{ji_dest}』風險，保住『{clash_palace}』。"
            }
        return res

    def get_innate_audit(self):
        dist = self.get_innate_distribution()["stars"]
        res = []
        for t, d in dist.items():
            internal_p_name = d['palace']
            palace_display = self.PALACE_NAME_MAP.get(internal_p_name, "未知宮位")
            star_name = d['star']
            scenario = self.STRATEGIC_SCENARIOS.get(internal_p_name, {}).get(t, {})
            is_inner = internal_p_name in {"soulPalace", "wealthPalace", "healthPalace", "careerPalace", "propertyPalace", "spiritPalace"}
            meaning = scenario.get("sop", "待定策略位")
            impact = scenario.get("inner" if is_inner else "outer", "待定影響位")
            res.append({
                "header": f"【生年化{t} ➔ {star_name} ({palace_display})】",
                "palace_def": f"一生核心『{t}』之氣。",
                "meaning": meaning, "impact": impact, "sop": scenario.get("sop", "待定策略位")
            })
        return res
