# ====================================================================================================
# ██████╗ ██╗    █████╗  ██████╗██╗  ██╗    ██████╗ ██╗███╗    ██╗██╗  ██╗    ██████╗  ██████╗ ████████╗
# ██╔══██╗██║    ██╔══██╗██╔════╝██║ ██╔╝    ██╔══██╗██║████╗   ██║██║ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
# ██████╔╝██║    ███████║██║     █████╔╝     ██████╔╝██║██╔██╗  ██║█████╔╝     ██████╔╝██║   ██║   ██║   
# ██╔══██╗██║    ██╔══██║██║     ██╔═██╗     ██╔═══╝ ██║██║╚██╗ ██║██╔═██╗     ██╔══██╗██║   ██║   ██║   
# ██████╔╗███████╗██║  ██║╚██████╗██║  ██╗    ██║     ██║██║ ╚████║██║  ██╗    ██████╔╝╚██████╔╝   ██║   
# ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝    ╚═════╝  ╚═╝    ╚═╝   
#                                                                                                   
# PURE FUN ENTERPRISE - BLACK & SAKURA PINK GOTHIC ARCADE ULTIMATE (v7.9.3 - Restart Fix)
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
from urllib.parse import quote
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
    VERSION: str = "7.9.3 Sakura Gothic Restart Fix"
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

    EMOJI_TICK: str = "<:ChatGPT_Image_Aug_17__2026__05_0:1538854979832516698>"
    EMOJI_X: str = "<:0646ba929fef4ab299a9b8f82ed20378:1538880451718938684>"

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
    {"title": "harry potter", "clue": "⚡ Phù thủy, trường Hogwarts 🦉", "image": "https://image.tmdb.org/t/p/w500/3yEUqjTrfyOaIctqLqA7Wc6c9w.jpg"}
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
    return "<h1>Sakura Black Pink Arcade (v7.9.3)</h1><p style='color:#FFB7C5'>Status: <strong>ONLINE & AESTHETIC</strong></p>"

def launch_web_server() -> None:
    try:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        keep_alive_app.run(host=BotConfig.WEB_SERVER_HOST, port=BotConfig.WEB_SERVER_PORT, debug=False, use_reloader=False, threaded=True)
    except Exception as server_err:
        logger.error(f"Lỗi Flask Server: {server_err}")

threading.Thread(target=launch_web_server, daemon=True).start()

# ====================================================================================================
# PHẦN 3.5: QUẢN LÝ DỮ LIỆU NGƯỜI DÙNG (HINT & DAILY SYSTEM)
# ====================================================================================================

