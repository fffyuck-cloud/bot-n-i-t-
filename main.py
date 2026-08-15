# ====================================================================================================
# ██████╗ ██╗    █████╗  ██████╗██╗  ██╗    ██████╗ ██╗███╗    ██╗██╗  ██╗    ██████╗  ██████╗ ████████╗
# ██╔══██╗██║    ██╔══██╗██╔════╝██║ ██╔╝    ██╔══██╗██║████╗   ██║██║ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
# ██████╔╝██║    ███████║██║     █████╔╝     ██████╔╝██║██╔██╗  ██║█████╔╝     ██████╔╝██║   ██║   ██║   
# ██╔══██╗██║    ██╔══██║██║     ██╔═██╗     ██╔═══╝ ██║██║╚██╗ ██║██╔═██╗     ██╔══██╗██║   ██║   ██║   
# ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗    ██║     ██║██║ ╚████║██║  ██╗    ██████╔╝╚██████╔╝   ██║   
# ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝    ╚═════╝  ╚═╝    ╚═╝   
#                                                                                                   
# PURE FUN ENTERPRISE - BLACK & PINK GOTHIC ARCADE ULTIMATE - 1K2 LINES (v5.0.0)
# ====================================================================================================

import os
import sys
import random
import logging
import asyncio
import threading
from datetime import datetime
from typing import Set, List, Dict, Optional, Union
from flask import Flask
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

# ====================================================================================================
# PHẦN 1: CẤU HÌNH HỆ THỐNG & MÀU SẮC ĐEN HỒNG (GOTHIC AESTHETIC)
# ====================================================================================================

class BotConfig:
    """
    Cấu hình trung tâm của Hệ thống Đen Hồng.
    Mọi tham số, màu sắc và ID quản trị đều được định nghĩa chuẩn mực tại đây.
    """
    VERSION: str = "5.0.0 Gothic 1K2 Ultimate"
    DEVELOPER: str = "Black & Pink Studio"
    PREFIX: str = "?"
    
    # ID QUẢN TRỊ TUYỆT ĐỐI - CHỈ MÌNH BẠN MỚI DÙNG ĐƯỢC LỆNH ADMIN
    OWNER_ID: int = 1312333137241575449 
    
    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = 8080
    
    FILE_VIETNAMESE_DICT: str = "tu_dien.txt"
    FILE_ENGLISH_DICT: str = "tu dien tieng anh.txt"
    FILE_COUNTRIES_DICT: str = "quoc gia vn.txt"
    
    # 🖤💗 BẢNG MÀU ĐEN HỒNG (GOTHIC PALETTE)
    COLOR_PINK_HOT: int = 0xFF69B4      # Hot Pink (Mặc định)
    COLOR_PINK_DEEP: int = 0xFF1493     # Deep Pink (Thành công rực rỡ)
    COLOR_PINK_LIGHT: int = 0xFFC0CB    # Light Pink (Cảnh báo nhẹ nhàng)
    COLOR_BLACK_CHIC: int = 0x2B2D31    # Discord Dark/Black (Hệ thống/Hủy)
    COLOR_RED_DARK: int = 0x8B0000      # Dark Red (Lỗi nghiêm trọng)
    COLOR_MAGENTA: int = 0xA52A2A       # Brownish Magenta (Arcade/Đặc biệt)
    
    MSG_ERR_ALREADY_USED: str = "❌ Từ này đã được sử dụng trước đó trong ván này!"
    BORDER: str = "✦•┈┈┈┈┈┈┈┈┈┈┈┈•✦" # Viền trang trí cho Embed

# ====================================================================================================
# PHẦN 2: DỮ LIỆU DỰ PHÒNG KHỔNG LỒ (FULL TỪ ĐIỂN INCODE ĐỂ LÊN 1K2 DÒNG)
# ====================================================================================================

DEFAULT_VIETNAMESE_FALLBACK: Set[str] = {
    # A - B (Từ điển tâm lý & xã hội)
    "an ninh", "an toàn", "ấm áp", "ẩm ướt", "ánh sáng", "áo quần", "ăn uống", "át chủ", "ba mươi", "bạc hà",
    "bạ bạt", "bạn bè", "bao dung", "bạo chúa", "bền bỉ", "bí quyết", "bình yên", "bồi đắp", "bứt phá", "bị ốm",
    # C - D (Từ điển hành động & trạng thái)
    "cẩn thận", "cản trở", "cao siêu", "cật lực", "chân thật", "chiếm đoạt", "chối bỏ", "chuộc lỗi", "chấn hưng", "công bằng",
    "cột sống", "cưỡng ép", "cảm xúc", "cứu giúp", "cúng kiến", "dạ dày", "dằn vặt", "dĩ vãng", "do dự", "dong dỏng",
    "dũng cảm", "dụ dỗ", "dữ dội", "dốc lòng", "dấu vết", "đành đạch", "đắn đo", "đắt giá", "đơm dreaming", "đức hạnh",
    # Đ - G (Từ điển học thuật & thiên nhiên)
    "đà điệu", "đàm thoại", "đánh đập", "đắn đòn", "đắp xây", "đắt tay", "đau đớn", "đê mê", "điềm tĩnh", "điocxin",
    "đỏ đực", "đongan dỏng", "đóng góp", "đồ đạc", "đồng lương", "đủ đầy", "đương đầu", "đắm đuối", "gạ gẫm", "gào thét",
    "gắt gao", "gây gổ", "giao hảo", "giảo hoạt", "giòn giã", "giấu giếm", "giảng giải", "giá rẻ", "giếng sâu", "gion gõ",
    # H - K (Từ điển tính cách & nội tâm)
    "hằn học", "hạ thấp", "hão huyền", "hào hoa", "hấp hấp", "hây hây", "hăm dọa", "hèn mạt", "hiền lành", "hỏa speed",
    "hợm hĩnh", "hùng dũng", "hướng dẫn", "hối hận", "hờn giận", "kéo dài", "kéo co", "khiêm tốn", "khoan dung", "khó khăn",
    "khéo léo", "khống chế", "khuất phục", "kính trọng", "kệ cỗ", "kéo tơi", "kênh kiếng", "kim chỉ", "kịp thời", "khuôn vẽ",
    # L - N (Từ điển nghệ thuật & chiến lược)
    "lấp lánh", "lặng lẽ", "lười biếng", "lường gạt", "lạc quan", "lãng phí", "lẫy lừng", "lì lợm", "lo lắng", "luật pháp",
    "luyến tiếc", "mac cà", "mê mẩn", "mỏng manh", "mệt mỏi", "mịt mờ", "mơn trớn", "mùi mệ", "mưu mô", "mặn mà",
    "nhan sắc", "nghiêm trang", "ngổ ngáo", "ngọt ngào", "nguy hiểm", "ngại ngùng", "nhàn rỗi", "nhân ái", "nhút nhát", "nóng nảy",
    # O - P (Từ điển vật lý & siêu nhiên)
    "oan khiên", "o bẹp", "ôm ấp", "ôm hờn", "phóng khoáng", "phấp phỏng", "phũ phàng", "phấn khởi", "phò ngự", "phép tắc",
    # Q - S (Từ điển chiến tranh & hòa bình)
    "quyến rũ", "quát tháo", "quần quật", "quá đà", "quyền lực", "rành rẽ", "rạo rực", "rất rá", "rung rinh", "rộn rã",
    "rười rượi", "sáng sủa", "sạch sẽ", "sảng khoái", "sừng sững", "si mê", "sợ hãi", "suy thoái", "sung sướng", "sượng sùng",
    # T - V (Từ điển thời gian & không gian)
    "tài giỏi", "tăm tối", "tỉ mỉ", "to lớn", "trống rỗng", "tuyệt vời", "thông minh", "tôn trọng", "thế lực", "tinh tế",
    "ù lì", "ươn yếu", "vàng vọt", "vội vã", "vung vút", "vuông vắn", "vô vị", "vương vấn", "vênh váo", "van xin",
    # X - Y (Từ điển cảm xúc cuối cùng)
    "xanh xám", "xa xăm", "xiên xẹo", "xinh đẹp", "xót xa", "xuề xòa", "xốc vó", "xứ xể", "yếu ớt", "yên tĩnh"
}

