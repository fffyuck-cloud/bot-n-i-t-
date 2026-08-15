# ====================================================================================================
# ██████╗ ██╗    █████╗  ██████╗██╗  ██╗    ██████╗ ██╗███╗    ██╗██╗  ██╗    ██████╗  ██████╗ ████████╗
# ██╔══██╗██║    ██╔══██╗██╔════╝██║ ██╔╝    ██╔══██╗██║████╗   ██║██║ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
# ██████╔╝██║    ███████║██║     █████╔╝     ██████╔╝██║██╔██╗  ██║█████╔╝     ██████╔╝██║   ██║   ██║   
# ██╔══██╗██║    ██╔══██║██║     ██╔═██╗     ██╔═══╝ ██║██║╚██╗ ██║██╔═██╗     ██╔══██╗██║   ██║   ██║   
# ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗    ██║     ██║██║ ╚████║██║  ██╗    ██████╔╝╚██████╔╝   ██║   
# ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝    ╚═════╝  ╚═╝    ╚═╝   
#                                                                                                   
# PURE FUN ENTERPRISE - BLACK & PINK ARCADE EDITION - 1K2 LINES (v4.2.0)
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
    VERSION: str = "4.2.0 Black & Pink 1K2 Arcade"
    DEVELOPER: str = "Black & Pink Studio"
    PREFIX: str = "?"
    OWNER_ID: int = 1312333137241575449 # ID Discord của bạn - Toàn quyền
    
    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = 8080
    
    FILE_VIETNAMESE_DICT: str = "tu_dien.txt"
    FILE_ENGLISH_DICT: str = "tu dien tieng anh.txt"
    FILE_COUNTRIES_DICT: str = "quoc gia vn.txt"
    
    # 🖤💗 BẢNG MÀU ĐEN HỒNG (GOTHIC PALETTE)
    COLOR_PINK_HOT: int = 0xFF69B4      # Hot Pink (Mặc định)
    COLOR_PINK_DEEP: int = 0xFF1493     # Deep Pink (Thành công)
    COLOR_PINK_LIGHT: int = 0xFFC0CB    # Light Pink (Cảnh báo)
    COLOR_BLACK_CHIC: int = 0x2B2D31    # Discord Dark/Black (Hệ thống/Hủy)
    COLOR_RED_DARK: int = 0x8B0000      # Dark Red (Lỗi nghiêm trọng)
    COLOR_MAGENTA: int = 0xA52A2A       # Brownish Magenta (Lỗi từ điển)
    
    MSG_ERR_ALREADY_USED: str = "❌ Từ này đã được sử dụng trước đó trong ván này!"

# ====================================================================================================
# PHẦN 2: DỮ LIỆU DỰ PHÒNG KHỔNG LỒ (FULL TỪ ĐIỂN INCODE)
# ====================================================================================================

