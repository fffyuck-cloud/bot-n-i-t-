# ====================================================================================================
# ██████╗ ██╗    █████╗  ██████╗██╗  ██╗    ██████╗ ██╗███╗    ██╗██╗  ██╗    ██████╗  ██████╗ ████████╗
# ██╔══██╗██║    ██╔══██╗██╔════╝██║ ██╔╝    ██╔══██╗██║████╗   ██║██║ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
# ██████╔╝██║    ███████║██║     █████╔╝     ██████╔╝██║██╔██╗  ██║█████╔╝     ██████╔╝██║   ██║   ██║   
# ██╔══██╗██║    ██╔══██║██║     ██╔═██╗     ██╔═══╝ ██║██║╚██╗ ██║██╔═██╗     ██╔══██╗██║   ██║   ██║   
# ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗    ██║     ██║██║ ╚████║██║  ██╗    ██████╔╝╚██████╔╝   ██║   
# ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝    ╚═════╝  ╚═╝    ╚═╝   
#                                                                                                   
# PURE FUN ENTERPRISE EDITION - FULL FILE I/O & MULTI-DICTIONARY INTEGRATED (v2.1.5)
# ====================================================================================================

import os
import sys
import random
import logging
import asyncio
import threading
from datetime import datetime
from typing import Set, List, Dict, Optional, Any, Union
from flask import Flask, jsonify
import discord
from discord.ext import commands

# ====================================================================================================
# PHẦN 1: CẤU HÌNH HỆ THỐNG & DỮ LIỆU DỰ PHÒNG
# ====================================================================================================

class BotConfig:
    VERSION: str = "2.1.5 Full Integrated Enterprise"
    DEVELOPER: str = "Black & Pink Studio"
    PREFIX: str = "?"
    
    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = 8080
    
    FILE_VIETNAMESE_DICT: str = "tu_dien.txt"
    FILE_ENGLISH_DICT: str = "tu dien tieng anh.txt"
    FILE_COUNTRIES_DICT: str = "quoc gia vn.txt"
    
    COLOR_DEFAULT: int = 0xFF69B4     # Hot Pink
    COLOR_SUCCESS: int = 0x2ECC71     # Green
    COLOR_WARNING: int = 0xF1C40F     # Yellow
    COLOR_ERROR: int = 0xE74C3C       # Red
    COLOR_BLACK: int = 0x000000       # Black
    
    MSG_ERR_ALREADY_USED: str = "❌ Từ này đã được sử dụng trước đó trong ván này!"

DEFAULT_VIETNAMESE_FALLBACK: Set[str] = {
    "học tập", "tập thể", "thể thao", "áo quần", "nước non", "non sông", "sông núi", "núi cao", "cao cấp", "cấp tốc",
    "chiếu tướng", "tướng quân", "quân đội", "đội ngũ", "ngũ cốc", "cốc sấy", "sấy khô", "khô khan", "khan hiếm",
    "yêu thương", "thương nhớ", "nhớ mong", "mong mỏi", "mỏi mệt", "mệt mỏi", "thời gian", "gian nan", "nan giải",
    "giải quyết", "quyết tâm", "tâm hồn", "hồn nhiên", "nhiên liệu", "liệu định", "định hướng", "hướng dẫn", "dẫn dắt",
    "đất nước", "nước nhà", "hòa bình", "bình yên", "yên vui", "vui vẻ", "vẻ vang", "vang dội", "dội ngược", "ngược xuôi"
}

DEFAULT_ENGLISH_FALLBACK: Set[str] = {
    "apple", "elephant", "tiger", "rabbit", "turtle", "eagle", "room", "mouse", "engine",
    "nest", "train", "night", "rose", "ear", "toe", "egg", "goal", "lemon", "nut", "rest"
}

DEFAULT_COUNTRIES_FALLBACK: Set[str] = {
    "việt nam", "nhật bản", "hàn quốc", "pháp", "mỹ", "anh", "đức", "ý", "nga", "trung quốc", 
    "thái lan", "lào", "campuchia", "singapore", "malaysia", "indonesia", "philippines", "ấn độ", "canada", "úc"
}