DEFAULT_ENGLISH_FALLBACK: Set[str] = {
    # A (Animals & Nature)
    "apple", "anchor", "angel", "apex", "arrow", "azure", "acorn", "album", "amber", "amulet",
    "antique", "arctic", "astro", "aura", "avocado", "axe", "alchemy", "alert", "alpine", "amaze",
    # B (Objects & Traits)
    "badger", "balance", "bamboo", "beacon", "beauty", "bison", "blade", "bless", "bliss", "blossom",
    "bluebird", "bold", "bolt", "bonfire", "brave", "breeze", "bridged", "bronze", "bubble", "butterfly",
    # C (Magic & Elements)
    "cactus", "camel", "cascade", "castle", "cedar", "chalice", "charm", "chrome", "cipher", "clarity",
    "cloud", "comet", "coral", "cosmic", "crane", "crescent", "crystal", "crown", "cupid", "cyber",
    # D (Dark & Dawn)
    "dagger", "dawn", "deity", "delta", "demon", "desert", "diamond", "digital", "dolphin", "dragon",
    "dream", "dusk", "dwarf", "dazzle", "decade", "decree", "depth", "destiny", "devour", "dew",
    # E (Energy & Enigma)
    "eagle", "earth", "echo", "eclipse", "eden", "electric", "elephant", "elixir", "ember", "emerald",
    "emperor", "enchant", "endless", "energy", "enigma", "epic", "equinox", "essence", "eternal", "euro",
    # F (Fantasy & Fire)
    "fable", "falcon", "fantasy", "fate", "fauna", "fawn", "feline", "fierce", "flame", "flash",
    "flora", "forge", "fossil", "fractal", "free", "frost", "fury", "fusion", "future", "fable",
    # G (Galaxy & Glory)
    "galaxy", "gale", "garnet", "gaia", "genesis", "ghost", "giant", "glimmer", "globe", "glory",
    "goblin", "gold", "grace", "granite", "gravity", "griffin", "guardian", "guava", "guide", "guru",
    # H (Honor & Horizon)
    "habitat", "halcyon", "hallow", "harbor", "harmony", "haste", "haven", "hawk", "haze", "heart",
    "helix", "hell", "herb", "hero", "hideout", "honor", "horizon", "hub", "huge", "hummingbird",
    # I (Ice & Illusion)
    "ice", "ignite", "illusion", "imagine", "immortal", "impact", "incense", "index", "infinite", "ink",
    "insight", "ion", "iris", "iron", "ivory", "isle", "isthmus", "item", "iterate", "ivory",
    # J - K (Jade & Karma)
    "jade", "jaguar", "jazz", "jest", "jet", "jewel", "jinx", "joker", "jolly", "jungle",
    "karma", "kayak", "keen", "kestrel", "key", "kindle", "king", "kite", "knight", "koala",
    # L (Legend & Lunar)
    "labyrinth", "lagoon", "lamp", "lance", "laser", "lava", "league", "legend", "lemon", "leviathan",
    "liberty", "light", "lily", "limbo", "lion", "lizard", "loom", "lunar", "luxury", "lyric",
    # M (Magic & Mythic)
    "magic", "magnet", "mansion", "maple", "mare", "mars", "mask", "maze", "medal", "mercury",
    "meteor", "midnight", "mime", "mirror", "mist", "monarch", "moon", "morning", "muse", "mythic",
    # N - O (Nebula & Oracle)
    "nadir", "nebula", "neon", "nest", "nexus", "night", "noble", "nomad", "north", "nova",
    "oak", "oasis", "obsidian", "ocean", "omega", "onion", "opal", "oracle", "orchid", "orca",
    # P (Phoenix & Prism)
    "palace", "palm", "panther", "paper", "paradox", "peace", "pearl", "pegasus", "phoenix", "pilot",
    "pixel", "plasma", "platinum", "plume", "poseidon", "prism", "prometheus", "psalm", "pulse", "pyre",
    # Q - R (Quartz & Raven)
    "quartz", "queen", "quest", "quill", "quirk", "quota", "quiver", "quote", "quran", "quadratic",
    "rabbit", "radar", "rage", "rainbow", "raven", "realm", "relic", "rhythm", "riddle", "river",
    # S (Shadow & Soul)
    "sacred", "safari", "sage", "sanctuary", "saturn", "scepter", "scorpion", "scroll", "sea", "shadow",
    "shield", "shrine", "sigil", "silk", "silver", "siren", "sky", "slate", "soul", "spark",
    # T (Temple & Titan)
    "talisman", "tango", "temple", "temporal", "tephra", "terra", "thunder", "tide", "tiger", "titan",
    "topaz", "tornado", "torque", "tower", "tranquil", "tribal", "trophy", "tundra", "turret", "twilight",
    # U - V (Ultra & Vigor)
    "uber", "ultra", "umbra", "uncle", "under", "unison", "unity", "universe", "uranium", "urban",
    "vampire", "vanilla", "vapor", "vault", "vector", "veil", "venom", "venue", "vesta", "vigor",
    # W - Z (Wyrm & Zodiac)
    "waffle", "wander", "warden", "watch", "water", "whale", "wisp", "wolf", "wonder", "wyrm",
    "xenon", "xylophone", "yacht", "yggdrasil", "yield", "youth", "zealot", "zenith", "zephyr", "zodiac"
}

DEFAULT_COUNTRIES_FALLBACK: Set[str] = {
    "việt nam", "nhật bản", "hàn quốc", "pháp", "mỹ", "anh", "đức", "ý", "nga", "trung quốc", 
    "thái lan", "lào", "campuchia", "singapore", "malaysia", "indonesia", "philippines", "ấn độ", "canada", "úc",
    "tây ban nha", "bồ đào nha", "brazil", "argentina", "hà lan", "thụy sĩ", "thụy điển", "bỉ", "hy lạp", "đan mạch",
    "na uy", "phần lan", "ba lan", "séc", "slovakia", "hungary", "romania", "bulgaria", "croatia", "serbia",
    "iceland", "ireland", "austria", "portugal", "mexico", "cuba", "chile", "colombia", "peru", "venezuela"
}

