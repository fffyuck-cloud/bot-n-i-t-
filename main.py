# ====================================================================================================
# ██████╗ ██╗    █████╗  ██████╗██╗  ██╗    ██████╗ ██╗███╗    ██╗██╗  ██╗    ██████╗  ██████╗ ████████╗
# ██╔══██╗██║    ██╔══██╗██╔════╝██║ ██╔╝    ██╔══██╗██║████╗   ██║██║ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
# ██████╔╗██║    ███████║██║     █████╔╝     ██████╔╝██║██╔██╗  ██║█████╔╝     ██████╔╝██║   ██║   ██║   
# ██╔══██╗██║    ██╔══██║██║     ██╔═██╗     ██╔═══╝ ██║██║╚██╗ ██║██╔═██╗     ██╔══██╗██║   ██║   ██║   
# ██████╔╗███████╗██║  ██║╚██████╗██║  ██╗    ██║     ██║██║ ╚████║██║  ██╗    ██████╔╝╚██████╔╝   ██║   
# ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝    ╚═════╝  ╚═╝    ╚═╝   
#                                                                                                   
# PURE FUN ENTERPRISE - BLACK & SAKURA PINK GOTHIC ARCADE ULTIMATE (v7.6.5 - Meme/Say/DM)
# ====================================================================================================

import os
import sys
import random
import logging
import asyncio
import threading
import unicodedata
import aiohttp
from datetime import datetime, timedelta
from typing import Set, List, Dict, Optional, Union
from flask import Flask
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

# ====================================================================================================
# PHẦN 1: CẤU HÌNH HỆ THỐNG & MÀU SẮC ĐEN HỒNG CÁNH HOA (SAKURA GOTHIC)
# ====================================================================================================

class BotConfig:
    VERSION: str = "7.6.5 Sakura Gothic Meme & Say & DM"
    DEVELOPER: str = "Black & Pink Studio"
    PREFIX: str = "?"
    OWNER_ID: int = 1312333137241575449 
    
    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = int(os.getenv("PORT", 8080))
    
    FILE_VIETNAMESE_DICT: str = "TuDien_TiengViet_Ghep_2Ban.txt"
    FILE_ENGLISH_DICT: str = "tu dien tieng anh.txt"
    FILE_COUNTRIES_DICT: str = "quoc gia vn.txt"
    
    COLOR_SAKURA_PINK: int = 0xFFB7C5   
    COLOR_DEEP_PINK: int = 0xFF1493     
    COLOR_BLACK_CHIC: int = 0x10001A    
    COLOR_RED_DARK: int = 0x8B0000      
    COLOR_GOLD: int = 0xFFD700          
    
    MSG_ERR_ALREADY_USED: str = "❌ Từ này đã được sử dụng trước đó trong ván này!"
    BORDER: str = "🌸・━━━━━━━━━━━━━━━━━━━━━━━━━━━・🌸" 

# ====================================================================================================
# PHẦN 2: DỮ LIỆU DỰ PHÒNG & GAME DATA
# ====================================================================================================

DEFAULT_VIETNAMESE_FALLBACK: Set[str] = {
    "an ninh", "an toàn", "ấm áp", "ẩm ướt", "ánh sáng", "áo quần", "ăn uống", "át chủ", "ba mươi", "bạc hà",
    "bạ bạt", "bạn bè", "bao dung", "bạo chúa", "bền bỉ", "bí quyết", "bình yên", "bồi đắp", "bứt phá", "bị ốm"
}

DEFAULT_ENGLISH_FALLBACK: Set[str] = {
    "apple", "anchor", "angel", "apex", "arrow", "azure", "acorn", "album", "amber", "amulet",
    "antique", "arctic", "astro", "aura", "avocado", "axe", "alchemy", "alert", "alpine", "amaze"
}

DEFAULT_COUNTRIES_FALLBACK: Set[str] = {
    "việt nam", "nhật bản", "hàn quốc", "pháp", "mỹ", "anh", "đức", "ý", "nga", "trung quốc"
}

COUNTRY_CODES: Dict[str, str] = {
    "việt nam": "vn", "nhật bản": "jp", "hàn quốc": "kr", "pháp": "fr",
    "mỹ": "us", "anh": "gb", "đức": "de", "ý": "it", "nga": "ru", "trung quốc": "cn"
}

EASY_START_WORDS: Set[str] = {
    "an ninh", "an toàn", "bình yên", "hạnh phúc", "cảm ơn", "xinh đẹp", "đẹp trai",
    "học sinh", "sinh viên", "gia đình", "bạn bè", "thầy giáo", "cô giáo", "máy tính",
    "điện thoại", "nước mắm", "cơm tấm", "xôi gấc", "trà sữa", "cà phê", "mưa rào",
    "nắng nóng", "mặt trời", "ánh sáng", "đêm tối", "ban ngày", "ban đêm", "thời gian",
    "không gian", "hoa hồng", "cây cối", "động vật", "con mèo", "con chó", "sông sâu",
    "biển cả", "núi cao", "đồng cỏ", "bầu trời", "mây trắng", "gió mát", "nước trong",
    "lửa nóng", "đất lành", "vàng bạc", "đồng xu", "tiền bạc", "giấy bút", "sách vở",
    "bàn ghế", "nhà cửa", "xe cộ", "thuyền bè", "máy bay", "tàu hỏa", "ông bà",
    "cha mẹ", "anh chị", "em út", "cô chú", "bác sĩ", "y tá", "công an", "bộ đội",
    "giáo viên", "ca sĩ", "nhạc cụ", "màu sắc", "bức tranh", "bài thơ", "câu chuyện",
    "sự kiện", "tin tức", "báo chí", "truyền hình", "thư viện", "bảo tàng", "rạp chiếu",
    "quán ăn", "cửa hàng", "chợ búa", "siêu thị", "trung tâm", "thành phố", "thủ đô",
    "quê hương", "đất nước", "thế giới", "vũ trụ", "hành tinh", "mặt đất", "bầu bạn",
    "tình yêu", "tình bạn", "trung thành", "chân thật", "thành thật", "vui vẻ", "buồn bã",
    "giận dữ", "hơi nước", "nhiệt độ", "khí hậu", "bão táp", "mưa bão", "nắng hạn",
    "thủy lợi", "thủy tinh", "kim loại", "thủy ngân", "đường sá", "ngõ hẻm"
}

FALLBACK_MOVIES_DATA: List[Dict[str, str]] = [
    {"title": "kẻ trộm giấc mơ", "clue": "🌟 Ngủ đông trong mơ, con quay còn xoay... 🌀", "image": "https://image.tmdb.org/t/p/w500/s3TBrRGB1iav7gFOCNx3HvMo4J4.jpg"},
    {"title": "titanic", "clue": "🚢 Tảng băng trôi, bài hát My Heart Will Go On 💔", "image": "https://image.tmdb.org/t/p/w500/2bXcWyivE3atm2bUCVn0gSZweBO.jpg"},
    {"title": "avatar", "clue": "👽 Người Na'vi màu xanh 🌳", "image": "https://image.tmdb.org/t/p/w500/2B0bWqU7lTr7gRgSjIwO4W4cQ0M.jpg"},
    {"title": "ký sinh trùng", "clue": "🪨 Giới siêu giàu và gia đình nghèo len lỏi 🏠", "image": "https://image.tmdb.org/t/p/w500/TU9NIjwzjoKPwQHoHshkFcQUCG.jpg"},
    {"title": "joker", "clue": "🃏 Kẻ thù của Batman, nụ cười rùng rợn 🤡", "image": "https://image.tmdb.org/t/p/w500/ijQ4s9h7KQ3oJX47j7zev8a3Jhf.jpg"},
    {"title": "hack não", "clue": "💊 Viên thuốc đỏ hay xanh? 🕶️ Mã nhị phân", "image": "https://image.tmdb.org/t/p/w500/icmmSD4vTTDKOq2vvdulafOGw93.jpg"},
    {"title": "nữ hoàng băng giá", "clue": "❄️ Elsa và Anna ⛄", "image": "https://image.tmdb.org/t/p/w500/7H7TrYnHqNLUc5AknSdVZPbZm5B.jpg"},
    {"title": "người nhện", "clue": "🕷️ Người hàng xóm thân thiện 🕸️", "image": "https://image.tmdb.org/t/p/w500/1R6cvRtZgsYC5pQmDh2nO3tdY4w.jpg"},
    {"title": "hố đen vũ trụ", "clue": "🌌 Du hành vũ trụ, tìm hành tinh mới 🚀", "image": "https://image.tmdb.org/t/p/w500/xJHokMbljvjADYdit5fS5JsdtyZ.jpg"},
    {"title": "kỵ sĩ bóng đêm", "clue": "🦇 Người dơi và Joker ⚡", "image": "https://image.tmdb.org/t/p/w500/hqkIcbrOHL86UncnHIsHVcVmzue.jpg"},
    {"title": "biệt đội siêu anh hùng", "clue": "💥 Đánh bại Thanos, hoàn nguyên ★", "image": "https://image.tmdb.org/t/p/w500/7RyHsO4yDXtBv1zUU3mTpHeQ0d5.jpg"},
    {"title": "vua sư tử", "clue": "🦁 Simba và Pride Rock 🌅", "image": "https://image.tmdb.org/t/p/w500/wTXs2WdH9N2mP3fRbExXe5Jz0pI.jpg"},
    {"title": "chàng trai tốt bụng", "clue": "🏃 Chạy xuyên nước Mỹ, hộp sô-cô-la 🍫", "image": "https://image.tmdb.org/t/p/w500/3h1JZGDhZ8nzxdgvkxha0qBqi05.jpg"},
    {"title": "bố già", "clue": "🐎 Mafia Ý, gia đình Corleone 🍷", "image": "https://image.tmdb.org/t/p/w500/tmU7GeKVybMWFButWEGl2M4GeiP.jpg"},
    {"title": "harry potter", "clue": "⚡ Phù thủy, trường Hogwarts 🦉", "image": "https://image.tmdb.org/t/p/w500/3yEUqjTrfyOaIctqL2t7gWc6c9w.jpg"}
]

