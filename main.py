# ====================================================================================================
# ██████╗ ██╗    █████╗  ██████╗██╗  ██╗    ██████╗ ██╗███╗    ██╗██╗  ██╗    ██████╗  ██████╗ ████████╗
# ██╔══██╗██║    ██╔══██╗██╔════╝██║ ██╔╝    ██╔══██╗██║████╗   ██║██║ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
# ██████╔╝██║    ███████║██║     █████╔╝     ██████╔╝██║██╔██╗  ██║█████╔╝     ██████╔╝██║   ██║   ██║   
# ██╔══██╗██║    ██╔══██╗██║     ██╔═██╗     ██╔═══╝ ██║██║╚██╗ ██║██╔═██╗     ██╔══██╗██║   ██║   ██║   
# ██████╔╗███████╗██║  ██║╚██████╗██║  ██╗    ██║     ██║██║ ╚████║██║  ██╗    ██████╔╝╚██████╔╝   ██║   
# ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝    ╚═════╝  ╚═╝    ╚═╝   
#                                                                                                   
# SAKURA BLACK PINK ARCADE ULTIMATE (v8.0.0 - Full Fix + Math + Diagnostic)
# ====================================================================================================

import os
import sys
import json
import random
import logging
import asyncio
import threading
import unicodedata
import math as math_module
import re
import traceback
import aiohttp
from urllib.parse import quote
from datetime import datetime, timedelta
from typing import Set, List, Dict, Optional, Union
from flask import Flask, Response
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

# ====================================================================================================
# PHẦN 1: CẤU HÌNH
# ====================================================================================================

class BotConfig:
    VERSION: str = "8.0.0 Full Fix"
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
# PHẦN 2: DỮ LIỆU DỰ PHÒNG
# ====================================================================================================

DEFAULT_VIETNAMESE_FALLBACK: Set[str] = {
    "an ninh", "an toàn", "ấm áp", "ẩm ướt", "ánh sáng", "áo quần", "ăn uống", "át chủ",
    "ba mươi", "bạc hà", "bạ bạt", "bạn bè", "bao dung", "bạo chúa", "bền bỉ",
    "bí quyết", "bình yên", "bồi đắp", "bứt phá", "bị ốm"
}