FILE_USER_DATA = "user_data_sakura.json"

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
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Lỗi ghi file user data: {e}")

    @staticmethod
    def get_user(user_id: int) -> dict:
        data = UserDataManager.load_data()
        uid_str = str(user_id)
        if uid_str not in data:
            data[uid_str] = {"hints": 5, "last_daily": ""}
            UserDataManager.save_data(data)
        return data[uid_str]

    @staticmethod
    def update_user(user_id: int, hints: int = None, last_daily: str = None) -> None:
        data = UserDataManager.load_data()
        uid_str = str(user_id)
        if uid_str not in data:
            data[uid_str] = {"hints": 5, "last_daily": ""}
        
        if hints is not None:
            data[uid_str]["hints"] = hints
        if last_daily is not None:
            data[uid_str]["last_daily"] = last_daily
            
        UserDataManager.save_data(data)

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
                    if self.active_mode in [GameMode.PVP_VIETNAMESE, GameMode.PVP_ENGLISH]:
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
afk_users: Dict[int, Dict[int, Dict[str, Union[datetime, str]]]] = {}

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
            f"❯ `{BotConfig.PREFIX}doanemoji` ❯ **Đoán Emoji**\n"
            f"❯ `{BotConfig.PREFIX}tictactoe` ❯ **Cờ Caro**\n"
            f"❯ `{BotConfig.PREFIX}rps` ❯ **Oẳn tù tì**\n"
            f"❯ `{BotConfig.PREFIX}ship [@user1] [@user2]` ❯ **Tính độ hợp mạng (Có ảnh)**\n\n"

            f"⚙️🌸 **[ QUẢN LÝ & TIỆN ÍCH ]** 🌸⚙️\n"
            f"❯ `/themtu [từ]` ❯ **Thêm từ (Admin)**\n"
            f"❯ `/say [nội dung]` ❯ **Bot nói thay bạn (Chỉ bạn thấy)**\n"
            f"❯ `/dm [@user] [nội dung]` ❯ **Gửi DM ẩn danh (Chỉ bạn thấy)**\n"
            f"❯ `{BotConfig.PREFIX}admin` ❯ **Panel (Admin)**\n"
            f"❯ `{BotConfig.PREFIX}afk [lý do]` ❯ **Bật chế độ AFK**\n"
            f"❯ `{BotConfig.PREFIX}countsetup` ❯ **Bật kênh đếm số (Admin)**\n"
            f"❯ `{BotConfig.PREFIX}daily` ❯ **Nhận 3 lượt Gợi Ý mỗi ngày**\n"
            f"❯ `{BotConfig.PREFIX}hint` ❯ **Dùng 1 lượt Gợi Ý khi đang bí**\n"
            f"❯ `{BotConfig.PREFIX}restart` ❯ **Chơi lại ván mới ngay lập tức**\n"
            f"❯ `{BotConfig.PREFIX}huyvanchoi` ❯ **Hủy ván chơi**\n"
            f"❯ `{BotConfig.PREFIX}nghia [từ]` ❯ **Tra cứu từ điển**\n"
            f"❯ `{BotConfig.PREFIX}tiepterauma [@user]` ❯ **Tiếp tế rau má**\n"
            f"❯ `{BotConfig.PREFIX}meme` ❯ **Lấy ảnh meme ngẫu nhiên**\n"
            f"❯ `{BotConfig.PREFIX}avt [@user]` ❯ **Xem ảnh đại diện**\n"
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

class RpsView(View):
    def __init__(self):
        super().__init__(timeout=60.0)
        self.choices = ["✂️", "🪨", "📄"]

    def check_result(self, user_choice: str, bot_choice: str) -> str:
        if user_choice == bot_choice: return "Hòa! 🤝"
        if (user_choice == "✂️" and bot_choice == "📄") or \
           (user_choice == "🪨" and bot_choice == "✂️") or \
           (user_choice == "📄" and bot_choice == "🪨"):
            return "Bạn thắng! 🎉"
        return "Bot thắng! 🤖"

    @discord.ui.button(label="Kéo", emoji="✂️", style=discord.ButtonStyle.success)
    async def button_kéo(self, interaction: discord.Interaction, button: Button):
        bot_choice = random.choice(self.choices)
        result = self.check_result("✂️", bot_choice)
        self.clear_items()
        await interaction.response.edit_message(content=f"✂️ Bạn chọn: Kéo | 🤖 Bot chọn: {bot_choice}\n**Kết quả: {result}**", view=self)

    @discord.ui.button(label="Búa", emoji="🪨", style=discord.ButtonStyle.primary)
    async def button_búa(self, interaction: discord.Interaction, button: Button):
        bot_choice = random.choice(self.choices)
        result = self.check_result("🪨", bot_choice)
        self.clear_items()
        await interaction.response.edit_message(content=f"🪨 Bạn chọn: Búa | 🤖 Bot chọn: {bot_choice}\n**Kết quả: {result}**", view=self)

    @discord.ui.button(label="Bao", emoji="📄", style=discord.ButtonStyle.danger)
    async def button_bao(self, interaction: discord.Interaction, button: Button):
        bot_choice = random.choice(self.choices)
        result = self.check_result("📄", bot_choice)
        self.clear_items()
        await interaction.response.edit_message(content=f"📄 Bạn chọn: Bao | 🤖 Bot chọn: {bot_choice}\n**Kết quả: {result}**", view=self)

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
    logger.info(f"✅ Bot Đen Hồng Cánh Hoa đã đăng nhập: {bot.user}")
    try:
        synced = await bot.tree.sync()
        logger.info(f"✅ Đã đồng bộ {len(synced)} lệnh Slash.")
    except Exception as e: 
        logger.error(f"Lỗi đồng bộ Slash: {e}")
        
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