EMOJI_DATA: List[Dict[str, str]] = [
    {"phrase": "mưa rơi", "emojis": "🌧️☔💧"},
    {"phrase": "cá mập", "emojis": "🦈🌊🩸"},
    {"phrase": "bàn tay vàng", "emojis": "✋💛🏆"},
    {"phrase": "mặt trời mọc", "emojis": "🌅☀️🌄"},
    {"phrase": "chim cánh cụt", "emojis": "🐧🐧🐧"},
    {"phrase": "con mèo đen", "emojis": "🐈‍⬛🖤🌙"},
    {"phrase": "quả táo đỏ", "emojis": "🍎🔴🌳"},
    {"phrase": "máy bay giấy", "emojis": "✈️📄✨"}
]

# ====================================================================================================
# PHẦN 3: HỆ THỐNG LOGGING & WEB SERVER
# ====================================================================================================

class LoggerSetup:
    @staticmethod
    def initialize_logger() -> logging.Logger:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        formatter = logging.Formatter(fmt="[%(asctime)s] | %(levelname)-8s | [%(module)s.%(funcName)s] : %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger_instance = logging.getLogger("SakuraGothicBot")
        logger_instance.setLevel(logging.INFO)
        logger_instance.addHandler(console_handler)
        return logger_instance

logger = LoggerSetup.initialize_logger()

keep_alive_app = Flask("SakuraKeepAlive")

@keep_alive_app.route('/')
def route_home() -> str:
    return "<h1>Sakura Black Pink Arcade (v7.6)</h1><p style='color:#FFB7C5'>Status: <strong>ONLINE & AESTHETIC</strong></p>"

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
                        if clean: words.add(clean)
                logger.info(f"🖤🌸 Đã nạp {len(words):,} mục từ file [{filepath}].")
            except Exception as err:
                logger.error(f"Lỗi đọc file {filepath}: {err}")
        else:
            logger.warning(f"Không tìm thấy file [{filepath}]. Tạo mới bằng dữ liệu Sakura.")
            try:
                with open(filepath, "w", encoding="utf-8") as f: f.write("\n".join(fallback_dataset))
            except Exception: pass
        return words

    @staticmethod
    def append_word_to_file(filepath: str, word: str) -> bool:
        try:
            mode = "a" if os.path.exists(filepath) else "w"
            with open(filepath, mode, encoding="utf-8") as f: f.write(f"\n{word}")
            return True
        except Exception as err:
            logger.error(f"Lỗi ghi file {filepath}: {err}")
            return False

RAW_VIETNAMESE_DICT: Set[str] = DataManager.load_text_file(BotConfig.FILE_VIETNAMESE_DICT, DEFAULT_VIETNAMESE_FALLBACK)
ENGLISH_DICT: Set[str] = DataManager.load_text_file(BotConfig.FILE_ENGLISH_DICT, DEFAULT_ENGLISH_FALLBACK)
COUNTRIES_VN_DICT: Set[str] = DataManager.load_text_file(BotConfig.FILE_COUNTRIES_DICT, DEFAULT_COUNTRIES_FALLBACK)

COMBINED_VIETNAMESE_DICTIONARY: Set[str] = {w for w in RAW_VIETNAMESE_DICT if len(w.split()) == 2}

COMBINED_VIETNAMESE_LIST: List[str] = list(COMBINED_VIETNAMESE_DICTIONARY)
EASY_START_LIST: List[str] = list(EASY_START_WORDS)
ENGLISH_LIST: List[str] = list(ENGLISH_DICT)
COUNTRIES_VN_LIST: List[str] = list(COUNTRIES_VN_DICT)
VUA_TIENG_VIET_CANDIDATES: List[str] = [w for w in COMBINED_VIETNAMESE_DICTIONARY if len(w.split()) >= 2]

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
# PHẦN 5: QUẢN LÝ PHIÊN CHƠI & UI ĐEN HỒNG CÁNH HOA
# ====================================================================================================

class GameMode:
    NONE = "none"
    PVP_VIETNAMESE = "pvp_vi"
    BOT_VIETNAMESE = "bot_vi"
    PVP_ENGLISH = "pvp_en"
    BOT_ENGLISH = "bot_en"
    VUA_TIENG_VIET = "vua_vi"
    GUESS_COUNTRY = "doan_quoc_gia"
    GUESS_MOVIE = "guess_movie"
    GUESS_EMOJI = "guess_emoji"

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
        self.secret_target = "" 
        
        self.is_hardcore: bool = False
        self.hardcore_time: int = 15
        self.hardcore_task: Optional[asyncio.Task] = None
        self.last_player_id: Optional[int] = None
        
        self.is_banned_mode: bool = False
        self.banned_letter: str = ""

    def initialize_session(self, mode: str, start_word: str = "", target: str = "") -> None:
        self.reset()
        self.is_active = True
        self.active_mode = mode
        if mode in [GameMode.PVP_VIETNAMESE, GameMode.BOT_VIETNAMESE, GameMode.PVP_ENGLISH, GameMode.BOT_ENGLISH]:
            self.current_word = start_word
            self.used_words_history.add(start_word)
            self.turn_counter = 1
        elif mode == GameMode.VUA_TIENG_VIET: self.scrambled_target = target
        elif mode == GameMode.GUESS_COUNTRY: self.secret_country = target
        elif mode in [GameMode.GUESS_MOVIE, GameMode.GUESS_EMOJI]: self.secret_target = target

    def reset(self) -> None:
        if self.hardcore_task and not self.hardcore_task.done():
            self.hardcore_task.cancel()
        self.active_mode = GameMode.NONE
        self.is_active = False
        self.current_word = ""
        self.used_words_history.clear()
        self.turn_counter = 0
        self.scrambled_target = ""
        self.secret_country = ""
        self.secret_target = ""
        
        self.is_hardcore = False
        self.hardcore_time = 15
        self.last_player_id = None
        self.is_banned_mode = False
        self.banned_letter = ""

    async def start_hardcore_timer(self, channel: discord.TextChannel):
        if self.hardcore_task and not self.hardcore_task.done():
            self.hardcore_task.cancel()
            
        async def timer_callback():
            try:
                await asyncio.sleep(self.hardcore_time)
                if self.is_active:
                    self.is_active = False
                    if self.active_mode == GameMode.PVP_VIETNAMESE:
                        winner_msg = f"🏆 Người chiến thắng là <@{self.last_player_id}> vì không ai nối kịp từ sau họ!" if self.last_player_id else "Không ai nối kịp từ!"
                    else:
                        winner_msg = "🤖 Bot chiến thắng vì bạn không nối kịp từ!"
                    
                    desc = f"{BotConfig.BORDER}\n\n⏰ **HẾT GIỜ!**\n💀 Ván chơi Hardcore kết thúc!\n{winner_msg}\n\n{BotConfig.BORDER}"
                    embed = UIUtils.create_embed("⏳ [ HẾT GIỜ! ] ⏳", desc, BotConfig.COLOR_BLACK_CHIC)
                    await channel.send(embed=embed)
                    self.reset()
            except asyncio.CancelledError:
                pass
            
        self.hardcore_task = asyncio.create_task(timer_callback())

class SessionManager:
    def __init__(self): self._sessions: Dict[int, ChannelSession] = {}
    def get_session(self, channel_id: int) -> ChannelSession:
        if channel_id not in self._sessions: self._sessions[channel_id] = ChannelSession(channel_id)
        return self._sessions[channel_id]

global_session_manager = SessionManager()

counting_channels: Dict[int, Dict[str, int]] = {} 
mention_tracker: Dict[int, Dict[str, Union[int, datetime]]] = {} 

class GameUtils:
    @staticmethod
    def remove_diacritics(text: str) -> str:
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

    @staticmethod
    def scramble_vietnamese_syllables(phrase: str) -> str:
        syllables = phrase.split()
        if len(syllables) <= 1: return phrase
        shuffled = syllables.copy()
        attempts = 0
        while shuffled == syllables and attempts < 10:
            random.shuffle(shuffled)
            attempts += 1
        return " ".join(shuffled)

    @staticmethod
    def generate_country_mask(country_name: str) -> str:
        if not country_name: return ""
        characters = list(country_name)
        masked_chars = []
        for index, char in enumerate(characters):
            if char == ' ': masked_chars.append(' ')
            elif index == 0 or index == len(characters) - 1: masked_chars.append(char.upper())
            else: masked_chars.append('_')
        return " ".join(masked_chars)

class UIUtils:
    DEFAULT_FOOTER_ICON = "https://cdn.discordapp.com/embed/avatars/0.png"
    DEFAULT_THUMBNAIL = "https://images.unsplash.com/photo-1522383225653-ed111181a951?ixlib=rb-4.0.3&auto=format&fit=crop&w=150&q=80"
    BANNER_IMAGE = "https://i.pinimg.com/736x/8c/a3/1f/8ca31f3c7f89c2a7a6575b06e3c7a1f2.jpg"

    @staticmethod
    def create_embed(title: str, description: str, color: int = BotConfig.COLOR_SAKURA_PINK, image_url: str = None) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now())
        embed.set_footer(text="🖤🌸 Sakura Black Pink Arcade 🌸🖤", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        embed.set_thumbnail(url=UIUtils.DEFAULT_THUMBNAIL)
        embed.set_image(url=image_url if image_url else UIUtils.BANNER_IMAGE)
        return embed

    @staticmethod
    def build_warning_embed(title: str, warning_msg: str) -> discord.Embed:
        desc = f"{BotConfig.BORDER}\n\n⚠️ **{title}**\n\n{warning_msg}\n\n{BotConfig.BORDER}"
        return UIUtils.create_embed("🚫 Cảnh Báo", desc, BotConfig.COLOR_RED_DARK)

    @staticmethod
    def build_invalid_word_embed(reason: str) -> discord.Embed:
        description = f"{BotConfig.BORDER}\n\n❌ **Từ không hợp lệ!**\n📌 **Nguyên nhân:** *{reason}*\n💡 Dùng `/themtu [từ]` để bổ sung!\n\n{BotConfig.BORDER}"
        return UIUtils.create_embed("💔 [ TỪ KHÔNG HỢP LỆ ] 💔", description, BotConfig.COLOR_RED_DARK)

    @staticmethod
    def build_success_embed(title: str, success_msg: str) -> discord.Embed:
        desc = f"{BotConfig.BORDER}\n\n✨ **{title.upper()}** ✨\n\n{success_msg}\n\n{BotConfig.BORDER}"
        return UIUtils.create_embed("🌸 Thành Công 🌸", desc, BotConfig.COLOR_DEEP_PINK)

    @staticmethod
    def build_help_embed() -> discord.Embed:
        description = (
            f"{BotConfig.BORDER}\n\n"
            f"🖤 **Chào mừng đến với Vườn hoa Đen Hồng Cánh Hoa!** 🌸\n"
            f"❯ Hãy chọn một lệnh để bắt đầu giải trí.\n\n"
            
            f"🇻🇳🌸 **[ NỐI TỪ TIẾNG VIỆT ]** 🌸🇻🇳\n"
            f"❯ `{BotConfig.PREFIX}noitu` ❯ **PvP**\n"
            f"❯ `{BotConfig.PREFIX}botnoitu` ❯ **Solo Bot**\n"
            f"❯ `{BotConfig.PREFIX}noituhc [giây]` ❯ **PvP Hardcore**\n"
            f"❯ `{BotConfig.PREFIX}botnoituhc [giây]` ❯ **Bot Hardcore**\n"
            f"❯ `{BotConfig.PREFIX}noitucam` ❯ **PvP Cấm Chữ**\n"
            f"❯ `{BotConfig.PREFIX}botnoitucam` ❯ **Bot Cấm Chữ**\n"
            f"❯ `{BotConfig.PREFIX}noitucamhc [giây]` ❯ **PvP Cấm Chữ + HC**\n"
            f"❯ `{BotConfig.PREFIX}botnoitucamhc [giây]` ❯ **Bot Cấm Chữ + HC**\n\n"

            f"🇬🇧🌸 **[ NỐI TỪ TIẾNG ANH ]** 🌸🇬🇧\n"
            f"❯ `{BotConfig.PREFIX}noitueng` ❯ **PvP**\n"
            f"❯ `{BotConfig.PREFIX}botnoitueng` ❯ **Solo Bot**\n\n"

            f"👑🌸 **[ GIẢI ĐỐ & ARCADE ]** 🌸👑\n"
            f"❯ `{BotConfig.PREFIX}vuatiengviet` ❯ **Sắp xếp âm**\n"
            f"❯ `{BotConfig.PREFIX}doanquocgia` ❯ **Đoán cờ**\n"
            f"❯ `{BotConfig.PREFIX}doantenphim` ❯ **Đoán tên phim**\n"
            f"❯ `{BotConfig.PREFIX}doanemoji` ❯ **Đoán Emoji**\n\n"

            f"⚙️🌸 **[ QUẢN LÝ & TIỆN ÍCH ]** 🌸⚙️\n"
            f"❯ `/themtu [từ]` ❯ **Thêm từ (Admin)**\n"
            f"❯ `{BotConfig.PREFIX}admin` ❯ **Panel (Admin)**\n"
            f"❯ `{BotConfig.PREFIX}afk [lý do]` ❯ **Bật chế độ AFK**\n"
            f"❯ `{BotConfig.PREFIX}countsetup` ❯ **Bật kênh đếm số (Admin)**\n"
            f"❯ `{BotConfig.PREFIX}restart` ❯ **Chơi lại từ đầu**\n"
            f"❯ `{BotConfig.PREFIX}huyvanchoi` ❯ **Hủy ván chơi**\n"
            f"❯ `{BotConfig.PREFIX}nghia [từ]` ❯ **Tra cứu từ điển**\n"
            f"❯ `{BotConfig.PREFIX}tiepterauma [@user]` ❯ **Tiếp tế rau má**\n"
            f"❯ `{BotConfig.PREFIX}meme` ❯ **Lấy ảnh meme ngẫu nhiên**\n"
            f"❯ `{BotConfig.PREFIX}say [nội dung]` ❯ **Bot nói thay bạn**\n"
            f"❯ `{BotConfig.PREFIX}dm [@user] [nội dung]` ❯ **Gửi DM ẩn danh**\n"
            f"❯ `{BotConfig.PREFIX}ping` ❯ **Kiểm tra độ trễ**\n\n"
            f"{BotConfig.BORDER}"
        )
        return UIUtils.create_embed("✦ HỆ THỐNG TRỢ GIÚP SAKURA ✦", description, BotConfig.COLOR_SAKURA_PINK)

class TicTacToeView(View):
    def __init__(self):
        super().__init__(timeout=120.0)
        self.board = [" " for _ in range(9)]
        self.update_buttons()

    def check_winner(self) -> str:
        wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in wins:
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] != " ": return self.board[a]
        return "tie" if " " not in self.board else "none"

    def update_buttons(self):
        self.clear_items()
        for i in range(9):
            style = discord.ButtonStyle.secondary
            label = str(i + 1) 
            if self.board[i] == "X": style, label = discord.ButtonStyle.danger, "❌"
            elif self.board[i] == "O": style, label = discord.ButtonStyle.success, "⭕"
            btn = Button(label=label, style=style, row=i//3, disabled=(self.board[i] != " "))
            btn.callback = self.make_callback(i)
            self.add_item(btn)

    def make_callback(self, idx):
        async def callback(interaction: discord.Interaction):
            if self.check_winner() != "none": return
            self.board[idx] = "X"
            winner = self.check_winner()
            if winner == "none":
                empty_spots = [i for i, val in enumerate(self.board) if val == " "]
                if empty_spots:
                    bot_move = random.choice(empty_spots)
                    self.board[bot_move] = "O"
                    winner = self.check_winner()
            self.update_buttons()
            if winner == "X": content = f"🎉 {interaction.user.mention} đã chiến thắng Bot!"; self.disable_all_items()
            elif winner == "O": content = "🤖 Bot đã chiến thắng!"; self.disable_all_items()
            elif winner == "tie": content = "🤝 Hòa!"; self.disable_all_items()
            else: content = f"🖤🌸 Lượt đi của **{interaction.user.display_name}** (X)"
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

afk_users: Dict[int, Dict[int, Dict[str, Union[datetime, str]]]] = {}

@bot.event
async def on_ready() -> None:
    logger.info(f"✅ Bot Đen Hồng Cánh Hoa đã đăng nhập: {bot.user}")
    try:
        synced = await bot.tree.sync()
        logger.info(f"✅ Đã đồng bộ {len(synced)} lệnh Slash.")
    except Exception as e: logger.error(f"Lỗi đồng bộ Slash: {e}")
    activity = discord.Activity(type=discord.ActivityType.playing, name=f"{BotConfig.PREFIX}help | 🖤🌸 Sakura Gothic")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_command_error(ctx: commands.Context, error: Exception) -> None:
    if isinstance(error, commands.CommandNotFound): pass
    elif isinstance(error, commands.MissingRequiredArgument): await ctx.send(embed=UIUtils.build_warning_embed("Thiếu Thông Tin", f"Vui lòng gõ `{BotConfig.PREFIX}help`."))
    elif isinstance(error, commands.CheckFailure): await ctx.send(embed=UIUtils.build_warning_embed("Quyền Truy Cập", "🖤 Lệnh này dành riêng cho **Owner**!"))
    else: logger.error(f"Lỗi lệnh: {error}")

@bot.command(name="ping")
async def sys_ping(ctx: commands.Context) -> None:
    latency = round(bot.latency * 1000)
    desc = f"{BotConfig.BORDER}\n\n💓 **Độ trễ:** `{latency}ms`\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🏓 Pong!", desc, BotConfig.COLOR_SAKURA_PINK))

