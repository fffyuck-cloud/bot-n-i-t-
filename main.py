# ====================================================================================================
# ██████╗ ██╗     █████╗  ██████╗██╗  ██╗    ██████╗ ██╗███╗   ██╗██╗  ██╗    ██████╗  ██████╗ ████████╗
# ██╔══██╗██║    ██╔══██╗██╔════╝██║ ██╔╝    ██╔══██╗██║████╗  ██║██║ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
# ██████╔╝██║    ███████║██║     █████╔╝     ██████╔╝██║██╔██╗ ██║█████╔╝     ██████╔╝██║   ██║   ██║   
# ██╔══██╗██║    ██╔══██║██║     ██╔═██╗     ██╔═══╝ ██║██║╚██╗██║██╔═██╗     ██╔══██╗██║   ██║   ██║   
# ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗    ██║     ██║██║ ╚████║██║  ██╗    ██████╔╝╚██████╔╝   ██║   
# ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝   
#                                                                                                    
# PURE FUN ENTERPRISE EDITION - ULTIMATE STRUCTURE (v2.1.1 - FIXED & OPTIMIZED)
# ====================================================================================================

import os
import sys
import random
import logging
import asyncio
import threading
import typing
from datetime import datetime
from typing import Set, List, Dict, Optional, Any, Union
from flask import Flask, jsonify
import discord
from discord.ext import commands

# ====================================================================================================
# PHẦN 1: HỆ THỐNG CẤU HÌNH & HẰNG SỐ (CONFIGURATION & CONSTANTS)
# ====================================================================================================

class BotConfig:
    VERSION: str = "2.1.1 Enterprise Fixed"
    DEVELOPER: str = "Black & Pink Studio"
    PREFIX: str = "?"
    
    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = 8080
    
    FILE_VIETNAMESE_DICT: str = "tu dien.txt"
    FILE_WORDS_DICT: str = "words.txt"
    FILE_ENGLISH_DICT: str = "tu dien tieng anh.txt"
    FILE_COUNTRIES_VN: str = "quoc gia vn.txt"
    FILE_COUNTRIES_EN: str = "quoc gia en.txt"
    
    COLOR_DEFAULT: int = 0xFF69B4     # Hot Pink
    COLOR_SUCCESS: int = 0x2ECC71     # Green
    COLOR_WARNING: int = 0xF1C40F     # Yellow
    COLOR_ERROR: int = 0xE74C3C       # Red
    COLOR_INFO: int = 0x3498DB        # Blue
    COLOR_BLACK: int = 0x000000       # Black
    
    MSG_ERR_NO_DATA: str = "Kho dữ liệu hiện đang trống. Vui lòng kiểm tra lại file txt."
    MSG_ERR_ALREADY_USED: str = "❌ Từ này đã được sử dụng trước đó trong ván này!"
    MSG_GAME_CANCELLED: str = "🚫 Phiên trò chơi trong kênh này đã được hủy bỏ thành công."
    MSG_NO_ACTIVE_GAME: str = "⚠️ Hiện tại không có phiên trò chơi nào đang hoạt động trong kênh này."
    
    FALLBACK_VIETNAMESE: Set[str] = {
        "học tập", "tập thể", "thể thao", "áo quần", "nước non", 
        "non sông", "sông núi", "núi cao", "cao cấp", "cấp tốc"
    }
    FALLBACK_ENGLISH: Set[str] = {
        "apple", "elephant", "tiger", "rabbit", "turtle", "eagle"
    }
    FALLBACK_COUNTRIES: Set[str] = {
        "việt nam", "nhật bản", "hàn quốc", "pháp", "mỹ", "anh", "đức"
    }

# ====================================================================================================
# PHẦN 2: HỆ THỐNG LOGGING CHUYÊN SÂU (ADVANCED LOGGING)
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

# ====================================================================================================
# PHẦN 3: HỆ THỐNG KEEP-ALIVE SERVER (FLASK BACKGROUND SERVICE)
# ====================================================================================================

keep_alive_app = Flask("EnterpriseKeepAlive")

@keep_alive_app.route('/')
def route_home() -> str:
    return (
        "<h1>Black & Pink Pure Fun Bot - Enterprise Edition</h1>"
        "<p>Hệ thống đang hoạt động 24/7 một cách ổn định.</p>"
        "<p>Trạng thái: <strong>ONLINE</strong></p>"
    )

@keep_alive_app.route('/health')
def route_health() -> Any:
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": BotConfig.VERSION
    }), 200

def launch_web_server() -> None:
    logger.info(f"Đang khởi chạy Flask Web Server trên cổng {BotConfig.WEB_SERVER_PORT}...")
    try:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        
        keep_alive_app.run(
            host=BotConfig.WEB_SERVER_HOST, 
            port=BotConfig.WEB_SERVER_PORT, 
            debug=False, 
            use_reloader=False,
            threaded=True
        )
    except Exception as server_err:
        logger.error(f"Lỗi nghiêm trọng khi khởi chạy Flask Server: {server_err}")