@bot.command(name="admin", aliases=["owner"])
@commands.is_owner()
async def cmd_admin(ctx: commands.Context) -> None:
    if ctx.author.id != BotConfig.OWNER_ID: return
    desc = f"{BotConfig.BORDER}\n\n🖤 **Chào mừng Quản trị viên tối cao!** 🌸\n• 🎮 Sessions: {len(global_session_manager._sessions)}\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🔒🌸 [ ADMIN PANEL ] 🌸🔒", desc, BotConfig.COLOR_BLACK_CHIC))

@bot.command(name="daily", aliases=["nhanthuong", "diemdanh"])
async def cmd_daily(ctx: commands.Context) -> None:
    user_data = UserDataManager.get_user(ctx.author.id)
    today = datetime.now().strftime("%Y-%m-%d")
    
    if user_data["last_daily"] == today:
        desc = f"{BotConfig.BORDER}\n\n⏳ Bạn đã nhận thưởng ngày hôm nay rồi!\nHãy quay lại vào ngày mai nhé 🌸\n\n💡 Số gợi ý hiện có: **{user_data['hints']}**\n\n{BotConfig.BORDER}"
        await ctx.send(embed=UIUtils.create_embed("🌸 Nhận Thưởng Hàng Ngày", desc, BotConfig.COLOR_DEEP_PINK))
        return
    
    new_hints = user_data["hints"] + 3
    UserDataManager.update_user(ctx.author.id, hints=new_hints, last_daily=today)
    
    desc = f"{BotConfig.BORDER}\n\n💖 {ctx.author.mention} đã nhận phần thưởng hàng ngày!\n➕ **+3 Gợi Ý** 🌸\n💡 Tổng gợi ý hiện có: **{new_hints}**\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("✨ Nhận Thưởng Thành Công", desc, BotConfig.COLOR_SAKURA_PINK))