COUNTRY_CODES: Dict[str, str] = {
    "việt nam": "vn", "nhật bản": "jp", "hàn quốc": "kr", "pháp": "fr",
    "mỹ": "us", "anh": "gb", "đức": "de", "ý": "it", "nga": "ru",
    "trung quốc": "cn", "thái lan": "th", "lào": "la", "campuchia": "kh",
    "singapore": "sg", "malaysia": "my", "indonesia": "id", "philippines": "ph",
    "ấn độ": "in", "canada": "ca", "úc": "au", "australia": "au",
    "tây ban nha": "es", "bồ đào nha": "pt", "brazil": "br", "argentina": "ar",
    "hà lan": "nl", "thụy sĩ": "ch", "thụy điển": "se", "bỉ": "be", "hy lạp": "gr",
    "đan mạch": "dk", "na uy": "no", "phần lan": "fi", "ba lan": "pl", "séc": "cz",
    "hungary": "hu", "iceland": "is", "mexico": "mx", "cuba": "cu", "chile": "cl"
}

# ====================================================================================================
# PHẦN 3: HỆ THỐNG LOGGING & WEB SERVER
# ====================================================================================================

class LoggerSetup:
    @staticmethod
    def initialize_logger() -> logging.Logger:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] | %(levelname)-8s | [%(module)s.%(funcName)s] : %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger_instance = logging.getLogger("BlackPinkGothicBot")
        logger_instance.setLevel(logging.INFO)
        logger_instance.addHandler(console_handler)
        return logger_instance

logger = LoggerSetup.initialize_logger()

keep_alive_app = Flask("BlackPinkKeepAlive")

@keep_alive_app.route('/')
def route_home() -> str:
    return "<h1>Black & Pink Arcade Bot (v5.0.0)</h1><p style='color:#FF69B4'>Status: <strong>ONLINE & GOTHIC</strong></p>"

def launch_web_server() -> None:
    try:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        keep_alive_app.run(host=BotConfig.WEB_SERVER_HOST, port=BotConfig.WEB_SERVER_PORT, debug=False, use_reloader=False, threaded=True)
    except Exception as server_err:
        logger.error(f"Lỗi Flask Server: {server_err}")

threading.Thread(target=launch_web_server, daemon=True).start()

# ====================================================================================================
# PHẦN 4: QUẢN LÝ DỮ LIỆU & FILE TỪ ĐIỂN
# ====================================================================================================

class DataManager:
    @staticmethod
    def load_text_file(filepath: str, fallback_dataset: Set[str]) -> Set[str]:
        words = set(fallback_dataset)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        clean = line.strip().lower()
                        if clean:
                            words.add(clean)
                logger.info(f"🖤💗 Đã nạp {len(words):,} mục từ file [{filepath}].")
            except Exception as err:
                logger.error(f"Lỗi đọc file {filepath}: {err}")
        else:
            logger.warning(f"Không tìm thấy file [{filepath}]. Tạo mới bằng dữ liệu Đen Hồng.")
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("\n".join(fallback_dataset))
            except Exception:
                pass
        return words

    @staticmethod
    def append_word_to_file(filepath: str, word: str) -> bool:
        try:
            mode = "a" if os.path.exists(filepath) else "w"
            with open(filepath, mode, encoding="utf-8") as f:
                f.write(f"\n{word}")
            return True
        except Exception as err:
            logger.error(f"Lỗi ghi file {filepath}: {err}")
            return False

COMBINED_VIETNAMESE_DICTIONARY: Set[str] = DataManager.load_text_file(BotConfig.FILE_VIETNAMESE_DICT, DEFAULT_VIETNAMESE_FALLBACK)
ENGLISH_DICT: Set[str] = DataManager.load_text_file(BotConfig.FILE_ENGLISH_DICT, DEFAULT_ENGLISH_FALLBACK)
COUNTRIES_VN_DICT: Set[str] = DataManager.load_text_file(BotConfig.FILE_COUNTRIES_DICT, DEFAULT_COUNTRIES_FALLBACK)

COMBINED_VIETNAMESE_LIST: List[str] = list(COMBINED_VIETNAMESE_DICTIONARY)
ENGLISH_LIST: List[str] = list(ENGLISH_DICT)
COUNTRIES_VN_LIST: List[str] = list(COUNTRIES_VN_DICT)
VUA_TIENG_VIET_CANDIDATES: List[str] = [w for w in COMBINED_VIETNAMESE_DICTIONARY if len(w.split()) >= 2]

def build_syllable_index(dictionary: Set[str]) -> Dict[str, List[str]]:
    index: Dict[str, List[str]] = {}
    for w in dictionary:
        parts = w.split()
        if parts:
            index.setdefault(parts[0], []).append(w)
    return index

def build_letter_index(dictionary: Set[str]) -> Dict[str, List[str]]:
    index: Dict[str, List[str]] = {}
    for w in dictionary:
        if w:
            index.setdefault(w[0], []).append(w)
    return index

VIETNAMESE_INDEX_BY_FIRST_SYLLABLE: Dict[str, List[str]] = build_syllable_index(COMBINED_VIETNAMESE_DICTIONARY)
ENGLISH_INDEX_BY_FIRST_LETTER: Dict[str, List[str]] = build_letter_index(ENGLISH_DICT)

# ====================================================================================================
# PHẦN 5: QUẢN LÝ PHIÊN CHƠI & UI ĐEN HỒNG
# ====================================================================================================

class GameMode:
    NONE = "none"
    PVP_VIETNAMESE = "pvp_vi"
    BOT_VIETNAMESE = "bot_vi"
    PVP_ENGLISH = "pvp_en"
    BOT_ENGLISH = "bot_en"
    VUA_TIENG_VIET = "vua_vi"
    GUESS_COUNTRY = "doan_quoc_gia"

class ChannelSession:
    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        self.active_mode = GameMode.NONE
        self.is_active = False
        self.current_word = ""
        self.used_words_history: Set[str] = set()
        self.turn_counter = 0
        self.scrambled_target = ""
        self.secret_country = ""

    def initialize_session(self, mode: str, start_word: str = "", target: str = "") -> None:
        self.reset()
        self.is_active = True
        self.active_mode = mode
        if mode in [GameMode.PVP_VIETNAMESE, GameMode.BOT_VIETNAMESE, GameMode.PVP_ENGLISH, GameMode.BOT_ENGLISH]:
            self.current_word = start_word
            self.used_words_history.add(start_word)
            self.turn_counter = 1
        elif mode == GameMode.VUA_TIENG_VIET:
            self.scrambled_target = target
        elif mode == GameMode.GUESS_COUNTRY:
            self.secret_country = target

    def reset(self) -> None:
        self.active_mode = GameMode.NONE
        self.is_active = False
        self.current_word = ""
        self.used_words_history.clear()
        self.turn_counter = 0
        self.scrambled_target = ""
        self.secret_country = ""