DEFAULT_ENGLISH_FALLBACK: Set[str] = {
    "apple", "anchor", "angel", "apex", "arrow", "azure", "acorn", "album",
    "amber", "amulet", "antique", "arctic", "astro", "aura", "avocado",
    "axe", "alchemy", "alert", "alpine", "amaze"
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
    {"title": "titanic", "clue": "🚢 Tảng băng trôi, My Heart Will Go On 💔", "image": "https://image.tmdb.org/t/p/w500/2bXcWyivE3atm2bUCVn0gSZweBO.jpg"},
    {"title": "avatar", "clue": "👽 Người Na'vi màu xanh 🌳", "image": "https://image.tmdb.org/t/p/w500/2B0bWqU7lTr7gRgSjIwO4W4cQ0M.jpg"},
    {"title": "ký sinh trùng", "clue": "🪨 Giới siêu giàu và gia đình nghèo 🏠", "image": "https://image.tmdb.org/t/p/w500/TU9NIjwzjoKPwQHoHshkFcQUCG.jpg"},
    {"title": "joker", "clue": "🃏 Kẻ thù của Batman, nụ cười rùng rợn 🤡", "image": "https://image.tmdb.org/t/p/w500/ijQ4s9h7KQ3oJX47j7zev8a3Jhf.jpg"},
    {"title": "hack não", "clue": "💊 Viên thuốc đỏ hay xanh? 🕶️", "image": "https://image.tmdb.org/t/p/w500/icmmSD4vTTDKOq2vvdulafOGw93.jpg"},
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
# PHẦN 3: LOGGING & WEB SERVER (FIXED)
# ====================================================================================================

class LoggerSetup:
    @staticmethod
    def initialize_logger() -> logging.Logger:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        # Tắt log từ các thư viện không cần thiết
        for mod in ['werkzeug', 'flask', 'gunicorn', 'urllib3', 'asyncio']:
            logging.getLogger(mod).setLevel(logging.CRITICAL)
            logging.getLogger(mod).disabled = True
        fmt = logging.Formatter("[%(asctime)s] | %(levelname)-8s | %(name)s : %(message)s", datefmt="%H:%M:%S")
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(fmt)
        lg = logging.getLogger("Sakura")
        lg.setLevel(logging.INFO)
        lg.addHandler(h)
        return lg

logger = LoggerSetup.initialize_logger()

keep_alive_app = Flask("SakuraKeepAlive")

@keep_alive_app.route('/')
def route_home() -> Response:
    return Response(response="OK", status=200, mimetype='text/plain')

def launch_web_server() -> None:
    try:
        logging.getLogger('werkzeug').disabled = True
        keep_alive_app.run(
            host=BotConfig.WEB_SERVER_HOST,
            port=BotConfig.WEB_SERVER_PORT,
            debug=False, use_reloader=False, threaded=True, log=None
        )
    except Exception as e:
        logger.error(f"Flask error: {e}")

threading.Thread(target=launch_web_server, daemon=True).start()

# ====================================================================================================
# PHẦN 4: SAFE FETCH HELPER
# ====================================================================================================

async def safe_fetch_json(session: aiohttp.ClientSession, url: str, timeout: int = 10) -> Optional[dict]:
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
            if resp.status != 200:
                return None
            ct = resp.headers.get('Content-Type', '')
            if 'application/json' not in ct:
                logger.warning(f"URL trả về {ct} thay vì JSON (Cloudflare chặn?)")
                return None
            return await resp.json()
    except Exception as e:
        logger.error(f"Fetch error {url}: {e}")
        return None

# ====================================================================================================
# PHẦN 5: USER DATA MANAGER
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
                logger.error(f"Lỗi đọc user data: {e}")
        return {}

    @staticmethod
    def save_data(data: dict) -> None:
        try:
            with open(FILE_USER_DATA, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Lỗi ghi user data: {e}")

    @staticmethod
    def get_user(user_id: int) -> dict:
        data = UserDataManager.load_data()
        uid = str(user_id)
        if uid not in data:
            data[uid] = {"hints": 5, "last_daily": ""}
            UserDataManager.save_data(data)
        return data[uid]

    @staticmethod
    def update_user(user_id: int, hints: int = None, last_daily: str = None) -> None:
        data = UserDataManager.load_data()
        uid = str(user_id)
        if uid not in data:
            data[uid] = {"hints": 5, "last_daily": ""}
        if hints is not None:
            data[uid]["hints"] = hints
        if last_daily is not None:
            data[uid]["last_daily"] = last_daily
        UserDataManager.save_data(data)

# ====================================================================================================
# PHẦN 6: TỪ ĐIỂN & INDEX
# ====================================================================================================

class DataManager:
    @staticmethod
    def load_text_file(filepath: str, fallback: Set[str]) -> Set[str]:
        words = set(fallback)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        c = line.strip().lower()
                        if c:
                            words.add(c)
                logger.info(f"Đã nạp {len(words):,} từ [{filepath}]")
            except Exception as err:
                logger.error(f"Lỗi đọc {filepath}: {err}")
        else:
            logger.warning(f"Không tìm thấy [{filepath}]. Tạo fallback.")
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("\n".join(fallback))
            except Exception:
                pass
        return words

    @staticmethod
    def append_word(filepath: str, word: str) -> bool:
        try:
            m = "a" if os.path.exists(filepath) else "w"
            with open(filepath, m, encoding="utf-8") as f:
                f.write(f"\n{word}")
            return True
        except Exception as err:
            logger.error(f"Lỗi ghi {filepath}: {err}")
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
    idx: Dict[str, List[str]] = {}
    for w in dictionary:
        parts = w.split()
        if parts:
            idx.setdefault(parts[0], []).append(w)
    return idx

def build_letter_index(dictionary: Set[str]) -> Dict[str, List[str]]:
    idx: Dict[str, List[str]] = {}
    for w in dictionary:
        if w:
            idx.setdefault(w[0], []).append(w)
    return idx

VIETNAMESE_INDEX_BY_FIRST_SYLLABLE: Dict[str, List[str]] = build_syllable_index(COMBINED_VIETNAMESE_DICTIONARY)
ENGLISH_INDEX_BY_FIRST_LETTER: Dict[str, List[str]] = build_letter_index(ENGLISH_DICT)

# ====================================================================================================
# PHẦN 7: GAME MODE, SESSION, GLOBAL STORAGE
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

    def init_session(self, mode: str, start_word: str = "", target: str = "") -> None:
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
        elif mode in [GameMode.GUESS_MOVIE, GameMode.GUESS_EMOJI]:
            self.secret_target = target

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
        async def _timer():
            try:
                await asyncio.sleep(self.hardcore_time)
                if self.is_active:
                    self.is_active = False
                    if self.active_mode in [GameMode.PVP_VIETNAMESE, GameMode.PVP_ENGLISH]:
                        w = f"🏆 <@{self.last_player_id}> thắng vì không ai nối kịp!" if self.last_player_id else "Không ai nối kịp!"
                    else:
                        w = "🤖 Bot thắng vì bạn không nối kịp!"
                    desc = f"{BotConfig.BORDER}\n\n⏰ **HẾT GIỌ!**\n💀 {w}\n\n{BotConfig.BORDER}"
                    await channel.send(embed=UIUtils.create_embed("⏳ HẾT GIỜ!", desc, BotConfig.COLOR_BLACK_CHIC))
                    self.reset()
            except asyncio.CancelledError:
                pass
        self.hardcore_task = asyncio.create_task(_timer())

class SessionManager:
    def __init__(self):
        self._sessions: Dict[int, ChannelSession] = {}
    def get(self, cid: int) -> ChannelSession:
        if cid not in self._sessions:
            self._sessions[cid] = ChannelSession(cid)
        return self._sessions[cid]

sessions = SessionManager()
counting_channels: Dict[int, Dict[str, int]] = {}
afk_users: Dict[int, Dict[int, Dict[str, Union[datetime, str]]]] = {}
math_questions: Dict[int, Dict[str, Union[int, float, str, bool]]] = {}

# ====================================================================================================
# PHẦN 8: MATH UTILS (DUY NHẤT)
# ====================================================================================================

class MathUtils:
    @staticmethod
    def generate_question(difficulty: str = "normal") -> Dict[str, Union[int, float, str]]:
        ops_map = {
            "easy": ["+", "-"],
            "normal": ["+", "-", "×", "÷"],
            "hard": ["+", "-", "×", "÷", "^", "√"],
            "expert": ["+", "-", "×", "÷", "^", "√", "%"]
        }
        ops = ops_map.get(difficulty, ops_map["normal"])
        op = random.choice(ops)

        if op == "+":
            if difficulty in ("hard", "expert"):
                a, b = random.randint(50, 500), random.randint(50, 500)
            elif difficulty == "normal":
                a, b = random.randint(10, 200), random.randint(10, 100)
            else:
                a, b = random.randint(1, 50), random.randint(1, 50)
            return {"question": f"{a} + {b}", "answer": a + b, "op": op, "difficulty": difficulty}

        elif op == "-":
            if difficulty in ("hard", "expert"):
                a, b = random.randint(100, 999), random.randint(50, 500)
            elif difficulty == "normal":
                a, b = random.randint(20, 200), random.randint(5, 100)
            else:
                a, b = random.randint(10, 50), random.randint(1, 30)
            if a < b:
                a, b = b, a
            return {"question": f"{a} - {b}", "answer": a - b, "op": op, "difficulty": difficulty}

        elif op == "×":
            if difficulty in ("hard", "expert"):
                a, b = random.randint(12, 50), random.randint(12, 50)
            elif difficulty == "normal":
                a, b = random.randint(5, 25), random.randint(3, 15)
            else:
                a, b = random.randint(2, 10), random.randint(2, 10)
            return {"question": f"{a} × {b}", "answer": a * b, "op": op, "difficulty": difficulty}

        elif op == "÷":
            if difficulty in ("hard", "expert"):
                b = random.randint(3, 25); ans = random.randint(5, 50)
            elif difficulty == "normal":
                b = random.randint(2, 15); ans = random.randint(2, 20)
            else:
                b = random.randint(2, 10); ans = random.randint(1, 10)
            a = b * ans
            return {"question": f"{a} ÷ {b}", "answer": ans, "op": op, "difficulty": difficulty}

        elif op == "^":
            base = random.randint(2, 12)
            exp = random.randint(2, 4) if difficulty == "expert" else random.randint(2, 3)
            return {"question": f"{base}^{exp}", "answer": base ** exp, "op": op, "difficulty": difficulty}

        elif op == "√":
            base = random.randint(2, 20) if difficulty == "expert" else random.randint(2, 15)
            return {"question": f"√{base * base}", "answer": base, "op": op, "difficulty": difficulty}

        elif op == "%":
            pct = random.choice([10, 20, 25, 30, 40, 50, 60, 75, 80])
            total = random.choice([100, 200, 300, 400, 500, 1000])
            return {"question": f"{pct}% của {total}", "answer": (pct / 100) * total, "op": op, "difficulty": difficulty}

        return {"question": "1 + 1", "answer": 2, "op": "+", "difficulty": difficulty}

    @staticmethod
    def solve_expression(expr: str) -> Optional[Dict[str, Union[str, float, int]]]:
        original = expr.strip()
        cleaned = original.replace(" ", "").replace(",", "")
        cleaned = cleaned.replace("×", "*").replace("÷", "/").replace("x", "*").replace("X", "*")
        cleaned = re.sub(r'(\d+)\^(\d+)', r'\1**\2', cleaned)

        pct_m = re.match(r'^(\d+)%\s*của\s*(\d+)$', original, re.IGNORECASE)
        if pct_m:
            pct, total = float(pct_m.group(1)), float(pct_m.group(2))
            result = (pct / 100) * total
            if result == int(result):
                result = int(result)
            return {"result": result, "steps": [f"📝 `{original}`", f"🧮 = {result}"], "type": "phần trăm"}

        cleaned = re.sub(r'√(\d+)', lambda m: f"({m.group(1)}**0.5)", cleaned)
        if not re.compile(r'^[\d\+\-\*\/\.\(\)]+$').match(cleaned):
            return None

        try:
            result = eval(cleaned, {"__builtins__": {}}, {})
            if not isinstance(result, (int, float)):
                return None
            if math_module.isnan(result) or math_module.isinf(result):
                return None
            if isinstance(result, float) and result == int(result):
                result = int(result)
            elif isinstance(result, float):
                result = round(result, 6)
                if result == int(result):
                    result = int(result)
            return {"result": result, "steps": [f"📝 `{original}`", f"🧮 = {result}"], "type": "biểu thức"}
        except ZeroDivisionError:
            return {"result": None, "steps": [f"📝 `{original}`", "❌ Chia cho 0!"], "type": "lỗi"}
        except Exception:
            return None

    @staticmethod
    def fmt(n: Union[int, float]) -> str:
        if isinstance(n, float):
            if n == int(n):
                return str(int(n))
            return f"{n:.4f}".rstrip("0").rstrip(".")
        return str(n)

# ====================================================================================================
# PHẦN 9: GAME UTILS
# ====================================================================================================

class GameUtils:
    @staticmethod
    def remove_diacritics(text: str) -> str:
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

    @staticmethod
    def scramble(phrase: str) -> str:
        syl = phrase.split()
        if len(syl) <= 1:
            return phrase
        sh = syl.copy()
        for _ in range(10):
            random.shuffle(sh)
            if sh != syl:
                break
        return " ".join(sh)

    @staticmethod
    def country_mask(name: str) -> str:
        if not name:
            return ""
        chars = list(name)
        masked = []
        for i, c in enumerate(chars):
            if c == ' ':
                masked.append(' ')
            elif i == 0 or i == len(chars) - 1:
                masked.append(c.upper())
            else:
                masked.append('_')
        return " ".join(masked)

# ====================================================================
# PHẦN 10: UI UTILS
# ====================================================================

class UIUtils:
    BANNER = "https://z-cdn-media.chatglm.cn/files/389fe242-44cf-4125-a5a9-50b3ebd66bf1.png?auth_key=1887393535-7807479087454b1aa9f9c86f6003f60e-0-7c1d04af7567d3dd1495b496f97955e3"
    FOOTER_ICON = "https://cdn.discordapp.com/embed/avatars/0.png"
    THUMB = "https://images.unsplash.com/photo-1522383225653-ed111181a951?ixlib=rb-4.0.3&auto=format&fit=crop&w=150&q=80"

    @staticmethod
    def create_embed(title: str, desc: str, color: int = BotConfig.COLOR_SAKURA_PINK, image_url: str = None) -> discord.Embed:
        e = discord.Embed(title=title, description=desc, color=color, timestamp=datetime.now())
        e.set_footer(text="🖤🌸 Sakura Black Pink Arcade 🌸🖤", icon_url=UIUtils.FOOTER_ICON)
        e.set_thumbnail(url=UIUtils.THUMB)
        e.set_image(url=image_url if image_url else UIUtils.BANNER)
        return e

    @staticmethod
    def math_embed(title: str, desc: str, difficulty: str = "normal") -> discord.Embed:
        colors = {"easy": 0xFFB7C5, "normal": 0xFF69B4, "hard": 0xFF1493, "expert": 0x9B59B6}
        e = discord.Embed(title=title, description=desc, color=colors.get(difficulty, 0xFF69B4), timestamp=datetime.now())
        e.set_footer(text="🧮🌸 Toán Học Hồng Cánh Sen 🌸🧮", icon_url=UIUtils.FOOTER_ICON)
        e.set_thumbnail(url=UIUtils.BANNER)
        dname = {"easy": "🟢 Dễ", "normal": "🟡 Thường", "hard": "🔴 Khó", "expert": "💜 Chuyên Gia"}
        e.add_field(name="Độ khó", value=dname.get(difficulty, "🟡 Thường"), inline=True)
        return e

    @staticmethod
    def warn_embed(title: str, msg: str) -> discord.Embed:
        d = f"{BotConfig.BORDER}\n\n⚠️ **{title}**\n\n{msg}\n\n{BotConfig.BORDER}"
        return UIUtils.create_embed("🚫 Cảnh Báo", d, BotConfig.COLOR_RED_DARK)

    @staticmethod
    def invalid_embed(reason: str) -> discord.Embed:
        d = f"{BotConfig.BORDER}\n\n❌ **Từ không hợp lệ!**\n📌 *{reason}*\n💡 Dùng `/themtu [từ]` để bổ sung!\n\n{BotConfig.BORDER}"
        return UIUtils.create_embed("💔 TỪ KHÔNG HỢP LỆ", d, BotConfig.COLOR_RED_DARK)

    @staticmethod
    def ok_embed(title: str, msg: str) -> discord.Embed:
        d = f"{BotConfig.BORDER}\n\n✨ **{title.upper()}** ✨\n\n{msg}\n\n{BotConfig.BORDER}"
        return UIUtils.create_embed("🌸 Thành Công", d, BotConfig.COLOR_DEEP_PINK)

    @staticmethod
    def help_embed() -> discord.Embed:
        p = BotConfig.PREFIX
        d = (
            f"{BotConfig.BORDER}\n\n"
            f"🖤 **Vườn hoa Đen Hồng Cánh Hoa** 🌸\n\n"
            f"🇻🇳 **[ NỐI TỪ TIẾNG VIỆT ]**\n"
            f"❯ `{p}noitu` ` `{p}botnoitu`\n"
            f"❯ `{p}noituhc [s]` ` `{p}botnoituhc [s]`\n"
            f"❯ `{p}noitucam [chữ]` ` `{p}botnoitucam [chữ]`\n"
            f"❯ `{p}noitucamhc [s] [chữ]` ` `{p}botnoitucamhc [s] [chữ]`\n\n"
            f"🇬🇧 **[ NỐI TỪ TIẾNG ANH ]**\n"
            f"❯ `{p}noitueng` ` `{p}botnoitueng`\n\n"
            f"👑 **[ GIẢI ĐỐ & ARCADE ]**\n"
            f"❯ `{p}vuatiengviet` ` `{p}doanquocgia`\n"
            f"❯ `{p}doantenphim` ` `{p}doanemoji`\n"
            f"❯ `{p}tictactoe` ` `{p}rps`\n"
            f"❯ `{p}ship @u1 @u2`\n\n"
            f"🧮 **[ TOÁN HỌC HỒNG CÁNH SEN ]**\n"
            f"❯ `{p}toan [easy/normal/hard/expert]`\n"
            f"❯ `{p}giaitoan 25 × 4 + 10`\n"
            f"❯ `{p}giaitoan √256`\n"
            f"❯ `{p}giaitoan 5^3`\n"
            f"❯ `{p}giaitoan 25% của 400`\n"
            f"❯ `{p}bangtoan [số]`\n"
            f"❯ `{p}toanhoc`\n\n"
            f"⚙️ **[ TIỆN ÍCH ]**\n"
            f"❯ `/themtu` ` `/xoatu` ` `/say` ` `/dm`\n"
            f"❯ `{p}daily` ` `{p}hint`\n"
            f"❯ `{p}restart` ` `{p}huyvanchoi`\n"
            f"❯ `{p}nghia [từ]` ` `{p}afk [lý do]`\n"
            f"❯ `{p}countsetup` ` `{p}tiepterauma @u`\n"
            f"❯ `{p}meme` ` `{p}avt @u` ` `{p}ping`\n\n"
            f"{BotConfig.BORDER}"
        )
        return UIUtils.create_embed("✦ TRỢ GIÚP SAKURA ✦", d, BotConfig.COLOR_SAKURA_PINK)

# ====================================================================
# PHẦN 11: VIEWS
# ====================================================================

class TicTacToeView(View):
    def __init__(self):
        super().__init__(timeout=120.0)
        self.board = [" " for _ in range(9)]
        self._update()

    def _winner(self) -> str:
        wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for a, b, c in wins:
            if self.board[a] == self.board[b] == self.board[c] != " ":
                return self.board[a]
        return "tie" if " " not in self.board else "none"

    def _update(self):
        self.clear_items()
        for i in range(9):
            style = discord.ButtonStyle.secondary
            lbl = str(i + 1)
            if self.board[i] == "X":
                style, lbl = discord.ButtonStyle.danger, "❌"
            elif self.board[i] == "O":
                style, lbl = discord.ButtonStyle.success, "⭕"
            btn = Button(label=lbl, style=style, row=i // 3, disabled=(self.board[i] != " "))
            btn.callback = self._mk(i)
            self.add_item(btn)

    def _mk(self, idx):
        async def cb(interaction: discord.Interaction):
            if self._winner() != "none":
                return
            self.board[idx] = "X"
            w = self._winner()
            if w == "none":
                empty = [i for i, v in enumerate(self.board) if v == " "]
                if empty:
                    self.board[random.choice(empty)] = "O"
                    w = self._winner()
            self._update()
            if w == "X":
                c = f"🎉 {interaction.user.mention} thắng!"
                self.disable_all_items()
            elif w == "O":
                c = "🤖 Bot thắng!"
                self.disable_all_items()
            elif w == "tie":
                c = "🤝 Hòa!"
                self.disable_all_items()
            else:
                c = f"🖤🌸 Lượt của **{interaction.user.display_name}** (X)"
            await interaction.response.edit_message(content=c, view=self)
        return cb

class RpsView(View):
    def __init__(self):
        super().__init__(timeout=60.0)
        self.choices = ["✂️", "🪨", "📄"]

    def _result(self, u: str, b: str) -> str:
        if u == b:
            return "Hòa! 🤝"
        if (u == "✂️" and b == "📄") or (u == "🪨" and b == "✂️") or (u == "📄" and b == "🪨"):
            return "Bạn thắng! 🎉"
        return "Bot thắng! 🤖"

    @discord.ui.button(label="Kéo", emoji="✂️", style=discord.ButtonStyle.success)
    async def btn_k(self, interaction: discord.Interaction, button: Button):
        b = random.choice(self.choices)
        self.clear_items()
        await interaction.response.edit_message(content=f"✂️ Bạn: Kéo | 🤖 Bot: {b}\n**{self._result('✂️', b)}**", view=self)

    @discord.ui.button(label="Búa", emoji="🪨", style=discord.ButtonStyle.primary)
    async def btn_b(self, interaction: discord.Interaction, button: Button):
        b = random.choice(self.choices)
        self.clear_items()
        await interaction.response.edit_message(content=f"🪨 Bạn: Búa | 🤖 Bot: {b}\n**{self._result('🪨', b)}**", view=self)

    @discord.ui.button(label="Bao", emoji="📄", style=discord.ButtonStyle.danger)
    async def btn_p(self, interaction: discord.Interaction, button: Button):
        b = random.choice(self.choices)
        self.clear_items()
        await interaction.response.edit_message(content=f"📄 Bạn: Bao | 🤖 Bot: {b}\n**{self._result('📄', b)}**", view=self)

# ====================================================================
# PHẦN 12: BOT INIT & EVENTS
# ====================================================================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix=BotConfig.PREFIX, intents=intents, help_command=None, case_insensitive=True)

@bot.event
async def on_ready():
    logger.info(f"✅ Bot online: {bot.user}")
    try:
        synced = await bot.tree.sync()
        logger.info(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        logger.error(f"Slash sync error: {e}")
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.playing, name=f"{BotConfig.PREFIX}help | 🖤🌸")
    )

@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=UIUtils.warn_embed("Thiếu Thông Tin", f"Gõ `{BotConfig.PREFIX}help`"))
    elif isinstance(error, commands.CheckFailure):
        await ctx.send(embed=UIUtils.warn_embed("Quyền", "🖤 Chỉ Owner!"))
    else:
        logger.error(f"Cmd error: {error}")

# ====================================================================
# PHẦN 13: SYSTEM COMMANDS
# ====================================================================

@bot.command(name="ping")
async def cmd_ping(ctx):
    ms = round(bot.latency * 1000)
    await ctx.send(embed=UIUtils.create_embed("🏓 Pong!", f"{BotConfig.BORDER}\n\n💓 `{ms}ms`\n\n{BotConfig.BORDER}"))

@bot.command(name="about")
async def cmd_about(ctx):
    d = f"{BotConfig.BORDER}\n\n🤖 **v{BotConfig.VERSION}**\n🇻🇳 TV: {len(COMBINED_VIETNAMESE_DICTIONARY):,}\n🇬🇧 TA: {len(ENGLISH_DICT):,}\n🌍 QG: {len(COUNTRIES_VN_DICT):,}\n🎬 Phim: {len(FALLBACK_MOVIES_DATA):,}\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🖤 Sakura Arcade", d, BotConfig.COLOR_BLACK_CHIC))