@bot.command(name="hint", aliases=["goiy"])
async def cmd_hint(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    
    if not session.is_active or session.active_mode not in [GameMode.PVP_VIETNAMESE, GameMode.BOT_VIETNAMESE, GameMode.PVP_ENGLISH, GameMode.BOT_ENGLISH]:
        await ctx.send(embed=UIUtils.build_warning_embed("Không Có Ván Chơi", "Lệnh này chỉ dùng khi đang chơi Nối Từ!"))
        return
        
    user_data = UserDataManager.get_user(ctx.author.id)
    if user_data["hints"] <= 0:
        await ctx.send(embed=UIUtils.build_warning_embed("Hết Gợi Ý", "Bạn không còn lượt gợi ý nào!\nDùng `?daily` để nhận thêm nhé."))
        return
        
    new_hints = user_data["hints"] - 1
    UserDataManager.update_user(ctx.author.id, hints=new_hints)
    
    current_word = session.current_word
    hint_text = ""
    
    if session.active_mode in [GameMode.PVP_VIETNAMESE, GameMode.BOT_VIETNAMESE]:
        last_syllable = current_word.split()[-1]
        possible_words = VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.get(last_syllable, [])
        valid_hints = [w for w in possible_words if w not in session.used_words_history]
        
        if valid_hints:
            chosen_word = random.choice(valid_hints)
            hint_text = f"🔍 Từ tiếp theo bắt đầu bằng: **`{last_syllable.upper()}`**\n💡 Gợi ý âm tiếp theo: **`{chosen_word.split()[-1][0].upper()}...`**"
        else:
            hint_text = f"🔍 Từ tiếp theo bắt đầu bằng: **`{last_syllable.upper()}`**\n⚠️ Bot không tìm thấy từ gợi ý phù hợp, bạn đang ở ngõ cụt!"
            
    elif session.active_mode in [GameMode.PVP_ENGLISH, GameMode.BOT_ENGLISH]:
        last_letter = current_word[-1]
        possible_words = ENGLISH_INDEX_BY_FIRST_LETTER.get(last_letter, [])
        valid_hints = [w for w in possible_words if w not in session.used_words_history]
        
        if valid_hints:
            chosen_word = random.choice(valid_hints)
            hint_text = f"🔍 Word starts with: **`{last_letter.upper()}`**\n💡 Hint: **`{chosen_word[:2].upper()}...`** (Length: {len(chosen_word)} letters)"
        else:
            hint_text = f"🔍 Word starts with: **`{last_letter.upper()}`**\n⚠️ No valid hints found, you are stuck!"
    
    desc = f"{BotConfig.BORDER}\n\n🎯 {ctx.author.mention} đã sử dụng 1 Gợi Ý!\n\n{hint_text}\n\n💡 Số gợi ý còn lại: **{new_hints}**\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("💡 [ GỢI Ý NỐI TỪ ] 💡", desc, BotConfig.COLOR_GOLD))

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

@bot.tree.command(name="say", description="Bot nói thay bạn (Chỉ bạn thấy thông báo)")
@app_commands.describe(text="Nội dung bạn muốn bot nói")
async def slash_say(interaction: discord.Interaction, text: str):
    await interaction.channel.send(text)
    await interaction.response.send_message("✅ Đã nói xong! 🌸", ephemeral=True)

@bot.tree.command(name="dm", description="Gửi tin nhắn ẩn danh cho người khác (Chỉ bạn thấy)")
@app_commands.describe(member="Người bạn muốn gửi", message="Nội dung tin nhắn")
async def slash_dm(interaction: discord.Interaction, member: discord.Member, message: str):
    if member.bot:
        await interaction.response.send_message("🤖 Bot không cần nhận tin nhắn đâu! 🌸", ephemeral=True)
        return
    try:
        await member.send(f"💌 **Bạn có 1 tin nhắn ẩn danh:**\n\n{message}\n\n*— Từ Vườn hoa Đen Hồng*")
        await interaction.response.send_message(f"✅ Đã gửi tin nhắn ẩn danh cho {member.mention}! 🌸", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"❌ Không thể gửi tin nhắn cho {member.mention}. Họ có thể đã tắt DM (Direct Messages) hoặc chặn bot. 🌸", ephemeral=True)
    except Exception as e:
        logger.error(f"Lỗi gửi DM: {e}")
        await interaction.response.send_message(f"❌ Lỗi không xác định khi gửi DM. 🌸", ephemeral=True)

@bot.command(name="afk", aliases=["away"])
async def cmd_afk(ctx: commands.Context, *, reason: str = "Không có lý do"):
    guild_id = ctx.guild.id
    user_id = ctx.author.id
    if guild_id not in afk_users: afk_users[guild_id] = {}
    afk_users[guild_id][user_id] = {"timestamp": datetime.now(), "reason": reason}
    try:
        if not ctx.author.display_name.startswith("[AFK] "):
            await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
    except: pass
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
    try: await ctx.message.delete()
    except: pass

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

@bot.command(name="avt", aliases=["avatar", "infoavt"])
async def cmd_avatar(ctx: commands.Context, member: Optional[discord.Member] = None) -> None:
    target = member or ctx.author
    avatar_url = target.display_avatar.with_size(1024).url
    desc = f"🖼️ **Ảnh đại diện của {target.mention}**\n[🔗 Tải ảnh chất lượng cao tại đây]({avatar_url})"
    embed = UIUtils.create_embed(f"Ảnh của {target.display_name}", desc, BotConfig.COLOR_DEEP_PINK)
    embed.set_image(url=avatar_url)
    await ctx.send(embed=embed)

@bot.command(name="rps", aliases=["oantuti", "keobuabao"])
async def cmd_rps(ctx: commands.Context) -> None:
    desc = f"{BotConfig.BORDER}\n\n✊ **Oẳn tù tì cùng Bot!**\nHãy chọn 1 trong 3 nút bên dưới để bắt đầu.\n\n{BotConfig.BORDER}"
    embed = UIUtils.create_embed("✊ Oẳn Tù Tì", desc, BotConfig.COLOR_DEEP_PINK)
    await ctx.send(embed=embed, view=RpsView())

@bot.command(name="ship", aliases=["hop"])
async def cmd_ship(ctx: commands.Context, member1: discord.Member, member2: Optional[discord.Member] = None) -> None:
    target2 = member2 or ctx.author
    if member1 == target2:
        await ctx.send("Bạn không thể ship với chính mình được! 🌸")
        return
    ship_val = random.randint(0, 100)
    bar_length = 10
    filled = int(ship_val / 100 * bar_length)
    if filled == 0 and ship_val > 0: filled = 1
    bar = "❤" * filled + "🖤" * (bar_length - filled)
    if ship_val < 20: msg = "💔 *Có vẻ không hợp lắm... Tránh xa ra thôi!*"
    elif ship_val < 50: msg = "🌹 *Thấy có tình chút chút! Thử tìm hiểu thêm xem sao!*"
    elif ship_val < 80: msg = "💞 *Rất hợp nha! Cố lên!*"
    else: msg = "💍 *Mệnh trời định! Mau cưới đi chớ chời!*"
    desc = f"💖 **Độ hợp mạng giữa {member1.mention} và {target2.mention}**\n\n{bar} **{ship_val}%**\n{msg}"
    avatar1 = quote(str(member1.display_avatar.with_format("png").with_size(256).url), safe='')
    avatar2 = quote(str(target2.display_avatar.with_format("png").with_size(256).url), safe='')
    ship_image_url = f"https://api.popcat.xyz/ship?user1={avatar1}&user2={avatar2}"
    embed = UIUtils.create_embed("💕 Độ Hợp Mạng", desc, BotConfig.COLOR_DEEP_PINK, image_url=ship_image_url)
    await ctx.send(embed=embed)

# ====================================================================================================
# PHẦN 7: CÁC LỆNH TRÒ CHƠI NỐI TỪ
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
    session.is_hardcore = True; session.hardcore_time = seconds; session.last_player_id = ctx.author.id
    desc = (f"{BotConfig.BORDER}\n\n💀 **CẢNH BÁO: CHẾ ĐỘ HARDCORE** 💀\n⏱️ **Thời gian trả lời:** `{seconds} giây`\n\n👉 Từ bắt đầu: **`{start_word.upper()}`**\n🌸 Cần nối bằng: **`{syllables[-1].upper()}`**\n\n⚠️ *Hết giờ mà không ai nối được -> Người cuối cùng nối thành công sẽ THẮNG!*\n\n{BotConfig.BORDER}")
    await ctx.send(embed=UIUtils.create_embed("🔥 [ NỐI TỪ HARDCORE ] 🔥", desc, BotConfig.COLOR_RED_DARK))
    await session.start_hardcore_timer(ctx.channel)

@bot.command(name="botnoituhc", aliases=["noituubothc"])
async def cmd_botnoituhc(ctx: commands.Context, seconds: int = 15) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    if seconds < 5 or seconds > 120: seconds = 15
    start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
    session.initialize_session(GameMode.BOT_VIETNAMESE, start_word=start_word)
    session.is_hardcore = True; session.hardcore_time = seconds; session.last_player_id = None
    desc = (f"{BotConfig.BORDER}\n\n🤖💀 **SOLO BOT HARDCORE** 💀🤖\n⏱️ **Thời gian trả lời:** `{seconds} giây`\n\n👉 Từ bắt đầu: **`{start_word.upper()}`**\n🌸 Cần nối bằng: **`{syllables[-1].upper()}`**\n\n⚠️ *Nếu bạn không nối kịp giờ, Bot sẽ thắng!*\n\n{BotConfig.BORDER}")
    await ctx.send(embed=UIUtils.create_embed("🔥 [ SOLO BOT HARDCORE ] 🔥", desc, BotConfig.COLOR_RED_DARK))
    await session.start_hardcore_timer(ctx.channel)

@bot.command(name="noitueng", aliases=["noituen"])
async def cmd_noitueng(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active: await ctx.send(embed=UIUtils.build_warning_embed("Bận", "Đang có ván.")); return
    start_word = random.choice(ENGLISH_LIST)
    session.initialize_session(GameMode.PVP_ENGLISH, start_word=start_word)
    await ctx.send(embed=UIUtils.create_embed("💕 Nối Từ PvP (English)", f"{BotConfig.BORDER}\n\n👉 Word: **`{start_word.upper()}`**\n🌸 Next: **`{start_word[-1].upper()}`**\n\n{BotConfig.BORDER}"))

@bot.command(name="huyvanchoi", aliases=["end", "stop"])
async def cmd_huyvanchoi(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if not session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Không Có Ván Chơi", "Hiện không có ván chơi nào đang diễn ra."))
        return
    session.reset()
    desc = f"{BotConfig.BORDER}\n\n🛑 Ván chơi hiện tại đã bị hủy bởi {ctx.author.mention}!\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🌸 Hủy Ván Chơi", desc, BotConfig.COLOR_BLACK_CHIC))

# LỆNH RESTART MỚI ĐƯỢC THÊM Ở ĐÂY
@bot.command(name="restart", aliases=["choilai", "reset"])
async def cmd_restart(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if not session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Không Có Ván Chơi", "Hiện không có ván chơi nào để restart."))
        return
    
    mode = session.active_mode
    session.reset()
    
    if mode in [GameMode.PVP_VIETNAMESE, GameMode.BOT_VIETNAMESE]:
        start_word = random.choice(EASY_START_LIST); syllables = start_word.split()
        new_mode = GameMode.PVP_VIETNAMESE if mode == GameMode.PVP_VIETNAMESE else GameMode.BOT_VIETNAMESE
        session.initialize_session(new_mode, start_word=start_word)
        desc = f"{BotConfig.BORDER}\n\n🔄 **Ván chơi đã được khởi động lại!**\n\n👉 Từ mới: **`{start_word.upper()}`**\n🌸 Tiếp: **`{syllables[-1].upper()}`**\n\n{BotConfig.BORDER}"
        await ctx.send(embed=UIUtils.create_embed("🌸 Restart Thành Công", desc, BotConfig.COLOR_SAKURA_PINK))
        
    elif mode in [GameMode.PVP_ENGLISH, GameMode.BOT_ENGLISH]:
        start_word = random.choice(ENGLISH_LIST)
        new_mode = GameMode.PVP_ENGLISH if mode == GameMode.PVP_ENGLISH else GameMode.BOT_ENGLISH
        session.initialize_session(new_mode, start_word=start_word)
        desc = f"{BotConfig.BORDER}\n\n🔄 **Game restarted!**\n\n👉 Word: **`{start_word.upper()}`**\n🌸 Next: **`{start_word[-1].upper()}`**\n\n{BotConfig.BORDER}"
        await ctx.send(embed=UIUtils.create_embed("🌸 Restart Success", desc, BotConfig.COLOR_SAKURA_PINK))
    else:
        await ctx.send(embed=UIUtils.build_warning_embed("Không Hỗ Trợ", "Không thể restart trò chơi này. Dùng lệnh bắt đầu lại."))

# ====================================================================================================
# PHẦN 8: XỬ LÝ TIN NHẮN (MESSAGE LISTENER) - Nơi cốt lõi để chơi nối từ
# ====================================================================================================

async def handle_word_chain(message: discord.Message) -> None:
    session = global_session_manager.get_session(message.channel.id)
    if not session.is_active: return
    
    content = message.content.strip().lower()
    if content.startswith(BotConfig.PREFIX): return
    
    is_english = session.active_mode in [GameMode.PVP_ENGLISH, GameMode.BOT_ENGLISH]
    
    # Xử lý nối từ Tiếng Anh
    if is_english:
        if not content.isalpha() or len(content.split()) > 1:
            return 
            
        last_char = session.current_word[-1]
        first_char = content[0]
        
        if first_char != last_char:
            await message.reply(embed=UIUtils.build_invalid_word_embed(f"Từ phải bắt đầu bằng chữ **`{last_char.upper()}`**!"), mention_author=False)
            await message.add_reaction(BotConfig.EMOJI_X) # Thả ảnh X
            return
            
        if content in session.used_words_history:
            await message.reply(embed=UIUtils.build_invalid_word_embed(BotConfig.MSG_ERR_ALREADY_USED), mention_author=False)
            await message.add_reaction(BotConfig.EMOJI_X) # Thả ảnh X
            return
            
        if content not in ENGLISH_DICT:
            await message.reply(embed=UIUtils.build_invalid_word_embed("Từ không có trong từ điển Tiếng Anh của bot!"), mention_author=False)
            await message.add_reaction(BotConfig.EMOJI_X) # Thả ảnh X
            return
            
        session.current_word = content
        session.used_words_history.add(content)
        await message.add_reaction(BotConfig.EMOJI_TICK) # Thả ảnh Tick
        
        if session.active_mode == GameMode.BOT_ENGLISH:
            bot_last_char = content[-1]
            possible_words = ENGLISH_INDEX_BY_FIRST_LETTER.get(bot_last_char, [])
            valid_bot_words = [w for w in possible_words if w not in session.used_words_history]
            
            if valid_bot_words:
                bot_word = random.choice(valid_bot_words)
                session.current_word = bot_word
                session.used_words_history.add(bot_word)
                await message.channel.send(embed=UIUtils.create_embed("🤖 Bot Nối Tiếng Anh", f"{BotConfig.BORDER}\n\n👉 Bot nói: **`{bot_word.upper()}`**\n🌸 Next: **`{bot_word[-1].upper()}`**\n\n{BotConfig.BORDER}"))
            else:
                desc = f"{BotConfig.BORDER}\n\n🏳️ Bot chịu thua! Không còn từ nào bắt đầu bằng **`{bot_last_char.upper()}`** nữa!\n🏆 {message.author.mention} đã chiến thắng Bot!\n\n{BotConfig.BORDER}"
                await message.channel.send(embed=UIUtils.create_embed("🎉 Chiến Thắng!", desc, BotConfig.COLOR_GOLD))
                session.reset()
            return
            
    # Xử lý nối từ Tiếng Việt
    else:
        parts = content.split()
        if len(parts) != 2:
            return 
            
        last_syllable = session.current_word.split()[-1]
        first_syllable = parts[0]
        
        if GameUtils.remove_diacritics(first_syllable) != GameUtils.remove_diacritics(last_syllable):
            await message.reply(embed=UIUtils.build_invalid_word_embed(f"Từ phải bắt đầu bằng tiếng **`{last_syllable.upper()}`**!"), mention_author=False)
            await message.add_reaction(BotConfig.EMOJI_X) # Thả ảnh X
            return
            
        if content in session.used_words_history:
            await message.reply(embed=UIUtils.build_invalid_word_embed(BotConfig.MSG_ERR_ALREADY_USED), mention_author=False)
            await message.add_reaction(BotConfig.EMOJI_X) # Thả ảnh X
            return
            
        if content not in COMBINED_VIETNAMESE_DICTIONARY:
            await message.reply(embed=UIUtils.build_invalid_word_embed("Từ không có trong từ điển Tiếng Việt của bot!"), mention_author=False)
            await message.add_reaction(BotConfig.EMOJI_X) # Thả ảnh X
            return
            
        if session.is_banned_mode:
            raw_content = GameUtils.remove_diacritics(content)
            if session.banned_letter in raw_content:
                await message.reply(embed=UIUtils.build_invalid_word_embed(f"💀 Bạn đã dùng chữ **`{session.banned_letter.upper()}`** bị cấm! Bạn THUA!"), mention_author=False)
                await message.add_reaction(BotConfig.EMOJI_X) # Thả ảnh X
                session.reset()
                return
                
        session.current_word = content
        session.used_words_history.add(content)
        session.last_player_id = message.author.id
        await message.add_reaction(BotConfig.EMOJI_TICK) # Thả ảnh Tick
        
        if session.is_hardcore:
            await session.start_hardcore_timer(message.channel)
            
        if session.active_mode == GameMode.BOT_VIETNAMESE:
            bot_last_syl = content.split()[-1]
            possible_words = VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.get(bot_last_syl, [])
            valid_bot_words = [w for w in possible_words if w not in session.used_words_history]
            
            if session.is_banned_mode:
                valid_bot_words = [w for w in valid_bot_words if session.banned_letter not in GameUtils.remove_diacritics(w)]
                
            if valid_bot_words:
                bot_word = random.choice(valid_bot_words)
                session.current_word = bot_word
                session.used_words_history.add(bot_word)
                await message.channel.send(embed=UIUtils.create_embed("🤖 Bot Nối Từ", f"{BotConfig.BORDER}\n\n👉 Bot nói: **`{bot_word.upper()}`**\n🌸 Tiếp: **`{bot_word.split()[-1].upper()}`**\n\n{BotConfig.BORDER}"))
            else:
                desc = f"{BotConfig.BORDER}\n\n🏳️ Bot chịu thua! Không còn từ nào nối tiếp!\n🏆 {message.author.mention} đã chiến thắng Bot!\n\n{BotConfig.BORDER}"
                await message.channel.send(embed=UIUtils.create_embed("🎉 Chiến Thắng!", desc, BotConfig.COLOR_GOLD))
                session.reset()

@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot or not message.guild: return

    if message.guild.id in afk_users:
        if message.author.id in afk_users[message.guild.id]:
            afk_users[message.guild.id].pop(message.author.id)
            try:
                if message.author.display_name.startswith("[AFK] "):
                    await message.author.edit(nick=message.author.display_name[6:])
            except: pass
            await message.reply(embed=UIUtils.create_embed("🌸 Welcome Back", f"{BotConfig.BORDER}\n\n💖 Chào mừng {message.author.mention} trở lại! Đã tắt AFK.\n\n{BotConfig.BORDER}", BotConfig.COLOR_SAKURA_PINK), delete_after=5)
            
        for mention in message.mentions:
            if mention.id in afk_users.get(message.guild.id, {}):
                afk_data = afk_users[message.guild.id][mention.id]
                desc = f"{BotConfig.BORDER}\n\n💤 **{mention.display_name}** đang AFK!\n📝 Lý do: *{afk_data['reason']}*\n\n{BotConfig.BORDER}"
                await message.reply(embed=UIUtils.create_embed("🌸 Người dùng AFK", desc, BotConfig.COLOR_BLACK_CHIC), delete_after=10)

    if message.channel.id in counting_channels:
        data = counting_channels[message.channel.id]
        try:
            num = int(message.content.strip())
            if data["last_user"] == message.author.id:
                await message.delete()
                return
            expected = data["current"] + 1
            if num == expected:
                data["current"] = num
                data["last_user"] = message.author.id
                if num > data["high_score"]: data["high_score"] = num
                await message.add_reaction(BotConfig.EMOJI_TICK) # Thả ảnh Tick
            else:
                data["current"] = 0
                data["last_user"] = 0
                await message.add_reaction(BotConfig.EMOJI_X) # Thả ảnh X
                await message.reply(embed=UIUtils.build_warning_embed("Đếm Sai!", "Bạn đã đếm sai! Kênh đếm số đã reset về 0."))
        except ValueError:
            pass

    await handle_word_chain(message)
    await bot.process_commands(message)

# ====================================================================================================
# PHẦN 9: CHẠY BOT
# ====================================================================================================
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        logger.error("❌ Không tìm thấy DISCORD_TOKEN! Vui lòng set environment variable.")
    else:
        bot.run(TOKEN)