@bot.command(name="about")
async def sys_about(ctx: commands.Context) -> None:
    desc = f"{BotConfig.BORDER}\n\n🤖 **Sakura Arcade ({BotConfig.VERSION})**\n• 🇻🇳 TV: {len(COMBINED_VIETNAMESE_DICTIONARY):,}\n• 🇬🇧 TA: {len(ENGLISH_DICT):,}\n• 🌍 QG: {len(COUNTRIES_VN_DICT):,}\n• 🎬 Phim: {len(FALLBACK_MOVIES_DATA):,}\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🖤🌸 Về Hệ Thống", desc, BotConfig.COLOR_BLACK_CHIC))

@bot.command(name="help", aliases=["menu"])
async def sys_help(ctx: commands.Context) -> None: await ctx.send(embed=UIUtils.build_help_embed())

@bot.command(name="userinfo", aliases=["whois"])
async def sys_userinfo(ctx: commands.Context, member: Optional[discord.Member] = None) -> None:
    target = member or ctx.author
    desc = f"{BotConfig.BORDER}\n\n👤 **Tên:** {target.display_name}\n🆔 **ID:** `{target.id}`\n📅 **Tạo:** {target.created_at.strftime('%d/%m/%Y')}\n📥 **Vào:** {target.joined_at.strftime('%d/%m/%Y') if target.joined_at else 'N/A'}\n\n{BotConfig.BORDER}"
    embed = UIUtils.create_embed("🖤🌸 Thông Tin Người Dùng", desc, BotConfig.COLOR_DEEP_PINK)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="serverinfo", aliases=["svinfo"])