web_server_thread = threading.Thread(target=launch_web_server, daemon=True)
web_server_thread.start()

# ====================================================================================================
# PHẦN 4: HỆ THỐNG ĐỌC VÀ XỬ LÝ DỮ LIỆU TỪ TỆP (FILE I/O MANAGER)
# ====================================================================================================

class DataManager:
    @staticmethod
    def load_text_file(filepath: str, fallback_dataset: Set[str]) -> Set[str]:
        if not os.path.exists(filepath):
            logger.warning(f"CẢNH BÁO: Không tìm thấy tệp [{filepath}]. Đang nạp dữ liệu dự phòng.")
            return set(fallback_dataset)
            
        loaded_words: Set[str] = set()
        try:
            with open(filepath, "r", encoding="utf-8") as file_object:
                for line_content in file_object:
                    cleaned_line = line_content.strip().lower()
                    if cleaned_line:
                        loaded_words.add(cleaned_line)
                        
            if len(loaded_words) > 0:
                logger.info(f"THÀNH CÔNG: Đã nạp {len(loaded_words)} mục từ tệp [{filepath}].")
                return loaded_words
            else:
                logger.warning(f"CẢNH BÁO: Tệp [{filepath}] hoàn toàn trống. Đang nạp dữ liệu dự phòng.")
                return set(fallback_dataset)
        except Exception as err:
            logger.error(f"LỖI KHI ĐỌC TỆP [{filepath}]: {err}")
            return set(fallback_dataset)

logger.info("Bắt đầu tiến trình nạp dữ liệu từ kho lưu trữ (Local Cache)...")

VIETNAMESE_DICT = DataManager.load_text_file(BotConfig.FILE_VIETNAMESE_DICT, BotConfig.FALLBACK_VIETNAMESE)
WORDS_DICT = DataManager.load_text_file(BotConfig.FILE_WORDS_DICT, BotConfig.FALLBACK_VIETNAMESE)
ENGLISH_DICT = DataManager.load_text_file(BotConfig.FILE_ENGLISH_DICT, BotConfig.FALLBACK_ENGLISH)
COUNTRIES_VN_DICT = DataManager.load_text_file(BotConfig.FILE_COUNTRIES_VN, BotConfig.FALLBACK_COUNTRIES)
COUNTRIES_EN_DICT = DataManager.load_text_file(BotConfig.FILE_COUNTRIES_EN, BotConfig.FALLBACK_COUNTRIES)

COMBINED_VIETNAMESE_DICTIONARY: Set[str] = VIETNAMESE_DICT.union(WORDS_DICT)
logger.info(f"Tổng hợp dữ liệu: {len(COMBINED_VIETNAMESE_DICTIONARY)} từ TV, {len(ENGLISH_DICT)} từ TA, {len(COUNTRIES_VN_DICT)} quốc gia.")

COMBINED_VIETNAMESE_LIST: List[str] = list(COMBINED_VIETNAMESE_DICTIONARY)
ENGLISH_LIST: List[str] = list(ENGLISH_DICT)
COUNTRIES_VN_LIST: List[str] = list(COUNTRIES_VN_DICT) if COUNTRIES_VN_DICT else list(BotConfig.FALLBACK_COUNTRIES)
VUA_TIENG_VIET_CANDIDATES: List[str] = [w for w in COMBINED_VIETNAMESE_DICTIONARY if len(w.split()) >= 2] or list(BotConfig.FALLBACK_VIETNAMESE)

def build_syllable_index(dictionary: Set[str]) -> Dict[str, List[str]]:
    index: Dict[str, List[str]] = {}
    for word_entry in dictionary:
        parts = word_entry.split()
        if not parts:
            continue
        index.setdefault(parts[0], []).append(word_entry)
    return index

def build_letter_index(dictionary: Set[str]) -> Dict[str, List[str]]:
    index: Dict[str, List[str]] = {}
    for word_entry in dictionary:
        if not word_entry:
            continue
        index.setdefault(word_entry[0], []).append(word_entry)
    return index

VIETNAMESE_INDEX_BY_FIRST_SYLLABLE: Dict[str, List[str]] = build_syllable_index(COMBINED_VIETNAMESE_DICTIONARY)
ENGLISH_INDEX_BY_FIRST_LETTER: Dict[str, List[str]] = build_letter_index(ENGLISH_DICT)
logger.info(f"Đã lập chỉ mục tra cứu nhanh: {len(VIETNAMESE_INDEX_BY_FIRST_SYLLABLE)} nhóm âm tiết TV, {len(ENGLISH_INDEX_BY_FIRST_LETTER)} nhóm ký tự TA.")