# ====================================================================================================
# PHẦN 2: HỆ THỐNG LOGGING & WEB SERVER (KEEP-ALIVE)
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
        logger_instance = logging.getLogger("EnterpriseBot")
        logger_instance.setLevel(logging.INFO)
        logger_instance.addHandler(console_handler)
        return logger_instance

logger = LoggerSetup.initialize_logger()

keep_alive_app = Flask("EnterpriseKeepAlive")

@keep_alive_app.route('/')
def route_home() -> str:
    return "<h1>Black & Pink Pure Fun Bot - Enterprise Edition</h1><p>Status: <strong>ONLINE</strong></p>"

def launch_web_server() -> None:
    try:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        keep_alive_app.run(host=BotConfig.WEB_SERVER_HOST, port=BotConfig.WEB_SERVER_PORT, debug=False, use_reloader=False, threaded=True)
    except Exception as server_err:
        logger.error(f"Lỗi Flask Server: {server_err}")

threading.Thread(target=launch_web_server, daemon=True).start()

# ====================================================================================================
# PHẦN 3: HỆ THỐNG QUẢN LÝ FILE DỮ LIỆU (DATA MANAGER)
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
                logger.info(f"Đã nạp {len(words)} mục từ file [{filepath}].")
            except Exception as err:
                logger.error(f"Lỗi đọc file {filepath}: {err}")
        else:
            logger.warning(f"Không tìm thấy file [{filepath}]. Đang tạo file mới với dữ liệu dự phòng.")
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

# Nạp toàn bộ dữ liệu từ các file tương ứng
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
# PHẦN 4: QUẢN LÝ PHIÊN CHƠI (SESSION ARCHITECTURE)
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
USER_DATA: Dict[int, Dict[str, Any]] = {}

def get_user_data(user_id: int) -> Dict[str, Any]:
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {"xp": 0, "level": 1}
    return USER_DATA[user_id]