@bot.command(name="help", aliases=["menu"])
async def cmd_help(ctx):
    await ctx.send(embed=UIUtils.help_embed())

@bot.command(name="admin")
@commands.is_owner()
async def cmd_admin(ctx):
    if ctx.author.id != BotConfig.OWNER_ID:
        return
    d = f"{BotConfig.BORDER}\n\n🖤 **Admin Panel** 🌸\n🎮 Sessions: {len(sessions._sessions)}\n🧮 Math Q: {len(math_questions)}\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("🔒 ADMIN", d, BotConfig.COLOR_BLACK_CHIC))

@bot.command(name="daily")
async def cmd_daily(ctx):
    ud = UserDataManager.get_user(ctx.author.id)
    today = datetime.now().strftime("%Y-%m-%d")
    if ud["last_daily"] == today:
        await ctx.send(embed=UIUtils.create_embed("🌸 Daily", f"{BotConfig.BORDER}\n\n⏳ Đã nhận hôm nay!\n💡 Còn: **{ud['hints']}** gợi ý\n\n{BotConfig.BORDER}", BotConfig.COLOR_DEEP_PINK))
        return
    nh = ud["hints"] + 3
    UserDataManager.update_user(ctx.author.id, hints=nh, last_daily=today)
    await ctx.send(embed=UIUtils.ok_embed("Daily!", f"💖 {ctx.author.mention} +3 Gợi Ý\n💡 Tổng: **{nh}**"))

