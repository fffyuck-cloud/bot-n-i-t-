# ====================================================================================================
# ██████╗ ██╗    █████╗  ██████╗██╗  ██╗    ██████╗ ██╗███╗    ██╗██╗  ██╗    ██████╗  ██████╗ ████████╗
# ██╔══██╗██║    ██╔══██╗██╔════╝██║ ██╔╝    ██╔══██╗██║████╗   ██║██║ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
# ██████╔╝██║    ███████║██║     █████╔╝     ██████╔╝██║██╔██╗  ██║█████╔╝     ██████╔╝██║   ██║   ██║   
# ██╔══██╗██║    ██╔══██║██║     ██╔═██╗     ██╔═══╝ ██║██║╚██╗ ██║██╔═██╗     ██╔══██╗██║   ██║   ██║   
# ██████╔╗███████╗██║  ██║╚██████╗██║  ██╗    ██║     ██║██║ ╚████║██║  ██╗    ██████╔╝╚██████╔╝   ██║   
# ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═════╝ ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝    ╚═════╝  ╚═╝    ╚═╝   
#                                                                                                   
# SAKURA GOTHIC ARCADE ENTERPRISE v9.6.5 - ULTRA MASSIVE EXTENSION & MEGA VOCABULARY MODULES
# ====================================================================================================

import os
import sys
import json
import random
import logging
import asyncio
import threading
import unicodedata
import aiohttp
from datetime import datetime, timedelta
from typing import Set, List, Dict, Optional, Union, Tuple
from flask import Flask
import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import View, Button, Select

# ====================================================================================================
# PHẦN 1: CẤU HÌNH HỆ THỐNG & GIAO DIỆN EMBED GOTHIC NÂNG CAO MỞ RỘNG (1000+ DÒNG ARCHITECTURE)
# ====================================================================================================

class BotConfig:
    VERSION: str = "9.6.5 Sakura Gothic Ultimate Massive Vocabulary & Extended Arcade Edition"
    DEVELOPER: str = "Black & Pink Studio Enterprise Architecture"
    PREFIX: str = "?"
    OWNER_ID: int = 1312333137241575449 
    
    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = int(os.getenv("PORT", 8080))
    
    FILE_VIETNAMESE_DICT: str = "TuDien_TiengViet_Ghep_2Ban.txt"
    FILE_ENGLISH_DICT: str = "tu dien tieng anh.txt"
    FILE_COUNTRIES_DICT: str = "quoc gia vn.txt"
    FILE_VOCABULARY_DICT: str = "tu_vung_nang_cao.txt"
    
    COLOR_SAKURA_PINK: int = 0xFFB7C5   
    COLOR_DEEP_PINK: int = 0xFF1493     
    COLOR_BLACK_CHIC: int = 0x10001A    
    COLOR_RED_DARK: int = 0x8B0000      
    COLOR_GOLD: int = 0xFFD700          
    COLOR_PURPLE: int = 0x9400D3
    COLOR_CYAN: int = 0x00CED1
    COLOR_EMERALD: int = 0x00FA9A
    COLOR_NEON_BLUE: int = 0x00BFFF
    COLOR_CRIMSON: int = 0xDC143C
    COLOR_VIOLET: int = 0xEE82EE
    
    MSG_ERR_ALREADY_USED: str = "❌ Từ này đã được sử dụng trước đó trong ván này hoặc không có thực!"
    BORDER: str = "🌸・━━━━━━━━━━━━━━━━━━━━━━━━━━━・🌸" 
    THICK_BORDER: str = "🖤═════════════════════════════════🌸"

    EMOJI_TICK: str = "✅"
    EMOJI_X: str = "❌"
    EMOJI_SAKURA: str = "🌸"
    EMOJI_GOTHIC: str = "🖤"

# ====================================================================================================
# PHẦN 2: KHO DỮ LIỆU ĐỒ SỘ & FULL TỪ ĐIỂN TỰ ĐỘNG KHỞI TẠO MỞ RỘNG
# ====================================================================================================

DEFAULT_VIETNAMESE_FALLBACK: Set[str] = {
    "an ninh", "an toàn", "ấm áp", "ẩm ướt", "ánh sáng", "áo quần", "ăn uống", "át chủ", "ba mươi", "bạc hà",
    "bạ bạt", "bạn bè", "bao dung", "bạo chúa", "bền bỉ", "bí quyết", "bình yên", "bồi đắp", "bứt phá", "bị ốm",
    "ca dao", "ca khúc", "cá mập", "cá tính", "can đảm", "cao cấp", "cầu vồng", "chăm chỉ", "chân thành", "chính nghĩa",
    "chủ nhật", "chúc mừng", "danh lam", "dân tộc", "dấu ấn", "dễ thương", "dũng cảm", "dư dả", "dưới quê", "du lịch",
    "đà điểu", "đại dương", "đảm đang", "đất nước", "đầu bếp", "đặc sản", "đẹp đẽ", "địa lý", "định mệnh", "đối thoại",
    "êm đềm", "em gái", "fa lăng", "gà trống", "giao lưu", "gia đình", "giá trị", "giải pháp", "giảm giá", "giàu có",
    "hà nội", "hải sản", "hạnh phúc", "hiểu biết", "hoa hậu", "hòa bình", "học tập", "hùng vĩ", "hương thơm", "hướng dẫn",
    "ích kỷ", "im lặng", "yêu thương", "ỷ lại", "kiên nhẫn", "kỷ niệm", "kỹ năng", "kỳ vĩ", "kết quả", "không khí",
    "la bàn", "lạc quan", "lịch sự", "long lanh", "lương tâm", "lướt ván", "lý tưởng", "làm việc", "lắp ráp", "lặng lẽ",
    "màu hồng", "mặt trời", "mẹ hiếm", "mỉm cười", "mong mỏi", "mùa xuân", "mực tím", "mạnh mẽ", "mật ong", "mỹ phẩm",
    "nam sinh", "ngây thơ", "nghệ thuật", "nghiêm túc", "ngọc trai", "nguồn cội", "nhà cửa", "nhân ái", "nhịp điệu", "nhỏ nhắn",
    "ổn định", "ông bà", "phát triển", "phim ảnh", "phong phú", "phượng hoàng", "phương pháp", "phước lành", "phút chốc", "phục vụ",
    "quà cáp", "quan tâm", "quảng đại", "quê hương", "quyết tâm", "quý giá", "quốc kỳ", "ra khơi", "rạng rỡ", "rừng rậm",
    "sáng tạo", "sân khấu", "sile sỏi", "sinh nhật", "sông ngòi", "sức khỏe", "suy nghĩ", "sự thật", "sử sách", "sạch sẽ",
    "tài sản", "tâm sự", "tập thể", "thanh bình", "thiên nhiên", "thông minh", "thực tế", "tình yêu", "tự do", "tươi cười",
    "ưa nhìn", "ước mơ", "văn hóa", "vẻ đẹp", "việt nam", "vui vẻ", "vươn lên", "vườn hoa", "vận động", "vị tha",
    "xinh đẹp", "xôn xao", "xứ sở", "xây dựng", "xứng đáng", "xanh biếc", "xa xôi", "xúc động", "xám xịt", "xì tin",
    "hệ thống", "lập trình", "phần mềm", "máy chủ", "bảo mật", "dữ liệu", "truyền thông", "mạng xã hội", "trực tuyến",
    "giải trí", "âm nhạc", "hội họa", "vũ trụ", "ngân hà", "thiên hà", "hố đen", "sao hỏa", "trái đất", "mặt trăng"
}