# ====================================================================================================
# PHẦN 5: CẤU TRÚC QUẢN LÝ PHIÊN CHƠI (GAME SESSION ARCHITECTURE)
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
        self.channel_id: int = channel_id
        self.active_mode: str = GameMode.NONE
        self.is_active: bool = False
        
        self.current_word: str = ""
        self.used_words_history: Set[str] = set()
        self.turn_counter: int = 0
        
        self.scrambled_target: str = ""
        self.secret_country: str = ""
        self.session_start_time: Optional[datetime] = None

    def initialize_session(self, mode: str, start_word: str = "", target: str = "") -> None:
        self.reset()
        self.is_active = True
        self.active_mode = mode
        self.session_start_time = datetime.now()
        
        logger.info(f"[CH-{self.channel_id}] Khởi tạo phiên Nối Từ. Mode: {mode}, Từ đầu: {start_word or target}")
        
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
        self.session_start_time = None

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
        USER_DATA[user_id] = {"xp": 0, "level": 1, "last_daily": None}
    return USER_DATA[user_id]

# ====================================================================================================
# PHẦN 6: HỆ THỐNG GIAO DIỆN & THẨM MỸ (ENTERPRISE UI & AESTHETICS)
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
                masked_chars.append('  ')
            elif index == 0 or index == len(characters) - 1:
                masked_chars.append(char.upper())
            else:
                masked_chars.append('_')
        return " ".join(masked_chars)

class PetalAesthetics:
    VICTORY_QUOTES: list[str] = [
        "Một cánh hoa hồng 🌸 vừa rơi xuống, vinh danh người chiến thắng!",
        "Trong bóng tối 🖤, trí tuệ của bạn bừng sáng rực rỡ như sắc hồng 💗.",
        "Gió cuốn cánh hoa bay 🥀, mang theo chiến thắng gọi tên bạn hôm nay.",
        "Từng nhịp nối từ tựa như từng cánh hoa đan xen vào nhau thật hoàn mỹ.",
        "Bức tranh đen hồng lại khắc thêm một dấu ấn từ vựng tuyệt vời từ bạn 🌸."
    ]

    @staticmethod
    def get_falling_petal_quote() -> str:
        return random.choice(PetalAesthetics.VICTORY_QUOTES)