@bot.command(name="hint")
async def cmd_hint(ctx):
    s = sessions.get(ctx.channel.id)
    if not s.is_active or s.active_mode not in [GameMode.PVP_VIETNAMESE, GameMode.BOT_VIETNAMESE, GameMode.PVP_ENGLISH, GameMode.BOT_ENGLISH]:
        await ctx.send(embed=UIUtils.warn_embed("Lỗi", "Chỉ dùng khi đang Nối Từ!"))
        return
    ud = UserDataManager.get_user(ctx.author.id)
    if ud["hints"] <= 0:
        await ctx.send(embed=UIUtils.warn_embed("Hết", f"Dùng `{BotConfig.PREFIX}daily` để nhận thêm."))
        return
    nh = ud["hints"] - 1
    UserDataManager.update_user(ctx.author.id, hints=nh)
    ht = ""
    if s.active_mode in [GameMode.PVP_VIETNAMESE, GameMode.BOT_VIETNAMESE]:
        ls = s.current_word.split()[-1]
        pw = [w for w in VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.get(ls, []) if w not in s.used_words_history]
        if pw:
            cw = random.choice(pw)
            ht = f"🔍 Bắt đầu: **`{ls.upper()}`**\n💡 Gợi ý: **`{cw.split()[-1][0].upper()}...`**"
        else:
            ht = f"🔍 Bắt đầu: **`{ls.upper()}`**\n⚠️ Không tìm thấy từ!"
    elif s.active_mode in [GameMode.PVP_ENGLISH, GameMode.BOT_ENGLISH]:
        ll = s.current_word[-1]
        pw = [w for w in ENGLISH_INDEX_BY_FIRST_LETTER.get(ll, []) if w not in s.used_words_history]
        if pw:
            cw = random.choice(pw)
            ht = f"🔍 Starts: **`{ll.upper()}`**\n💡 Hint: **`{cw[:2].upper()}...`** ({len(cw)} chars)"
        else:
            ht = f"🔍 Starts: **`{ll.upper()}`**\n⚠️ No hints!"
    d = f"{BotConfig.BORDER}\n\n🎯 {ctx.author.mention} dùng 1 Gợi Ý\n\n{ht}\n\n💡 Còn: **{nh}**\n\n{BotConfig.BORDER}"
    await ctx.send(embed=UIUtils.create_embed("💡 GỢI Ý", d, BotConfig.COLOR_GOLD))

# ====================================================================
# PHẦN 14: SLASH COMMANDS
# ====================================================================

@bot.tree.command(name="themtu", description="Thêm từ (Owner)")
async def sl_themtu(interaction: discord.Interaction, word: str):
    if interaction.user.id != BotConfig.OWNER_ID:
        await interaction.response.send_message(embed=discord.Embed(title="⛔", description="Không có quyền!", color=BotConfig.COLOR_RED_DARK), ephemeral=True)
        return
    w = word.strip().lower()
    sp = w.split()
    if len(sp) == 2:
        if w in COMBINED_VIETNAMESE_DICTIONARY:
            await interaction.response.send_message(embed=UIUtils.warn_embed("Có rồi", f"`{w}` đã có!"), ephemeral=True)
            return
        COMBINED_VIETNAMESE_DICTIONARY.add(w)
        COMBINED_VIETNAMESE_LIST.append(w)
        VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.setdefault(sp[0], []).append(w)
        DataManager.append_word(BotConfig.FILE_VIETNAMESE_DICT, w)
        await interaction.response.send_message(embed=UIUtils.ok_embed("OK", f"Đã thêm TV `{w}`!"))
    elif len(sp) == 1 and w.isalpha():
        if w in ENGLISH_DICT:
            await interaction.response.send_message(embed=UIUtils.warn_embed("Có rồi", f"`{w}` đã có!"), ephemeral=True)
            return
        ENGLISH_DICT.add(w)
        ENGLISH_LIST.append(w)
        ENGLISH_INDEX_BY_FIRST_LETTER.setdefault(w[0], []).append(w)
        DataManager.append_word(BotConfig.FILE_ENGLISH_DICT, w)
        await interaction.response.send_message(embed=UIUtils.ok_embed("OK", f"Đã thêm TA `{w}`!"))
    else:
        await interaction.response.send_message(embed=UIUtils.invalid_embed("TV 2 tiếng, TA 1 tiếng!"), ephemeral=True)

@bot.tree.command(name="xoatu", description="Xóa từ (Owner)")
@app_commands.describe(word="Từ cần xóa")
async def sl_xoatu(interaction: discord.Interaction, word: str):
    if interaction.user.id != BotConfig.OWNER_ID:
        await interaction.response.send_message(embed=discord.Embed(title="⛔", description="Không có quyền!", color=BotConfig.COLOR_RED_DARK), ephemeral=True)
        return
    w = word.strip().lower()
    sp = w.split()
    if len(sp) == 2:
        if w not in COMBINED_VIETNAMESE_DICTIONARY:
            await interaction.response.send_message(embed=UIUtils.warn_embed("Không có", f"`{w}` không tìm thấy!"), ephemeral=True)
            return
        COMBINED_VIETNAMESE_DICTIONARY.discard(w)
        if w in COMBINED_VIETNAMESE_LIST:
            COMBINED_VIETNAMESE_LIST.remove(w)
        lst = VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.get(sp[0], [])
        if w in lst:
            lst.remove(w)
        try:
            with open(BotConfig.FILE_VIETNAMESE_DICT, "w", encoding="utf-8") as f:
                f.write("\n".join(COMBINED_VIETNAMESE_DICTIONARY))
        except Exception as e:
            logger.error(f"Write error: {e}")
        await interaction.response.send_message(embed=UIUtils.ok_embed("OK", f"Đã xóa TV `{w}`!"))
    elif len(sp) == 1 and w.isalpha():
        if w not in ENGLISH_DICT:
            await interaction.response.send_message(embed=UIUtils.warn_embed("Không có", f"`{w}` không tìm thấy!"), ephemeral=True)
            return
        ENGLISH_DICT.discard(w)
        if w in ENGLISH_LIST:
            ENGLISH_LIST.remove(w)
        lst = ENGLISH_INDEX_BY_FIRST_LETTER.get(w[0], [])
        if w in lst:
            lst.remove(w)
        try:
            with open(BotConfig.FILE_ENGLISH_DICT, "w", encoding="utf-8") as f:
                f.write("\n".join(ENGLISH_DICT))
        except Exception as e:
            logger.error(f"Write error: {e}")
        await interaction.response.send_message(embed=UIUtils.ok_embed("OK", f"Đã xóa TA `{w}`!"))
    else:
        await interaction.response.send_message(embed=UIUtils.invalid_embed("TV 2 tiếng, TA 1 tiếng!"), ephemeral=True)

@bot.tree.command(name="say", description="Bot nói thay bạn")
@app_commands.describe(text="Nội dung")
async def sl_say(interaction: discord.Interaction, text: str):
    await interaction.channel.send(text)
    await interaction.response.send_message("✅ Done! 🌸", ephemeral=True)

@bot.tree.command(name="dm", description="Gửi DM ẩn danh")
@app_commands.describe(member="Người nhận", message="Nội dung")
async def sl_dm(interaction: discord.Interaction, member: discord.Member, message: str):
    if member.bot:
        await interaction.response.send_message("🤖 Bot không cần DM! 🌸", ephemeral=True)
        return
    try:
        await member.send(f"💌 **Tin nhắn ẩn danh:**\n\n{message}\n\n*— Sakura*")
        await interaction.response.send_message(f"✅ Đã gửi cho {member.mention}! 🌸", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"❌ {member.mention} đã tắt DM.", ephemeral=True)
    except Exception as e:
        logger.error(f"DM error: {e}")
        await interaction.response.send_message("❌ Lỗi!", ephemeral=True)

# ====================================================================
# PHẦN 15: UTILITY COMMANDS
# ====================================================================

@bot.command(name="afk")
async def cmd_afk(ctx, *, reason="Không có lý do"):
    gid = ctx.guild.id
    uid = ctx.author.id
    if gid not in afk_users:
        afk_users[gid] = {}
    afk_users[gid][uid] = {"timestamp": datetime.now(), "reason": reason}
    try:
        if not ctx.author.display_name.startswith("[AFK] "):
            await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
    except Exception:
        pass
    await ctx.send(embed=UIUtils.create_embed("🌸 AFK", f"{BotConfig.BORDER}\n\n💤 {ctx.author.mention} AFK\n📝 *{reason}*\n\n{BotConfig.BORDER}", BotConfig.COLOR_BLACK_CHIC))

@bot.command(name="tiepterauma", aliases=["trauma", "rauma", "tra"])
async def cmd_trauma(ctx, member: Optional[discord.Member] = None):
    if not member:
        await ctx.send(embed=UIUtils.warn_embed("Thiếu", f"VD: `{BotConfig.PREFIX}tiepterauma @user`"))
        return
    if member.id == bot.user.id:
        await ctx.send("🤖 Bot không uống rau má! 🌸")
        return
    await ctx.send(embed=UIUtils.create_embed("🌿 Rau Má", f"{BotConfig.BORDER}\n\nĐã tiếp tế 36 rau má cho {member.mention}! 💚\n\n{BotConfig.BORDER}"))

@bot.command(name="countsetup")
@commands.has_permissions(administrator=True)
async def cmd_count(ctx):
    counting_channels[ctx.channel.id] = {"current": 0, "high_score": 0, "last_user": 0}
    await ctx.send(embed=UIUtils.create_embed("🌸 Đếm Số", f"{BotConfig.BORDER}\n\n🔢 Kích hoạt! Gõ **1** để bắt đầu.\n⚠️ Sai hoặc 2 lần liên tiếp → về 0!\n\n{BotConfig.BORDER}"))
    try:
        await ctx.message.delete()
    except Exception:
        pass

@bot.command(name="meme")
async def cmd_meme(ctx):
    async with aiohttp.ClientSession() as session:
        data = await safe_fetch_json(session, "https://meme-api.com/gimme")
        if not data:
            await ctx.send("🖤 Không lấy được meme! 🌸")
            return
        t = data.get("title", "Meme")
        u = data.get("url")
        p = data.get("postLink", "")
        d = f"[🔗 Reddit]({p})" if p else ""
        await ctx.send(embed=UIUtils.create_embed(f"🖼️ {t}", d, image_url=u))