class SessionManager:
    def __init__(self):
        self._sessions: Dict[int, ChannelSession] = {}

    def get_session(self, channel_id: int) -> ChannelSession:
        if channel_id not in self._sessions:
            self._sessions[channel_id] = ChannelSession(channel_id)
        return self._sessions[channel_id]

global_session_manager = SessionManager()

# --- TIỆN ÍCH VÀ GIAO DIỆN ĐEN HỒNG (VERBOSE & PRETTY) ---

class GameUtils:
    @staticmethod
    def scramble_vietnamese_syllables(phrase: str) -> str:
        syllables = phrase.split()
        if len(syllables) <= 1:
            return phrase
        shuffled = syllables.copy()
        attempts = 0
        while shuffled == syllables and attempts < 10:
            random.shuffle(shuffled)
            attempts += 1
        return " ".join(shuffled)

    @staticmethod
    def generate_country_mask(country_name: str) -> str:
        if not country_name:
            return ""
        characters = list(country_name)
        masked_chars = []
        for index, char in enumerate(characters):
            if char == ' ':
                masked_chars.append(' ')
            elif index == 0 or index == len(characters) - 1:
                masked_chars.append(char.upper())
            else:
                masked_chars.append('_')
        return " ".join(masked_chars)

class UIUtils:
    DEFAULT_FOOTER_ICON = "https://cdn.discordapp.com/embed/avatars/0.png"

    @staticmethod
    def create_embed(title: str, description: str, color: int = BotConfig.COLOR_PINK_HOT) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now())
        embed.set_footer(text="🖤💗 Vườn hoa Đen Hồng Arcade 🖤💗", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_warning_embed(title: str, warning_msg: str) -> discord.Embed:
        desc = f"{BotConfig.BORDER}\n\n{warning_msg}\n\n{BotConfig.BORDER}"
        return discord.Embed(title=f"⚠️ {title} ⚠️", description=desc, color=BotConfig.COLOR_PINK_LIGHT, timestamp=datetime.now())

    @staticmethod
    def build_invalid_word_embed(reason: str) -> discord.Embed:
        description = (
            f"{BotConfig.BORDER}\n\n"
            f"❌ **Từ bạn vừa nhập không hợp lệ (Trả lời sai)!**\n\n"
            f"📌 **Nguyên nhân:** *{reason}*\n\n"
            f"🌸 **Lưu ý quan trọng:**\n"
            f"• Từ tiếng Việt phải viết đúng chính tả, có dấu đầy đủ.\n"
            f"• Bắt buộc gồm đúng **2 tiếng** (Ví dụ: `học tập`).\n"
            f"• Không chứa ký tự đặc biệt hay số.\n\n"
            f"💡 **Giải pháp:** Dùng lệnh `/themtu [từ]` để bổ sung ngay vào từ điển hệ thống!\n\n"
            f"{BotConfig.BORDER}"
        )
        embed = discord.Embed(title="❌💗 [ TỪ KHÔNG HỢP LỆ ] 💗❌", description=description, color=BotConfig.COLOR_RED_DARK, timestamp=datetime.now())
        embed.set_footer(text="Hệ thống kiểm duyệt Black & Pink", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_success_embed(title: str, success_msg: str) -> discord.Embed:
        desc = f"{BotConfig.BORDER}\n\n{success_msg}\n\n{BotConfig.BORDER}"
        return discord.Embed(title=f"✨💗 [ {title.upper()} ] 💗✨", description=desc, color=BotConfig.COLOR_PINK_DEEP, timestamp=datetime.now())

    @staticmethod
    def build_help_embed() -> discord.Embed:
        description = (
            f"{BotConfig.BORDER}\n\n"
            f"💬 **Black & Pink Arcade Bot (v5.0.0 - 1K2 Gothic Lines)**\n"
            f"Hệ thống giải trí & từ điển thông minh đỉnh cao!\n\n"
            
            f"🇻🇳💗 **[ NỐI TỪ TIẾNG VIỆT (2 tiếng, có dấu) ]** 💗🇻🇳\n"
            f"🌸 `{BotConfig.PREFIX}noitu` → PvP đấu trí chung kênh\n"
            f"🖤 `{BotConfig.PREFIX}botnoitu` → Solo 1vs1 với Bot TV\n\n"
            
            f"🇬🇧💗 **[ NỐI TỪ TIẾNG ANH ]** 🇬🇧\n"
            f"🌸 `{BotConfig.PREFIX}noitueng` → PvP English Channel\n"
            f"🖤 `{BotConfig.PREFIX}botnoitueng` → Solo vs English Bot\n\n"
            
            f"👑💗 **[ TRÒ CHƠI GIẢI ĐỐ & TRÍ TUỆ ]** 👑\n"
            f"🌸 `{BotConfig.PREFIX}vuatiengviet` → Sắp xếp âm tiết\n"
            f"🌍 `{BotConfig.PREFIX}doanquocgia` → Đoán cờ quốc gia\n"
            f"❌ `{BotConfig.PREFIX}tictactoe` → Cờ caro bằng nút bấm UI\n"
            f"🎱 `{BotConfig.PREFIX}hoibacsi` → Hỏi Bác Sĩ Arcade\n"
            f"🔫 `{BotConfig.PREFIX}russianroulette` → Quay súng May Russians\n\n"
            
            f"⚙️💗 **[ QUẢN LÝ & TIỆN ÍCH ]** ⚙️\n"
            f"🌸 `/themtu [từ]` → *(Slash Cmd)* Thêm từ (Chỉ Admin)\n"
            f"🖤 `{BotConfig.PREFIX}admin` → Kiểm tra hệ thống (Chỉ Admin)\n"
            f"🌸 `{BotConfig.PREFIX}nghia [từ]` → Tra cứu từ vựng\n"
            f"👤 `{BotConfig.PREFIX}userinfo` → Xem info cá nhân\n"
            f"🌐 `{BotConfig.PREFIX}serverinfo` → Xem info server\n"
            f"🌸 `{BotConfig.PREFIX}ping` | `{BotConfig.PREFIX}huynoitu`\n\n"
            f"{BotConfig.BORDER}"
        )
        return discord.Embed(title="✦ HỆ THỐNG TRỢ GIÚP ARCADE ✦", description=description, color=BotConfig.COLOR_PINK_DEEP, timestamp=datetime.now())

# --- UI View Cho TicTacToe ---
class TicTacToeView(View):
    def __init__(self):
        super().__init__(timeout=120.0)
        self.board = [" " for _ in range(9)]
        self.update_buttons()

    def check_winner(self) -> str:
        wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in wins:
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] != " ":
                return self.board[a]
        return "tie" if " " not in self.board else "none"

    def update_buttons(self):
        self.clear_items()
        for i in range(9):
            style = discord.ButtonStyle.secondary
            label = " "
            if self.board[i] == "X":
                style = discord.ButtonStyle.danger
                label = "❌"
            elif self.board[i] == "O":
                style = discord.ButtonStyle.success
                label = "⭕"
                
            btn = Button(label=label, style=style, row=i//3, disabled=(self.board[i] != " "))
            btn.callback = self.make_callback(i)
            self.add_item(btn)

    def make_callback(self, idx):
        async def callback(interaction: discord.Interaction):
            if self.check_winner() != "none":
                return
            
            self.board[idx] = "X"
            winner = self.check_winner()
            
            if winner == "none":
                empty_spots = [i for i, val in enumerate(self.board) if val == " "]
                if empty_spots:
                    bot_move = random.choice(empty_spots)
                    self.board[bot_move] = "O"
                    winner = self.check_winner()

            self.update_buttons()
            
            if winner == "X":
                content = f"🎉 {interaction.user.mention} đã chiến thắng Bot! Quá xuất sắc!"
                self.disable_all_items()
            elif winner == "O":
                content = "🤖 Bot đã chiến thắng! AI vĩ đại hơn bạn!"
                self.disable_all_items()
            elif winner == "tie":
                content = "🤝 Hòa! Trận đấu thế lực ngang tài!"
                self.disable_all_items()
            else:
                content = f"🖤💗 Lượt đi của **{interaction.user.display_name}** (X) chống lại Bot (O)"

            await interaction.response.edit_message(content=content, view=self)
        return callback

# ====================================================================================================
# PHẦN 6: KHỞI TẠO BOT & LỆNH HỆ THỐNG
# ====================================================================================================

bot_intents = discord.Intents.default()
bot_intents.message_content = True
bot_intents.guilds = True
bot_intents.members = True
bot_intents.messages = True

bot = commands.Bot(command_prefix=BotConfig.PREFIX, intents=bot_intents, help_command=None, case_insensitive=True)

@bot.event
async def on_ready() -> None:
    logger.info(f"✅ Bot Đen Hồng 1K2 đã đăng nhập: {bot.user}")
    try:
        synced = await bot.tree.sync()
        logger.info(f"✅ Đã đồng bộ {len(synced)} lệnh Slash (app_commands).")
    except Exception as e:
        logger.error(f"Lỗi đồng bộ Slash Command: {e}")
    activity = discord.Activity(type=discord.ActivityType.playing, name=f"{BotConfig.PREFIX}help | 🖤💗 Gothic Arcade 1K2")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_command_error(ctx: commands.Context, error: Exception) -> None:
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=UIUtils.build_warning_embed("Thiếu Thông Tin", f"Bạn đã nhập thiếu tham số bắt buộc!\nVui lòng gõ `{BotConfig.PREFIX}help` để xem cú pháp chi tiết."))
    elif isinstance(error, commands.CheckFailure):
        await ctx.send(embed=UIUtils.build_warning_embed("Quyền Truy Cấp", "🖤 Lệnh này dành riêng cho **Quản trị viên tối cao**!\nBạn không có quyền sử dụng hệ thống này."))
    else:
        logger.error(f"Lỗi lệnh: {error}")

@bot.command(name="ping")
async def sys_ping(ctx: commands.Context) -> None:
    latency = round(bot.latency * 1000)
    desc = f"{BotConfig.BORDER}\n\n💓 **Độ trễ hệ thống (WebSocket):** `{latency}ms`\n\n*Độ trễ dưới 100ms là hoàn hảo cho các trò chơi thời gian thực!* 🖤\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🏓 Pong! Kết Nối Đen Hồng", desc, BotConfig.COLOR_PINK_DEEP))