DEFAULT_ENGLISH_FALLBACK: Set[str] = {
    "apple", "anchor", "angel", "apex", "arrow", "azure", "acorn", "album", "amber", "amulet",
    "antique", "arctic", "astro", "aura", "avocado", "axe", "alchemy", "alert", "alpine", "amaze",
    "banana", "basket", "beacon", "blossom", "breeze", "butter", "bubble", "bizarre", "balance", "bandit",
    "cactus", "canyon", "castle", "cherry", "circus", "cloud", "comet", "cookie", "crystal", "cinder",
    "dagger", "dancer", "desert", "diamond", "dolphin", "dragon", "dream", "dynamo", "eclipse", "energy",
    "falcon", "feather", "firefly", "forest", "fountain", "galaxy", "garden", "glacier", "giggle", "gravity",
    "harmony", "horizon", "iceberg", "infinite", "jasmine", "jungle", "kingdom", "lantern", "legend", "lotus",
    "magic", "marble", "melody", "miracle", "nebula", "oasis", "orchid", "palace", "phoenix", "planet",
    "quartz", "rainbow", "ripple", "rocket", "sapphire", "shadow", "silence", "starlight", "summit", "symphony",
    "tempering", "thunder", "tornado", "umbrella", "universe", "valiant", "vortex", "whisper", "zenith", "zephyr",
    "cyber", "matrix", "quantum", "neural", "plasma", "vector", "syntax", "runtime", "kernel", "protocol"
}

DEFAULT_COUNTRIES_FALLBACK: Set[str] = {
    "việt nam", "hoa kỳ", "pháp", "đức", "nhật bản", "hàn quốc", "trung quốc", "anh", "ý", "tây ban nha",
    "canada", "úc", "nga", "thụy sĩ", "thụy điển", "na uy", "đan mạch", "phần lan", "hà lan", "bỉ"
}

DEFAULT_VOCABULARY_FALLBACK: Dict[str, str] = {
    "resilience": "Khả năng phục hồi nhanh chóng, kiên cường trước khó khăn.",
    "ephemeral": "Phù du, ngắn ngủi, tồn tại trong thời gian rất ngắn.",
    "serendipity": "Sự tình cờ may mắn khi phát hiện điều tốt đẹp.",
    "mellifluous": "Ngọt ngào, du dương (thường dùng cho âm thanh hoặc giọng nói).",
    "labyrinth": "Mê cung quanh co, phức tạp, khó tìm lối thoát.",
    "petrichor": "Mùi hương dễ chịu của đất sau cơn mưa đầu mùa.",
    "solitude": "Trạng thái cô đơn nhưng bình yên, tận hưởng một mình.",
    "halcyon": "Bình yên, thịnh vượng, hạnh phúc yên ả trong quá khứ.",
    "aurora": "Hiện tượng quang phổ rực rỡ ở cực (cực quang).",
    "zenith": "Đỉnh cao nhất, điểm thiên đỉnh trên bầu trời.",
    "ubiquitous": "Có mặt ở khắp mọi nơi, phổ biến rộng rãi.",
    "ineffable": "Không thể diễn tả bằng lời, quá tuyệt vời.",
    "mellifluous": "Ngọt ngào, êm dịu.",
    "halcyon": "Yên bình, thanh thản."
}

EASY_START_WORDS: Set[str] = {
    "an ninh", "an toàn", "bình yên", "hạnh phúc", "cảm ơn", "xinh đẹp", "đẹp trai",
    "học sinh", "sinh viên", "gia đình", "bạn bè", "thầy giáo", "cô giáo", "máy tính",
    "điện thoại", "nước mắm", "cơm tấm", "xôi gấc", "trà sữa", "cà phê", "mưa rào",
    "nắng nóng", "mặt trời", "ánh sáng", "đêm tối", "ban ngày", "ban đêm", "thời gian",
    "không gian", "hoa hồng", "cây cối", "động vật", "con mèo", "con chó", "sông sâu",
    "biển cả", "núi cao", "đồng cỏ", "bầu trời", "mây trắng", "gió mát", "nước trong"
}

TRIVIA_QUESTIONS = [
    {"q": "Thủ đô của Nhật Bản là gì?", "ans": "tokyo", "hint": "Thành phố hiện đại bậc nhất châu Á."},
    {"q": "Hành tinh nào gần Mặt Trời nhất?", "ans": "sao thủy", "hint": "Tên có chữ 'sao'."},
    {"q": "Đâu là ngôn ngữ lập trình phổ biến cho Trí tuệ nhân tạo (AI)?", "ans": "python", "hint": "Trùng tên với một loài trăn."},
    {"q": "Đại dương lớn nhất trên Trái Đất là gì?", "ans": "thai binh duong", "hint": "Bắt đầu bằng chữ T."},
    {"q": "Núi cao nhất thế giới là núi nào?", "ans": "everest", "hint": "Nằm ở dãy Himalaya."},
    {"q": "Kim loại nào dẫn điện tốt nhất?", "ans": "bac", "hint": "Ký hiệu hóa học là Ag."},
    {"q": "Cơ quan nào trong cơ thể người bơm máu?", "ans": "tim", "hint": "Nằm ở lồng ngực trái."},
    {"q": "Ngôn ngữ nào được sử dụng nhiều nhất thế giới?", "ans": "tieng anh", "hint": "English."},
}

# ====================================================================================================
# PHẦN 3: HỆ THỐNG LOGGING VÀ KEEP ALIVE SERVER TÍCH HỢP ĐA LUỒNG
# ====================================================================================================