@bot.command(name="avt", aliases=["avatar"])
async def cmd_avt(ctx, member: Optional[discord.Member] = None):
    tgt = member or ctx.author
    url = tgt.display_avatar.with_size(1024).url
    e = UIUtils.create_embed(f"Ảnh {tgt.display_name}", f"[🔗 Tải]({url})", BotConfig.COLOR_DEEP_PINK)
    e.set_image(url=url)
    await ctx.send(embed=e)

@bot.command(name="rps", aliases=["oantuti"])
async def cmd_rps(ctx):
    await ctx.send(embed=UIUtils.create_embed("✊ Oẳn Tù Tì", f"{BotConfig.BORDER}\n\nChọn nút bên dưới!\n\n{BotConfig.BORDER}", BotConfig.COLOR_DEEP_PINK), view=RpsView())

@bot.command(name="ship")
async def cmd_ship(ctx, m1: discord.Member, m2: Optional[discord.Member] = None):
    t2 = m2 or ctx.author
    if m1 == t2:
        await ctx.send("Không ship chính mình! 🌸")
        return
    v = random.randint(0, 100)
    f = int(v / 100 * 10)
    if f == 0 and v > 0:
        f = 1
    bar = "❤" * f + "🖤" * (10 - f)
    if v < 20:
        msg = "💔 Không hợp..."
    elif v < 50:
        msg = "🌹 Có tình chút!"
    elif v < 80:
        msg = "💞 Rất hợp!"
    else:
        msg = "💍 Mệnh trời!"
    d = f"💖 **{m1.mention} × {t2.mention}**\n\n{bar} **{v}%**\n{msg}"
    img = None
    try:
        a1 = quote(str(m1.display_avatar.with_format("png").with_size(256).url), safe='')
        a2 = quote(str(t2.display_avatar.with_format("png").with_size(256).url), safe='')
        u = f"https://api.popcat.xyz/ship?user1={a1}&user2={a2}"
        if len(u) <= 2000:
            img = u
    except Exception:
        pass
    await ctx.send(embed=UIUtils.create_embed("💕 Ship", d, BotConfig.COLOR_DEEP_PINK, image_url=img))

# ====================================================================
# PHẦN 16: GAME START COMMANDS
# ====================================================================

@bot.command(name="noitu")
async def cmd_noitu(ctx):
    s = sessions.get(ctx.channel.id)
    if s.is_active:
        await ctx.send(embed=UIUtils.warn_embed("Bận", "Dùng `?huyvanchoi` để hủy.")); return
    w = random.choice(EASY_START_LIST)
    s.init_session(GameMode.PVP_VIETNAMESE, start_word=w)
    await ctx.send(embed=UIUtils.create_embed("💕 Nối Từ PvP", f"{BotConfig.BORDER}\n\n👉 **`{w.upper()}`**\n🌸 **`{w.split()[-1].upper()}`**\n\n{BotConfig.BORDER}"))

@bot.command(name="botnoitu", aliases=["noituubot"])
async def cmd_botnoitu(ctx):
    s = sessions.get(ctx.channel.id)
    if s.is_active:
        await ctx.send(embed=UIUtils.warn_embed("Bận", "")); return
    w = random.choice(EASY_START_LIST)
    s.init_session(GameMode.BOT_VIETNAMESE, start_word=w)
    await ctx.send(embed=UIUtils.create_embed("🤖 Solo Bot TV", f"{BotConfig.BORDER}\n\n👉 **`{w.upper()}`**\n🌸 **`{w.split()[-1].upper()}`**\n\n{BotConfig.BORDER}"))

@bot.command(name="noituhc")
async def cmd_noituhc(ctx, seconds: int = 15):
    s = sessions.get(ctx.channel.id)
    if s.is_active:
        await ctx.send(embed=UIUtils.warn_embed("Bận", "")); return
    seconds = max(5, min(120, seconds))
    w = random.choice(EASY_START_LIST)
    s.init_session(GameMode.PVP_VIETNAMESE, start_word=w)
    s.is_hardcore = True
    s.hardcore_time = seconds
    s.last_player_id = ctx.author.id
    await ctx.send(embed=UIUtils.create_embed("🔥 NỐI TỪ HC", f"{BotConfig.BORDER}\n\n💀 `{seconds}s`\n👉 **`{w.upper()}`**\n🌸 **`{w.split()[-1].upper()}`**\n\n{BotConfig.BORDER}", BotConfig.COLOR_RED_DARK))
    await s.start_hardcore_timer(ctx.channel)

@bot.command(name="botnoituhc")
async def cmd_botnoituhc(ctx, seconds: int = 15):
    s = sessions.get(ctx.channel.id)
    if s.is_active:
        await ctx.send(embed=UIUtils.warn_embed("Bận", "")); return
    seconds = max(5, min(120, seconds))
    w = random.choice(EASY_START_LIST)
    s.init_session(GameMode.BOT_VIETNAMESE, start_word=w)
    s.is_hardcore = True
    s.hardcore_time = seconds
    s.last_player_id = None
    await ctx.send(embed=UIUtils.create_embed("🔥 BOT HC", f"{BotConfig.BORDER}\n\n🤖💀 `{seconds}s`\n👉 **`{w.upper()}`**\n🌸 **`{w.split()[-1].upper()}`**\n\n{BotConfig.BORDER}", BotConfig.COLOR_RED_DARK))
    await s.start_hardcore_timer(ctx.channel)

@bot.command(name="noitucam")
async def cmd_noitucam(ctx, letter: str = ""):
    s = sessions.get(ctx.channel.id)
    if s.is_active:
        await ctx.send(embed=UIUtils.warn_embed("Bận", "")); return
    if not letter or len(letter) != 1:
        await ctx.send(embed=UIUtils.warn_embed("Thiếu", f"VD: `{BotConfig.PREFIX}noitucam a`")); return
    banned = letter.lower()
    w = random.choice(EASY_START_LIST)
    s.init_session(GameMode.PVP_VIETNAMESE, start_word=w)
    s.is_banned_mode = True
    s.banned_letter = banned
    await ctx.send(embed=UIUtils.create_embed("🚫 Cấm Chữ", f"{BotConfig.BORDER}\n\n👉 **`{w.upper()}`**\n🌸 **`{w.split()[-1].upper()}`**\n⛔ Cấm: **`{banned.upper()}`**\n\n{BotConfig.BORDER}", BotConfig.COLOR_RED_DARK))

@bot.command(name="botnoitucam")
async def cmd_botnoitucam(ctx, letter: str = ""):
    s = sessions.get(ctx.channel.id)
    if s.is_active:
        await ctx.send(embed=UIUtils.warn_embed("Bận", "")); return
    if not letter or len(letter) != 1:
        await ctx.send(embed=UIUtils.warn_embed("Thiếu", f"VD: `{BotConfig.PREFIX}botnoitucam a`")); return
    banned = letter.lower()
    w = random.choice(EASY_START_LIST)
    s.init_session(GameMode.BOT_VIETNAMESE, start_word=w)
    s.is_banned_mode = True
    s.banned_letter = banned
    await ctx.send(embed=UIUtils.create_embed("🤖🚫 Bot Cấm Chữ", f"{BotConfig.BORDER}\n\n👉 **`{w.upper()}`**\n🌸 **`{w.split()[-1].upper()}`**\n⛔ Cấm: **`{banned.upper()}`**\n\n{BotConfig.BORDER}", BotConfig.COLOR_RED_DARK))

@bot.command(name="noitucamhc")
async def cmd_noitucamhc(ctx, seconds: int = 15, letter: str = ""):
    s = sessions.get(ctx.channel.id)
    if s.is_active:
        await ctx.send(embed=UIUtils.warn_embed("Bận", "")); return
    if not letter or len(letter) != 1:
        await ctx.send(embed=UIUtils.warn_embed("Thiếu", f"VD: `{BotConfig.PREFIX}noitucamhc 15 a`")); return
    seconds = max(5, min(120, seconds))
    banned = letter.lower()
    w = random.choice(EASY_START_LIST)
    s.init_session(GameMode.PVP_VIETNAMESE, start_word=w)
    s.is_hardcore = True
    s.hardcore_time = seconds
    s.is_banned_mode = True
    s.banned_letter = banned
    s.last_player_id = ctx.author.id
    await ctx.send(embed=UIUtils.create_embed("💀🚫 Cấm Chữ HC", f"{BotConfig.BORDER}\n\n⏱️ `{seconds}s` ⛔ **`{banned.upper()}`**\n👉 **`{w.upper()}`**\n🌸 **`{w.split()[-1].upper()}`**\n\n{BotConfig.BORDER}", BotConfig.COLOR_RED_DARK))
    await s.start_hardcore_timer(ctx.channel)

@bot.command(name="botnoitucamhc")
async def cmd_botnoitucamhc(ctx, seconds: int = 15, letter: str = ""):
    s = sessions.get(ctx.channel.id)
    if s.is_active:
        await ctx.send(embed=UIUtils.warn_embed("Bận", "")); return
    if not letter or len(letter) != 1:
        await ctx.send(embed=UIUtils.warn_embed("Thiếu", f"VD: `{BotConfig.PREFIX}botnoitucamhc 15 a`")); return
    seconds = max(5, min(120, seconds))
    banned = letter.lower()
    w = random.choice(EASY_START_LIST)
    s.init_session(GameMode.BOT_VIETNAMESE, start_word=w)
    s.is_hardcore = True
    s.hardcore_time = seconds
    s.is_banned_mode = True
    s.banned_letter = banned
    s.last_player_id = None
    await ctx.send(embed=UIUtils.create_embed("🤖💀🚫 Bot Cấm HC", f"{BotConfig.BORDER}\n\n⏱️ `{seconds}s` ⛔ **`{banned.upper()}`**\n👉 **`{w.upper()}`**\n🌸 **`{w.split()[-1].upper()}`**\n\n{BotConfig.BORDER}", BotConfig.COLOR_RED_DARK))
    await s.start_hardcore_timer(ctx.channel)