DEFAULT_VIETNAMESE_FALLBACK: Set[str] = {
    # A - B
    "an ninh", "an toàn", "ấm áp", "ẩm ướt", "ánh sáng", "áo quần", "ăn uống", "át chủ", "ba mươi", "bạc hà",
    "bạ bạt", "bạn bè", "bao dung", "bạo chúa", "bền bỉ", "bí quyết", "bình yên", "bồi đắp", "bứt phá", "bị ốm",
    # C - D
    "cẩn thận", "cản trở", "cao siêu", "cật lực", "chân thật", "chiếm đoạt", "chối bỏ", "chuộc lỗi", "chấn hưng", "công bằng",
    "cột sống", "cưỡng ép", "cảm xúc", "cứu giúp", "cúng kiến", "dạ dày", "dằn vặt", "dĩ vãng", "do dự", "dong dỏng",
    "dũng cảm", "dụ dỗ", "dữ dội", "dốc lòng", "dấu vết", "đành đạch", "đắn đo", "đắt giá", "đơm dreaming", "đức hạnh",
    # Đ - G
    "đà điệu", "đàm thoại", "đánh đập", "đắn đòn", "đắp xây", "đắt tay", "đau đớn", "đê mê", "điềm tĩnh", "điocxin",
    "đỏ đực", "đongan dỏng", "đóng góp", "đồ đạc", "đồng lương", "đủ đầy", "đương đầu", "đắm đuối", "gạ gẫm", "gào thét",
    "gắt gao", "gây gổ", "giao hảo", "giảo hoạt", "giòn giã", "giấu giếm", "giảng giải", "giá rẻ", "giếng sâu", "gion gõ",
    # H - K
    "hằn học", "hạ thấp", "hão huyền", "hào hoa", "hấp hấp", "hây hây", "hăm dọa", "hèn mạt", "hiền lành", "hỏa speed",
    "hợm hĩnh", "hùng dũng", "hướng dẫn", "hối hận", "hờn giận", "kéo dài", "kéo co", "khiêm tốn", "khoan dung", "khó khăn",
    "khéo léo", "khống chế", "khuất phục", "kính trọng", "kệ cỗ", "kéo tơi", "kênh kiếng", "kim chỉ", "kịp thời", "khuôn vẽ",
    # L - N
    "lấp lánh", "lặng lẽ", "lười biếng", "lường gạt", "lạc quan", "lãng phí", "lẫy lừng", "lì lợm", "lo lắng", "luật pháp",
    "luyến tiếc", "mac cà", "mê mẩn", "mỏng manh", "mệt mỏi", "mịt mờ", "mơn trớn", "mùi mệ", "mưu mô", "mặn mà",
    "nhan sắc", "nghiêm trang", "ngổ ngáo", "ngọt ngào", "nguy hiểm", "ngại ngùng", "nhàn rỗi", "nhân ái", "nhút nhát", "nóng nảy",
    # O - P
    "oan khiên", "o bẹp", "ôm ấp", "ôm hờn", "phóng khoáng", "phấp phỏng", "phũ phàng", "phấn khởi", "phò ngự", "phép tắc",
    # Q - S
    "quyến rũ", "quát tháo", "quần quật", "quá đà", "quyền lực", "rành rẽ", "rạo rực", "rất rá", "rung rinh", "rộn rã",
    "rười rượi", "sáng sủa", "sạch sẽ", "sảng khoái", "sừng sững", "si mê", "sợ hãi", "suy thoái", "sung sướng", "sượng sùng",
    # T - V
    "tài giỏi", "tăm tối", "tỉ mỉ", "to lớn", "trống rỗng", "tuyệt vời", "thông minh", "tôn trọng", "thế lực", "tinh tế",
    "ù lì", "ươn yếu", "vàng vọt", "vội vã", "vung vút", "vuông vắn", "vô vị", "vương vấn", "vênh váo", "van xin",
    # X - Y
    "xanh xám", "xa xăm", "xiên xẹo", "xinh đẹp", "xót xa", "xuề xòa", "xốc vó", "xứ xể", "yếu ớt", "yên tĩnh"
}