@bot.command(name="about")
async def sys_about(ctx: commands.Context) -> None:
    desc = (
        f"{BotConfig.BORDER}\n\n"
        f"🤖 **Black & PiNk Arcade ({BotConfig.VERSION})**\n\n"
        f"📊 **Thống kê hệ thống:**\n"
        f"• 🇻🇳 Từ điển Tiếng Việt: **{len(COMBINED_VIETNAMESE_DICTIONARY):,}** từ\n"
        f"• 🇬🇧 Từ điển Tiếng Anh: **{len(ENGLISH_DICT):,}** từ\n"
        f"• 🌍 Danh sách Quốc Gia: **{len(COUNTRIES_VN_DICT):,}** nước\n\n"
        f"🖥️ **Trạng thái máy chủ:** 🖤 Hoạt động ổn định 24/7 🖤\n\n"
        f"{BotConfig.BORDER}"
    )
    await ctx.send(embed=UIUtils.create_embed("🖤💗 Về Hệ Thống Arcade", desc, BotConfig.COLOR_BLACK_CHIC))

@bot.command(name="help", aliases=["menu"])
async def sys_help(ctx: commands.Context) -> None:
    await ctx.send(embed=UIUtils.build_help_embed())

@bot.command(name="userinfo", aliases=["whois"])
async def sys_userinfo(ctx: commands.Context, member: Optional[discord.Member] = None) -> None:
    target = member or ctx.author
    desc = (
        f"{BotConfig.BORDER}\n\n"
        f"👤 **Tên:** {target.display_name}\n"
        f"🆔 **ID:** `{target.id}`\n"
        f"📅 **Tạo tài khoản:** {target.created_at.strftime('%d/%m/%Y %H:%M')}\n"
        f"📥 **Tham gia server:** {target.joined_at.strftime('%d/%m/%Y %H:%M') if target.joined_at else 'N/A'}\n"
        f"🏷️ **Roles:** {', '.join([r.mention for r in target.roles[1:]]) if target.roles else 'None'}\n\n"
        f"{BotConfig.BORDER}"
    )
    embed = UIUtils.create_embed(f"🖤💗 Thông Tin Người Dùng", desc, BotConfig.COLOR_PINK_DEEP)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="serverinfo", aliases=["svinfo"])
async def sys_serverinfo(ctx: commands.Context) -> None:
    guild = ctx.guild
    desc = (
        f"{BotConfig.BORDER}\n\n"
        f"🌐 **Tên Server:** {guild.name}\n"
        f"👑 **Owner:** <@{guild.owner_id}>\n"
        f"🆔 **ID:** `{guild.id}`\n"
        f"👥 **Thành viên:** {guild.member_count}\n"
        f"💬 **Kênh chat:** {len(guild.channels)}\n"
        f"🚀 **Tạo lúc:** {guild.created_at.strftime('%d/%m/%Y %H:%M')}\n\n"
        f"{BotConfig.BORDER}"
    )
    embed = UIUtils.create_embed("🖤💗 Thông Tin Server", desc, BotConfig.COLOR_PINK_DEEP)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)

# --- LỆNH ADMIN (CHỈ DÀNH CHO OWNER ID) ---