@bot.command(name="noitueng", aliases=["noituen"])
async def cmd_noitueng(ctx):
    s = sessions.get(ctx.channel.id)
    if s.is_active:
        await ctx.send(embed=UIUtils.warn_embed("Bận", "")); return
    w = random.choice(ENGLISH_LIST)
    s.init_session(GameMode.PVP_ENGLISH, start_word=w)
    await ctx.send(embed=UIUtils.create_embed("💕 Word Chain PvP", f"{BotConfig.BORDER}\n\n👉 **`{w.upper()}`**\n🌸 **`{w[-1].upper()}`**\n\n{BotConfig.BORDER}"))

@bot.command(name="botnoitueng", aliases=["noituenbot"])
async def cmd_botnoitueng(ctx):
    s = sessions.get(ctx.channel.id)
    if s.is_active:
        await ctx.send(embed=UIUtils.warn_embed("Bận", "")); return
    w = random.choice(ENGLISH_LIST)
    s.init_session(GameMode.BOT_ENGLISH, start_word=w)
    await ctx.send(embed=UIUtils.create_embed("🤖 Solo Bot EN", f"{BotConfig.BORDER}\n\n👉 **`{w.upper()}`**\n🌸 **`{w[-1].upper()}`**\n\n{BotConfig.BORDER}"))

# ====================================================================
# PHẦN 17: GUESS GAMES
# ====================================================================

@bot.command(name="vuatiengviet", aliases=["vuatv"])
async def cmd_vuatv(ctx):
    s = sessions.get(ctx.channel.id)
    if s.is_active:
        await ctx.send(embed=UIUtils.warn_embed("Bận", "")); return
    if not VUA_TIENG_VIET_CANDIDATES:
        await ctx.send("🖤 Không có dữ liệu!"); return
    t = random.choice(VUA_TIENG_VIET_CANDIDATES)
    sc = GameUtils.scramble(t)
    s.init_session(GameMode.VUA_TIENG_VIET, target=t)
    await ctx.send(embed=UIUtils.create_embed("👑 VUA TIẾNG VIỆT", f"{BotConfig.BORDER}\n\n🔀 **`{sc.upper()}`**\n📝 {len(t.split())} âm tiết\n\nGõ đáp án!\n\n{BotConfig.BORDER}", BotConfig.COLOR_GOLD))

@bot.command(name="doanquocgia", aliases=["doanquoc"])
async def cmd_doanqg(ctx):
    s = sessions.get(ctx.channel.id)
    if s.is_active:
        await ctx.send(embed=UIUtils.warn_embed("Bận", "")); return
    if not COUNTRIES_VN_LIST:
        await ctx.send("🖤 Không có dữ liệu!"); return
    c = random.choice(COUNTRIES_VN_LIST)
    m = GameUtils.country_mask(c)
    s.init_session(GameMode.GUESS_COUNTRY, target=c)
    code = COUNTRY_CODES.get(c, "??")
    flag = f"https://flagcdn.com/w320/{code}.png" if code != "??" else None
    await ctx.send(embed=UIUtils.create_embed("🌍 ĐOÁN QUỐC GIA", f"{BotConfig.BORDER}\n\n🔲 `{m}`\n📝 {len(c.split())} chữ\n\nGõ tên quốc gia!\n\n{BotConfig.BORDER}", image_url=flag))

@bot.command(name="doantenphim", aliases=["doanphim"])
async def cmd_doanphim(ctx):
    s = sessions.get(ctx.channel.id)
    if s.is_active:
        await ctx.send(embed=UIUtils.warn_embed("Bận", "")); return
    mv = random.choice(FALLBACK_MOVIES_DATA)
    s.init_session(GameMode.GUESS_MOVIE, target=mv["title"])
    await ctx.send(embed=UIUtils.create_embed("🎬 ĐOÁN PHIM", f"{BotConfig.BORDER}\n\n💡 {mv['clue']}\n\nGõ tên phim!\n\n{BotConfig.BORDER}", BotConfig.COLOR_DEEP_PINK, image_url=mv["image"]))

@bot.command(name="doanemoji", aliases=["emoji"])
async def cmd_doanemoji(ctx):
    s = sessions.get(ctx.channel.id)
    if s.is_active:
        await ctx.send(embed=UIUtils.warn_embed("Bận", "")); return
    ei = random.choice(EMOJI_DATA)
    s.init_session(GameMode.GUESS_EMOJI, target=ei["phrase"])
    await ctx.send(embed=UIUtils.create_embed("🔤 ĐOÁN EMOJI", f"{BotConfig.BORDER}\n\n🎨 {ei['emojis']}\n\nGõ cụm từ!\n\n{BotConfig.BORDER}"))

@bot.command(name="tictactoe", aliases=["caro"])
async def_cmd_tictactoe(ctx):
    await ctx.send(embed=UIUtils.create_embed("❌⭕ Cờ Caro", f"{BotConfig.BORDER}\n\nBạn **X**, Bot **O**.\n\n{BotConfig.BORDER}", BotConfig.COLOR_DEEP_PINK), view=TicTacToeView())

# ====================================================================
# PHẦN 18: MATH COMMANDS
# ====================================================================

@bot.command(name="toan", aliases=["math", "quiztoan"])
async def cmd_toan(ctx, difficulty: str = "normal"):
    if difficulty.lower() not in ("easy", "normal", "hard", "expert"):
        difficulty = "normal"
    d = difficulty.lower()
    q = MathUtils.generate_question(d)
    math_questions[ctx.channel.id] = {"answer": q["answer"], "active": True, "asked_by": ctx.author.id, "difficulty": d}
    de = {"easy": "🟢 Dễ", "normal": "🟡 Thường", "hard": "🔴 Khó", "expert": "💜 Chuyên Gia"}
    desc = (
        f"{BotConfig.BORDER}\n\n"
        f"🧮 **CÂU HỎI:**\n\n"
        f"   ╭───────────────────────╮\n"
        f"   │                       │\n"
        f"   │   {q['question'] + ' = ?':^19s}│\n"
        f"   │                       │\n"
        f"   ╰───────────────────────╯\n\n"
        f"🌸 Gõ số đáp án!\n"
        f"{de[d]} | Phép: **{q['op']}**\n\n"
        f"{BotConfig.BORDER}"
    )
    await ctx.send(embed=UIUtils.math_embed("🧮 Toán Học Hồng Cánh Sen", desc, d))

@bot.command(name="giaitoan", aliases=["solve", "tinh", "calc"])
async def cmd_giaitoan(ctx, *, expression: str = ""):
    if not expression:
        ex = (
            f"{BotConfig.BORDER}\n\n"
            f"🧮 **CÁCH DÙNG:**\n\n"
            f"```\n"
            f"?giaitoan 15 + 27\n"
            f"?giaitoan 100 - 38\n"
            f"?giaitoan 12 × 5\n"
            f"?giaitoan 144 ÷ 12\n"
            f"?giaitoan 5^3\n"
            f"?giaitoan √256\n"
            f"?giaitoan (25+15) × 3 - 10\n"
            f"?giaitoan 25% của 400\n"
            f"```\n\n"
            f"{BotConfig.BORDER}"
        )
        await ctx.send(embed=UIUtils.math_embed("🧮 Hướng Dẫn", ex, "normal"))
        return
    if len(expression) > 200:
        await ctx.send(embed=UIUtils.warn_embed("Dài", "Tối đa 200 ký tự!")); return
    r = MathUtils.solve_expression(expression)
    if r is None:
        await ctx.send(embed=UIUtils.math_embed("❌ Lỗi", f"{BotConfig.BORDER}\n\n❌ Biểu thức không hợp lệ!\n\nGõ `?giaitoan` xem hướng dẫn.\n\n{BotConfig.BORDER}", "hard"))
        return
    if r["result"] is None:
        await ctx.send(embed=UIUtils.math_embed("⚠️", "\n".join(r["steps"]) + f"\n\n{BotConfig.BORDER}", "hard"))
        return
    a = MathUtils.fmt(r["result"])
    await ctx.send(embed=UIUtils.math_embed(f"🧮✨ `{a}` ✨🧮", f"{BotConfig.BORDER}\n\n" + "\n".join(r["steps"]) + f"\n\n🏷️ {r['type']} | 👤 {ctx.author.mention}\n\n{BotConfig.BORDER}", "normal"))

@bot.command(name="bangtoan", aliases=["cuuchuong"])
async def cmd_bangtoan(ctx, number: Optional[int] = None):
    if number is None:
        await ctx.send(embed=UIUtils.math_embed("📊 Bảng Cửu Chương", f"{BotConfig.BORDER}\n\nGõ `?bangtoan [1-20]`\n\n{BotConfig.BORDER}", "easy"))
        return
    if number < 1 or number > 20:
        await ctx.send(embed=UIUtils.warn_embed("Sai", "Chỉ 1-20!")); return
    lines = []
    for i in range(1, 11):
        lines.append(f"  {number:>2} × {i:<2} = {number * i:<4}")
    tbl = "```\n" + "\n".join(lines) + "\n```"
    tips = {2: "Cộng 2 lần!", 4: "Nhân 2 rồi ×2!", 5: "Kết thúc 0 hoặc 5!", 9: "Tổng chữ số = 9!", 10: "Thêm số 0!", 11: "Ghép đôi!"}
    tip = f"💡 {tips.get(number, '')}" if number in tips else ""
    await ctx.send(embed=UIUtils.math_embed(f"📊 Bảng {number}", f"{BotConfig.BORDER}\n\n{tbl}\n\n{tip}\n\n{BotConfig.BORDER}", "easy"))