async def sys_serverinfo(ctx: commands.Context) -> None:
    guild = ctx.guild
    desc = f"{BotConfig.BORDER}\n\n🌐 **Server:** {guild.name}\n👑 **Owner:** <@{guild.owner_id}>\n👥 **Members:** {guild.member_count}\n\n{BotConfig.BORDER}"
    embed = UIUtils.create_embed("🖤🌸 Thông Tin Server", desc, BotConfig.COLOR_DEEP_PINK)
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)

@bot.command(name="admin", aliases=["owner"])
@commands.is_owner()
async def cmd_admin(ctx: commands.Context) -> None:
    if ctx.author.id != BotConfig.OWNER_ID: return
    desc = f"{BotConfig.BORDER}\n\n🖤 **Chào mừng Quản trị viên tối cao!** 🌸\n• 🎮 Sessions: {len(global_session_manager._sessions)}\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🔒🌸 [ ADMIN PANEL ] 🌸🔒", desc, BotConfig.COLOR_BLACK_CHIC))

@bot.tree.command(name="themtu", description="Thêm từ mới vào từ điển (Chỉ Owner)")
async def slash_themtu(interaction: discord.Interaction, word: str):
    if interaction.user.id != BotConfig.OWNER_ID:
        err_msg = f"{BotConfig.BORDER}\n\n🖤 Bạn không có quyền dùng lệnh này!\n\n{BotConfig.BORDER}"
        await interaction.response.send_message(embed=discord.Embed(title="⛔ CHẶN QUYỀN", description=err_msg, color=BotConfig.COLOR_RED_DARK), ephemeral=True)
        return
    clean_w = word.strip().lower()
    syl_parts = clean_w.split()
    if len(syl_parts) == 2:
        if clean_w in COMBINED_VIETNAMESE_DICTIONARY:
            await interaction.response.send_message(embed=UIUtils.build_warning_embed("Đã tồn tại", f"Từ **`{clean_w.upper()}`** đã có!"), ephemeral=True)
            return
        COMBINED_VIETNAMESE_DICTIONARY.add(clean_w); COMBINED_VIETNAMESE_LIST.append(clean_w)
        VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.setdefault(syl_parts[0], []).append(clean_w)
        DataManager.append_word_to_file(BotConfig.FILE_VIETNAMESE_DICT, clean_w)
        await interaction.response.send_message(embed=UIUtils.build_success_embed("Thêm từ thành công", f"Đã lưu TV **`{clean_w.upper()}`**!"))
    elif len(syl_parts) == 1 and clean_w.isalpha():
        if clean_w in ENGLISH_DICT:
            await interaction.response.send_message(embed=UIUtils.build_warning_embed("Đã tồn tại", f"Word **`{clean_w.upper()}`** already exists!"), ephemeral=True)
            return
        ENGLISH_DICT.add(clean_w); ENGLISH_LIST.append(clean_w)
        ENGLISH_INDEX_BY_FIRST_LETTER.setdefault(clean_w[0], []).append(clean_w)
        DataManager.append_word_to_file(BotConfig.FILE_ENGLISH_DICT, clean_w)
        await interaction.response.send_message(embed=UIUtils.build_success_embed("Thêm từ thành công", f"Đã lưu TA **`{clean_w.upper()}`**!"))
    else:
        await interaction.response.send_message(embed=UIUtils.build_invalid_word_embed("Từ TV phải 2 tiếng, TA phải 1 tiếng!"), ephemeral=True)

@bot.command(name="afk", aliases=["away"])
async def cmd_afk(ctx: commands.Context, *, reason: str = "Không có lý do"):
    guild_id = ctx.guild.id
    user_id = ctx.author.id
    
    if guild_id not in afk_users:
        afk_users[guild_id] = {}
        
    afk_users[guild_id][user_id] = {
        "timestamp": datetime.now(),
        "reason": reason
    }
    
    try:
        if not ctx.author.display_name.startswith("[AFK] "):
            await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
    except discord.Forbidden:
        pass
    except Exception as e:
        logger.error(f"Lỗi đổi tên AFK: {e}")
        
    desc = f"{BotConfig.BORDER}\n\n💤 {ctx.author.mention} đã chuyển sang chế độ AFK.\n📝 Lý do: *{reason}*\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🌸 Chế Độ AFK", desc, BotConfig.COLOR_BLACK_CHIC))

@bot.command(name="tiepterauma", aliases=["trauma", "rauma", "tra"])
async def cmd_tiepterauma(ctx: commands.Context, member: Optional[discord.Member] = None) -> None:
    if not member:
        await ctx.send(embed=UIUtils.build_warning_embed("Thiếu Người Chơi", f"Vui lòng tag người bạn muốn tiếp tế. VD: `{BotConfig.PREFIX}tiepterauma @user`"))
        return
    
    if member.id == bot.user.id:
        await ctx.send("🤖 Bot không cần uống rau má đâu! 🌸")
        return
        
    desc = f"{BotConfig.BORDER}\n\n🌿 Đã tiếp tế 36 rau má cho {member.mention}! 💚\n\n{BotConfig.BORDER}"
        
    await ctx.send(embed=UIUtils.create_embed("Tiếp tế rau má", desc, BotConfig.COLOR_SAKURA_PINK))

@bot.command(name="countsetup", aliases=["setupcount", "demso"])
@commands.has_permissions(administrator=True)
async def cmd_countsetup(ctx: commands.Context):
    counting_channels[ctx.channel.id] = {"current": 0, "high_score": 0, "last_user": 0}
    desc = f"{BotConfig.BORDER}\n\n🔢 **Kênh Đếm Số đã được kích hoạt!**\n\nNgười tiếp theo hãy gõ số **1** để bắt đầu.\n⚠️ *Lưu ý: Không được đếm 2 lần liên tiếp, đếm sai là về 0!* 🌸\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🌸 Đếm Số Sakura", desc, BotConfig.COLOR_SAKURA_PINK))
    try:
        await ctx.message.delete()
    except:
        pass

@bot.command(name="countstatus", aliases=["diemdem"])
async def cmd_countstatus(ctx: commands.Context):
    if ctx.channel.id in counting_channels:
        data = counting_channels[ctx.channel.id]
        desc = f"{BotConfig.BORDER}\n\n🔢 Số hiện tại: **{data['current']}**\n🏆 Kỷ lục: **{data['high_score']}**\n\n{BotConfig.BORDER}"
        await ctx.send(embed=UIUtils.create_embed("🌸 Trạng Thái Đếm Số", desc, BotConfig.COLOR_DEEP_PINK))
    else:
        await ctx.send(embed=UIUtils.build_warning_embed("Chưa bật kênh", "Kênh này chưa bật tính năng đếm số. Admin hãy dùng `?countsetup`."))

# LỆNH MỚI: MEME NGẪU NHIÊN
@bot.command(name="meme", aliases=["meme random"])
async def cmd_meme(ctx: commands.Context) -> None:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://meme-api.com/gimme") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    title = data.get("title", "Meme Ngẫu Nhiên")
                    url = data.get("url")
                    post_link = data.get("postLink", "")
                    desc = f"[🔗 Nguồn: Reddit]({post_link})" if post_link else "Meme từ Reddit"
                    embed = UIUtils.create_embed(f"🖼️ {title}", desc, BotConfig.COLOR_SAKURA_PINK, image_url=url)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("🖤 Không lấy được meme lúc này, thử lại sau nhé! 🌸")
        except Exception as e:
            logger.error(f"Lỗi lấy meme: {e}")
            await ctx.send("🖤 Lỗi kết nối API meme! 🌸")

# LỆNH MỚI: SAY (BOT NÓI THAY)
@bot.command(name="say", aliases=["echo"])
async def cmd_say(ctx: commands.Context, *, text: str) -> None:
    try:
        await ctx.message.delete()
    except:
        pass
    await ctx.send(text)