@bot.command(name="admin", aliases=["owner"])
@commands.is_owner()
async def cmd_admin(ctx: commands.Context) -> None:
    if ctx.author.id != BotConfig.OWNER_ID:
        return
    desc = (
        f"{BotConfig.BORDER}\n\n"
        f"🖤 **Chào mừng Quản trị viên tối cao!** 💗\n\n"
        f"📊 **Tài nguyên hệ thống:**\n"
        f"• 🇻🇳 TV Dict: {len(COMBINED_VIETNAMESE_DICTIONARY):,}\n"
        f"• 🇬🇧 EN Dict: {len(ENGLISH_DICT):,}\n"
        f"• 🌍 Country Dict: {len(COUNTRIES_VN_DICT):,}\n"
        f"• 🎮 Active Sessions: {len(global_session_manager._sessions)}\n\n"
        f"✅ *Mọi hệ thống đang vận hành trong trạng thái tối ưu.*\n\n"
        f"{BotConfig.BORDER}"
    )
    await ctx.send(embed=UIUtils.create_embed("🔒💗 [ ADMIN PANEL ] 💗🔒", desc, BotConfig.COLOR_BLACK_CHIC))

# --- LỆNH SLASH /themtu (CHỈ DÀNH CHO OWNER ID) ---
@bot.tree.command(name="themtu", description="Thêm từ mới vào từ điển (Chỉ Owner)")
async def slash_themtu(interaction: discord.Interaction, word: str):
    # Kiểm tra khóa ID Discord tuyệt đối
    if interaction.user.id != BotConfig.OWNER_ID:
        err_msg = f"{BotConfig.BORDER}\n\n🖤 Bạn không có quyền sử dụng lệnh này!\nNó được khóa chặt chỉ dành riêng cho **Owner tối cao**.\n\n{BotConfig.BORDER}"
        await interaction.response.send_message(embed=discord.Embed(title="⛔ CHẶN QUYỀN TRUY CẬP", description=err_msg, color=BotConfig.COLOR_RED_DARK), ephemeral=True)
        return
    
    clean_w = word.strip().lower()
    syl_parts = clean_w.split()
    
    if len(syl_parts) == 2:
        if clean_w in COMBINED_VIETNAMESE_DICTIONARY:
            await interaction.response.send_message(embed=UIUtils.build_warning_embed("Đã tồn tại", f"Từ **`{clean_w.upper()}`** đã có sẵn trong kho từ điển Tiếng Việt!"), ephemeral=True)
            return
        
        COMBINED_VIETNAMESE_DICTIONARY.add(clean_w)
        COMBINED_VIETNAMESE_LIST.append(clean_w)
        VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.setdefault(syl_parts[0], []).append(clean_w)
        DataManager.append_word_to_file(BotConfig.FILE_VIETNAMESE_DICT, clean_w)
        
        msg = f"Đã lưu thành công từ Tiếng Việt **`{clean_w.upper()}`** vào cả file và RAM!\nHệ thống từ điển đã được cập nhật tự động."
        await interaction.response.send_message(embed=UIUtils.build_success_embed("Thêm từ thành công", msg))
        
    elif len(syl_parts) == 1 and clean_w.isalpha():
        if clean_w in ENGLISH_DICT:
            await interaction.response.send_message(embed=UIUtils.build_warning_embed("Đã tồn tại", f"Word **`{clean_w.upper()}`** already exists in English Dictionary!"), ephemeral=True)
            return
        
        ENGLISH_DICT.add(clean_w)
        ENGLISH_LIST.append(clean_w)
        ENGLISH_INDEX_BY_FIRST_LETTER.setdefault(clean_w[0], []).append(clean_w)
        DataManager.append_word_to_file(BotConfig.FILE_ENGLISH_DICT, clean_w)
        
        msg = f"Đã lưu thành công từ Tiếng Anh **`{clean_w.upper()}`** vào file và RAM!\nWord chain engine is now updated."
        await interaction.response.send_message(embed=UIUtils.build_success_embed("Thêm từ thành công", msg))
    else:
        await interaction.response.send_message(embed=UIUtils.build_invalid_word_embed("Từ tiếng Việt phải gồm đúng 2 tiếng, hoặc 1 tiếng cho Tiếng Anh!"), ephemeral=True)

# ====================================================================================================
# PHẦN 7: CÁC LỆNH TRÒ CHƠI & GIẢI TRÍ ARCADE
# ====================================================================================================

@bot.command(name="noitu")
async def cmd_noitu(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Kênh Đang Bận", "Kênh này đang có một ván chơi hoạt động.\nHãy dùng `?huynoitu` để hủy ván cũ trước khi bắt đầu ván mới!"))
        return
    start_word = random.choice(COMBINED_VIETNAMESE_LIST)
    syllables = start_word.split()
    session.initialize_session(GameMode.PVP_VIETNAMESE, start_word=start_word)
    desc = f"{BotConfig.BORDER}\n\nTừ mở màn:\n\n## {start_word.upper()}\n\n🌸 Âm tiết tiếp theo: **`{syllables[-1].upper()}`**\n\n*Hãy trả lời tin nhắn này để nối tiếp chuỗi!* 🖤\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("💕 Nối Từ Tiếng Việt (PvP)", desc))

@bot.command(name="botnoitu", aliases=["noituubot"])
async def cmd_botnoitu(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Kênh Đang Bận", "Kênh này đang có một ván chơi hoạt động."))
        return
    start_word = random.choice(COMBINED_VIETNAMESE_LIST)
    syllables = start_word.split()
    session.initialize_session(GameMode.BOT_VIETNAMESE, start_word=start_word)
    desc = f"{BotConfig.BORDER}\n\nTừ mở màn:\n\n## {start_word.upper()}\n\n🌸 Âm tiết tiếp theo: **`{syllables[-1].upper()}`**\n\n*Bạn có dám thách thức AI của hệ thống?* 🤖\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🤖 Thách Đấu Bot Tiếng Việt", desc))

@bot.command(name="noitueng", aliases=["noituen"])
async def cmd_noitueng(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Kênh Đang Bận", "Kênh này đang có một ván chơi hoạt động."))
        return
    start_word = random.choice(ENGLISH_LIST)
    session.initialize_session(GameMode.PVP_ENGLISH, start_word=start_word)
    desc = f"{BotConfig.BORDER}\n\nStarting word:\n\n## {start_word.upper()}\n\nRequired letter: **`{start_word[-1].upper()}`**\n\n*Type your word to continue the chain!* 🇬🇧\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🇬🇧 English Word Chain", desc))

@bot.command(name="botnoitueng", aliases=["noituubotteng"])
async def cmd_botnoitueng(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Kênh Đang Bận", "Kênh này đang có một ván chơi hoạt động."))
        return
    start_word = random.choice(ENGLISH_LIST)
    session.initialize_session(GameMode.BOT_ENGLISH, start_word=start_word)
    desc = f"{BotConfig.BORDER}\n\nStarting word:\n\n## {start_word.upper()}\n\nRequired letter: **`{start_word[-1].upper()}`**\n\n*Challenge the English AI Bot!* 🤖\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🤖 English Bot Challenge", desc))