@bot.command(name="toanhoc", aliases=["menutoan"])
async def cmd_toanhoc(ctx):
    p = BotConfig.PREFIX
    await ctx.send(embed=UIUtils.math_embed("🧮 Menu Toán", f"{BotConfig.BORDER}\n\n"
        f"**HỎI:** `{p}toan [easy/normal/hard/expert]`\n\n"
        f"**GIẢI:**\n"
        f"`{p}giaitoan 15 + 27`\n"
        f"`{p}giaitoan 5^3`\n"
        f"`{p}giaitoan √256`\n"
        f"`{p}giaitoan 25% của 400`\n\n"
        f"**THAM KHẢO:** `{p}bangtoan [số]`\n\n"
        f"{BotConfig.BORDER}", "normal"))

# ====================================================================
# PHẦN 19: GAME MANAGEMENT
# ====================================================================

@bot.command(name="huyvanchoi", aliases=["end", "stop", "cancel"])
async def cmd_huy(ctx):
    s = sessions.get(ctx.channel.id)
    if not s.is_active:
        if ctx.channel.id in math_questions and math_questions[ctx.channel.id].get("active"):
            math_questions[ctx.channel.id]["active"] = False
            del math_questions[ctx.channel.id]
            await ctx.send(embed=UIUtils.ok_embed("Đã Hủy", "🧮 Câu toán bị hủy!")); return
        await ctx.send(embed=UIUtils.warn_embed("Không", "Không có ván nào!")); return
    names = {
        GameMode.PVP_VIETNAMESE: "Nối Từ PvP TV", GameMode.BOT_VIETNAMESE: "Solo Bot TV",
        GameMode.PVP_ENGLISH: "Nối Từ PvP TA", GameMode.BOT_ENGLISH: "Solo Bot TA",
        GameMode.VUA_TIENG_VIET: "Vua TV", GameMode.GUESS_COUNTRY: "Đoán QG",
        GameMode.GUESS_MOVIE: "Đoán Phim", GameMode.GUESS_EMOJI: "Đoán Emoji"
    }
    n = names.get(s.active_mode, "?")
    s.reset()
    await ctx.send(embed=UIUtils.create_embed("⛔ HỦY", f"{BotConfig.BORDER}\n\nĐã hủy: *{n}*\n\n{BotConfig.BORDER}", BotConfig.COLOR_RED_DARK))

@bot.command(name="restart", aliases=["choilai", "lai"])
async def cmd_restart(ctx):
    s = sessions.get(ctx.channel.id)
    if not s.is_active and ctx.channel.id not in math_questions:
        await ctx.send(embed=UIUtils.warn_embed("Không", "Không có ván!")); return
    if ctx.channel.id in math_questions:
        del math_questions[ctx.channel.id]
    old = s.active_mode
    s.reset()
    cmds = {
        GameMode.PVP_VIETNAMESE: cmd_noitu, GameMode.BOT_VIETNAMESE: cmd_botnoitu,
        GameMode.PVP_ENGLISH: cmd_noitueng, GameMode.BOT_ENGLISH: cmd_botnoitueng,
        GameMode.VUA_TIENG_VIET: cmd_vuatv, GameMode.GUESS_COUNTRY: cmd_doanqg,
        GameMode.GUESS_MOVIE: cmd_doanphim, GameMode.GUESS_EMOJI: cmd_doanemoji
    }
    fn = cmds.get(old)
    if fn:
        await fn(ctx)
    else:
        await ctx.send(embed=UIUtils.warn_embed("Lỗi", "Bắt đầu thủ công!"))

@bot.command(name="nghia", aliases=["tra", "tudien"])
async def cmd_nghia(ctx, *, word: str = ""):
    if not word:
        await ctx.send(embed=UIUtils.warn_embed("Thiếu", f"VD: `{BotConfig.PREFIX}nghia bình yên`")); return
    w = word.strip().lower()
    found = []
    if w in COMBINED_VIETNAMESE_DICTIONARY:
        found.append("🇻🇳 Có trong từ điển TV (2 âm tiết)")
    if w in RAW_VIETNAMESE_DICT:
        found.append("🇻🇳 Có trong TV gốc")
    if w in ENGLISH_DICT:
        found.append("🇬🇧 Có trong TA")
    if w in COUNTRIES_VN_DICT:
        c = COUNTRY_CODES.get(w, "??")
        found.append(f"🌍 Quốc gia (Mã: `{c.upper()}`)")
    if w in COMBINED_VIETNAMESE_DICTIONARY:
        ls = w.split()[-1]
        nw = [x for x in VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.get(ls, []) if x != w]
        if nw:
            s = random.sample(nw, min(5, len(nw)))
            found.append(f"🌸 Nối: {', '.join(f'`{x}`' for x in s)}")
    if not found:
        await ctx.send(embed=UIUtils.create_embed("📖 Tra Cứu", f"{BotConfig.BORDER}\n\n❌ `{w}` không tìm thấy.\n💡 `/themtu {w}` (Owner)\n\n{BotConfig.BORDER}", BotConfig.COLOR_RED_DARK))
    else:
        await ctx.send(embed=UIUtils.create_embed("📖 Tra Cứu", f"{BotConfig.BORDER}\n\n🔍 `{w.upper()}`\n\n" + "\n".join(found) + f"\n\n{BotConfig.BORDER}"))

# ====================================================================
# PHẦN 20: BOT RESPONDER
# ====================================================================

def bot_next_vi(last_syl: str, used: Set[str], banned: str = "") -> Optional[str]:
    cands = [w for w in VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.get(last_syl, []) if w not in used]
    if banned:
        cands = [w for w in cands if banned not in GameUtils.remove_diacritics(w)]
    return random.choice(cands) if cands else None

def bot_next_en(last_letter: str, used: Set[str]) -> Optional[str]:
    cands = [w for w in ENGLISH_INDEX_BY_FIRST_LETTER.get(last_letter, []) if w not in used]
    return random.choice(cands) if cands else None