# LỆNH MỚI: DM (GỬI TIN NHẮN ẨN DANH)
@bot.command(name="dm", aliases=["guian", "gui_dm"])
async def cmd_dm(ctx: commands.Context, member: discord.Member, *, message: str) -> None:
    if member.bot:
        await ctx.send("🤖 Bot không cần nhận tin nhắn đâu! 🌸")
        return
        
    try:
        await member.send(f"💌 **Bạn có 1 tin nhắn ẩn danh:**\n\n{message}\n\n*— Từ Vườn hoa Đen Hồng*")
        await ctx.send(f"✅ Đã gửi tin nhắn ẩn danh cho {member.mention}! 🌸")
    except discord.Forbidden:
        await ctx.send(f"❌ Không thể gửi tin nhắn cho {member.mention}. Họ có thể đã tắt DM (Direct Messages) hoặc không cho phép bot nhắn tin. 🌸")
    except Exception as e:
        logger.error(f"Lỗi gửi DM: {e}")
        await ctx.send(f"❌ Lỗi không xác định khi gửi DM. 🌸")

# ====================================================================================================
# PHẦN 7: CÁC LỆNH TRÒ CHƠI & GIẢI TRÍ ARCADE
# ====================================================================================================

@bot.command(name="noitu")
async def cmd_noitu(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
    session.initialize_session(GameMode.PVP_VIETNAMESE, start_word=start_word)
    await ctx.send(embed=UIUtils.create_embed("💕 Nối Từ PvP", f"{BotConfig.BORDER}\n\n👉 Từ: **`{start_word.upper()}`**\n🌸 Tiếp: **`{syllables[-1].upper()}`**\n\n{BotConfig.BORDER}"))

@bot.command(name="botnoitu", aliases=["noituubot"])
async def cmd_botnoitu(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
    session.initialize_session(GameMode.BOT_VIETNAMESE, start_word=start_word)
    await ctx.send(embed=UIUtils.create_embed("🤖 Solo Bot TV", f"{BotConfig.BORDER}\n\n👉 Từ: **`{start_word.upper()}`**\n🌸 Tiếp: **`{syllables[-1].upper()}`**\n\n{BotConfig.BORDER}"))

@bot.command(name="noituhc", aliases=["noituhardcore", "hardcorenoitu"])
async def cmd_noituhc(ctx: commands.Context, seconds: int = 15) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    if seconds < 5 or seconds > 120: seconds = 15
    start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
    session.initialize_session(GameMode.PVP_VIETNAMESE, start_word=start_word)
    session.is_hardcore = True
    session.hardcore_time = seconds
    session.last_player_id = ctx.author.id
    
    desc = (f"{BotConfig.BORDER}\n\n"
            f"💀 **CẢNH BÁO: CHẾ ĐỘ HARDCORE** 💀\n"
            f"⏱️ **Thời gian trả lời:** `{seconds} giây`\n\n"
            f"👉 Từ bắt đầu: **`{start_word.upper()}`**\n"
            f"🌸 Cần nối bằng: **`{syllables[-1].upper()}`**\n\n"
            f"⚠️ *Hết giờ mà không ai nối được -> Người cuối cùng nối thành công sẽ THẮNG!*\n\n{BotConfig.BORDER}")
    
    await ctx.send(embed=UIUtils.create_embed("🔥 [ NỐI TỪ HARDCORE ] 🔥", desc, BotConfig.COLOR_RED_DARK))
    await session.start_hardcore_timer(ctx.channel)

@bot.command(name="botnoituhc", aliases=["noituubothc"])
async def cmd_botnoituhc(ctx: commands.Context, seconds: int = 15) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    if seconds < 5 or seconds > 120: seconds = 15
    start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
    session.initialize_session(GameMode.BOT_VIETNAMESE, start_word=start_word)
    session.is_hardcore = True
    session.hardcore_time = seconds
    session.last_player_id = None
    
    desc = (f"{BotConfig.BORDER}\n\n"
            f"🤖💀 **SOLO BOT HARDCORE** 💀🤖\n"
            f"⏱️ **Thời gian trả lời:** `{seconds} giây`\n\n"
            f"👉 Từ bắt đầu: **`{start_word.upper()}`**\n"
            f"🌸 Cần nối bằng: **`{syllables[-1].upper()}`**\n\n"
            f"⚠️ *Nếu bạn không nối kịp giờ, Bot sẽ thắng!*\n\n{BotConfig.BORDER}")
    
    await ctx.send(embed=UIUtils.create_embed("🔥 [ SOLO BOT HARDCORE ] 🔥", desc, BotConfig.COLOR_RED_DARK))
    await session.start_hardcore_timer(ctx.channel)

@bot.command(name="noitucam", aliases=["noitucombanned"])
async def cmd_noitucam(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    
    banned_letter = random.choice("abcdefghijklmnopqrstuvwxyz")
    start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
    while banned_letter in GameUtils.remove_diacritics(start_word):
        start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
        
    session.initialize_session(GameMode.PVP_VIETNAMESE, start_word=start_word)
    session.is_banned_mode = True
    session.banned_letter = banned_letter
    
    desc = (f"{BotConfig.BORDER}\n\n"
            f"💥 **CHẾ ĐỘ NỐI TỪ CẤM** 💥\n"
            f"🚫 **Chữ cái bị cấm:** `{banned_letter.upper()}`\n"
            f"⚠️ *Bất kỳ từ nào có chứa chữ này - dù có dấu hay không - đều sẽ khiến bạn THUA ngay lập tức!*\n\n"
            f"👉 **Từ bắt đầu:** `{start_word.upper()}`\n"
            f"🌸 **Cần nối bằng:** `{syllables[-1].upper()}`\n\n{BotConfig.BORDER}")
    
    await ctx.send(embed=UIUtils.create_embed("🚫 [ NỐI TỪ CẤM PvP ] 🚫", desc, BotConfig.COLOR_BLACK_CHIC))

@bot.command(name="botnoitucam", aliases=["botnoitucombanned"])
async def cmd_botnoitucam(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    
    banned_letter = random.choice("abcdefghijklmnopqrstuvwxyz")
    start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
    while banned_letter in GameUtils.remove_diacritics(start_word):
        start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
        
    session.initialize_session(GameMode.BOT_VIETNAMESE, start_word=start_word)
    session.is_banned_mode = True
    session.banned_letter = banned_letter
    
    desc = (f"{BotConfig.BORDER}\n\n"
            f"🤖💥 **SOLO BOT NỐI TỪ CẤM** 💥🤖\n"
            f"🚫 **Chữ cái bị cấm:** `{banned_letter.upper()}`\n\n"
            f"👉 **Từ bắt đầu:** `{start_word.upper()}`\n"
            f"🌸 **Cần nối bằng:** `{syllables[-1].upper()}`\n\n"
            f"⚠️ *Nếu bạn dùng chữ cấm, bạn thua. Nếu Bot không tìm được từ hợp lệ, Bot thua!*\n\n{BotConfig.BORDER}")
    
    await ctx.send(embed=UIUtils.create_embed("🚫 [ BOT NỐI TỪ CẤM ] 🚫", desc, BotConfig.COLOR_BLACK_CHIC))

@bot.command(name="noitucamhc", aliases=["noitucombannedhc"])
async def cmd_noitucamhc(ctx: commands.Context, seconds: int = 15) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    if seconds < 5 or seconds > 120: seconds = 15
    
    banned_letter = random.choice("abcdefghijklmnopqrstuvwxyz")
    start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
    while banned_letter in GameUtils.remove_diacritics(start_word):
        start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
        
    session.initialize_session(GameMode.PVP_VIETNAMESE, start_word=start_word)
    session.is_banned_mode = True
    session.banned_letter = banned_letter
    session.is_hardcore = True
    session.hardcore_time = seconds
    session.last_player_id = ctx.author.id
    
    desc = (f"{BotConfig.BORDER}\n\n"
            f"🔥💀 **NỐI TỪ CẤM HARDCORE** 💀🔥\n"
            f"⏱️ **Thời gian trả lời:** `{seconds} giây`\n"
            f"🚫 **Chữ cái bị cấm:** `{banned_letter.upper()}`\n\n"
            f"👉 **Từ bắt đầu:** `{start_word.upper()}`\n"
            f"🌸 **Cần nối bằng:** `{syllables[-1].upper()}`\n\n"
            f"⚠️ *Hết giờ -> Người cuối cùng thắng. Chạm chữ cấm -> Thua ngay lập tức!*\n\n{BotConfig.BORDER}")
    
    await ctx.send(embed=UIUtils.create_embed("💀 [ CẤM CHỮ + HARDCORE ] 💀", desc, BotConfig.COLOR_BLACK_CHIC))
    await session.start_hardcore_timer(ctx.channel)

@bot.command(name="botnoitucamhc", aliases=["botnoitucombannedhc"])
async def cmd_botnoitucamhc(ctx: commands.Context, seconds: int = 15) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    if seconds < 5 or seconds > 120: seconds = 15
    
    banned_letter = random.choice("abcdefghijklmnopqrstuvwxyz")
    start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
    while banned_letter in GameUtils.remove_diacritics(start_word):
        start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
        
    session.initialize_session(GameMode.BOT_VIETNAMESE, start_word=start_word)
    session.is_banned_mode = True
    session.banned_letter = banned_letter
    session.is_hardcore = True
    session.hardcore_time = seconds
    session.last_player_id = None
    
    desc = (f"{BotConfig.BORDER}\n\n"
            f"🤖🔥💀 **BOT CẤM CHỮ + HARDCORE** 💀🔥🤖\n"
            f"⏱️ **Thời gian trả lời:** `{seconds} giây`\n"
            f"🚫 **Chữ cái bị cấm:** `{banned_letter.upper()}`\n\n"
            f"👉 **Từ bắt đầu:** `{start_word.upper()}`\n"
            f"🌸 **Cần nối bằng:** `{syllables[-1].upper()}`\n\n"
            f"⚠️ *Trễ giờ -> Bot thắng. Dùng chữ cấm -> Bạn thua!*\n\n{BotConfig.BORDER}")
    
    await ctx.send(embed=UIUtils.create_embed("💀 [ BOT CẤM CHỮ + HC ] 💀", desc, BotConfig.COLOR_BLACK_CHIC))
    await session.start_hardcore_timer(ctx.channel)

@bot.command(name="noitueng", aliases=["noituen"])
async def cmd_noitueng(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    start_word = random.choice(ENGLISH_LIST)
    session.initialize_session(GameMode.PVP_ENGLISH, start_word=start_word)
    await ctx.send(embed=UIUtils.create_embed("🇬🇧 English PvP", f"{BotConfig.BORDER}\n\n👉 Word: **`{start_word.upper()}`**\n🌸 Letter: **`{start_word[-1].upper()}`**\n\n{BotConfig.BORDER}"))

@bot.command(name="botnoitueng", aliases=["noituubotteng"])
async def cmd_botnoitueng(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    start_word = random.choice(ENGLISH_LIST)
    session.initialize_session(GameMode.BOT_ENGLISH, start_word=start_word)
    await ctx.send(embed=UIUtils.create_embed("🤖 English Bot", f"{BotConfig.BORDER}\n\n👉 Word: **`{start_word.upper()}`**\n🌸 Letter: **`{start_word[-1].upper()}`**\n\n{BotConfig.BORDER}"))

@bot.command(name="vuatiengviet")
async def cmd_vuatiengviet(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    target = random.choice(VUA_TIENG_VIET_CANDIDATES); scrambled = GameUtils.scramble_vietnamese_syllables(target)
    session.initialize_session(GameMode.VUA_TIENG_VIET, target=target)
    await ctx.send(embed=UIUtils.create_embed("👑 Vua Tiếng Việt", f"{BotConfig.BORDER}\n\n🔀 **`{scrambled.upper()}`**\n\n{BotConfig.BORDER}"))

@bot.command(name="doanquocgia")
async def cmd_doanquocgia(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    target = random.choice(COUNTRIES_VN_LIST); masked = GameUtils.generate_country_mask(target)
    session.initialize_session(GameMode.GUESS_COUNTRY, target=target)
    iso_code = COUNTRY_CODES.get(target, "un"); flag_url = f"https://flagcdn.com/w320/{iso_code}.png"
    await ctx.send(embed=UIUtils.create_embed("🌍 Đoán Quốc Gia", f"{BotConfig.BORDER}\n\n🗺️ **`{masked}`**\n\n{BotConfig.BORDER}", image_url=flag_url))

@bot.command(name="doantenphim", aliases=["tenphim", "phim"])
async def cmd_doantenphim(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    
    movie = random.choice(FALLBACK_MOVIES_DATA)
    session.initialize_session(GameMode.GUESS_MOVIE, target=movie["title"])
    
    desc = (f"{BotConfig.BORDER}\n\n"
            f"🎬 **RẠP CHIẾU ĐEN HỒNG** 🍿\n\n"
            f"❓ **Gợi ý:** {movie['clue']}\n\n"
            f"💡 *Hãy gõ tên phim (không dấu) vào chat để trả lời!*\n"
            f"⏳ *Không có giới hạn thời gian, nhưng hãy nhanh lên!*\n\n"
            f"{BotConfig.BORDER}")
    
    await ctx.send(embed=UIUtils.create_embed("🎟️ [ ĐOÁN TÊN PHIM ] 🎟️", desc, BotConfig.COLOR_DEEP_PINK, movie.get("image", None)))

@bot.command(name="doanemoji", aliases=["emoji", "phanloaiemoji"])
async def cmd_doanemoji(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    
    emoji_data = random.choice(EMOJI_DATA)
    session.initialize_session(GameMode.GUESS_EMOJI, target=emoji_data["phrase"])
    
    desc = (f"{BotConfig.BORDER}\n\n"
            f"🎭 **GIẢI MÃ EMOJI** 🧩\n\n"
            f"🔑 **Chuỗi Emoji:** {emoji_data['emojis']}\n\n"
            f"💡 *Hãy gõ từ/cụm từ tiếng Việt (không dấu) tương ứng vào chat!*\n\n"
            f"{BotConfig.BORDER}")
    await ctx.send(embed=UIUtils.create_embed("🎨 [ ĐOÁN EMOJI ] 🎨", desc, BotConfig.COLOR_SAKURA_PINK))

@bot.command(name="tictactoe", aliases=["caro"])
async def cmd_tictactoe(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    await ctx.send(embed=UIUtils.create_embed("❌⭕ Cờ Caro", f"{BotConfig.BORDER}\n\nChọn ô để đánh **❌** chống Bot **⭕**!\n\n{BotConfig.BORDER}"), view=TicTacToeView())

@bot.command(name="hoibacsi", aliases=["8ball", "ask"])
async def cmd_hoibacsi(ctx: commands.Context, *, question: str) -> None:
    responses = ["Chắc chắn. 🖤", "Không nghi ngờ. 💗", "Yếu, nhưng có thể. 🥀", "Hỏi lại sau... 🌑", "Tuyệt đối không! 🚫", "Không ổn. 🥀", "Khả năng cao. 💖", "Triển vọng tốt. 🌸", "Dự báo xấu. ⛈️", "Phức tạp. 🕸️", "Đều có thể. ✨", "Tự quyết định! 🗝️"]
    desc = f"{BotConfig.BORDER}\n\n❓ **Câu hỏi:** *{question}*\n💡 **Trả lời:** {random.choice(responses)}\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🎱 Hỏi Bác Sĩ", desc, BotConfig.COLOR_DEEP_PINK))

@bot.command(name="russianroulette", aliases=["rr", "roulette"])
async def cmd_russianroulette(ctx: commands.Context) -> None:
    bullet, chamber = random.randint(1, 6), random.randint(1, 6)
    if bullet == chamber: desc = f"{BotConfig.BORDER}\n\n💥 **BÙMMM!** 💥\n{ctx.author.mention} đã hy sinh! 🪦\n\n{BotConfig.BORDER}"; color = BotConfig.COLOR_RED_DARK
    else: desc = f"{BotConfig.BORDER}\n\n💨 *Click...*\nTrống! {ctx.author.mention} sống sót! 🖤\n\n{BotConfig.BORDER}"; color = BotConfig.COLOR_SAKURA_PINK
    await ctx.send(embed=UIUtils.create_embed("🔫 Russian Roulette", desc, color))

@bot.command(name="restart", aliases=["choilai", "resetgame"])
async def cmd_restart(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if not session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Lỗi", "Không có ván chơi nào đang hoạt động để restart."))
        return
    
    mode = session.active_mode
    is_hc = session.is_hardcore
    hc_time = session.hardcore_time
    is_banned = session.is_banned_mode
    
    if mode in [GameMode.PVP_VIETNAMESE, GameMode.BOT_VIETNAMESE]:
        banned_letter = random.choice("abcdefghijklmnopqrstuvwxyz") if is_banned else ""
        start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
        
        if is_banned:
            while banned_letter in GameUtils.remove_diacritics(start_word):
                start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
                
        session.initialize_session(mode, start_word=start_word)
        session.is_banned_mode = is_banned
        session.banned_letter = banned_letter
        
        if is_hc:
            session.is_hardcore = True
            session.hardcore_time = hc_time
            session.last_player_id = ctx.author.id if mode == GameMode.PVP_VIETNAMESE else None
            
        title = "🔄 Bắt Đầu Lại"
        desc = f"{BotConfig.BORDER}\n\nVán chơi đã được làm mới!\n"
        if is_banned: desc += f"🚫 **Chữ cấm:** `{banned_letter.upper()}`\n"
        if is_hc: desc += f"⏱️ **Giây:** `{hc_time}`\n"
        desc += f"👉 **Từ:** `{start_word.upper()}`\n🌸 **Tiếp:** `{syllables[-1].upper()}`\n\n{BotConfig.BORDER}"
        
        await ctx.send(embed=UIUtils.create_embed(title, desc, BotConfig.COLOR_RED_DARK if (is_hc or is_banned) else BotConfig.COLOR_SAKURA_PINK))
        if is_hc: await session.start_hardcore_timer(ctx.channel)
        
    elif mode in [GameMode.PVP_ENGLISH, GameMode.BOT_ENGLISH]:
        start_word = random.choice(ENGLISH_LIST)
        session.initialize_session(mode, start_word=start_word)
        await ctx.send(embed=UIUtils.create_embed("🔄 Restart Game", f"{BotConfig.BORDER}\n\nGame has been restarted!\n👉 Word: **`{start_word.upper()}`**\n🌸 Letter: **`{start_word[-1].upper()}`**\n\n{BotConfig.BORDER}"))
        
    elif mode == GameMode.VUA_TIENG_VIET:
        target = random.choice(VUA_TIENG_VIET_CANDIDATES); scrambled = GameUtils.scramble_vietnamese_syllables(target)
        session.initialize_session(GameMode.VUA_TIENG_VIET, target=target)
        await ctx.send(embed=UIUtils.create_embed("🔄 Bắt Đầu Lại", f"{BotConfig.BORDER}\n\nVán chơi đã được làm mới!\n🔀 **`{scrambled.upper()}`**\n\n{BotConfig.BORDER}"))
        
    elif mode == GameMode.GUESS_COUNTRY:
        target = random.choice(COUNTRIES_VN_LIST); masked = GameUtils.generate_country_mask(target)
        session.initialize_session(GameMode.GUESS_COUNTRY, target=target)
        iso_code = COUNTRY_CODES.get(target, "un"); flag_url = f"https://flagcdn.com/w320/{iso_code}.png"
        await ctx.send(embed=UIUtils.create_embed("🔄 Bắt Đầu Lại", f"{BotConfig.BORDER}\n\nVán chơi đã được làm mới!\n🗺️ **`{masked}`**\n\n{BotConfig.BORDER}", image_url=flag_url))
        
    elif mode == GameMode.GUESS_MOVIE:
        movie = random.choice(FALLBACK_MOVIES_DATA)
        session.initialize_session(GameMode.GUESS_MOVIE, target=movie["title"])
        desc = (f"{BotConfig.BORDER}\n\n"
                f"🎬 Ván chơi đã được làm mới!\n"
                f"❓ **Gợi ý:** {movie['clue']}\n\n{BotConfig.BORDER}")
        await ctx.send(embed=UIUtils.create_embed("🔄 Bắt Đầu Lại", desc, BotConfig.COLOR_DEEP_PINK, movie.get("image", None)))
        
    elif mode == GameMode.GUESS_EMOJI:
        emoji_data = random.choice(EMOJI_DATA)
        session.initialize_session(GameMode.GUESS_EMOJI, target=emoji_data["phrase"])
        desc = (f"{BotConfig.BORDER}\n\n"
                f"🎭 Ván chơi đã được làm mới!\n"
                f"🔑 **Emoji:** {emoji_data['emojis']}\n\n{BotConfig.BORDER}")
        await ctx.send(embed=UIUtils.create_embed("🔄 Bắt Đầu Lại", desc, BotConfig.COLOR_SAKURA_PINK))

@bot.command(name="huyvanchoi", aliases=["huynoitu", "huygame", "huy"])
async def cmd_huyvanchoi(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if not session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Lỗi", "Không có ván chơi.")); return
    session.reset()
    await ctx.send(embed=UIUtils.create_embed("🖤 Đã Hủy", f"{BotConfig.BORDER}\n\nPhiên chơi kết thúc.\n\n{BotConfig.BORDER}", BotConfig.COLOR_BLACK_CHIC))

@bot.command(name="nghia")
async def cmd_nghia(ctx: commands.Context, *, word: str = "") -> None:
    if not word: await ctx.send(embed=UIUtils.build_warning_embed("Thiếu từ", "Nhập từ cần tra.")); return
    clean_w = word.strip().lower()
    found = clean_w in COMBINED_VIETNAMESE_DICTIONARY or clean_w in ENGLISH_DICT or clean_w in COUNTRIES_VN_DICT
    if found: await ctx.send(embed=UIUtils.create_embed("📖 Tra Cứu", f"{BotConfig.BORDER}\n\nTừ **`{clean_w.upper()}`** CÓ TRONG hệ thống! 🖤🌸\n\n{BotConfig.BORDER}", BotConfig.COLOR_SAKURA_PINK))
    else: await ctx.send(embed=UIUtils.create_embed("📖 Tra Cứu", f"{BotConfig.BORDER}\n\nKhông thấy **`{clean_w.upper()}`**. Dùng `/themtu` để bổ sung!\n\n{BotConfig.BORDER}", BotConfig.COLOR_RED_DARK))

# ====================================================================================================
# PHẦN 8: XỬ LÝ SỰ KIỆN TRÒ CHƠI QUA TIN NHẮN (SILENT IGNORE)
# ====================================================================================================

@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot: return
    
    # TÍNH NĂNG: Auto-reply khi bị tag, bực mình và MUTE (Time-out) 1 phút
    if bot.user.mentioned_in(message) and not message.content.startswith(BotConfig.PREFIX):
        user_id = message.author.id
        now = datetime.now()
        
        if user_id not in mention_tracker:
            mention_tracker[user_id] = {"count": 1, "last_mention": now}
        else:
            if (now - mention_tracker[user_id]["last_mention"]).total_seconds() > 300:
                mention_tracker[user_id]["count"] = 1
            else:
                mention_tracker[user_id]["count"] += 1
            mention_tracker[user_id]["last_mention"] = now
            
        count = mention_tracker[user_id]["count"]
        
        if count == 1:
            await message.channel.send("dạ e đây 🌸")
        elif count == 2:
            await message.channel.send("sao")
        elif count == 3:
            await message.channel.send("**sao**")
        elif count == 4:
            await message.channel.send("đĩ mẹ mày, sủa đi")
        else: # Tag từ 5 lần trở lên
            try:
                # Mute người dùng 1 phút
                await message.author.timeout(timedelta(minutes=1), reason="Tag bot quá nhiều lần liên tiếp!")
                await message.channel.send(f"🔇 {message.author.mention} đã bị mute 1 phút vì tag bot liên tục! 🌸")
                # Reset lượt tag để tránh bị mute liên tục
                mention_tracker[user_id] = {"count": 0, "last_mention": now}
            except discord.Forbidden:
                await message.channel.send("⚠️ Bot không có quyền Timeout/Mute bạn. Vui lòng cấp quyền 'Quản lý thành viên' cho Bot!")
            except Exception as e:
                logger.error(f"Lỗi mute user: {e}")
            
    if message.guild:
        guild_id = message.guild.id
        if guild_id not in afk_users:
            afk_users[guild_id] = {}

        if message.author.id in afk_users[guild_id] and not message.content.startswith(f"{BotConfig.PREFIX}afk"):
            del afk_users[guild_id][message.author.id]
            try:
                if message.author.display_name.startswith("[AFK] "):
                    new_nick = message.author.display_name[6:]
                    await message.author.edit(nick=new_nick if new_nick else None)
            except discord.Forbidden:
                pass
            except Exception as e:
                logger.error(f"Lỗi đổi tên khi hết AFK: {e}")
                
            desc = f"{BotConfig.BORDER}\n\n👋 Chào mừng {message.author.mention} trở lại! Bot đã tự động tắt chế độ AFK. 🌸\n\n{BotConfig.BORDER}"
            await message.channel.send(embed=UIUtils.create_embed("🌸 Hết AFK", desc, BotConfig.COLOR_SAKURA_PINK))

        for mentioned_user in message.mentions:
            if mentioned_user.id in afk_users.get(guild_id, {}):
                afk_data = afk_users[guild_id][mentioned_user.id]
                time_diff = datetime.now() - afk_data["timestamp"]
                secs = int(time_diff.total_seconds())
                
                if secs < 60: time_str = f"{secs} giây trước"
                elif secs < 3600: time_str = f"{secs // 60} phút trước"
                else: time_str = f"{secs // 3600} giờ trước"
                
                reason = afk_data.get("reason", "không có lý do")
                await message.channel.send(f"💤 **NGƯỜI DÙNG NÀY ĐÃ AFK.** (Thời gian: {time_str})\n📝 Lý do: *{reason}*")
                break

    if message.channel.id in counting_channels and not message.content.startswith(BotConfig.PREFIX):
        data = counting_channels[message.channel.id]
        content = message.content.strip()
        
        if not content.isdigit():
            try:
                await message.delete()
            except:
                pass
            return
            
        num = int(content)
        
        if message.author.id == data["last_user"]:
            data["current"] = 0
            data["last_user"] = 0
            await message.add_reaction("❌")
            await message.channel.send(f"💥 {message.author.mention} không thể đếm 2 lần liên tiếp! Đếm lại từ 1. 🌸\n*(Kỷ lục: {data['high_score']})*", delete_after=10)
            try:
                await message.delete()
            except:
                pass
            return
            
        expected_num = data["current"] + 1
        
        if num == expected_num:
            data["current"] = num
            data["last_user"] = message.author.id
            await message.add_reaction("✅")
            
            if num > data["high_score"]:
                data["high_score"] = num
                if num % 10 == 0:
                    await message.channel.send(f"🎉 Wooo! Kỷ lục mới: **{num}**! Cố lên nào! 🌸")
        else:
            data["current"] = 0
            data["last_user"] = 0
            await message.add_reaction("💥")
            await message.channel.send(f"💥 {message.author.mention} đếm sai rồi! Phải là số **{expected_num}** chứ không phải **{num}**.\nChơi lại từ 1! 🌸\n*(Kỷ lục server: {data['high_score']})*")
            try:
                await message.delete()
            except:
                pass
                
        return 

    await bot.process_commands(message)
    session = global_session_manager.get_session(message.channel.id)
    if not session.is_active: return

    content = message.content.strip().lower()
    if content.startswith(BotConfig.PREFIX): return

    # 1. Vua Tiếng Việt
    if session.active_mode == GameMode.VUA_TIENG_VIET:
        if content == session.scrambled_target.lower():
            target = session.scrambled_target; session.reset()
            await message.channel.send(embed=UIUtils.create_embed("🏆 Thắng VTV", f"{BotConfig.BORDER}\n\n🎉 {message.author.mention} giải đúng: **`{target.upper()}`**!\n\n{BotConfig.BORDER}", BotConfig.COLOR_SAKURA_PINK))
        return

    # 2. Đoán Quốc Gia
    if session.active_mode == GameMode.GUESS_COUNTRY:
        if content == session.secret_country.lower():
            target = session.secret_country; session.reset()
            await message.channel.send(embed=UIUtils.create_embed("🏆 Thắng ĐQG", f"{BotConfig.BORDER}\n\n🎉 {message.author.mention} đoán đúng: **`{target.upper()}`**!\n\n{BotConfig.BORDER}", BotConfig.COLOR_SAKURA_PINK))
        return

    # 3. Đoán Tên Phim
    if session.active_mode == GameMode.GUESS_MOVIE:
        target = session.secret_target
        target_no_diacritics = GameUtils.remove_diacritics(target).lower()
        content_no_diacritics = GameUtils.remove_diacritics(content).lower()
        
        if content == target or content == target_no_diacritics or content_no_diacritics == target or content_no_diacritics == target_no_diacritics or content_no_diacritics in target_no_diacritics or target_no_diacritics in content_no_diacritics:
            session.reset()
            await message.channel.send(embed=UIUtils.create_embed("🏆 Trả Lời Đúng!", f"{BotConfig.BORDER}\n\n🎉 {message.author.mention} đã trả lời đúng!\n🎬 Tên phim: **`{target.upper()}`**\n\n{BotConfig.BORDER}", BotConfig.COLOR_DEEP_PINK))
        return

    # 4. Đoán Emoji
    if session.active_mode == GameMode.GUESS_EMOJI:
        target = session.secret_target
        target_no_diacritics = GameUtils.remove_diacritics(target).lower()
        content_no_diacritics = GameUtils.remove_diacritics(content).lower()
        
        if content == target or content == target_no_diacritics or content_no_diacritics == target or content_no_diacritics == target_no_diacritics or content_no_diacritics in target_no_diacritics or target_no_diacritics in content_no_diacritics:
            session.reset()
            await message.channel.send(embed=UIUtils.create_embed("🏆 Thắng Emoji", f"{BotConfig.BORDER}\n\n🎉 {message.author.mention} đoán đúng: **`{target.upper()}`**!\n\n{BotConfig.BORDER}", BotConfig.COLOR_SAKURA_PINK))
        return

    # 5. Nối Từ Tiếng Việt (Bao gồm Hardcore và Cấm Chữ)
    if session.active_mode in [GameMode.PVP_VIETNAMESE, GameMode.BOT_VIETNAMESE]:
        parts = content.split()
        if len(parts) != 2: return 
        
        if session.is_banned_mode:
            word_base = GameUtils.remove_diacritics(content)
            if session.banned_letter in word_base:
                desc = f"{BotConfig.BORDER}\n\n💥 **BÙM!** 💥\n{message.author.mention} đã dùng từ chứa chữ cấm **`{session.banned_letter.upper()}`**!\n💀 Bạn đã thua cuộc!\n\n{BotConfig.BORDER}"
                await message.channel.send(embed=UIUtils.create_embed("🚫 [ CHẠM CẤM! ] 🚫", desc, BotConfig.COLOR_BLACK_CHIC))
                session.reset()
                return
            
        if content not in COMBINED_VIETNAMESE_DICTIONARY:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed("Từ không có trong từ điển (thiếu dấu/sai chính tả)!"))
            return
        if content in session.used_words_history:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(BotConfig.MSG_ERR_ALREADY_USED))
            return
        current_syllables = session.current_word.split()
        required_syl = current_syllables[-1] if current_syllables else ""
        if parts[0] != required_syl:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(f"Từ phải bắt đầu bằng âm **`{required_syl.upper()}`**!"))
            return
        
        session.used_words_history.add(content); session.current_word = content; session.turn_counter += 1
        session.last_player_id = message.author.id
        next_syl = parts[-1]
        
        if session.active_mode == GameMode.PVP_VIETNAMESE:
            if session.is_hardcore:
                desc = (f"{BotConfig.BORDER}\n\n"
                        f"⚡ **Nối thành công!**\n"
                        f"👉 <@{message.author.id}>: **`{content.upper()}`**\n"
                        f"🌸 Tiếp: **`{next_syl.upper()}`**\n"
                        f"⏱️ Đồng hồ đếm ngược đã reset!\n\n{BotConfig.BORDER}")
                await message.channel.send(embed=UIUtils.create_embed("⏳ Đang Đếm Ngược...", desc, BotConfig.COLOR_DEEP_PINK))
                await session.start_hardcore_timer(message.channel)
            else:
                await message.channel.send(embed=UIUtils.create_embed("✨ Thành Công!", f"{BotConfig.BORDER}\n\n👉 Bạn: **`{content.upper()}`**\n🌸 Tiếp: **`{next_syl.upper()}`**\n\n{BotConfig.BORDER}", BotConfig.COLOR_SAKURA_PINK))
        elif session.active_mode == GameMode.BOT_VIETNAMESE:
            candidates = VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.get(next_syl, [])
            valid_candidates = [w for w in candidates if w not in session.used_words_history]
            
            if session.is_banned_mode:
                valid_candidates = [w for w in valid_candidates if session.banned_letter not in GameUtils.remove_diacritics(w)]
            
            if not valid_candidates:
                session.reset()
                await message.channel.send(embed=UIUtils.create_embed("🏆 Thắng Bot", f"{BotConfig.BORDER}\n\n🎉 {message.author.mention} đánh bại Bot!\nBot không tìm được từ hợp lệ (hoặc do bị cấm chữ)!\n\n{BotConfig.BORDER}", BotConfig.COLOR_SAKURA_PINK))
                return
            
            ending_syllables_map = {}
            for w in valid_candidates:
                last_syl = w.split()[-1]
                ending_syllables_map.setdefault(last_syl, []).append(w)
                
            random_end_syl = random.choice(list(ending_syllables_map.keys()))
            bot_word = random.choice(ending_syllables_map[random_end_syl])
            
            session.used_words_history.add(bot_word); session.current_word = bot_word
            bot_syllables = bot_word.split(); next_bot_syl = bot_syllables[-1] if bot_syllables else bot_word
            session.last_player_id = None
            
            if session.is_hardcore:
                desc = (f"{BotConfig.BORDER}\n\n"
                        f"👉 Bạn: **`{content.upper()}`**\n"
                        f"🤖 Bot: **`{bot_word.upper()}`**\n"
                        f"🌸 Tiếp: **`{next_bot_syl.upper()}`**\n"
                        f"⏱️ Đồng hồ đếm ngược đã reset!\n\n{BotConfig.BORDER}")
                await message.channel.send(embed=UIUtils.create_embed("⏳ Đang Đếm Ngược...", desc, BotConfig.COLOR_DEEP_PINK))
                await session.start_hardcore_timer(message.channel)
            else:
                await message.channel.send(embed=UIUtils.create_embed("✨🌸 Lượt Đấu", f"{BotConfig.BORDER}\n\n👉 Bạn: **`{content.upper()}`**\n🤖 Bot: **`{bot_word.upper()}`**\n🌸 Tiếp: **`{next_bot_syl.upper()}`**\n\n{BotConfig.BORDER}", BotConfig.COLOR_SAKURA_PINK))
        return

    # 6. Nối Từ Tiếng Anh
    if session.active_mode in [GameMode.PVP_ENGLISH, GameMode.BOT_ENGLISH]:
        if not content.isalpha(): return
            
        if content not in ENGLISH_DICT:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed("Từ không có trong từ điển TA!"))
            return
        if content in session.used_words_history:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(BotConfig.MSG_ERR_ALREADY_USED))
            return
        required_letter = session.current_word[-1]
        if content[0] != required_letter:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(f"Must start with **`{required_letter.upper()}`**!"))
            return
        
        session.used_words_history.add(content); session.current_word = content; session.turn_counter += 1
        next_letter = content[-1]
        
        if session.active_mode == GameMode.PVP_ENGLISH:
            await message.channel.send(embed=UIUtils.create_embed("✨ Success!", f"{BotConfig.BORDER}\n\n👉 You: **`{content.upper()}`**\n🌸 Letter: **`{next_letter.upper()}`**\n\n{BotConfig.BORDER}", BotConfig.COLOR_SAKURA_PINK))
        elif session.active_mode == GameMode.BOT_ENGLISH:
            candidates = ENGLISH_INDEX_BY_FIRST_LETTER.get(next_letter, [])
            valid_candidates = [w for w in candidates if w not in session.used_words_history]
            if not valid_candidates:
                session.reset()
                await message.channel.send(embed=UIUtils.create_embed("🏆 Thắng Bot", f"{BotConfig.BORDER}\n\n🎉 {message.author.mention} defeated Bot!\n\n{BotConfig.BORDER}", BotConfig.COLOR_SAKURA_PINK))
                return
            
            ending_letters_map = {}
            for w in valid_candidates:
                ending_letters_map.setdefault(w[-1], []).append(w)
            
            random_end_letter = random.choice(list(ending_letters_map.keys()))
            bot_word = random.choice(ending_letters_map[random_end_letter])
            
            session.used_words_history.add(bot_word); session.current_word = bot_word
            next_bot_letter = bot_word[-1]
            await message.channel.send(embed=UIUtils.create_embed("✨🌸 Round", f"{BotConfig.BORDER}\n\n👉 You: **`{content.upper()}`**\n🤖 Bot: **`{bot_word.upper()}`**\n🌸 Letter: **`{next_bot_letter.upper()}`**\n\n{BotConfig.BORDER}", BotConfig.COLOR_SAKURA_PINK))
        return

# ====================================================================================================
# PHẦN 9: KHỞI CHẠY HỆ THỐNG
# ====================================================================================================

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token: logger.warning("🖤 Không tìm thấy DISCORD_TOKEN.")
    else: bot.run(token)