DEFAULT_ENGLISH_FALLBACK: Set[str] = {
    # A
    "apple", "anchor", "angel", "apex", "arrow", "azure", "acorn", "album", "amber", "amulet",
    "antique", "arctic", "astro", "aura", "avocado", "axe", "alchemy", "alert", "alpine", "amaze",
    # B
    "badger", "balance", "bamboo", "beacon", "beauty", "bison", "blade", "bless", "bliss", "blossom",
    "bluebird", "bold", "bolt", "bonfire", "brave", "breeze", "bridged", "bronze", "bubble", "butterfly",
    # C
    "cactus", "camel", "cascade", "castle", "cedar", "chalice", "charm", "chrome", "cipher", "clarity",
    "cloud", "comet", "coral", "cosmic", "crane", "crescent", "crystal", "crown", "cupid", "cyber",
    # D
    "dagger", "dawn", "deity", "delta", "demon", "desert", "diamond", "digital", "dolphin", "dragon",
    "dream", "dusk", "dwarf", "dazzle", "decade", "decree", "depth", "destiny", "devour", "dew",
    # E
    "eagle", "earth", "echo", "eclipse", "eden", "electric", "elephant", "elixir", "ember", "emerald",
    "emperor", "enchant", "endless", "energy", "enigma", "epic", "equinox", "essence", "eternal", "euro",
    # F
    "fable", "falcon", "fantasy", "fate", "fauna", "fawn", "feline", "fierce", "flame", "flash",
    "flora", "forge", "fossil", "fractal", "free", "frost", "fury", "fusion", "future", "fable",
    # G
    "galaxy", "gale", "garnet", "gaia", "genesis", "ghost", "giant", "glimmer", "globe", "glory",
    "goblin", "gold", "grace", "granite", "gravity", "griffin", "guardian", "guava", "guide", "guru",
    # H
    "habitat", "halcyon", "hallow", "harbor", "harmony", "haste", "haven", "hawk", "haze", "heart",
    "helix", "hell", "herb", "hero", "hideout", "honor", "horizon", "hub", "huge", "hummingbird",
    # I
    "ice", "ignite", "illusion", "imagine", "immortal", "impact", "incense", "index", "infinite", "ink",
    "insight", "ion", "iris", "iron", "ivory", "isle", "isthmus", "item", "iterate", "ivory",
    # J - K
    "jade", "jaguar", "jazz", "jest", "jet", "jewel", "jinx", "joker", "jolly", "jungle",
    "karma", "kayak", "keen", "kestrel", "key", "kindle", "king", "kite", "knight", "koala",
    # L
    "labyrinth", "lagoon", "lamp", "lance", "laser", "lava", "league", "legend", "lemon", "leviathan",
    "liberty", "light", "lily", "limbo", "lion", "lizard", "loom", "lunar", "luxury", "lyric",
    # M
    "magic", "magnet", "mansion", "maple", "mare", "mars", "mask", "maze", "medal", "mercury",
    "meteor", "midnight", "mime", "mirror", "mist", "monarch", "moon", "morning", "muse", "mythic",
    # N - O
    "nadir", "nebula", "neon", "nest", "nexus", "night", "noble", "nomad", "north", "nova",
    "oak", "oasis", "obsidian", "ocean", "omega", "onion", "opal", "oracle", "orchid", "orca",
    # P
    "palace", "palm", "panther", "paper", "paradox", "peace", "pearl", "pegasus", "phoenix", "pilot",
    "pixel", "plasma", "platinum", "plume", "poseidon", "prism", "prometheus", "psalm", "pulse", "pyre",
    # Q - R
    "quartz", "queen", "quest", "quill", "quirk", "quota", "quiver", "quote", "quran", "quadratic",
    "rabbit", "radar", "rage", "rainbow", "raven", "realm", "relic", "rhythm", "riddle", "river",
    # S
    "sacred", "safari", "sage", "sanctuary", "saturn", "scepter", "scorpion", "scroll", "sea", "shadow",
    "shield", "shrine", "sigil", "silk", "silver", "siren", "sky", "slate", "soul", "spark",
    # T
    "talisman", "tango", "temple", "temporal", "tephra", "terra", "thunder", "tide", "tiger", "titan",
    "topaz", "tornado", "torque", "tower", "tranquil", "tribal", "trophy", "tundra", "turret", "twilight",
    # U - V
    "uber", "ultra", "umbra", "uncle", "under", "unison", "unity", "universe", "uranium", "urban",
    "vampire", "vanilla", "vapor", "vault", "vector", "veil", "venom", "venue", "vesta", "vigor",
    # W - Z
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
        logger_instance = logging.getLogger("BlackPinkArcadeBot")
        logger_instance.setLevel(logging.INFO)
        logger_instance.addHandler(console_handler)
        return logger_instance

logger = LoggerSetup.initialize_logger()

keep_alive_app = Flask("BlackPinkKeepAlive")

@keep_alive_app.route('/')
def route_home() -> str:
    return "<h1>Black & Pink Arcade Bot (v4.2.0)</h1><p style='color:#FF69B4'>Status: <strong>ONLINE & GOTHIC</strong></p>"

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

# --- TIỆN ÍCH VÀ GIAO DIỆN ĐEN HỒNG ---

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
        embed.set_footer(text="Vườn hoa Đen Hồng Arcade 🖤💗", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_warning_embed(title: str, warning_msg: str) -> discord.Embed:
        return discord.Embed(title=f"⚠️ {title}", description=warning_msg, color=BotConfig.COLOR_PINK_LIGHT, timestamp=datetime.now())

    @staticmethod
    def build_invalid_word_embed(reason: str) -> discord.Embed:
        description = (
            f"❌ **Từ bạn vừa nhập không hợp lệ!**\n\n"
            f"📌 **Nguyên nhân:** {reason}\n"
            f"🌸 *Lưu ý: Từ tiếng Việt phải viết đúng chính tả, có dấu đầy đủ và gồm đúng 2 tiếng!*\n"
            f"💡 *Dùng lệnh `/themtu [từ]` để bổ sung ngay vào file từ điển!*"
        )
        embed = discord.Embed(title="❌💗 [ TỪ KHÔNG HỢP LỆ ] 💗❌", description=description, color=BotConfig.COLOR_RED_DARK, timestamp=datetime.now())
        embed.set_footer(text="Hệ thống kiểm duyệt Black & Pink", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_success_embed(title: str, success_msg: str) -> discord.Embed:
        return discord.Embed(title=f"✨💗 [ {title.upper()} ] 💗✨", description=success_msg, color=BotConfig.COLOR_PINK_DEEP, timestamp=datetime.now())

    @staticmethod
    def build_help_embed() -> discord.Embed:
        description = (
            f"💬 **Black & Pink Arcade Bot (v4.2.0 - 1K2 Lines)**\n"
            f"Hệ thống trò chơi giải trí và từ điển thông minh!\n\n"
            f"🇻🇳💗 **[ NỐI TỪ TIẾNG VIỆT (2 tiếng, có dấu) ]** 💗🇻🇳\n"
            f"🌸 `{BotConfig.PREFIX}noitu` → PvP chung kênh\n"
            f"🖤 `{BotConfig.PREFIX}botnoitu` → Solo với Bot TV\n\n"
            f"🇬🇧💗 **[ NỐI TỪ TIẾNG ANH ]** 🇬🇧\n"
            f"🌸 `{BotConfig.PREFIX}noitueng` | `{BotConfig.PREFIX}botnoitueng`\n\n"
            f"👑💗 **[ TRÒ CHƠI GIẢI ĐỐ & TRÍ TUỆ ]** 👑\n"
            f"🌸 `{BotConfig.PREFIX}vuatiengviet`\n"
            f"🌍 `{BotConfig.PREFIX}doanquocgia` (Kèm ảnh lá cờ)\n"
            f"❌ `{BotConfig.PREFIX}tictactoe` (Cờ caro bằng nút bấm UI)\n"
            f"🎱 `{BotConfig.PREFIX}hoibacsi` (Hỏi Bác Sĩ Arcade)\n\n"
            f"⚙️💗 **[ QUẢN LÝ TỪ ĐIỂN & TIỆN ÍCH ]** ⚙️\n"
            f"🌸 `/themtu [từ]` → (Slash Cmd) Thêm từ mới (Chỉ Owner)\n"
            f"🖤 `{BotConfig.PREFIX}nghia [từ]` → Tra cứu từ vựng\n"
            f"🌸 `{BotConfig.PREFIX}ping` | `{BotConfig.PREFIX}huynoitu`"
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
                content = f"🎉 {interaction.user.mention} đã chiến thắng Bot!"
                self.disable_all_items()
            elif winner == "O":
                content = "🤖 Bot đã chiến thắng!"
                self.disable_all_items()
            elif winner == "tie":
                content = "🤝 Hòa! Không ai thua ai!"
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
    activity = discord.Activity(type=discord.ActivityType.playing, name=f"{BotConfig.PREFIX}help | 🖤💗 Arcade 1K2")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_command_error(ctx: commands.Context, error: Exception) -> None:
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=UIUtils.build_warning_embed("Thiếu Thông Tin", f"Vui lòng gõ `{BotConfig.PREFIX}help` để xem hướng dẫn chi tiết."))
    else:
        logger.error(f"Lỗi lệnh: {error}")

@bot.command(name="ping")
async def sys_ping(ctx: commands.Context) -> None:
    await ctx.send(embed=UIUtils.create_embed("🏓 Pong!", f"Độ trễ hệ thống: **{round(bot.latency * 1000)}ms**", BotConfig.COLOR_PINK_DEEP))

@bot.command(name="about")
async def sys_about(ctx: commands.Context) -> None:
    desc = (
        f"🤖 **Black & PiNk Arcade ({BotConfig.VERSION})**\n"
        f"• Từ điển Tiếng Việt: {len(COMBINED_VIETNAMESE_DICTIONARY):,} từ\n"
        f"• Từ điển Tiếng Anh: {len(ENGLISH_DICT):,} từ\n"
        f"• Danh sách Quốc Gia: {len(COUNTRIES_VN_DICT):,} nước\n"
        f"• Trạng thái: 🖤💗 Hoạt động ổn định 24/7"
    )
    await ctx.send(embed=UIUtils.create_embed("🖤💗 Về Hệ Thống Arcade", desc, BotConfig.COLOR_BLACK_CHIC))

@bot.command(name="help", aliases=["menu"])
async def sys_help(ctx: commands.Context) -> None:
    await ctx.send(embed=UIUtils.build_help_embed())

# --- LỆNH SLASH /themtu (CHỈ DÀNH CHO OWNER ID) ---
@bot.tree.command(name="themtu", description="Thêm từ mới vào từ điển (Chỉ Owner)")
async def slash_themtu(interaction: discord.Interaction, word: str):
    # Kiểm tra khóa ID Discord
    if interaction.user.id != BotConfig.OWNER_ID:
        await interaction.response.send_message("🖤 Bạn không có quyền sử dụng lệnh này! Dành riêng cho Owner.", ephemeral=True)
        return
    
    clean_w = word.strip().lower()
    syl_parts = clean_w.split()
    
    if len(syl_parts) == 2:
        if clean_w in COMBINED_VIETNAMESE_DICTIONARY:
            await interaction.response.send_message(embed=UIUtils.build_warning_embed("Đã tồn tại", f"Từ **`{clean_w.upper()}`** đã có sẵn trong từ điển TV!"), ephemeral=True)
            return
        
        COMBINED_VIETNAMESE_DICTIONARY.add(clean_w)
        COMBINED_VIETNAMESE_LIST.append(clean_w)
        VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.setdefault(syl_parts[0], []).append(clean_w)
        DataManager.append_word_to_file(BotConfig.FILE_VIETNAMESE_DICT, clean_w)
        
        await interaction.response.send_message(embed=UIUtils.build_success_embed("Thêm từ thành công", f"Đã lưu từ TV **`{clean_w.upper()}`** vào file và RAM!"))
        
    elif len(syl_parts) == 1 and clean_w.isalpha():
        if clean_w in ENGLISH_DICT:
            await interaction.response.send_message(embed=UIUtils.build_warning_embed("Đã tồn tại", f"Word **`{clean_w.upper()}`** already exists!"), ephemeral=True)
            return
        
        ENGLISH_DICT.add(clean_w)
        ENGLISH_LIST.append(clean_w)
        ENGLISH_INDEX_BY_FIRST_LETTER.setdefault(clean_w[0], []).append(clean_w)
        DataManager.append_word_to_file(BotConfig.FILE_ENGLISH_DICT, clean_w)
        
        await interaction.response.send_message(embed=UIUtils.build_success_embed("Thêm từ thành công", f"Đã lưu từ TA **`{clean_w.upper()}`** vào file và RAM!"))
    else:
        await interaction.response.send_message(embed=UIUtils.build_invalid_word_embed("Từ tiếng Việt phải gồm đúng 2 tiếng!"), ephemeral=True)

# ====================================================================================================
# PHẦN 7: CÁC LỆNH TRÒ CHƠI & TỪ ĐIỂN
# ====================================================================================================

@bot.command(name="noitu")
async def cmd_noitu(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có ván chơi hoạt động."))
        return
    start_word = random.choice(COMBINED_VIETNAMESE_LIST)
    syllables = start_word.split()
    session.initialize_session(GameMode.PVP_VIETNAMESE, start_word=start_word)
    await ctx.send(embed=UIUtils.create_embed("💕 Nối Từ Tiếng Việt (PvP)", f"Từ mở màn:\n\n## {start_word.upper()}\n\n🌸 Âm tiết tiếp theo: **`{syllables[-1].upper()}`**"))

@bot.command(name="botnoitu", aliases=["noituubot"])
async def cmd_botnoitu(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có ván chơi hoạt động."))
        return
    start_word = random.choice(COMBINED_VIETNAMESE_LIST)
    syllables = start_word.split()
    session.initialize_session(GameMode.BOT_VIETNAMESE, start_word=start_word)
    await ctx.send(embed=UIUtils.create_embed("🤖 Thách Đấu Bot Tiếng Việt", f"Từ mở màn:\n\n## {start_word.upper()}\n\n🌸 Âm tiết tiếp theo: **`{syllables[-1].upper()}`**"))

@bot.command(name="noitueng", aliases=["noituen"])
async def cmd_noitueng(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có ván chơi hoạt động."))
        return
    start_word = random.choice(ENGLISH_LIST)
    session.initialize_session(GameMode.PVP_ENGLISH, start_word=start_word)
    await ctx.send(embed=UIUtils.create_embed("🇬🇧 English Word Chain", f"Starting word:\n\n## {start_word.upper()}\n\nRequired letter: **`{start_word[-1].upper()}`**"))

@bot.command(name="botnoitueng", aliases=["noituubotteng"])
async def cmd_botnoitueng(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có ván chơi hoạt động."))
        return
    start_word = random.choice(ENGLISH_LIST)
    session.initialize_session(GameMode.BOT_ENGLISH, start_word=start_word)
    await ctx.send(embed=UIUtils.create_embed("🤖 English Bot Challenge", f"Starting word:\n\n## {start_word.upper()}\n\nRequired letter: **`{start_word[-1].upper()}`**"))

@bot.command(name="vuatiengviet")
async def cmd_vuatiengviet(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có ván chơi hoạt động."))
        return
    target = random.choice(VUA_TIENG_VIET_CANDIDATES)
    scrambled = GameUtils.scramble_vietnamese_syllables(target)
    session.initialize_session(GameMode.VUA_TIENG_VIET, target=target)
    await ctx.send(embed=UIUtils.create_embed("👑 Vua Tiếng Việt", f"Sắp xếp lại các âm tiết sau:\n\n## 🔀 {scrambled}"))

@bot.command(name="doanquocgia")
async def cmd_doanquocgia(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có ván chơi hoạt động."))
        return
    
    target = random.choice(COUNTRIES_VN_LIST)
    masked = GameUtils.generate_country_mask(target)
    session.initialize_session(GameMode.GUESS_COUNTRY, target=target)
    
    iso_code = COUNTRY_CODES.get(target, "un")
    flag_url = f"https://flagcdn.com/w320/{iso_code}.png"
    
    embed = UIUtils.create_embed("🌍 Đoán Quốc Gia (Kèm Cờ)", f"Hãy nhìn hình ảnh lá cờ bên dưới và đoán tên quốc gia:\n\n## 🗺️ {masked}")
    embed.set_image(url=flag_url)
    await ctx.send(embed=embed)

@bot.command(name="tictactoe", aliases=["caro"])
async def cmd_tictactoe(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có ván chơi hoạt động."))
        return
    view = TicTacToeView()
    await ctx.send(embed=UIUtils.create_embed("❌⭕ Cờ Caro (UI Buttons)", "Chọn ô để đánh **X** chống lại Bot **O**!\nLượt đi của bạn trước:"), view=view)

@bot.command(name="hoibacsi", aliases=["8ball", "ask"])
async def cmd_hoibacsi(ctx: commands.Context, *, question: str) -> None:
    responses = [
        "Chắc chắn là vậy. 🖤", "Không nghi ngờ gì. 💗", "Yếu, nhưng có thể. 🥀",
        "Hỏi lại sau nhé... 🌑", "Tuyệt đối không! 🚫", "Thấy không ổn lắm. 🥀",
        "Khả năng rất cao. 💖", "Triển vọng tốt. 🌸", "Dự báo xấu. ⛈️",
        "Rất phức tạp. 🕸️", "Mọi thứ đều có thể. ✨", "Hãy tự quyết định đi! 🗝️"
    ]
    answer = random.choice(responses)
    await ctx.send(embed=UIUtils.create_embed("🎱 Hỏi Bác Sĩ Arcade", f"❓ **Câu hỏi:** {question}\n💡 **Trả lời:** {answer}", BotConfig.COLOR_MAGENTA))

@bot.command(name="huynoitu", aliases=["huygame"])
async def cmd_huynoitu(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if not session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Không có ván chơi", "Hiện không có ván trò chơi nào đang diễn ra tại kênh này."))
        return
    session.reset()
    await ctx.send(embed=UIUtils.create_embed("🖤 Đã hủy phiên chơi", "Phiên trò chơi tại kênh này đã được kết thúc thành công.", BotConfig.COLOR_BLACK_CHIC))

@bot.command(name="nghia")
async def cmd_nghia(ctx: commands.Context, *, word: str = "") -> None:
    if not word:
        await ctx.send(embed=UIUtils.build_warning_embed("Thiếu từ", "Vui lòng nhập từ cần tra."))
        return
    clean_w = word.strip().lower()
    found = clean_w in COMBINED_VIETNAMESE_DICTIONARY or clean_w in ENGLISH_DICT or clean_w in COUNTRIES_VN_DICT
    if found:
        await ctx.send(embed=UIUtils.create_embed("📖 Tra cứu từ vựng", f"Từ **`{clean_w.upper()}`** CÓ TRONG hệ thống dữ liệu.", BotConfig.COLOR_PINK_DEEP))
    else:
        await ctx.send(embed=UIUtils.create_embed("📖 Tra cứu từ vựng", f"Không tìm thấy từ **`{clean_w.upper()}`**. Dùng lệnh `/themtu {clean_w}` để bổ sung ngay!", BotConfig.COLOR_RED_DARK))

# ====================================================================================================
# PHẦN 8: XỬ LÝ SỰ KIỆN TRÒ CHƠI QUA TIN NHẮN
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
            await message.channel.send(embed=UIUtils.create_embed("🏆 Chiến Thắng Vua Tiếng Việt", f"🎉 {message.author.mention} đã giải đúng từ: **`{target.upper()}`**", BotConfig.COLOR_PINK_DEEP))
        return

    # 2. Đoán Quốc Gia
    if session.active_mode == GameMode.GUESS_COUNTRY:
        if content == session.secret_country.lower():
            target = session.secret_country
            session.reset()
            await message.channel.send(embed=UIUtils.create_embed("🏆 Chiến Thắng Đoán Quốc Gia", f"🎉 {message.author.mention} đoán đúng quốc gia: **`{target.upper()}`**", BotConfig.COLOR_PINK_DEEP))
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
            await message.channel.send(embed=UIUtils.create_embed("✨ Nối từ thành công!", f"Từ hợp lệ: **`{content.upper()}`**\nÂm tiếp theo: **`{next_syl.upper()}`**", BotConfig.COLOR_PINK_DEEP))
        elif session.active_mode == GameMode.BOT_VIETNAMESE:
            candidates = VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.get(next_syl, [])
            valid_candidates = [w for w in candidates if w not in session.used_words_history]
            
            if not valid_candidates:
                session.reset()
                await message.channel.send(embed=UIUtils.create_embed("🏆 Người Chơi Thắng Bot", f"🎉 {message.author.mention} đã đánh bại Bot vì hết từ nối bắt đầu bằng: **`{next_syl.upper()}`**", BotConfig.COLOR_PINK_DEEP))
                return
            
            bot_word = random.choice(valid_candidates)
            session.used_words_history.add(bot_word)
            session.current_word = bot_word
            bot_syllables = bot_word.split()
            next_bot_syl = bot_syllables[-1] if bot_syllables else bot_word
            
            desc = f"✨ Từ của bạn: **`{content.upper()}`**\n🤖 **Bot phản đòn:** ## {bot_word.upper()}\n🌸 Âm tiết tiếp theo cho bạn: **`{next_bot_syl.upper()}`**"
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
            await message.channel.send(embed=UIUtils.create_embed("✨ Word chain success!", f"Valid word: **`{content.upper()}`**\nNext letter: **`{next_letter.upper()}`**", BotConfig.COLOR_PINK_DEEP))
        elif session.active_mode == GameMode.BOT_ENGLISH:
            candidates = ENGLISH_INDEX_BY_FIRST_LETTER.get(next_letter, [])
            valid_candidates = [w for w in candidates if w not in session.used_words_history]
            
            if not valid_candidates:
                session.reset()
                await message.channel.send(embed=UIUtils.create_embed("🏆 Player Defeated Bot", f"🎉 {message.author.mention} defeated the Bot!", BotConfig.COLOR_PINK_DEEP))
                return
            
            bot_word = random.choice(valid_candidates)
            session.used_words_history.add(bot_word)
            session.current_word = bot_word
            next_bot_letter = bot_word[-1]
            
            await message.channel.send(embed=UIUtils.create_embed("✨ Lượt đấu thành công", f"Từ của bạn: **`{content.upper()}`**\n🤖 **Bot phản đòn:** ## {bot_word.upper()}\nKý tự tiếp theo: **`{next_bot_letter.upper()}`**", BotConfig.COLOR_PINK_DEEP))
        return

# ====================================================================================================
# PHẦN 9: KHỞI CHẠY HỆ THỐNG
# ====================================================================================================

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.warning("🖤 Không tìm thấy biến môi trường DISCORD_TOKEN.")
    else:
        bot.run(token)