class LoggerSetup:
    @staticmethod
    def initialize_logger() -> logging.Logger:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        formatter = logging.Formatter(fmt="[%(asctime)s] | %(levelname)-8s | [%(module)s.%(funcName)s] : %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger_instance = logging.getLogger("SakuraUltimateBotExtended")
        logger_instance.setLevel(logging.INFO)
        logger_instance.addHandler(console_handler)
        return logger_instance

logger = LoggerSetup.initialize_logger()

keep_alive_app = Flask("SakuraUltimateKeepAliveExtended")

@keep_alive_app.route('/')
def route_home() -> str:
    return """
    <html>
        <head><title>Sakura Gothic Massive Arcade v9.6.5 Extended</title></head>
        <body style='background:#10001A; color:#FFB7C5; font-family:sans-serif; text-align:center; padding-top:50px;'>
            <h1>🌸 Sakura Black Pink Arcade Ultimate (v9.6.5 Extended 1000+ Lines) 🌸</h1>
            <p>System Status: <strong style='color:#00FF00'>ONLINE & FULLY OPERATIONAL</strong></p>
            <p>Active Modules: Math 15+, Full Vocabulary Dictionary, Mini-games, Advanced Custom Embed UI, Shop, Inventory, Economy.</p>
        </body>
    </html>
    """

@keep_alive_app.route('/health')
def route_health() -> str:
    return {"status": "healthy", "version": BotConfig.VERSION, "timestamp": datetime.now().isoformat(), "mode": "extended_production"}

def launch_web_server() -> None:
    try:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        keep_alive_app.run(host=BotConfig.WEB_SERVER_HOST, port=BotConfig.WEB_SERVER_PORT, debug=False, use_reloader=False, threaded=True)
    except Exception as server_err:
        logger.error(f"Lỗi Flask Server: {server_err}")

threading.Thread(target=launch_web_server, daemon=True).start()

# ====================================================================================================
# PHẦN 4: HỆ THỐNG QUẢN LÝ DƯ LIỆU NGƯỜI DÙNG, KINH TẾ & KHO ĐỒ NÂNG CAO
# ====================================================================================================

FILE_USER_DATA = "user_data_sakura_ultimate_v965.json"

class UserDataManager:
    @staticmethod
    def load_data() -> dict:
        if os.path.exists(FILE_USER_DATA):
            try:
                with open(FILE_USER_DATA, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Lỗi đọc file user data: {e}")
        return {}

    @staticmethod
    def save_data(data: dict) -> None:
        try:
            with open(FILE_USER_DATA, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Lỗi ghi file user data: {e}")

    @staticmethod
    def get_user(user_id: int) -> dict:
        data = UserDataManager.load_data()
        uid_str = str(user_id)
        if uid_str not in data:
            data[uid_str] = {
                "hints": 25,
                "coins": 2000,
                "last_daily": "",
                "math_score": 0,
                "arcade_wins": 0,
                "trivia_score": 0,
                "vocab_learned": 0,
                "inventory": ["Hoa Anh Đào Mặc Định", "Thẻ Gợi Ý Cao Cấp", "Sổ Tay Từ Vựng Gothic"],
                "title": "Tân Thủ Sakura Gothic"
            }
            UserDataManager.save_data(data)
        return data[uid_str]

    @staticmethod
    def update_user(user_id: int, **kwargs) -> dict:
        data = UserDataManager.load_data()
        uid_str = str(user_id)
        if uid_str not in data:
            data[uid_str] = {
                "hints": 25,
                "coins": 2000,
                "last_daily": "",
                "math_score": 0,
                "arcade_wins": 0,
                "trivia_score": 0,
                "vocab_learned": 0,
                "inventory": ["Hoa Anh Đào Mặc Định", "Thẻ Gợi Ý Cao Cấp", "Sổ Tay Từ Vựng Gothic"],
                "title": "Tân Thủ Sakura Gothic"
            }
        for key, value in kwargs.items():
            data[uid_str][key] = value
        UserDataManager.save_data(data)
        return data[uid_str]

# ====================================================================================================
# PHẦN 5: HỆ THỐNG TOÁN HỌC NÂNG CAO MỞ RỘNG (15+ DẠNG BÀI TẬP VÀ XỬ LÝ CHI TIẾT)
# ====================================================================================================

class MathGameSession:
    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        self.active = False
        self.answer: float = 0.0
        self.question: str = ""
        self.explanation: str = ""
        self.category: str = "none"

class MathGameManager:
    def __init__(self):
        self._sessions: Dict[int, MathGameSession] = {}

    def get_session(self, channel_id: int) -> MathGameSession:
        if channel_id not in self._sessions:
            self._sessions[channel_id] = MathGameSession(channel_id)
        return self._sessions[channel_id]

    def generate_random_problem(self) -> tuple[str, float, str, str]:
        game_type = random.choice([
            "geometry_cube", "fraction_advanced", "algebra_linear", 
            "percentage_logic", "geometry_sphere", "quadratic_equation",
            "ratio_proportion", "statistics_mean", "speed_distance", 
            "exponent_power", "geometry_cylinder", "logarithm_basic",
            "matrix_determinant", "trigonometry_sin", "combinatorics_permutations"
        ])
        
        if game_type == "geometry_cube":
            side = random.randint(2, 15)
            ans = float(side ** 3)
            question = f"📦 **[Hình Học Không Gian]** Tính thể tích $V$ của hình lập phương có cạnh $a = {side}$?"
            explanation = f"Công thức thể tích hình lập phương: $V = a^3 = {side}^3 = {ans:.2f}$."
            return question, ans, explanation, "Hình Học"
            
        elif game_type == "fraction_advanced":
            a, b = random.randint(1, 9), random.randint(2, 9)
            c, d = random.randint(1, 9), random.randint(2, 9)
            ans = round((a/b) + (c/d), 2)
            question = f"🧮 **[Số Hữu Tỉ & Phân Số]** Tính giá trị biểu thức (làm tròn 2 chữ số thập phân):\n$$\\frac{{{a}}}{{{b}}} + \\frac{{{c}}}{{{d}}}$$"
            explanation = f"Quy đồng và tính toán: $({a}/{b}) + ({c}/{d}) \\approx {ans}$."
            return question, ans, explanation, "Phân Số"
            
        elif game_type == "algebra_linear":
            coeff = random.randint(2, 9)
            const_add = random.randint(5, 40)
            target_val = random.randint(60, 180)
            ans = round((target_val - const_add) / coeff, 2)
            question = f"🔢 **[Đại Số Cơ Bản]** Tìm nghiệm $x$ của phương trình:\n$${coeff}x + {const_add} = {target_val}$$"
            explanation = f"Giải phương trình tuyến tính: $x = ({target_val} - {const_add}) / {coeff} = {ans}$."
            return question, ans, explanation, "Đại Số"
            
        elif game_type == "percentage_logic":
            original_price = random.randint(100, 990) * 1000
            discount_pct = random.choice([10, 15, 20, 25, 30, 35, 40, 50])
            ans = float(original_price * (1 - discount_pct / 100))
            question = f"🏷️ **[Toán Thực Tế]** Giá gốc `{original_price:,}đ`, giảm giá `{discount_pct}%`. Tính số tiền thực tế cần thanh toán?"
            explanation = f"Số tiền thực tế = ${original_price:,} \\times (1 - {discount_pct}/100) = {ans:,.0f}đ$."
            return question, ans, explanation, "Thực Tế"

        elif game_type == "geometry_sphere":
            r = random.randint(3, 12)
            ans = round((4/3) * 3.14159 * (r**3), 2)
            question = f"🌐 **[Hình Học Tròn]** Tính thể tích khối cầu bán kính $r = {r}$ (lấy $\\pi \\approx 3.14159$ và làm tròn 2 chữ số)?"
            explanation = f"Công thức thể tích hình cầu: $V = \\frac{{4}}{{{3}}}\\pi r^3 = \\frac{{4}}{{{3}}} \\times 3.14159 \\times {r}^3 \\approx {ans}$."
            return question, ans, explanation, "Hình Học"

        elif game_type == "quadratic_equation":
            x1 = random.randint(-6, 6)
            x2 = random.randint(-6, 6)
            b = -(x1 + x2)
            c = x1 * x2
            ans = float(max(x1, x2))
            question = f"📈 **[Phương Trình Bậc Hai]** Tìm nghiệm lớn hơn của phương trình:\n$$x^2 {'+' if b >= 0 else ''}{b}x {'+' if c >= 0 else ''}{c} = 0$$"
            explanation = f"Phân tích đa thức thành nhân tử: $(x - {x1})(x - {x2}) = 0$. Các nghiệm là ${x1}$ và ${x2}$. Nghiệm lớn hơn là {ans}."
            return question, ans, explanation, "Đại Số"

        elif game_type == "ratio_proportion":
            v1 = random.randint(2, 9)
            v2 = random.randint(3, 15)
            total = random.randint(60, 250)
            ans = round(total * (v1 / (v1 + v2)), 2)
            question = f"⚖️ **[Tỉ Lệ Thức]** Chia tổng số `{total}` theo tỉ lệ ${v1} : {v2}$. Hãy tìm giá trị của phần thứ nhất (làm tròn 2 chữ số)?"
            explanation = f"Tổng số phần bằng nhau = ${v1} + {v2} = {v1+v2}$. Phần thứ nhất = ${total} \\times \\frac{{{v1}}}{{{v1+v2}}} \\approx {ans}$."
            return question, ans, explanation, "Tỉ Lệ"

        elif game_type == "statistics_mean":
            nums = [random.randint(10, 99) for _ in range(5)]
            ans = round(sum(nums) / len(nums), 2)
            question = f"📊 **[Thống Kê]** Tính số trung bình cộng của dãy số sau: `{nums}`?"
            explanation = f"Trung bình cộng = Tổng các số / Số lượng = ${sum(nums)} / {len(nums)} = {ans}$."
            return question, ans, explanation, "Thống Kê"

        elif game_type == "speed_distance":
            speed = random.randint(35, 100)
            time_h = random.randint(2, 7)
            ans = float(speed * time_h)
            question = f"🚗 **[Chuyển Động]** Một ô tô di chuyển với vận tốc trung bình `{speed} km/h` trong thời gian `{time_h} giờ`. Tính quãng đường đi được?"
            explanation = f"Quãng đường = Vận tốc $\\times$ Thời gian = ${speed} \\times {time_h} = {ans} \\text{{ km}}$."
            return question, ans, explanation, "Vật Lý"

        elif game_type == "exponent_power":
            base = random.randint(2, 6)
            exponent = random.randint(3, 6)
            ans = float(base ** exponent)
            question = f"⚡ **[Lũy Thừa]** Tính giá trị biểu thức lũy thừa sau:\n$${base}^{{ {exponent} }}$$"
            explanation = f"Tính lũy thừa: ${base}^{{{exponent}}} = {ans:,.0f}$."
            return question, ans, explanation, "Đại Số"

        elif game_type == "geometry_cylinder":
            r = random.randint(2, 8)
            h = random.randint(5, 20)
            ans = round(3.14159 * (r**2) * h, 2)
            question = f"🧪 **[Hình Trụ]** Tính thể tích hình trụ có bán kính đáy $r = {r}$ và chiều cao $h = {h}$ (lấy $\\pi \\approx 3.14159$ và làm tròn 2 chữ số)?"
            explanation = f"Thể tích hình trụ: $V = \\pi r^2 h = 3.14159 \\times {r}^2 \\times {h} \\approx {ans}$."
            return question, ans, explanation, "Hình Học"

        elif game_type == "logarithm_basic":
            base_val = random.choice([2, 4, 8, 16])
            ans = float(round(float(base_val.bit_length() - 1), 2))
            question = f"📐 **[Logarithm]** Tính giá trị cơ bản: $\\log_2({base_val})$?"
            explanation = f"Giải logarithm cơ bản: $\\log_2({base_val}) = {ans}$ vì $2^{{{ans}}} = {base_val}$."
            return question, ans, explanation, "Giải Tích"

        elif game_type == "matrix_determinant":
            a, b = random.randint(1, 5), random.randint(1, 5)
            c, d = random.randint(1, 5), random.randint(1, 5)
            ans = float((a * d) - (b * c))
            question = f"🔢 **[Đại Số Tuyến Tính]** Tính định thức (Determinant) của ma trận vuông cấp 2:\n$$\\begin{vmatrix} {a} & {b} \\\\ {c} & {d} \\end{vmatrix}$$"
            explanation = f"Công thức định thức cấp 2: $ad - bc = ({a} \\times {d}) - ({b} \\times {c}) = {ans}$."
            return question, ans, explanation, "Đại Số"

        elif game_type == "trigonometry_sin":
            angle = random.choice([0, 30, 90])
            if angle == 0: ans = 0.0
            elif angle == 30: ans = 0.5
            else: ans = 1.0
            question = f"📐 **[Lượng Giác]** Tính giá trị của biểu thức lượng giác: $\\sin({angle}^\\circ)$ (làm tròn 2 chữ số)?"
            explanation = f"Giá trị chuẩn của hàm lượng giác cơ bản tại góc ${angle}^\\circ$ là ${ans}$."
            return question, ans, explanation, "Lượng Giác"

        else:
            n = random.randint(4, 7)
            k = random.randint(2, 3)
            import math
            ans = float(math.comb(n, k))
            question = f"🎲 **[Tổ Hợp Xác Suất]** Tính số cách chọn chập $k = {k}$ phần tử từ tập hợp có $n = {n}$ phần tử ($C_n^k$):"
            explanation = f"Công thức tổ hợp chập $k$ của $n$: $C_n^k = \\frac{{n!}}{{k!(n-k)!}} = {ans}$."
            return question, ans, explanation, "Xác Suất"

math_manager = MathGameManager()

# ====================================================================================================
# PHẦN 6: QUẢN LÝ TỪ ĐIỂN, TRA CỨU TỪ VỰNG NÂNG CAO VÀ CHỈ MỤC TỐC ĐỘ CAO
# ====================================================================================================

class VocabularyManager:
    @staticmethod
    def load_vocab_file(filepath: str, fallback_dict: Dict[str, str]) -> Dict[str, str]:
        vocab_map = dict(fallback_dict)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split("|")
                        if len(parts) >= 2:
                            w, meaning = parts[0].strip().lower(), parts[1].strip()
                            if w: vocab_map[w] = meaning
                logger.info(f"🖤🌸 Đã nạp thành công {len(vocab_map):,} từ vựng chuyên sâu từ [{filepath}].")
            except Exception as err:
                logger.error(f"Lỗi đọc file từ vựng {filepath}: {err}")
        else:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    for w, m in fallback_dict.items():
                        f.write(f"{w}|{m}\n")
            except Exception: pass
        return vocab_map

class DataManager:
    @staticmethod
    def load_text_file(filepath: str, fallback_dataset: Set[str]) -> Set[str]:
        words = set(fallback_dataset)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        clean = line.strip().lower()
                        if clean: words.add(clean)
                logger.info(f"🖤🌸 Đã nạp {len(words):,} mục từ file [{filepath}].")
            except Exception as err:
                logger.error(f"Lỗi đọc file {filepath}: {err}")
        else:
            try:
                with open(filepath, "w", encoding="utf-8") as f: f.write("\n".join(fallback_dataset))
            except Exception: pass
        return words

RAW_VIETNAMESE_DICT: Set[str] = DataManager.load_text_file(BotConfig.FILE_VIETNAMESE_DICT, DEFAULT_VIETNAMESE_FALLBACK)
ENGLISH_DICT: Set[str] = DataManager.load_text_file(BotConfig.FILE_ENGLISH_DICT, DEFAULT_ENGLISH_FALLBACK)
COUNTRIES_VN_DICT: Set[str] = DataManager.load_text_file(BotConfig.FILE_COUNTRIES_DICT, DEFAULT_COUNTRIES_FALLBACK)
FULL_VOCABULARY_MAP: Dict[str, str] = VocabularyManager.load_vocab_file(BotConfig.FILE_VOCABULARY_DICT, DEFAULT_VOCABULARY_FALLBACK)

for vocab_word in FULL_VOCABULARY_MAP.keys():
    ENGLISH_DICT.add(vocab_word)

COMBINED_VIETNAMESE_DICTIONARY: Set[str] = {w for w in RAW_VIETNAMESE_DICT if len(w.split()) >= 2}
COMBINED_VIETNAMESE_LIST: List[str] = list(COMBINED_VIETNAMESE_DICTIONARY)
EASY_START_LIST: List[str] = list(EASY_START_WORDS)
ENGLISH_LIST: List[str] = list(ENGLISH_DICT)

def build_syllable_index(dictionary: Set[str]) -> Dict[str, List[str]]:
    index: Dict[str, List[str]] = {}
    for w in dictionary:
        parts = w.split()
        if parts: index.setdefault(parts[0], []).append(w)
    return index

def build_letter_index(dictionary: Set[str]) -> Dict[str, List[str]]:
    index: Dict[str, List[str]] = {}
    for w in dictionary:
        if w: index.setdefault(w[0], []).append(w)
    return index

VIETNAMESE_INDEX_BY_FIRST_SYLLABLE: Dict[str, List[str]] = build_syllable_index(COMBINED_VIETNAMESE_DICTIONARY)
ENGLISH_INDEX_BY_FIRST_LETTER: Dict[str, List[str]] = build_letter_index(ENGLISH_DICT)

# ====================================================================================================
# PHẦN 7: HỆ THỐNG GIAO DIỆN EMBED GOTHIC ĐỈNH CAO & HOÀN HẢO (UI UTILS EXTENDED)
# ====================================================================================================

class GameMode:
    NONE = "none"
    PVP_VIETNAMESE = "pvp_vi"
    BOT_VIETNAMESE = "bot_vi"
    PVP_ENGLISH = "pvp_en"
    BOT_ENGLISH = "bot_en"

class ChannelSession:
    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        self.active_mode = GameMode.NONE
        self.is_active = False
        self.current_word = ""
        self.used_words_history: Set[str] = set()
        self.turn_counter = 0

    def initialize_session(self, mode: str, start_word: str = "") -> None:
        self.reset()
        self.is_active = True
        self.active_mode = mode
        self.current_word = start_word
        self.used_words_history.add(start_word)
        self.turn_counter = 1

    def reset(self) -> None:
        self.active_mode = GameMode.NONE
        self.is_active = False
        self.current_word = ""
        self.used_words_history.clear()
        self.turn_counter = 0

class SessionManager:
    def __init__(self): self._sessions: Dict[int, ChannelSession] = {}
    def get_session(self, channel_id: int) -> ChannelSession:
        if channel_id not in self._sessions: self._sessions[channel_id] = ChannelSession(channel_id)
        return self._sessions[channel_id]

global_session_manager = SessionManager()

class UIUtils:
    DEFAULT_FOOTER_ICON = "https://cdn.discordapp.com/embed/avatars/0.png"
    DEFAULT_THUMBNAIL = "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=300&auto=format&fit=crop"
    BANNER_IMAGE = "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?q=80&w=1000&auto=format&fit=crop"

    @staticmethod
    def create_embed(title: str, description: str, color: int = BotConfig.COLOR_SAKURA_PINK, image_url: str = None) -> discord.Embed:
        embed = discord.Embed(
            title=f"🌸『 {title} 』🖤",
            description=description,
            color=color,
            timestamp=datetime.now()
        )
        embed.set_footer(
            text="🖤 Sakura Gothic Arcade Ultimate v9.6.5 Extended • Pure Fun Enterprise 🌸",
            icon_url=UIUtils.DEFAULT_FOOTER_ICON
        )
        embed.set_thumbnail(url=UIUtils.DEFAULT_THUMBNAIL)
        embed.set_image(url=image_url if image_url else UIUtils.BANNER_IMAGE)
        return embed

    @staticmethod
    def build_warning_embed(title: str, warning_msg: str) -> discord.Embed:
        desc = f"{BotConfig.THICK_BORDER}\n\n⚠️ **CẢNH BÁO HỆ THỐNG: {title.upper()}**\n\n> *{warning_msg}*\n\n{BotConfig.THICK_BORDER}"
        return UIUtils.create_embed("THÔNG BÁO LỖI", desc, BotConfig.COLOR_RED_DARK)

    @staticmethod
    def build_help_embed() -> discord.Embed:
        description = (
            f"{BotConfig.THICK_BORDER}\n\n"
            f"🖤 **TRUNG TÂM ĐIỀU KHIỂN SAKURA GOTHIC ULTIMATE v9.6.5 (1000+ DÒNG)** 🌸\n\n"
            f"📖 **[ HỆ THỐNG TỪ VỰNG & TRA CỨU ]**\n"
            f"❯ `{BotConfig.PREFIX}tuvung <từ>` ❯ Tra cứu nghĩa, giải thích chi tiết từ điển Anh/Việt.\n"
            f"❯ `{BotConfig.PREFIX}thuvientuvung` ❯ Khám phá kho từ vựng nâng cao ngẫu nhiên.\n\n"
            f"🇻🇳🇬🇧 **[ HỆ THỐNG NỐI TỪ ĐỈNH CAO ]**\n"
            f"❯ `{BotConfig.PREFIX}noitu` ❯ Nối từ Tiếng Việt PvP (Nhiều người chơi).\n"
            f"❯ `{BotConfig.PREFIX}botnoitu` ❯ Thách đấu Nối Từ Tiếng Việt trực tiếp với AI Bot.\n"
            f"❯ `{BotConfig.PREFIX}noitueng` ❯ Nối từ Tiếng Anh kết hợp kho từ điển khổng lồ.\n"
            f"❯ `{BotConfig.PREFIX}huyvanchoi` ❯ Hủy ván đấu đang diễn ra trong kênh hiện tại.\n\n"
            f"📐🧠 **[ TOÁN HỌC MỞ RỘNG & ĐỐ VUI KHO HỌC ]**\n"
            f"❯ `{BotConfig.PREFIX}toanhoc` ❯ Thử thách 15+ dạng toán học đỉnh cao (Nhận xu & điểm).\n"
            f"❯ `{BotConfig.PREFIX}dovui` ❯ Minigame trắc nghiệm kiến thức tổng hợp.\n\n"
            f"🪙🛍️ **[ KINH TẾ, KHO ĐỒ & TIỆN ÍCH ]**\n"
            f"❯ `{BotConfig.PREFIX}hoso` ❯ Xem profile, xu, điểm số và kho vật phẩm cá nhân.\n"
            f"❯ `{BotConfig.PREFIX}daily` ❯ Điểm danh nhận quà khủng mỗi ngày.\n"
            f"❯ `{BotConfig.PREFIX}shop` ❯ Cửa hàng mua thẻ gợi ý, hộp quà và danh hiệu.\n"
            f"❯ `{BotConfig.PREFIX}ping` ❯ Kiểm tra độ trễ server.\n"
            f"❯ `{BotConfig.PREFIX}meme` ❯ Xem ảnh meme giải trí cực chill.\n\n"
            f"{BotConfig.THICK_BORDER}"
        )
        return UIUtils.create_embed("BẢNG TRỢ GIÚP TOÀN DIỆN MỞ RỘNG", description, BotConfig.COLOR_SAKURA_PINK)

# ====================================================================================================
# PHẦN 8: KHỞI TẠO DISCORD BOT & CÁC LỆNH HỆ THỐNG CƠ BẢN (EXTENDED EVENT HOOKS)
# ====================================================================================================

bot_intents = discord.Intents.default()
bot_intents.message_content = True
bot_intents.guilds = True
bot_intents.members = True
bot_intents.messages = True

bot = commands.Bot(command_prefix=BotConfig.PREFIX, intents=bot_intents, help_command=None, case_insensitive=True)

@bot.event
async def on_ready() -> None:
    logger.info(f"✅ Bot Đen Hồng Cánh Hoa Ultimate v9.6.5 Extended đã đăng nhập thành công: {bot.user}")
    activity = discord.Activity(type=discord.ActivityType.playing, name=f"{BotConfig.PREFIX}help | 🖤🌸 1000+ Lines Massive Edition")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.command(name="ping")
async def sys_ping(ctx: commands.Context) -> None:
    latency = round(bot.latency * 1000)
    desc = f"{BotConfig.BORDER}\n\n💓 **Độ trễ hệ thống:** `{latency}ms`\n🌐 **Trạng thái:** `Hoạt động hoàn hảo vô cùng mượt mà (1000+ dòng kiến trúc độc quyền)`\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("Kiểm Tra Ping", desc, BotConfig.COLOR_EMERALD))

@bot.command(name="help", aliases=["menu"])
async def sys_help(ctx: commands.Context) -> None: 
    await ctx.send(embed=UIUtils.build_help_embed())

@bot.command(name="hoso", aliases=["profile", "diem"])
async def sys_profile(ctx: commands.Context) -> None:
    user_data = UserDataManager.get_user(ctx.author.id)
    inv_str = ", ".join(user_data["inventory"]) if user_data["inventory"] else "Trống"
    desc = (
        f"{BotConfig.THICK_BORDER}\n\n"
        f"👤 **Thành viên:** {ctx.author.mention}\n"
        f"👑 **Danh hiệu:** `{user_data.get('title', 'Tân Thủ Sakura Gothic')}`\n"
        f"⭐ **Điểm Toán Học:** `{user_data['math_score']} điểm`\n"
        f"🧠 **Điểm Đố Vui:** `{user_data.get('trivia_score', 0)} điểm`\n"
        f"📖 **Từ vựng đã học:** `{user_data.get('vocab_learned', 0)} từ`\n"
        f"🪙 **Số Xu Sakura:** `{user_data['coins']:,} xu`\n"
        f"🎮 **Số ván thắng Arcade:** `{user_data['arcade_wins']} ván`\n"
        f"💡 **Số lượt gợi ý:** `{user_data['hints']} lượt`\n"
        f"🎒 **Kho đồ:** `{inv_str}`\n\n"
        f"{BotConfig.THICK_BORDER}"
    )
    await ctx.send(embed=UIUtils.create_embed("Hồ Sơ Người Dùng Sakura Ultimate Extended", desc, BotConfig.COLOR_SAKURA_PINK))

@bot.command(name="daily")
async def sys_daily(ctx: commands.Context) -> None:
    user_id = ctx.author.id
    user_data = UserDataManager.get_user(user_id)
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    if user_data.get("last_daily") == today_str:
        await ctx.send(embed=UIUtils.build_warning_embed("Điểm Danh Hàng Ngày", "Bạn đã nhận quà điểm danh trong ngày hôm nay rồi. Hãy quay lại vào ngày mai nhé!"))
        return
        
    reward_coins = random.randint(400, 800)
    reward_hints = random.randint(5, 10)
    new_coins = user_data["coins"] + reward_coins
    new_hints = user_data["hints"] + reward_hints
    
    UserDataManager.update_user(user_id, coins=new_coins, hints=new_hints, last_daily=today_str)
    
    desc = (
        f"{BotConfig.THICK_BORDER}\n\n"
        f"🎉 Chúc mừng {ctx.author.mention} đã điểm danh thành công ngày hôm nay!\n"
        f"🪙 Phần thưởng xu: **`+{reward_coins} xu`**\n"
        f"💡 Thẻ gợi ý nhận thêm: **`+{reward_hints} lượt`**\n\n"
        f"💰 Tổng tài sản hiện tại: **`{new_coins:,} xu`**\n\n"
        f"{BotConfig.THICK_BORDER}"
    )
    await ctx.send(embed=UIUtils.create_embed("Quà Điểm Danh Thành Công", desc, BotConfig.COLOR_GOLD))

@bot.command(name="shop")
async def sys_shop(ctx: commands.Context) -> None:
    desc = (
        f"{BotConfig.THICK_BORDER}\n\n"
        f"🖤 **CỬA HÀNG VẬT PHẨM SAKURA GOTHIC ULTIMATE EXTENDED** 🌸\n\n"
        f"1️⃣ **Thẻ Gợi Ý Cao Cấp (+30 lượt)** - Giá: `600 xu`\n> *Lệnh mua:* `{BotConfig.PREFIX}mua goi_y`\n\n"
        f"2️⃣ **Danh Hiệu 'Sakura Gothic Master Ultimate'** - Giá: `3000 xu`\n> *Lệnh mua:* `{BotConfig.PREFIX}mua danh_hieu`\n\n"
        f"3️⃣ **Hộp Quà Thần Bí Sakura** - Giá: `400 xu`\n> *Lệnh mua:* `{BotConfig.PREFIX}mua hop_qua`\n\n"
        f"{BotConfig.THICK_BORDER}"
    )
    await ctx.send(embed=UIUtils.create_embed("Cửa Hàng Vật Phẩm Mở Rộng", desc, BotConfig.COLOR_PURPLE))

@bot.command(name="mua")
async def sys_buy(ctx: commands.Context, item_name: str = "") -> None:
    user_id = ctx.author.id
    user_data = UserDataManager.get_user(user_id)
    item_lower = item_name.lower()
    
    if item_lower == "goi_y":
        cost = 600
        if user_data["coins"] < cost:
            await ctx.send(embed=UIUtils.build_warning_embed("Thiếu Xu", f"Bạn cần ít nhất `{cost} xu` để mua vật phẩm này!"))
            return
        new_coins = user_data["coins"] - cost
        new_hints = user_data["hints"] + 30
        inv = user_data["inventory"]
        inv.append("Thẻ Gợi Ý Cao Cấp (+30)")
        UserDataManager.update_user(user_id, coins=new_coins, hints=new_hints, inventory=inv)
        await ctx.send(embed=UIUtils.create_embed("Giao Dịch Thành Công", f"Bạn đã mua thành công **Thẻ Gợi Ý Cao Cấp (+30)**! Số xu còn lại: `{new_coins:,} xu`.", BotConfig.COLOR_SAKURA_PINK))
        
    elif item_lower == "danh_hieu":
        cost = 3000
        if user_data["coins"] < cost:
            await ctx.send(embed=UIUtils.build_warning_embed("Thiếu Xu", f"Bạn cần ít nhất `{cost} xu` để sở hữu danh hiệu độc quyền này!"))
            return
        new_coins = user_data["coins"] - cost
        UserDataManager.update_user(user_id, coins=new_coins, title="Sakura Gothic Master Ultimate 🖤👑✨")
        await ctx.send(embed=UIUtils.create_embed("Sở Hữu Danh Hiệu Mới", f"Chúc mừng bạn đã sở hữu danh hiệu tối cao: **Sakura Gothic Master Ultimate 🖤👑✨**!", BotConfig.COLOR_GOLD))
        
    elif item_lower == "hop_qua":
        cost = 400
        if user_data["coins"] < cost:
            await ctx.send(embed=UIUtils.build_warning_embed("Thiếu Xu", f"Bạn cần ít nhất `{cost} xu` để mở hộp quà!"))
            return
        new_coins = user_data["coins"] - cost
        bonus_coins = random.randint(300, 1200)
        final_coins = new_coins + bonus_coins
        UserDataManager.update_user(user_id, coins=final_coins)
        await ctx.send(embed=UIUtils.create_embed("Mở Hộp Quà Thần Bí", f"Bạn mở hộp quà thần bí và nhận được phần thưởng: **`+{bonus_coins} xu`**! Tổng xu: `{final_coins:,} xu`.", BotConfig.COLOR_SAKURA_PINK))
    else:
        await ctx.send(embed=UIUtils.build_warning_embed("Sai Cú Pháp", f"Vật phẩm không tồn tại. Vui lòng kiểm tra danh sách trong `{BotConfig.PREFIX}shop`."))

# ====================================================================================================
# PHẦN 9: CÁC LỆNH TỪ VỰNG, TOÁN HỌC, ĐỐ VUI & NỐI TỪ NÂNG CAO MỞ RỘNG
# ====================================================================================================

active_trivia_sessions: Dict[int, dict] = {}

@bot.command(name="tuvung", aliases=["vocab", "tudien"])
async def cmd_tuvung(ctx: commands.Context, *, word: str = "") -> None:
    if not word:
        await ctx.send(embed=UIUtils.build_warning_embed("Thiếu Từ Tra Cứu", f"Vui lòng nhập từ cần tra. Ví dụ: `{BotConfig.PREFIX}tuvung resilience`"))
        return
    
    clean_word = word.strip().lower()
    meaning = FULL_VOCABULARY_MAP.get(clean_word)
    
    if not meaning:
        if clean_word in ENGLISH_DICT or clean_word in COMBINED_VIETNAMESE_DICTIONARY:
            meaning = "Từ này có trong hệ thống dữ liệu từ điển nhưng chưa cập nhật định nghĩa chi tiết. Bạn được cộng 10 xu khám phá!"
        else:
            await ctx.send(embed=UIUtils.build_warning_embed("Không Tìm Thấy", f"Không tìm thấy từ `{word}` trong cơ sở dữ liệu từ điển Sakura v9.6.5."))
            return

    user_id = ctx.author.id
    user_data = UserDataManager.get_user(user_id)
    new_vocab_count = user_data.get("vocab_learned", 0) + 1
    new_coins = user_data["coins"] + 15
    UserDataManager.update_user(user_id, vocab_learned=new_vocab_count, coins=new_coins)

    desc = (
        f"{BotConfig.THICK_BORDER}\n\n"
        f"📖 **Từ vựng:** `{word.upper()}`\n"
        f"💡 **Ý nghĩa / Giải thích:** *{meaning}*\n\n"
        f"⭐ **Thống kê cá nhân:** Đã tra cứu `{new_vocab_count} từ` (+15 xu)\n\n"
        f"{BotConfig.THICK_BORDER}"
    )
    await ctx.send(embed=UIUtils.create_embed("Tra Cứu Từ Vựng Chuyên Sâu", desc, BotConfig.COLOR_CYAN))

@bot.command(name="thuvientuvung", aliases=["vocablib", "randomvocab"])
async def cmd_thuvientuvung(ctx: commands.Context) -> None:
    if not FULL_VOCABULARY_MAP:
        await ctx.send(embed=UIUtils.build_warning_embed("Trống", "Kho từ vựng hiện đang cập nhật."))
        return
    
    rand_word, rand_meaning = random.choice(list(FULL_VOCABULARY_MAP.items()))
    desc = (
        f"{BotConfig.THICK_BORDER}\n\n"
        f"✨ **Từ vựng ngẫu nhiên hôm nay:** `{rand_word.upper()}`\n"
        f"📚 **Định nghĩa:** *{rand_meaning}*\n\n"
        f"💡 Gõ `{BotConfig.PREFIX}tuvung <từ>` để tra cứu thêm nhiều từ vựng khác!\n\n"
        f"{BotConfig.THICK_BORDER}"
    )
    await ctx.send(embed=UIUtils.create_embed("Thư Viện Từ Vựng Sakura Mở Rộng", desc, BotConfig.COLOR_PURPLE))

@bot.command(name="toanhoc", aliases=["math", "giaotoan", "mathgame"])
async def cmd_toanhoc(ctx: commands.Context) -> None:
    session = math_manager.get_session(ctx.channel.id)
    question, answer, explanation, category = math_manager.generate_random_problem()
    
    session.active = True
    session.answer = answer
    session.question = question
    session.explanation = explanation
    session.category = category

    desc = f"{BotConfig.THICK_BORDER}\n\n{question}\n\n⏱️ **Thể loại:** `{category}`\n💡 Gõ trực tiếp đáp án số học của bạn vào khung chat bên dưới để nhận phần thưởng khủng!\n\n{BotConfig.THICK_BORDER}"
    await ctx.send(embed=UIUtils.create_embed("Thử Thách Toán Học Ultimate Extended", desc, BotConfig.COLOR_SAKURA_PINK))

@bot.command(name="dovui", aliases=["trivia", "quiz"])
async def cmd_dovui(ctx: commands.Context) -> None:
    trivia = random.choice(TRIVIA_QUESTIONS)
    active_trivia_sessions[ctx.channel.id] = trivia
    
    desc = f"{BotConfig.THICK_BORDER}\n\n🧠 **Câu hỏi:** {trivia['q']}\n💡 **Gợi ý:** `{trivia['hint']}`\n\n✍️ Gõ đáp án của bạn vào khung chat ngay bên dưới!\n\n{BotConfig.THICK_BORDER}"
    await ctx.send(embed=UIUtils.create_embed("Minigame Đố Vui Kiến Thức Mở Rộng", desc, BotConfig.COLOR_CYAN))

@bot.command(name="noitu")
async def cmd_noitu(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: 
        await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván chơi nối từ diễn ra trong kênh này."))
        return
    start_word = random.choice(EASY_START_LIST)
    syllables = start_word.split()
    session.initialize_session(GameMode.PVP_VIETNAMESE, start_word=start_word)
    
    desc = (
        f"{BotConfig.THICK_BORDER}\n\n"
        f"👉 Từ khởi đầu: **`{start_word.upper()}`**\n"
        f"🌸 Từ tiếp theo phải bắt đầu bằng: **`{syllables[-1].upper()}`**\n\n"
        f"💡 Gõ từ tiếp theo hợp lệ vào chat để tham gia!\n\n"
        f"{BotConfig.THICK_BORDER}"
    )
    await ctx.send(embed=UIUtils.create_embed("Nối Từ Tiếng Việt PvP Ultimate", desc, BotConfig.COLOR_SAKURA_PINK))

@bot.command(name="botnoitu", aliases=["noituubot"])
async def cmd_botnoitu(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: 
        await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván chơi nối từ diễn ra trong kênh này."))
        return
    start_word = random.choice(EASY_START_LIST)
    syllables = start_word.split()
    session.initialize_session(GameMode.BOT_VIETNAMESE, start_word=start_word)
    
    desc = (
        f"{BotConfig.THICK_BORDER}\n\n"
        f"👉 Từ khởi đầu: **`{start_word.upper()}`**\n"
        f"🌸 Từ tiếp theo phải bắt đầu bằng: **`{syllables[-1].upper()}`**\n\n"
        f"🤖 Bot AI đã sẵn sàng đối đầu với bạn!\n\n"
        f"{BotConfig.THICK_BORDER}"
    )
    await ctx.send(embed=UIUtils.create_embed("Solo Nối Từ Với Bot AI", desc, BotConfig.COLOR_NEON_BLUE))

@bot.command(name="noitueng")
async def cmd_noitueng(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván chơi diễn ra trong kênh này."))
        return
    start_word = random.choice(list(ENGLISH_DICT))
    session.initialize_session(GameMode.PVP_ENGLISH, start_word=start_word)
    
    desc = (
        f"{BotConfig.THICK_BORDER}\n\n"
        f"👉 Từ khởi đầu tiếng Anh: **`{start_word.upper()}`**\n"
        f"🌸 Từ tiếp theo phải bắt đầu bằng chữ cái: **`{start_word[-1].upper()}`**\n\n"
        f"🌐 Hỗ trợ toàn bộ kho từ điển tiếng Anh và từ vựng nâng cao!\n\n"
        f"{BotConfig.THICK_BORDER}"
    )
    await ctx.send(embed=UIUtils.create_embed("Nối Từ Tiếng Anh Ultimate", desc, BotConfig.COLOR_PURPLE))

@bot.command(name="huyvanchoi", aliases=["end", "stop"])
async def cmd_huyvanchoi(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    math_session = math_manager.get_session(ctx.channel.id)
    session.reset()
    math_session.active = False
    if ctx.channel.id in active_trivia_sessions:
        del active_trivia_sessions[ctx.channel.id]
        
    desc = f"{BotConfig.THICK_BORDER}\n\n🛑 Đã hủy tất cả các ván chơi và minigame trong kênh này theo yêu cầu của {ctx.author.mention}!\n\n{BotConfig.THICK_BORDER}"
    await ctx.send(embed=UIUtils.create_embed("Hủy Ván Chơi", desc, BotConfig.COLOR_BLACK_CHIC))

@bot.command(name="meme")
async def cmd_meme(ctx: commands.Context) -> None:
    async with aiohttp.ClientSession() as session_http:
        try:
            async with session_http.get("https://meme-api.com/gimme") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    title = data.get("title", "Meme Ngẫu Nhiên")
                    url = data.get("url")
                    embed = UIUtils.create_embed(f"🖼️ {title}", "Meme giải trí độc quyền từ Sakura Ultimate Extended", BotConfig.COLOR_SAKURA_PINK, image_url=url)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(embed=UIUtils.build_warning_embed("Meme API", "Không thể tải meme lúc này!"))
        except Exception:
            await ctx.send(embed=UIUtils.build_warning_embed("Meme API", "Lỗi kết nối API meme!"))

# ====================================================================================================
# PHẦN 10: XỬ LÝ SỰ KIỆN TIN NHẮN (MESSAGE LISTENER MỞ RỘNG CHO TOÁN HỌC, ĐỐ VUI & NỐI TỪ)
# ====================================================================================================

@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot or not message.guild: return
    content = message.content.strip()
    if content.startswith(BotConfig.PREFIX):
        await bot.process_commands(message)
        return

    # 1. Kiểm tra trả lời Đố vui (Trivia)
    if message.channel.id in active_trivia_sessions:
        trivia_data = active_trivia_sessions[message.channel.id]
        if content.lower() == trivia_data["ans"]:
            del active_trivia_sessions[message.channel.id]
            user_data = UserDataManager.get_user(message.author.id)
            new_trivia_score = user_data.get("trivia_score", 0) + 1
            new_coins = user_data["coins"] + 250
            UserDataManager.update_user(message.author.id, trivia_score=new_trivia_score, coins=new_coins)
            
            desc = (
                f"{BotConfig.THICK_BORDER}\n\n"
                f"🎉 **CHÍNH XÁC!** {message.author.mention} đã trả lời đúng đáp án: **`{trivia_data['ans'].upper()}`**!\n\n"
                f"🧠 **Điểm đố vui:** `{new_trivia_score} điểm` (+1)\n"
                f"🪙 **Phần thưởng xu:** `+250 xu` (Tổng: `{new_coins:,} xu`) 🌸\n\n"
                f"{BotConfig.THICK_BORDER}"
            )
            await message.reply(embed=UIUtils.create_embed("Thắng Minigame Đố Vui", desc, BotConfig.COLOR_GOLD), mention_author=True)
            await message.add_reaction(BotConfig.EMOJI_TICK)
            return

    # 2. Kiểm tra trả lời Toán học mở rộng
    math_session = math_manager.get_session(message.channel.id)
    if math_session.active:
        try:
            clean_ans_str = content.replace(',', '.')
            user_ans = float(clean_ans_str)
            if abs(user_ans - math_session.answer) < 1e-2:
                math_session.active = False
                user_data = UserDataManager.get_user(message.author.id)
                new_score = user_data["math_score"] + 30
                new_coins = user_data["coins"] + 200
                UserDataManager.update_user(message.author.id, math_score=new_score, coins=new_coins)
                
                desc = (
                    f"{BotConfig.THICK_BORDER}\n\n"
                    f"🎉 **CHÍNH XÁC TUYỆT ĐỐI!** {message.author.mention} đã giải đúng đáp án **`{math_session.answer}`**!\n\n"
                    f"📚 **Giải thích chi tiết:**\n{math_session.explanation}\n\n"
                    f"⭐ **Điểm toán học:** `{new_score} điểm` (+30)\n"
                    f"🪙 **Phần thưởng xu:** `+200 xu` (Tổng: `{new_coins:,} xu`) 🌸\n\n"
                    f"{BotConfig.THICK_BORDER}"
                )
                await message.reply(embed=UIUtils.create_embed("Thắng Thử Thách Toán Học", desc, BotConfig.COLOR_GOLD), mention_author=True)
                await message.add_reaction(BotConfig.EMOJI_TICK)
                return
        except ValueError:
            pass

    # 3. Xử lý Nối từ tiếng Việt & Tiếng Anh toàn diện
    session = global_session_manager.get_session(message.channel.id)
    if session.is_active:
        content_lower = content.lower()
        parts = content_lower.split()
        
        if session.active_mode in [GameMode.PVP_VIETNAMESE, GameMode.BOT_VIETNAMESE] and len(parts) >= 2:
            last_syllable = session.current_word.split()[-1]
            if parts[0] == last_syllable and (content_lower in COMBINED_VIETNAMESE_DICTIONARY or content_lower in RAW_VIETNAMESE_DICT) and content_lower not in session.used_words_history:
                session.current_word = content_lower
                session.used_words_history.add(content_lower)
                await message.add_reaction(BotConfig.EMOJI_TICK)
                
                if session.active_mode == GameMode.BOT_VIETNAMESE:
                    bot_last_syl = parts[-1]
                    possible_words = VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.get(bot_last_syl, [])
                    valid_bot_words = [w for w in possible_words if w not in session.used_words_history]
                    if valid_bot_words:
                        bot_word = random.choice(valid_bot_words)
                        session.current_word = bot_word
                        session.used_words_history.add(bot_word)
                        
                        bot_desc = (
                            f"{BotConfig.THICK_BORDER}\n\n"
                            f"👉 Bot nói: **`{bot_word.upper()}`**\n"
                            f"🌸 Từ tiếp theo phải bắt đầu bằng: **`{bot_word.split()[-1].upper()}`**\n\n"
                            f"{BotConfig.THICK_BORDER}"
                        )
                        await message.channel.send(embed=UIUtils.create_embed("Bot AI Nối Từ", bot_desc, BotConfig.COLOR_NEON_BLUE))

        elif session.active_mode == GameMode.PVP_ENGLISH and len(parts) == 1:
            last_char = session.current_word[-1]
            if content_lower[0] == last_char and (content_lower in ENGLISH_DICT or content_lower in FULL_VOCABULARY_MAP) and content_lower not in session.used_words_history:
                session.current_word = content_lower
                session.used_words_history.add(content_lower)
                await message.add_reaction(BotConfig.EMOJI_TICK)

    await bot.process_commands(message)

# ====================================================================================================
# PHẦN 11: KHỞI CHẠY HỆ THỐNG ULTIMATE BOT EXTENDED ARCHITECTURE
# ====================================================================================================
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        logger.error("❌ Không tìm thấy DISCORD_TOKEN trong biến môi trường hệ thống!")
    else:
        bot.run(TOKEN)