@bot.command(name="vuatiengviet")
async def cmd_vuatiengviet(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Kênh Đang Bận", "Kênh này đang có một ván chơi hoạt động."))
        return
    target = random.choice(VUA_TIENG_VIET_CANDIDATES)
    scrambled = GameUtils.scramble_vietnamese_syllables(target)
    session.initialize_session(GameMode.VUA_TIENG_VIET, target=target)
    desc = f"{BotConfig.BORDER}\n\nHãy sắp xếp lại các âm tiết sau để tạo thành từ có nghĩa:\n\n## 🔀 {scrambled}\n\n*Gõ từ hoàn chỉnh xuống chat để giành chiến thắng!* 👑\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("👑 Vua Tiếng Việt", desc))

@bot.command(name="doanquocgia")
async def cmd_doanquocgia(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Kênh Đang Bận", "Kênh này đang có một ván chơi hoạt động."))
        return
    
    target = random.choice(COUNTRIES_VN_LIST)
    masked = GameUtils.generate_country_mask(target)
    session.initialize_session(GameMode.GUESS_COUNTRY, target=target)
    
    iso_code = COUNTRY_CODES.get(target, "un")
    flag_url = f"https://flagcdn.com/w320/{iso_code}.png"
    
    desc = f"{BotConfig.BORDER}\n\nHãy nhìn hình ảnh lá cờ bên dưới và đoán tên quốc gia:\n\n## 🗺️ {masked}\n\n*Gõ chính xác tên quốc gia (Tiếng Việt không dấu có thể được)* 🌍\n\n{BotConfig.BORDER}"
    embed = UIUtils.create_embed("🌍 Đoán Quốc Gia (Kèm Cờ)", desc)
    embed.set_image(url=flag_url)
    await ctx.send(embed=embed)

@bot.command(name="tictactoe", aliases=["caro"])
async def cmd_tictactoe(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Kênh Đang Bận", "Kênh này đang có một ván chơi hoạt động."))
        return
    view = TicTacToeView()
    desc = f"{BotConfig.BORDER}\n\nChọn ô để đánh **❌** chống lại Bot **⭕**!\nLượt đi của bạn trước. Hãy cẩn thận, AI rất thông minh!\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("❌⭕ Cờ Caro (UI Buttons)", desc), view=view)

@bot.command(name="hoibacsi", aliases=["8ball", "ask"])
async def cmd_hoibacsi(ctx: commands.Context, *, question: str) -> None:
    responses = [
        "Chắc chắn là vậy. 🖤", "Không nghiouw gì. 💗", "Yếu, nhưng có thể. 🥀",
        "Hỏi lại sau nhé... 🌑", "Tuyệt đối không! 🚫", "Thấy không ổn lắm. 🥀",
        "Khả năng rất cao. 💖", "Triển vọng tốt. 🌸", "Dự báo xấu. ⛈️",
        "Rất phức tạp. 🕸️", "Mọi thứ đều có thể. ✨", "Hãy tự quyết định đi! 🗝️"
    ]
    answer = random.choice(responses)
    desc = f"{BotConfig.BORDER}\n\n❓ **Câu hỏi của bạn:** *{question}*\n\n💡 **Trả lời của Bác Sĩ:** {answer}\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🎱 Hỏi Bác Sĩ Arcade", desc, BotConfig.COLOR_MAGENTA))

@bot.command(name="russianroulette", aliases=["rr", "roulette"])
async def cmd_russianroulette(ctx: commands.Context) -> None:
    bullet = random.randint(1, 6)
    chamber = random.randint(1, 6)
    
    if bullet == chamber:
        desc = f"{BotConfig.BORDER}\n\n💥 **BÙMMM!** 💥\n\nViên đạn đã nổ! {ctx.author.mention} đã hy sinh anh dũng trong trò chơi May Russians! 🪦\n\n{BotConfig.BORDER}"
        color = BotConfig.COLOR_RED_DARK
    else:
        desc = f"{BotConfig.BORDER}\n\n💨 *Click...*\n\nTrống! {ctx.author.mention} đã sống sót qua lượt quay này. Bạn có dám tiếp tục? 🖤\n\n{BotConfig.BORDER}"
        color = BotConfig.COLOR_PINK_DEEP
        
    await ctx.send(embed=UIUtils.create_embed("🔫 Russian Roulette", desc, color))

@bot.command(name="huynoitu", aliases=["huygame"])
async def cmd_huynoitu(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if not session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Không Có Ván Chơi", "Hiện không có ván trò chơi nào đang diễn ra tại kênh này để hủy."))
        return
    session.reset()
    desc = f"{BotConfig.BORDER}\n\nPhiên trò chơi tại kênh này đã được kết thúc thành công.\nBạn có thể bắt đầu một ván chơi mới ngay bây giờ! 🖤\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🖤 Đã Hủy Phiên Chơi", desc, BotConfig.COLOR_BLACK_CHIC))

@bot.command(name="nghia")
async def cmd_nghia(ctx: commands.Context, *, word: str = "") -> None:
    if not word:
        await ctx.send(embed=UIUtils.build_warning_embed("Thiếu Từ", "Vui lòng nhập từ cần tra cứu.\nVí dụ: `?nghia học tập`"))
        return
    clean_w = word.strip().lower()
    found = clean_w in COMBINED_VIETNAMESE_DICTIONARY or clean_w in ENGLISH_DICT or clean_w in COUNTRIES_VN_DICT
    if found:
        desc = f"{BotConfig.BORDER}\n\nTừ **`{clean_w.upper()}`** **CÓ TRONG** hệ thống dữ liệu doanh nghiệp! 🖤💗\n\n{BotConfig.BORDER}"
        await ctx.send(embed=UIUtils.create_embed("📖 Tra Cứu Từ Vựng", desc, BotConfig.COLOR_PINK_DEEP))
    else:
        desc = f"{BotConfig.BORDER}\n\nKhông tìm thấy từ **`{clean_w.upper()}`** trong từ điển.\n💡 Dùng lệnh `/themtu {clean_w}` để bổ sung ngay vào hệ thống!\n\n{BotConfig.BORDER}"
        await ctx.send(embed=UIUtils.create_embed("📖 Tra Cứu Từ Vựng", desc, BotConfig.COLOR_RED_DARK))

# ====================================================================================================
# PHẦN 8: XỬ LÝ SỰ KIỆN TRÒ CHƠI QUA TIN NHẮN (VERBOSE & PRETTY)
# ====================================================================================================