class UIUtils:
    DEFAULT_FOOTER_ICON = "https://cdn.discordapp.com/embed/avatars/0.png"
    
    @staticmethod
    def create_embed(title: str, description: str, color: int = BotConfig.COLOR_DEFAULT, footer_text: Optional[str] = None) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now())
        final_footer = footer_text if footer_text else f"Vườn hoa Đen Hồng 🖤💗"
        embed.set_footer(text=final_footer, icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_error_embed(error_message: str, error_code: str = "SYS_ERR") -> discord.Embed:
        embed = discord.Embed(
            title="❌ [ LỖI HỆ THỐNG NGHIÊM TRỌNG ]",
            description=f"**Chi tiết:** {error_message}\n\n*Vui lòng liên hệ Admin nếu lỗi này tiếp diễn.*",
            color=BotConfig.COLOR_ERROR,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Mã lỗi: {error_code} | Black & Pink Edition", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_warning_embed(title: str, warning_msg: str) -> discord.Embed:
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=warning_msg,
            color=BotConfig.COLOR_WARNING,
            timestamp=datetime.now()
        )
        return embed

    @staticmethod
    def build_invalid_word_embed(reason: str) -> discord.Embed:
        description = (
            f"⚠️ **Từ bạn vừa nhập không hợp lệ!**\n\n"
            f"📌 **Nguyên nhân:** {reason}\n"
            f"🌸 *Vui lòng kiểm tra lại chính tả hoặc chọn từ khác phù hợp với quy tắc.*"
        )
        embed = discord.Embed(
            title="❌💗 [ TỪ KHÔNG HỢP LỆ ] 💗❌",
            description=description,
            color=BotConfig.COLOR_ERROR,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Hệ thống kiểm duyệt Black & Pink", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_huygame_embed() -> discord.Embed:
        description = (
            f"🥀 Một cánh hoa vừa lìa cành, phiên chơi tại kênh này chính thức khép lại.\n\n"
            f"🖤 **Trạng thái:** Đã hủy thành công — toàn bộ dữ liệu ván đấu đã được xóa sạch.\n\n"
            f"🌸 Muốn chơi tiếp? Gõ `{BotConfig.PREFIX}help` để xem lại toàn bộ các chế độ."
        )
        embed = discord.Embed(
            title="🖤 [ PHIÊN NỐI TỪ ĐÃ KẾT THÚC ] 🖤",
            description=description,
            color=BotConfig.COLOR_BLACK,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Hệ thống Black & Pink • Phiên chơi đã kết thúc 🖤", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_huygame_no_active_embed() -> discord.Embed:
        description = (
            f"🖤 Khu vườn nơi đây đang tĩnh lặng, chưa có ván nối từ nào được mở ra để hủy cả.\n\n"
            f"🌸 Gõ `{BotConfig.PREFIX}help` để xem toàn bộ chế độ chơi."
        )
        embed = discord.Embed(
            title="🖤 Không Có Phiên Nào Đang Diễn Ra 🖤",
            description=description,
            color=BotConfig.COLOR_BLACK,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Hệ thống Black & Pink 🖤", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_success_embed(title: str, success_msg: str) -> discord.Embed:
        embed = discord.Embed(
            title=f"✨💗 [ {title.upper()} ] 💗✨",
            description=success_msg,
            color=0xFF69B4,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Black & Pink Word Chain System • Active Session.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_noitu_pvp_start(start_word: str, next_syllable: str) -> discord.Embed:
        description = (
            f"✨ Chào mừng các bạn đến với phòng chơi đối kháng tiếng Việt!\n"
            f"🌸 Yêu cầu bắt buộc: Mỗi từ phải gồm **2 tiếng** (vd: học tập).\n"
            f"🖤 Từ mở màn:\n\n## {start_word.upper()}\n\n"
            f"🌸 Âm tiết bắt buộc cho từ tiếp theo: **`{next_syllable.upper()}`**"
        )
        embed = discord.Embed(title="💕 [ NỐI TỪ TIẾNG VIỆT: PvP ] 🖤", description=description, color=0xFF69B4, timestamp=datetime.now())
        embed.set_footer(text="Gõ ?huynoitu để dừng phiên chơi.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_noitu_bot_start(start_word: str, next_syllable: str) -> discord.Embed:
        description = (
            f"✨ Thử thách trí tuệ trực tiếp cùng AI Bot tiếng Việt!\n"
            f"🌸 Yêu cầu: Mỗi từ gồm đúng **2 tiếng**.\n"
            f"🖤 Từ mở màn:\n\n## {start_word.upper()}\n\n"
            f"🌸 Âm tiết tiếp theo: **`{next_syllable.upper()}`**"
        )
        embed = discord.Embed(title="🤖💗 [ THÁCH ĐẤU BOT TIẾNG VIỆT ] 💗🤖", description=description, color=0xFF69B4, timestamp=datetime.now())
        embed.set_footer(text="Chế độ Solo Bot • Black & Pink Edition.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_noitu_bot_turn_success(user_word: str, next_syllable: str, bot_word: str, next_bot_syllable: str) -> discord.Embed:
        description = (
            f"✨ Đường đi nước bước hoàn hảo! (+10 điểm tích lũy)\n"
            f"🌸 Từ vừa được hệ thống ghi nhận: **`{user_word.upper()}`**\n"
            f"🖤 Âm tiết / ký tự bắt buộc cho lượt kế tiếp: **`{next_syllable.upper()}`**\n\n"
            f"🤖💗 **Phản đòn chớp nhoáng từ AI Bot:**\n\n"
            f"## {bot_word.upper()}\n\n"
            f"🌸 Lượt tiếp theo dành cho bạn, bắt đầu bằng: **`{next_bot_syllable.upper()}`**"
        )
        embed = discord.Embed(title="✨💗 [ LƯỢT ĐẤU HỢP LỆ THÀNH CÔNG ] 💗✨", description=description, color=0xFF69B4, timestamp=datetime.now())
        embed.set_footer(text="Black & Pink Word Chain System • Active Session.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_noitu_english_start(start_word: str, next_letter: str) -> discord.Embed:
        description = (
            f"✨ Welcome to the global English word chain battle arena!\n"
            f"🌸 Rule: Connect using the last letter of the previous word.\n"
            f"🖤 Starting word:\n\n## {start_word.upper()}\n\n"
            f"🌸 Required starting letter: **`{next_letter.upper()}`**"
        )
        embed = discord.Embed(title="🇬🇧💗 [ ENGLISH WORD CHAIN MODE ] 💗🖤", description=description, color=0xFF69B4, timestamp=datetime.now())
        embed.set_footer(text="Gõ ?huynoitu để dừng phiên chơi.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_noitu_bot_english_start(start_word: str, next_letter: str) -> discord.Embed:
        description = (
            f"✨ Thử thách trực tiếp cùng AI Bot tiếng Anh!\n"
            f"🌸 Rule: Từ tiếp theo bắt đầu bằng ký tự cuối từ trước.\n"
            f"🖤 Starting word:\n\n## {start_word.upper()}\n\n"
            f"🌸 Required starting letter: **`{next_letter.upper()}`**"
        )
        embed = discord.Embed(title="🤖💗 [ THÁCH ĐẤU BOT TIẾNG ANH ] 💗🤖", description=description, color=0xFF69B4, timestamp=datetime.now())
        embed.set_footer(text="English Bot Challenge • Black & Pink Edition.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_noitu_bot_english_turn_success(user_word: str, next_letter: str, bot_word: str, next_bot_letter: str) -> discord.Embed:
        description = (
            f"✨ Perfect word chain! (+10 XP)\n"
            f"🌸 Your word: **`{user_word.upper()}`**\n"
            f"🖤 Required starting letter: **`{next_letter.upper()}`**\n\n"
            f"🤖💗 **AI Bot counterattack:**\n\n"
            f"## {bot_word.upper()}\n\n"
            f"🌸 Next starting letter for you: **`{next_bot_letter.upper()}`**"
        )
        embed = discord.Embed(title="✨💗 [ LƯỢT ĐẤU HỢP LỆ THÀNH CÔNG ] 💗✨", description=description, color=0xFF69B4, timestamp=datetime.now())
        embed.set_footer(text="English Bot Challenge • Black & Pink Edition.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_vua_tieng_viet_start(scrambled_word: str) -> discord.Embed:
        description = f"✨ Sắp xếp lại các âm tiết sau thành từ có nghĩa:\n\n## 🔀 {scrambled_word}\n\n🖤 Gõ đáp án trực tiếp vào khung chat."
        embed = discord.Embed(title="👑💗 [ VUA TIẾNG VIỆT ] 💗👑", description=description, color=0xFF69B4, timestamp=datetime.now())
        return embed

    @staticmethod
    def build_doan_quoc_gia_start(masked_hint: str) -> discord.Embed:
        description = f"🌍 Gợi ý tên quốc gia:\n\n## 🗺️ {masked_hint}\n\n🖤 Nhập tên quốc gia bằng tiếng Việt."
        embed = discord.Embed(title="🌍💗 [ ĐOÁN QUỐC GIA ] 💗🌍", description=description, color=0xFF69B4, timestamp=datetime.now())
        return embed

    @staticmethod
    def build_game_victory(winner_mention: str, correct_answer: str, game_name: str) -> discord.Embed:
        poetic_quote = PetalAesthetics.get_falling_petal_quote()
        description = f"🎉 Xuất sắc! {winner_mention} đã tìm ra đáp án!\n\n✨ **ĐÁP ÁN:** **`{correct_answer.upper()}`**\n\n🌸 *{poetic_quote}*"
        embed = discord.Embed(title=f"🏆💗 [ CHIẾN THẮNG: {game_name.upper()} ] 💗🏆", description=description, color=0xFF69B4, timestamp=datetime.now())
        return embed

    @staticmethod
    def build_bot_victory(user_mention: str, missing_syllable: str, dict_size: int) -> discord.Embed:
        description = f"🎉 Chúc mừng {user_mention} đã đánh bại AI Bot!\n\n🥀 Bot đã tra **{dict_size:,}** từ nhưng không tìm được từ nào bắt đầu bằng: **`{missing_syllable.upper()}`**"
        embed = discord.Embed(title="🏆💗 [ NGƯỜI CHƠI ĐÁNH BẠI AI ] 💗🏆", description=description, color=0xFF69B4, timestamp=datetime.now())
        return embed

    @staticmethod
    def build_help_embed() -> discord.Embed:
        description = (
            f"💬 **Word Chain Ultimate Bot**\n"
            f"Hỗ trợ nối từ Tiếng Việt & Tiếng Anh, giải đố, xếp hạng.\n\n"
            f"🇻🇳💗 **[ NỐI TỪ TIẾNG VIỆT ]** 💗🇻🇳\n"
            f"🌸 `{BotConfig.PREFIX}noitu` → Chơi PvP chung kênh\n"
            f"🖤 `{BotConfig.PREFIX}noituubot` → Solo với Bot TV\n\n"
            f"🇬🇧💗 **[ NỐI TỪ TIẾNG ANH ]** 🇬🇧\n"
            f"🌸 `{BotConfig.PREFIX}noitueng` → Chơi PvP Tiếng Anh\n"
            f"🖤 `{BotConfig.PREFIX}noituubotteng` → Solo với Bot Tiếng Anh\n\n"
            f"👑💗 **[ TRÒ CHƠI KHÁC ]** 👑\n"
            f"🌸 `{BotConfig.PREFIX}vuatiengviet` | `{BotConfig.PREFIX}doanquocgia`\n\n"
            f"⚙️💗 **[ HỆ THỐNG ]** ⚙️\n"
            f"🌸 `{BotConfig.PREFIX}huynoitu` | `{BotConfig.PREFIX}nghia [từ]` | `{BotConfig.PREFIX}rank` | `{BotConfig.PREFIX}daily`"
        )
        embed = discord.Embed(title="✦ HỆ THỐNG TRỢ GIÚP NỐI TỪ ✦", description=description, color=0xFF69B4, timestamp=datetime.now())
        embed.set_footer(text="Black & Pink Edition", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

# ====================================================================================================
# PHẦN 7: KHỞI TẠO DISCORD BOT & ĐĂNG KÝ SỰ KIỆN
# ====================================================================================================

bot_intents = discord.Intents.default()
bot_intents.message_content = True
bot_intents.guilds = True
bot_intents.messages = True

bot = commands.Bot(
    command_prefix=BotConfig.PREFIX,
    intents=bot_intents,
    help_command=None,
    case_insensitive=True
)

@bot.event
async def on_ready() -> None:
    logger.info(f"✅ HỆ THỐNG SẴN SÀNG: Bot đăng nhập với tên {bot.user}")
    activity = discord.Activity(type=discord.ActivityType.playing, name=f"{BotConfig.PREFIX}help | Enterprise Logic")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_command_error(ctx: commands.Context, error: Exception) -> None:
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=UIUtils.create_embed("⚠️ Thiếu Thông Tin Lệnh", f"Vui lòng gõ `{BotConfig.PREFIX}help` để xem hướng dẫn.", BotConfig.COLOR_WARNING))
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed=UIUtils.create_embed("⏳ Thao Tác Quá Nhanh", f"Thử lại sau **{round(error.retry_after, 1)}s**.", BotConfig.COLOR_WARNING))
    else:
        logger.error(f"LỖI LỆNH (Context: {ctx.command}): {str(error)}")

# ====================================================================================================
# PHẦN 8 & 9: NHÓM LỆNH HỆ THỐNG & TRÒ CHƠI
# ====================================================================================================

@bot.command(name="ping")
async def sys_ping(ctx: commands.Context) -> None:
    bot_latency = round(bot.latency * 1000)
    await ctx.send(embed=UIUtils.create_embed("🏓 Pong!", f"Độ trễ: **{bot_latency}ms**", BotConfig.COLOR_SUCCESS))

@bot.command(name="about")
async def sys_about(ctx: commands.Context) -> None:
    desc = f"🤖 **Black & PiNk ({BotConfig.VERSION})**\n• Tiếng Việt: {len(COMBINED_VIETNAMESE_DICTIONARY):,} từ\n• Tiếng Anh: {len(ENGLISH_DICT):,} từ"
    await ctx.send(embed=UIUtils.create_embed("🖤💗 Về Hệ Thống", desc, BotConfig.COLOR_DEFAULT))

@bot.command(name="help", aliases=["menu"])
async def sys_help(ctx: commands.Context) -> None:
    await ctx.send(embed=UIUtils.build_help_embed())

@bot.command(name="noitu")
async def cmd_noitu(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có ván chơi hoạt động. Gõ `?huynoitu` để kết thúc."))
        return
    if not COMBINED_VIETNAMESE_DICTIONARY:
        await ctx.send(embed=UIUtils.build_error_embed(BotConfig.MSG_ERR_NO_DATA))
        return
    start_word = random.choice(COMBINED_VIETNAMESE_LIST)
    syllables = start_word.split()
    next_syl = syllables[-1] if syllables else start_word
    session.initialize_session(GameMode.PVP_VIETNAMESE, start_word=start_word)
    await ctx.send(embed=UIUtils.build_noitu_pvp_start(start_word, next_syl))

@bot.command(name="noituubot", aliases=["botnoitu"])
async def cmd_noituubot(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có ván chơi hoạt động."))
        return
    if not COMBINED_VIETNAMESE_DICTIONARY:
        await ctx.send(embed=UIUtils.build_error_embed(BotConfig.MSG_ERR_NO_DATA))
        return
    start_word = random.choice(COMBINED_VIETNAMESE_LIST)
    syllables = start_word.split()
    next_syl = syllables[-1] if syllables else start_word
    session.initialize_session(GameMode.BOT_VIETNAMESE, start_word=start_word)
    await ctx.send(embed=UIUtils.build_noitu_bot_start(start_word, next_syl))

@bot.command(name="noitueng", aliases=["noituen"])
async def cmd_noitueng(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có ván chơi hoạt động."))
        return
    if not ENGLISH_DICT:
        await ctx.send(embed=UIUtils.build_error_embed(BotConfig.MSG_ERR_NO_DATA))
        return
    start_word = random.choice(ENGLISH_LIST)
    next_letter = start_word[-1]
    session.initialize_session(GameMode.PVP_ENGLISH, start_word=start_word)
    await ctx.send(embed=UIUtils.build_noitu_english_start(start_word, next_letter))

@bot.command(name="noituubotteng", aliases=["botnoitueng", "noitubotteng"])
async def cmd_noituubotteng(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có ván chơi hoạt động."))
        return
    if not ENGLISH_DICT:
        await ctx.send(embed=UIUtils.build_error_embed(BotConfig.MSG_ERR_NO_DATA))
        return
    start_word = random.choice(ENGLISH_LIST)
    next_letter = start_word[-1]
    session.initialize_session(GameMode.BOT_ENGLISH, start_word=start_word)
    await ctx.send(embed=UIUtils.build_noitu_bot_english_start(start_word, next_letter))

@bot.command(name="vuatiengviet")
async def cmd_vuatiengviet(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có ván chơi hoạt động."))
        return
    target = random.choice(VUA_TIENG_VIET_CANDIDATES)
    scrambled = GameUtils.scramble_vietnamese_syllables(target)
    session.initialize_session(GameMode.VUA_TIENG_VIET, target=target)
    await ctx.send(embed=UIUtils.build_vua_tieng_viet_start(scrambled))

@bot.command(name="doanquocgia")
async def cmd_doanquocgia(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có ván chơi hoạt động."))
        return
    target = random.choice(COUNTRIES_VN_LIST)
    masked = GameUtils.generate_country_mask(target)
    session.initialize_session(GameMode.GUESS_COUNTRY, target=target)
    await ctx.send(embed=UIUtils.build_doan_quoc_gia_start(masked))

@bot.command(name="huygame", aliases=["huynoitu"])
async def cmd_huygame(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if not session.is_active:
        await ctx.send(embed=UIUtils.build_huygame_no_active_embed())
        return
    session.reset()
    await ctx.send(embed=UIUtils.build_huygame_embed())

@bot.command(name="nghia", aliases=["tracupha"])
async def cmd_nghia(ctx: commands.Context, *, word: str = "") -> None:
    if not word:
        await ctx.send(embed=UIUtils.build_warning_embed("Thiếu từ tra cứu", "Vui lòng nhập từ cần tra, ví dụ: `?nghia học tập`"))
        return
    clean_w = word.strip().lower()
    found_vi = clean_w in COMBINED_VIETNAMESE_DICTIONARY
    found_en = clean_w in ENGLISH_DICT
    desc = f"Từ khóa: **`{clean_w.upper()}`**\n\n"
    if found_vi or found_en:
        desc += "✅ **Trạng thái:** Từ này **CÓ** trong cơ sở dữ liệu chuẩn của hệ thống!"
    else:
        desc += "❌ **Trạng thái:** Từ này không có trong từ điển."
    await ctx.send(embed=UIUtils.create_embed("📖 Tra Cứu Từ Điển", desc, BotConfig.COLOR_INFO))

@bot.command(name="rank", aliases=["level"])
async def cmd_rank(ctx: commands.Context) -> None:
    u_data = get_user_data(ctx.author.id)
    desc = f"👤 **Thành viên:** {ctx.author.mention}\n⭐ **Level:** {u_data['level']}\n✨ **XP:** {u_data['xp']}"
    await ctx.send(embed=UIUtils.create_embed("📊 Thẻ Xếp Hạng", desc, BotConfig.COLOR_DEFAULT))

@bot.command(name="daily")
async def cmd_daily(ctx: commands.Context) -> None:
    u_data = get_user_data(ctx.author.id)
    today_str = datetime.now().strftime("%Y-%m-%d")
    if u_data["last_daily"] == today_str:
        await ctx.send(embed=UIUtils.build_warning_embed("Điểm Danh", "Bạn đã điểm danh hôm nay rồi!"))
        return
    u_data["last_daily"] = today_str
    u_data["xp"] += 50
    await ctx.send(embed=UIUtils.build_success_embed("Điểm Danh Thành Công", "Bạn đã nhận được **+50 XP**!"))

# ====================================================================================================
# PHẦN 10: TRÌNH LẮNG NGHE SỰ KIỆN TIN NHẮN (GAMEPLAY MESSAGE LISTENER - ĐÃ SỬA LỖI PHẢN HỒI)
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
    
    # 1. Chế độ Vua Tiếng Việt
    if session.active_mode == GameMode.VUA_TIENG_VIET:
        if content == session.scrambled_target.lower():
            u_data = get_user_data(message.author.id)
            u_data["xp"] += 20
            embed = UIUtils.build_game_victory(message.author.mention, session.scrambled_target, "Vua Tiếng Việt")
            session.reset()
            await message.channel.send(embed=embed)
            
    # 2. Chế độ Đoán Quốc Gia
    elif session.active_mode == GameMode.GUESS_COUNTRY:
        if content == session.secret_country.lower():
            u_data = get_user_data(message.author.id)
            u_data["xp"] += 20
            embed = UIUtils.build_game_victory(message.author.mention, session.secret_country, "Đoán Quốc Gia")
            session.reset()
            await message.channel.send(embed=embed)
            
    # 3. Chế độ Nối Từ Tiếng Việt (PvP)
    elif session.active_mode == GameMode.PVP_VIETNAMESE:
        syllables = content.split()
        if len(syllables) != 2:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed("Từ tiếng Việt phải gồm đúng 2 tiếng (ví dụ: học tập)."))
            return
            
        if content in session.used_words_history:
            await message.channel.send(BotConfig.MSG_ERR_ALREADY_USED)
            return
            
        if content not in COMBINED_VIETNAMESE_DICTIONARY:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(f"Từ `{content}` không tồn tại trong từ điển tiếng Việt."))
            return
            
        current_syllables = session.current_word.split()
        required_syl = current_syllables[-1] if current_syllables else ""
        
        if syllables[0] != required_syl:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(f"Từ phải bắt đầu bằng âm tiết **`{required_syl.upper()}`**!"))
            return
            
        session.used_words_history.add(content)
        session.current_word = content
        next_syl = syllables[-1]
        session.turn_counter += 1
        
        u_data = get_user_data(message.author.id)
        u_data["xp"] += 10
        
        embed = UIUtils.build_success_embed(
            "Lượt Nối Từ Hợp Lệ",
            f"✨ {message.author.mention} đã nối từ: **`{content.upper()}`**\n🌸 Âm tiết tiếp theo: **`{next_syl.upper()}`**"
        )
        await message.channel.send(embed=embed)

    # 4. Chế độ Đấu Với Bot (Bot Tiếng Việt)
    elif session.active_mode == GameMode.BOT_VIETNAMESE:
        syllables = content.split()
        if len(syllables) != 2:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed("Từ tiếng Việt phải gồm đúng 2 tiếng (ví dụ: vui chơi)."))
            return
            
        if content in session.used_words_history:
            await message.channel.send(BotConfig.MSG_ERR_ALREADY_USED)
            return
            
        if content not in COMBINED_VIETNAMESE_DICTIONARY:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(f"Từ `{content}` không tồn tại trong từ điển tiếng Việt."))
            return
            
        current_syllables = session.current_word.split()
        required_syl = current_syllables[-1] if current_syllables else ""
        
        if syllables[0] != required_syl:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(f"Từ phải bắt đầu bằng âm tiết **`{required_syl.upper()}`**!"))
            return
            
        session.used_words_history.add(content)
        user_next_syl = syllables[-1]
        
        possible_bot_words = [
            w for w in VIETNAMESE_INDEX_BY_FIRST_SYLLABLE.get(user_next_syl, [])
            if w not in session.used_words_history
        ]
        
        if not possible_bot_words:
            embed = UIUtils.build_bot_victory(message.author.mention, user_next_syl, len(COMBINED_VIETNAMESE_DICTIONARY))
            session.reset()
            await message.channel.send(embed=embed)
            return
            
        bot_word = random.choice(possible_bot_words)
        session.used_words_history.add(bot_word)
        session.current_word = bot_word
        bot_next_syl = bot_word.split()[-1]
        
        u_data = get_user_data(message.author.id)
        u_data["xp"] += 10
        
        embed = UIUtils.build_noitu_bot_turn_success(content, user_next_syl, bot_word, bot_next_syl)
        await message.channel.send(embed=embed)

    # 5. Chế độ Nối Từ Tiếng Anh (PvP)
    elif session.active_mode == GameMode.PVP_ENGLISH:
        word = content.lower()
        if not word.isalpha() or len(word) < 2:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed("Từ tiếng Anh phải từ 2 ký tự trở lên và chỉ chứa chữ cái."))
            return
            
        if word in session.used_words_history:
            await message.channel.send(BotConfig.MSG_ERR_ALREADY_USED)
            return
            
        if word not in ENGLISH_DICT:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(f"Từ `{word}` không tồn tại trong từ điển tiếng Anh chuẩn."))
            return
            
        required_letter = session.current_word[-1]
        if word[0] != required_letter:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(f"Từ phải bắt đầu bằng ký tự **`{required_letter.upper()}`**!"))
            return
            
        session.used_words_history.add(word)
        session.current_word = word
        next_letter = word[-1]
        
        u_data = get_user_data(message.author.id)
        u_data["xp"] += 10
        
        embed = UIUtils.build_success_embed(
            "English Word Chain",
            f"✨ {message.author.mention} accepted word: **`{word.upper()}`**\n🌸 Next starting letter: **`{next_letter.upper()}`**"
        )
        await message.channel.send(embed=embed)

    # 6. Chế độ Đấu Với Bot (Bot Tiếng Anh)
    elif session.active_mode == GameMode.BOT_ENGLISH:
        word = content.lower()
        if not word.isalpha() or len(word) < 2:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed("Từ tiếng Anh phải từ 2 ký tự trở lên và chỉ chứa chữ cái."))
            return

        if word in session.used_words_history:
            await message.channel.send(BotConfig.MSG_ERR_ALREADY_USED)
            return

        if word not in ENGLISH_DICT:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(f"Từ `{word}` không tồn tại trong từ điển tiếng Anh chuẩn."))
            return

        required_letter = session.current_word[-1]
        if word[0] != required_letter:
            await message.channel.send(embed=UIUtils.build_invalid_word_embed(f"Từ phải bắt đầu bằng ký tự **`{required_letter.upper()}`**!"))
            return

        session.used_words_history.add(word)
        user_next_letter = word[-1]

        possible_bot_words = [
            w for w in ENGLISH_INDEX_BY_FIRST_LETTER.get(user_next_letter, [])
            if w not in session.used_words_history
        ]

        if not possible_bot_words:
            embed = UIUtils.build_bot_victory(message.author.mention, user_next_letter, len(ENGLISH_DICT))
            session.reset()
            await message.channel.send(embed=embed)
            return

        bot_word = random.choice(possible_bot_words)
        session.used_words_history.add(bot_word)
        session.current_word = bot_word
        bot_next_letter = bot_word[-1]

        u_data = get_user_data(message.author.id)
        u_data["xp"] += 10

        embed = UIUtils.build_noitu_bot_english_turn_success(word, user_next_letter, bot_word, bot_next_letter)
        await message.channel.send(embed=embed)

# ====================================================================================================
# PHẦN 11: KHỞI CHẠY ỨNG DỤNG CHÍNH (MAIN ENTRY POINT)
# ====================================================================================================

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        logger.error("LỖI: Biến môi trường DISCORD_TOKEN chưa được thiết lập!")
    else:
        logger.info("Đang khởi động Discord Bot...")
        bot.run(TOKEN)