# ====================================================================
# PHẦN 21: ON_MESSAGE
# ====================================================================

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or message.author.system:
        return
    content = message.content.strip()
    if not content:
        return

    # ── AFK ──
    if message.guild:
        gid = message.guild.id
        if gid in afk_users:
            for uid_s, ad in list(afk_users[gid].items()):
                if int(uid_s) in [m.id for m in message.mentions]:
                    u = message.guild.get_member(int(uid_s))
                    if u:
                        await message.channel.send(f"💤 {u.mention} đang AFK: *{ad.get('reason', '')}*")
                if int(uid_s) == message.author.id:
                    del afk_users[gid][uid_s]
                    try:
                        if message.author.display_name.startswith("[AFK] "):
                            await message.author.edit(nick=message.author.display_name[5:])
                    except Exception:
                        pass

    # ── COUNTING ──
    if message.channel.id in counting_channels:
        cd = counting_channels[message.channel.id]
        try:
            num = int(content)
        except ValueError:
            await bot.process_commands(message)
            return
        exp = cd["current"] + 1
        if num == exp and cd["last_user"] != message.author.id:
            cd["current"] = num
            cd["last_user"] = message.author.id
            if num > cd["high_score"]:
                cd["high_score"] = num
                if num % 100 == 0:
                    await message.add_reaction("🎉")
            await message.add_reaction("✅")
        else:
            oh = cd["high_score"]
            cd["current"] = 0
            cd["last_user"] = 0
            await message.channel.send(embed=UIUtils.create_embed("💀 SAI!", f"{BotConfig.BORDER}\n\n❌ `{num}` | Cần: `{exp}`\n🏆 HS: `{oh}`\n\nBắt đầu từ **1**!\n\n{BotConfig.BORDER}", BotConfig.COLOR_RED_DARK))
        return

    # ── MATH ──
    if message.channel.id in math_questions:
        mq = math_questions[message.channel.id]
        if mq.get("active"):
            try:
                ua = float(content.replace(",", "."))
                ca = float(mq["answer"])
                if abs(ua - ca) < 0.0001:
                    mq["active"] = False
                    del math_questions[message.channel.id]
                    d = mq.get("difficulty", "normal")
                    dn = {"easy": "Dễ", "normal": "Thường", "hard": "Khó", "expert": "Chuyên Gia"}
                    de = {"easy": "🟢", "normal": "🟡", "hard": "🔴", "expert": "💜"}
                    ad = MathUtils.fmt(ca)
                    desc = (
                        f"{BotConfig.BORDER}\n\n"
                        f"🌸 **ĐÚNG!** 🌸\n\n"
                        f"✅ **`{ad}`**\n"
                        f"🏆 {message.author.mention}\n"
                        f"{de.get(d, '🟡')} {dn.get(d, 'Thường')}\n\n"
                        f"{BotConfig.BORDER}"
                    )
                    await message.channel.send(embed=UIUtils.math_embed("🧮✨ ĐÚNG RỒI! ✨🧮", desc, d))
                    return
            except ValueError:
                pass

    # ── GAME SESSIONS ──
    s = sessions.get(message.channel.id)
    if not s.is_active:
        await bot.process_commands(message)
        return

    mode = s.active_mode

    # ── NỐI TỪ TV ──
    if mode in (GameMode.PVP_VIETNAMESE, GameMode.BOT_VIETNAMESE):
        uw = content.lower().strip()
        if not uw:
            await bot.process_commands(message)
            return
        if uw in s.used_words_history:
            await message.channel.send(embed=UIUtils.warn_embed("Đã dùng", BotConfig.MSG_ERR_ALREADY_USED))
            await bot.process_commands(message)
            return
        syl = uw.split()
        if len(syl) != 2:
            await message.channel.send(embed=UIUtils.invalid_embed("Phải đúng 2 âm tiết!"))
            await bot.process_commands(message)
            return
        ls = s.current_word.split()[-1]
        if GameUtils.remove_diacritics(syl[0]) != GameUtils.remove_diacritics(ls):
            await message.channel.send(embed=UIUtils.invalid_embed(f"Phải bắt đầu bằng **`{ls.upper()}`**"))
            await bot.process_commands(message)
            return
        if s.is_banned_mode and s.banned_letter:
            if s.banned_letter in GameUtils.remove_diacritics(uw):
                await message.channel.send(embed=UIUtils.invalid_embed(f"Chứa chữ cấm **`{s.banned_letter.upper()}`**!"))
                await bot.process_commands(message)
                return
        if uw not in COMBINED_VIETNAMESE_DICTIONARY:
            await message.channel.send(embed=UIUtils.invalid_embed(f"`{uw}` không có trong từ điển!"))
            await bot.process_commands(message)
            return
        s.used_words_history.add(uw)
        s.current_word = uw
        s.turn_counter += 1
        s.last_player_id = message.author.id
        ns = uw.split()[-1]
        if s.is_hardcore:
            await s.start_hardcore_timer(message.channel)
        if mode == GameMode.BOT_VIETNAMESE:
            bw = bot_next_vi(ns, s.used_words_history, s.banned_letter if s.is_banned_mode else "")
            if bw:
                s.used_words_history.add(bw)
                s.current_word = bw
                s.turn_counter += 1
                bn = bw.split()[-1]
                await message.channel.send(embed=UIUtils.create_embed("💕 Nối Từ", f"{BotConfig.BORDER}\n\n✅ {message.author.mention}: **`{uw.upper()}`**\n🤖 Bot: **`{bw.upper()}`**\n🌸 **`{bn.upper()}`**\n📝 Lượt: **{s.turn_counter}**\n\n{BotConfig.BORDER}"))
            else:
                s.is_active = False
                await message.channel.send(embed=UIUtils.create_embed("🏆 THẮNG!", f"{BotConfig.BORDER}\n\n🎉 {message.author.mention} thắng Bot!\n✅ **`{uw.upper()}`**\n🤖 Bot không tìm được từ!\n📝 Lượt: **{s.turn_counter}**\n\n{BotConfig.BORDER}", BotConfig.COLOR_GOLD))
                s.reset()
        else:
            await message.channel.send(embed=UIUtils.create_embed("💕 Nối Từ PvP", f"{BotConfig.BORDER}\n\n✅ {message.author.mention}: **`{uw.upper()}`**\n🌸 **`{ns.upper()}`**\n📝 Lượt: **{s.turn_counter}**\n\n{BotConfig.BORDER}"))
        await bot.process_commands(message)
        return

    # ── NỐI TỪ EN ──
    if mode in (GameMode.PVP_ENGLISH, GameMode.BOT_ENGLISH):
        uw = content.lower().strip()
        if not uw or not uw.isalpha():
            await bot.process_commands(message)
            return
        if uw in s.used_words_history:
            await message.channel.send(embed=UIUtils.warn_embed("Đã dùng", "Already used!"))
            await bot.process_commands(message)
            return
        if uw[0] != s.current_word[-1]:
            await message.channel.send(embed=UIUtils.invalid_embed(f"Must start with **`{s.current_word[-1].upper()}`**!"))
            await bot.process_commands(message)
            return
        if uw not in ENGLISH_DICT:
            await message.channel.send(embed=UIUtils.invalid_embed(f"`{uw}` not in dictionary!"))
            await bot.process_commands(message)
            return
        s.used_words_history.add(uw)
        s.current_word = uw
        s.turn_counter += 1
        s.last_player_id = message.author.id
        nl = uw[-1]
        if s.is_hardcore:
            await s.start_hardcore_timer(message.channel)
        if mode == GameMode.BOT_ENGLISH:
            bw = bot_next_en(nl, s.used_words_history)
            if bw:
                s.used_words_history.add(bw)
                s.current_word = bw
                s.turn_counter += 1
                await message.channel.send(embed=UIUtils.create_embed("💕 Word Chain", f"{BotConfig.BORDER}\n\n✅ {message.author.mention}: **`{uw.upper()}`**\n🤖 Bot: **`{bw.upper()}`**\n🌸 **`{bw[-1].upper()}`**\n📝 Turn: **{s.turn_counter}**\n\n{BotConfig.BORDER}"))
            else:
                s.is_active = False
                await message.channel.send(embed=UIUtils.create_embed("🏆 YOU WIN!", f"{BotConfig.BORDER}\n\n🎉 {message.author.mention} wins!\n✅ **`{uw.upper()}`**\n📝 Turns: **{s.turn_counter}**\n\n{BotConfig.BORDER}", BotConfig.COLOR_GOLD))
                s.reset()
        else:
            await message.channel.send(embed=UIUtils.create_embed("💕 Word Chain PvP", f"{BotConfig.BORDER}\n\n✅ {message.author.mention}: **`{uw.upper()}`**\n🌸 **`{nl.upper()}`**\n📝 Turn: **{s.turn_counter}**\n\n{BotConfig.BORDER}"))
        await bot.process_commands(message)
        return

    # ── VUA TV ──
    if mode == GameMode.VUA_TIENG_VIET:
        if content.lower().strip() == s.scrambled_target:
            s.is_active = False
            await message.channel.send(embed=UIUtils.create_embed("👑 ĐÚNG!", f"{BotConfig.BORDER}\n\n✅ **`{s.scrambled_target.upper()}`**\n🏆 {message.author.mention}\n\n{BotConfig.BORDER}", BotConfig.COLOR_GOLD))
            s.reset()
        await bot.process_commands(message)
        return

    # ── ĐOÁN QG ──
    if mode == GameMode.GUESS_COUNTRY:
        if GameUtils.remove_diacritics(content.lower().strip()) == GameUtils.remove_diacritics(s.secret_country):
            s.is_active = False
            code = COUNTRY_CODES.get(s.secret_country, "??")
            flag = f"https://flagcdn.com/w320/{code}.png" if code != "??" else None
            await message.channel.send(embed=UIUtils.create_embed("🌍 ĐÚNG!", f"{BotConfig.BORDER}\n\n✅ **`{s.secret_country.upper()}`**\n🏆 {message.author.mention}\n\n{BotConfig.BORDER}", BotConfig.COLOR_GOLD, image_url=flag))
            s.reset()
        await bot.process_commands(message)
        return

    # ── ĐOÁN PHIM ──
    if mode == GameMode.GUESS_MOVIE:
        if GameUtils.remove_diacritics(content.lower().strip()) == GameUtils.remove_diacritics(s.secret_target):
            s.is_active = False
            mv = next((m for m in FALLBACK_MOVIES_DATA if m["title"] == s.secret_target), None)
            img = mv["image"] if mv else None
            await message.channel.send(embed=UIUtils.create_embed("🎬 ĐÚNG!", f"{BotConfig.BORDER}\n\n✅ **`{s.secret_target.upper()}`**\n🏆 {message.author.mention}\n\n{BotConfig.BORDER}", BotConfig.COLOR_GOLD, image_url=img))
            s.reset()
        await bot.process_commands(message)
        return

    # ── ĐOÁN EMOJI ──
    if mode == GameMode.GUESS_EMOJI:
        if GameUtils.remove_diacritics(content.lower().strip()) == GameUtils.remove_diacritics(s.secret_target):
            s.is_active = False
            await message.channel.send(embed=UIUtils.create_embed("🔤 ĐÚNG!", f"{BotConfig.BORDER}\n\n✅ **`{s.secret_target.upper()}`**\n🏆 {message.author.mention}\n\n{BotConfig.BORDER}", BotConfig.COLOR_GOLD))
            s.reset()
        await bot.process_commands(message)
        return

    await bot.process_commands(message)

# ====================================================================
# PHẦN 22: CHẠY BOT + DIAGNOSTIC
# ====================================================================

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        logger.error("❌ KHÔNG TÌM THẤY DISCORD_TOKEN!")
        sys.exit(1)

    logger.info("━━━━━━━━━━ DIAGNOSTIC ━━━━━━━━━━")
    errors = []

    try:
        logger.info(f"  ✅ TV dict: {len(COMBINED_VIETNAMESE_DICTIONARY)} từ")
    except Exception as e:
        logger.error(f"  ❌ TV dict: {e}")
        errors.append(str(e))

    try:
        logger.info(f"  ✅ EN dict: {len(ENGLISH_DICT)} từ")
    except Exception as e:
        logger.error(f"  ❌ EN dict: {e}")
        errors.append(str(e))

    try:
        q = MathUtils.generate_question("easy")
        logger.info(f"  ✅ Math: {q['question']} = {q['answer']}")
    except Exception as e:
        logger.error(f"  ❌ Math generate: {e}")
        errors.append(str(e))

    try:
        r = MathUtils.solve_expression("5 + 3")
        logger.info(f"  ✅ Math solve: {r}")
    except Exception as e:
        logger.error(f"  ❌ Math solve: {e}")
        errors.append(str(e))

    try:
        logger.info(f"  ✅ Flask port: {BotConfig.WEB_SERVER_PORT}")
    except Exception as e:
        logger.error(f"  ❌ Flask: {e}")
        errors.append(str(e))

    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if errors:
        logger.critical(f"❌ CÓ {len(errors)} LỖI! Sửa trước khi chạy.")
        for e in errors:
            logger.critical(f"  → {e}")
        sys.exit(1)

    logger.info(f"🖤🌸 Khởi động Sakura v{BotConfig.VERSION}...")
    try:
        bot.run(TOKEN, log_handler=None)
    except discord.LoginFailure:
        logger.critical("❌ TOKEN SAI! Kiểm tra DISCORD_TOKEN.")
    except Exception as e:
        logger.critical(f"❌ CRASH: {type(e).__name__}: {e}")
        traceback.print_exc()