# ====================================================================================================
# PHẦN 5: GIAO DIỆN & TIỆN ÍCH UI
# ====================================================================================================

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
    def create_embed(title: str, description: str, color: int = BotConfig.COLOR_DEFAULT) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now())
        embed.set_footer(text="Vườn hoa Đen Hồng 🖤💗", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_warning_embed(title: str, warning_msg: str) -> discord.Embed:
        return discord.Embed(title=f"⚠️ {title}", description=warning_msg, color=BotConfig.COLOR_WARNING, timestamp=datetime.now())

    @staticmethod
    def build_invalid_word_embed(reason: str) -> discord.Embed:
        description = (
            f"⚠️ **Từ bạn vừa nhập không hợp lệ!**\n\n"
            f"📌 **Nguyên nhân:** {reason}\n"
            f"🌸 *Dùng lệnh `{BotConfig.PREFIX}themtu [từ]` để bổ sung ngay lập tức vào file từ điển!*"
        )
        embed = discord.Embed(title="❌💗 [ TỪ KHÔNG HỢP LỆ ] 💗❌", description=description, color=BotConfig.COLOR_ERROR, timestamp=datetime.now())
        embed.set_footer(text="Hệ thống kiểm duyệt Black & Pink", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_success_embed(title: str, success_msg: str) -> discord.Embed:
        return discord.Embed(title=f"✨💗 [ {title.upper()} ] 💗✨", description=success_msg, color=0xFF69B4, timestamp=datetime.now())

    @staticmethod
    def build_help_embed() -> discord.Embed:
        description = (
            f"💬 **Word Chain Ultimate Bot**\n"
            f"Hỗ trợ nối từ Tiếng Việt & Tiếng Anh đọc file tự động.\n\n"
            f"🇻🇳💗 **[ NỐI TỪ TIẾNG VIỆT ]** 💗🇻🇳\n"
            f"🌸 `{BotConfig.PREFIX}noitu` → PvP chung kênh\n"
            f"🖤 `{BotConfig.PREFIX}botnoitu` → Solo với Bot TV\n\n"
            f"🇬🇧💗 **[ NỐI TỪ TIẾNG ANH ]** 🇬🇧\n"
            f"🌸 `{BotConfig.PREFIX}noitueng` | `{BotConfig.PREFIX}botnoitueng`\n\n"
            f"👑💗 **[ TRÒ CHƠI KHÁC ]** 👑\n"
            f"🌸 `{BotConfig.PREFIX}vuatiengviet` | `{BotConfig.PREFIX}doanquocgia`\n\n"
            f"⚙️💗 **[ QUẢN LÝ TỪ ĐIỂN & HỆ THỐNG ]** ⚙️\n"
            f"🌸 `{BotConfig.PREFIX}themtu [từ]` → Thêm từ vào file từ điển\n"
            f"🖤 `{BotConfig.PREFIX}nghia [từ]` → Tra cứu từ vựng\n"
            f"🌸 `{BotConfig.PREFIX}huynoitu` | `{BotConfig.PREFIX}rank` | `{BotConfig.PREFIX}daily`"
        )
        return discord.Embed(title="✦ HỆ THỐNG TRỢ GIÚP NỐI TỪ ✦", description=description, color=0xFF69B4, timestamp=datetime.now())

# ====================================================================================================
# PHẦN 6: KHỞI TẠO BOT & CÁC LỆNH
# ====================================================================================================

bot_intents = discord.Intents.default()
bot_intents.message_content = True
bot_intents.guilds = True
bot_intents.messages = True

bot = commands.Bot(command_prefix=BotConfig.PREFIX, intents=bot_intents, help_command=None, case_insensitive=True)

@bot.event
async def on_ready() -> None:
    logger.info(f"✅ Bot đã đăng nhập: {bot.user}")
    activity = discord.Activity(type=discord.ActivityType.playing, name=f"{BotConfig.PREFIX}help | File I/O Active")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_command_error(ctx: commands.Context, error: Exception) -> None:
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=UIUtils.create_embed("⚠️ Thiếu Thông Tin", f"Vui lòng gõ `{BotConfig.PREFIX}help` để xem hướng dẫn.", BotConfig.COLOR_WARNING))
    else:
        logger.error(f"Lỗi lệnh: {error}")

@bot.command(name="ping")
async def sys_ping(ctx: commands.Context) -> None:
    await ctx.send(embed=UIUtils.create_embed("🏓 Pong!", f"Độ trễ: **{round(bot.latency * 1000)}ms**", BotConfig.COLOR_SUCCESS))

@bot.command(name="about")
async def sys_about(ctx: commands.Context) -> None:
    desc = f"🤖 **Black & PiNk ({BotConfig.VERSION})**\n• Từ điển Tiếng Việt: {len(COMBINED_VIETNAMESE_DICTIONARY):,} từ\n• Từ điển Tiếng Anh: {len(ENGLISH_DICT):,} từ\n• Danh sách Quốc Gia: {len(COUNTRIES_VN_DICT):,} nước"
    await ctx.send(embed=UIUtils.create_embed("🖤💗 Về Hệ Thống", desc, BotConfig.COLOR_DEFAULT))

@bot.command(name="help", aliases=["menu"])
async def sys_help(ctx: commands.Context) -> None:
    await ctx.send(embed=UIUtils.build_help_embed())

@bot.command(name="themtu", aliases=["addword"])
async def cmd_themtu(ctx: commands.Context, *, word: str = "") -> None:
    if not word:
        await ctx.send(embed=UIUtils.build_warning_embed("Thiếu từ", f"Vui lòng nhập từ cần thêm.\nVí dụ: `{BotConfig.PREFIX}themtu chiếu tướng`"))
        return
    
    clean_w = word.strip().lower()
    syl_parts = clean_w.split()
    
    if len(syl_parts) == 2:
        if clean_w in COMBINED_VIETNAMESE_DICTIONARY:
            await ctx.send(embed=UIUtils.build_warning_embed("Đã tồn tại", f"Từ **`{clean_w.upper()}`** đã có sẵn trong từ điển Tiếng Việt!"))
            return
        
        COMBINED_VIETNAMESE_DICTIONARY.add(clean_w)
        COMBINED_VIETNAMESE_LIST.append(clean_w)
        VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.setdefault(syl_parts[0], []).append(clean_w)
        DataManager.append_word_to_file(BotConfig.FILE_VIETNAMESE_DICT, clean_w)
        
        await ctx.send(embed=UIUtils.build_success_embed("Thêm từ thành công", f"Đã lưu từ **`{clean_w.upper()}`** vào file `{BotConfig.FILE_VIETNAMESE_DICT}` và cập nhật RAM thành công!"))
    elif len(syl_parts) == 1 and clean_w.isalpha():
        if clean_w in ENGLISH_DICT:
            await ctx.send(embed=UIUtils.build_warning_embed("Đã tồn tại", f"Word **`{clean_w.upper()}`** already exists!"))
            return
        
        ENGLISH_DICT.add(clean_w)
        ENGLISH_LIST.append(clean_w)
        ENGLISH_INDEX_BY_FIRST_LETTER.setdefault(clean_w[0], []).append(clean_w)
        DataManager.append_word_to_file(BotConfig.FILE_ENGLISH_DICT, clean_w)
        
        await ctx.send(embed=UIUtils.build_success_embed("Thêm từ thành công", f"Đã lưu từ tiếng Anh **`{clean_w.upper()}`** vào file và RAM!"))
    else:
        await ctx.send(embed=UIUtils.build_invalid_word_embed("Từ tiếng Việt phải gồm đúng 2 tiếng (ví dụ: `chiếu tướng`)!"))

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
    await ctx.send(embed=UIUtils.create_embed("🌍 Đoán Quốc Gia", f"Gợi ý:\n\n## 🗺️ {masked}"))

@bot.command(name="huynoitu", aliases=["huygame"])
async def cmd_huynoitu(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if not session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Không có ván chơi", "Hiện không có ván nối từ nào đang diễn ra."))
        return
    session.reset()
    await ctx.send(embed=UIUtils.create_embed("🖤 Đã hủy phiên chơi", "Phiên nối từ tại kênh này đã được kết thúc thành công.", BotConfig.COLOR_BLACK))

@bot.command(name="nghia")
async def cmd_nghia(ctx: commands.Context, *, word: str = "") -> None:
    if not word:
        await ctx.send(embed=UIUtils.build_warning_embed("Thiếu từ", "Vui lòng nhập từ cần tra."))
        return
    clean_w = word.strip().lower()
    found = clean_w in COMBINED_VIETNAMESE_DICTIONARY or clean_w in ENGLISH_DICT or clean_w in COUNTRIES_VN_DICT
    if found:
        await ctx.send(embed=UIUtils.create_embed("📖 Tra cứu", f"Từ **`{clean_w.upper()}`** CÓ TRONG hệ thống dữ liệu.", BotConfig.COLOR_SUCCESS))
    else:
        await ctx.send(embed=UIUtils.create_embed("📖 Tra cứu", f"Không tìm thấy từ **`{clean_w.upper()}`**. Bạn có thể dùng lệnh `{BotConfig.PREFIX}themtu {clean_w}` để thêm vào file!", BotConfig.COLOR_WARNING))

@bot.command(name="rank", aliases=["top"])
async def cmd_rank(ctx: commands.Context) -> None:
    user_data = get_user_data(ctx.author.id)
    await ctx.send(embed=UIUtils.create_embed("🏆 Bảng Xếp Hạng", f"👤 **{ctx.author.name}**\n• Cấp độ: {user_data['level']}\n• Điểm XP: {user_data['xp']}"))

@bot.command(name="daily")
async def cmd_daily(ctx: commands.Context) -> None:
    user_data = get_user_data(ctx.author.id)
    user_data['xp'] += 50
    await ctx.send(embed=UIUtils.create_embed("🎁 Điểm Danh", "Bạn nhận được **50 XP** miễn phí!", BotConfig.COLOR_SUCCESS))

# ====================================================================================================
# PHẦN 7: XỬ LÝ SỰ KIỆN TRÒ CHƠI QUA TIN NHẮN
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
            get_user_data(message.author.id)['xp'] += 20
            await message.channel.send(embed=UIUtils.create_embed("🏆 Chiến Thắng", f"🎉 {message.author.mention} đã giải đúng: **`{target.upper()}`**", BotConfig.COLOR_SUCCESS))
        return

    # 2. Đoán Quốc Gia
    if session.active_mode == GameMode.GUESS_COUNTRY:
        if content == session.secret_country.lower():
            target = session.secret_country
            session.reset()
            get_user_data(message.author.id)['xp'] += 20
            await message.channel.send(embed=UIUtils.create_embed("🏆 Chiến Thắng", f"🎉 {message.author.mention} đoán đúng quốc gia: **`{target.upper()}`**", BotConfig.COLOR_SUCCESS))
        return

    # 3. Nối Từ Tiếng Việt
    if session.active_mode in [GameMode.PVP_VIETNAMESE, GameMode.BOT_VIETNAMESE]:
        parts = content.split()
        if len(parts) != 2:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed("Từ phải gồm đúng 2 tiếng!"))
            return
        
        if content not in COMBINED_VIETNAMESE_DICTIONARY:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed("Từ này chưa có trong file từ điển tiếng Việt!"))
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
        get_user_data(message.author.id)['xp'] += 10
        
        next_syl = parts[-1]
        
        if session.active_mode == GameMode.PVP_VIETNAMESE:
            await message.channel.send(embed=UIUtils.create_embed("✨ Nối từ thành công!", f"Từ hợp lệ: **`{content.upper()}`**\nÂm tiếp theo: **`{next_syl.upper()}`**", BotConfig.COLOR_SUCCESS))
        elif session.active_mode == GameMode.BOT_VIETNAMESE:
            candidates = VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.get(next_syl, [])
            valid_candidates = [w for w in candidates if w not in session.used_words_history]
            
            if not valid_candidates:
                session.reset()
                await message.channel.send(embed=UIUtils.create_embed("🏆 Người Chơi Thắng Bot", f"🎉 {message.author.mention} đã đánh bại Bot vì hết từ nối bắt đầu bằng: **`{next_syl.upper()}`**", BotConfig.COLOR_SUCCESS))
                return
            
            bot_word = random.choice(valid_candidates)
            session.used_words_history.add(bot_word)
            session.current_word = bot_word
            bot_syllables = bot_word.split()
            next_bot_syl = bot_syllables[-1] if bot_syllables else bot_word
            
            desc = f"✨ Từ của bạn: **`{content.upper()}`**\n🤖 **Bot phản đòn:** ## {bot_word.upper()}\n🌸 Âm tiết tiếp theo cho bạn: **`{next_bot_syl.upper()}`**"
            await message.channel.send(embed=UIUtils.create_embed("✨💗 Lượt Đấu Thành Công", desc, BotConfig.COLOR_SUCCESS))
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
        get_user_data(message.author.id)['xp'] += 10
        
        next_letter = content[-1]
        
        if session.active_mode == GameMode.PVP_ENGLISH:
            await message.channel.send(embed=UIUtils.create_embed("✨ Word chain success!", f"Valid word: **`{content.upper()}`**\nNext letter: **`{next_letter.upper()}`**", BotConfig.COLOR_SUCCESS))
        elif session.active_mode == GameMode.BOT_ENGLISH:
            candidates = ENGLISH_INDEX_BY_FIRST_LETTER.get(next_letter, [])
            valid_candidates = [w for w in candidates if w not in session.used_words_history]
            
            if not valid_candidates:
                session.reset()
                await message.channel.send(embed=UIUtils.create_embed("🏆 Player Defeated Bot", f"🎉 {message.author.mention} defeated the Bot!", BotConfig.COLOR_SUCCESS))
                return
            
            bot_word = random.choice(valid_candidates)
            session.used_words_history.add(bot_word)
            session.current_word = bot_word
            next_bot_letter = bot_word[-1]
            
            await message.channel.send(embed=UIUtils.create_embed("✨ Lượt đấu thành công", f"Từ của bạn: **`{content.upper()}`**\n🤖 **Bot phản đòn:** ## {bot_word.upper()}\nKý tự tiếp theo: **`{next_bot_letter.upper()}`**", BotConfig.COLOR_SUCCESS))
        return

# ====================================================================================================
# PHẦN 8: KHỞI CHẠY BOT
# ====================================================================================================

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.warning("Không tìm thấy biến môi trường DISCORD_TOKEN.")
    else:
        bot.run(token)