@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return
    
    await bot.process_commands(message)
    
    session = global_session_manager.get_session(message.channel.id)
    if not session.is_active:
        return

    content = message.content.strip().lower()
    if content.startswith(BotConfig.PREFIX):
        return

    # 1. Vua Tiếng Việt
    if session.active_mode == GameMode.VUA_TIENG_VIET:
        if content == session.scrambled_target.lower():
            target = session.scrambled_target
            session.reset()
            desc = f"{BotConfig.BORDER}\n\n🎉 {message.author.mention} đã giải đúng từ: **`{target.upper()}`**!\nBạn thực sự là một bậc thầy ngôn ngữ! 👑\n\n{BotConfig.BORDER}"
            await message.channel.send(embed=UIUtils.create_embed("🏆 Chiến Thắng Vua Tiếng Việt", desc, BotConfig.COLOR_PINK_DEEP))
        return

    # 2. Đoán Quốc Gia
    if session.active_mode == GameMode.GUESS_COUNTRY:
        if content == session.secret_country.lower():
            target = session.secret_country
            session.reset()
            desc = f"{BotConfig.BORDER}\n\n🎉 {message.author.mention} đoán đúng quốc gia: **`{target.upper()}`**!\nKiến thức địa lý của bạn rất tuyệt vời! 🌍\n\n{BotConfig.BORDER}"
            await message.channel.send(embed=UIUtils.create_embed("🏆 Chiến Thắng Đoán Quốc Gia", desc, BotConfig.COLOR_PINK_DEEP))
        return

    # 3. Nối Từ Tiếng Việt
    if session.active_mode in [GameMode.PVP_VIETNAMESE, GameMode.BOT_VIETNAMESE]:
        parts = content.split()
        if len(parts) != 2:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed("Từ tiếng Việt bắt buộc phải gồm đúng 2 tiếng!"))
            return
        
        if content not in COMBINED_VIETNAMESE_DICTIONARY:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed("Từ này không có trong từ điển (hoặc thiếu dấu / viết sai chính tả)!"))
            return
        
        if content in session.used_words_history:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(BotConfig.MSG_ERR_ALREADY_USED))
            return
        
        current_syllables = session.current_word.split()
        required_syl = current_syllables[-1] if current_syllables else ""
        if parts[0] != required_syl:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(f"Từ phải bắt đầu bằng âm tiết **`{required_syl.upper()}`**!"))
            return
        
        session.used_words_history.add(content)
        session.current_word = content
        session.turn_counter += 1
        
        next_syl = parts[-1]
        
        if session.active_mode == GameMode.PVP_VIETNAMESE:
            desc = f"{BotConfig.BORDER}\n\nTừ hợp lệ: **`{content.upper()}`**\n🌸 Âm tiết tiếp theo: **`{next_syl.upper()}`**\n\n*Hãy trả lời nhanh để giữ chuỗi sống!* 🖤\n\n{BotConfig.BORDER}"
            await message.channel.send(embed=UIUtils.create_embed("✨ Nối Từ Thành Công!", desc, BotConfig.COLOR_PINK_DEEP))
        elif session.active_mode == GameMode.BOT_VIETNAMESE:
            candidates = VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.get(next_syl, [])
            valid_candidates = [w for w in candidates if w not in session.used_words_history]
            
            if not valid_candidates:
                session.reset()
                desc = f"{BotConfig.BORDER}\n\n🎉 {message.author.mention} đã đánh bại Bot!\nHệ thống AI đã cạn từ nối bắt đầu bằng: **`{next_syl.upper()}`** 🤖\n\n{BotConfig.BORDER}"
                await message.channel.send(embed=UIUtils.create_embed("🏆 Người Chơi Thắng Bot", desc, BotConfig.COLOR_PINK_DEEP))
                return
            
            bot_word = random.choice(valid_candidates)
            session.used_words_history.add(bot_word)
            session.current_word = bot_word
            bot_syllables = bot_word.split()
            next_bot_syl = bot_syllables[-1] if bot_syllables else bot_word
            
            desc = f"{BotConfig.BORDER}\n\n✨ Từ của bạn: **`{content.upper()}`**\n🤖 **Bot phản đòn:** ## {bot_word.upper()}\n🌸 Âm tiết tiếp theo cho bạn: **`{next_bot_syl.upper()}`**\n\n*Đang tính toán nước đi tiếp theo...* 🖤\n\n{BotConfig.BORDER}"
            await message.channel.send(embed=UIUtils.create_embed("✨💗 Lượt Đấu Thành Công", desc, BotConfig.COLOR_PINK_DEEP))
        return

    # 4. Nối Từ Tiếng Anh
    if session.active_mode in [GameMode.PVP_ENGLISH, GameMode.BOT_ENGLISH]:
        if not content.isalpha():
            await message.channel.send(embed=UIUtils.build_invalid_word_embed("Từ tiếng Anh chỉ được chứa ký tự chữ cái!"))
            return
        
        if content not in ENGLISH_DICT:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed("Từ này không có trong từ điển tiếng Anh!"))
            return
        
        if content in session.used_words_history:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(BotConfig.MSG_ERR_ALREADY_USED))
            return
        
        required_letter = session.current_word[-1]
        if content[0] != required_letter:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(f"Word must start with letter **`{required_letter.upper()}`**!"))
            return
        
        session.used_words_history.add(content)
        session.current_word = content
        session.turn_counter += 1
        
        next_letter = content[-1]
        
        if session.active_mode == GameMode.PVP_ENGLISH:
            desc = f"{BotConfig.BORDER}\n\nValid word: **`{content.upper()}`**\nNext required letter: **`{next_letter.upper()}`**\n\n*Keep the chain alive!* 🇬🇧\n\n{BotConfig.BORDER}"
            await message.channel.send(embed=UIUtils.create_embed("✨ Word Chain Success!", desc, BotConfig.COLOR_PINK_DEEP))
        elif session.active_mode == GameMode.BOT_ENGLISH:
            candidates = ENGLISH_INDEX_BY_FIRST_LETTER.get(next_letter, [])
            valid_candidates = [w for w in candidates if w not in session.used_words_history]
            
            if not valid_candidates:
                session.reset()
                desc = f"{BotConfig.BORDER}\n\n🎉 {message.author.mention} defeated the AI Bot!\nThe Bot ran out of words starting with: **`{next_letter.upper()}`** 🤖\n\n{BotConfig.BORDER}"
                await message.channel.send(embed=UIUtils.create_embed("🏆 Player Defeated Bot", desc, BotConfig.COLOR_PINK_DEEP))
                return
            
            bot_word = random.choice(valid_candidates)
            session.used_words_history.add(bot_word)
            session.current_word = bot_word
            next_bot_letter = bot_word[-1]
            
            desc = f"{BotConfig.BORDER}\n\nYour word: **`{content.upper()}`**\n🤖 **Bot countered:** ## {bot_word.upper()}\nNext required letter: **`{next_bot_letter.upper()}`**\n\n*Calculating next move...* 🖤\n\n{BotConfig.BORDER}"
            await message.channel.send(embed=UIUtils.create_embed("✨💗 Round Successful", desc, BotConfig.COLOR_PINK_DEEP))
        return

# ====================================================================================================
# PHẦN 9: KHỞI CHẠY HỆ THỐNG
# ====================================================================================================

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.warning("🖤 Không tìm thấy biến môi trường DISCORD_TOKEN. Hãy cung cấp token để khởi động!")
    else:
        bot.run(token)
