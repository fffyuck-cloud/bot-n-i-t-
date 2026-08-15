# ====================================================================================================
# ██████╗ ██╗     █████╗  ██████╗██╗  ██╗    ██████╗ ██╗███╗   ██╗██╗  ██╗    ██████╗  ██████╗ ████████╗
# ██╔══██╗██║    ██╔══██╗██╔════╝██║ ██╔╝    ██╔══██╗██║████╗  ██║██║ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
# ██████╔╝██║    ███████║██║     █████╔╝     ██████╔╝██║██╔██╗ ██║█████╔╝     ██████╔╝██║   ██║   ██║   
# ██╔══██╗██║    ██╔══██║██║     ██╔═██╗     ██╔═══╝ ██║██║╚██╗██║██╔═██╗     ██╔══██╗██║   ██║   ██║   
# ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗    ██║     ██║██║ ╚████║██║  ██╗    ██████╔╝╚██████╔╝   ██║   
# ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝   
#                                                                                                    
# PURE FUN ENTERPRISE EDITION - ULTIMATE STRUCTURE (v2.0.1 - FIXED)
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
    VERSION: str = "2.0.1 Enterprise"
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
    logger.info("Ping nhận được tại endpoint: /")
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
            use_reloader=False
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

# ====================================================================================================
# PHẦN 5: CẤU TRÚC QUẢN LÝ PHIÊN CHƠI (GAME SESSION ARCHITECTURE)
# ====================================================================================================

class GameMode:
    NONE = "none"
    PVP_VIETNAMESE = "pvp_vi"
    BOT_VIETNAMESE = "bot_vi"
    PVP_ENGLISH = "pvp_en"
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
        
        logger.info(f"[CH-{channel_id if 'channel_id' in locals() else self.channel_id}] Khởi tạo phiên Nối Từ. Mode: {mode}, Từ đầu: {start_word or target}")
        
        if mode in [GameMode.PVP_VIETNAMESE, GameMode.BOT_VIETNAMESE, GameMode.PVP_ENGLISH]:
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
            f"✨ Chào mừng các bạn đến với phòng chơi đối kháng tiếng Việt đỉnh cao!\n"
            f"🌸 Yêu cầu bắt buộc: Mỗi từ phải gồm **2 tiếng** (vd: học tập, tập thể).\n"
            f"🖤 Hệ thống đã tự động random từ mở màn cho ván đấu:\n\n"
            f"## {start_word.upper()}\n\n"
            f"🌸 Âm tiết bắt buộc cho từ tiếp theo: **`{next_syllable.upper()}`**\n"
            f"🖤 Người chơi tiếp theo hãy nhập cụm từ 2 tiếng bắt đầu bằng âm tiết trên."
        )
        embed = discord.Embed(
            title="💕 [ CHẾ ĐỘ NỐI TỪ TIẾNG VIỆT: PvP ] 🖤",
            description=description,
            color=0xFF69B4,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Hệ thống Black & Pink • Gõ ?huynoitu để dừng phiên chơi.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_noitu_bot_start(start_word: str, next_syllable: str) -> discord.Embed:
        description = (
            f"✨ Thử thách trí tuệ trực tiếp cùng Trí tuệ nhân tạo (AI Bot) tiếng Việt!\n"
            f"🌸 Yêu cầu bắt buộc: Mỗi từ phải gồm đúng **2 tiếng** (vd: vui chơi, chơi đùa).\n"
            f"🖤 Bot đi trước với từ: **{start_word.upper()}**\n\n"
            f"🌸 Lượt của bạn phải bắt đầu bằng: **`{next_syllable.upper()}`**"
        )
        embed = discord.Embed(
            title="🤖💗 [ THÁCH ĐẤU BOT TIẾNG VIỆT ] 💗🤖",
            description=description,
            color=0xFF69B4,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Chế độ Solo Bot • Bản quyền Black & Pink Edition.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_noitu_bot_turn_success(user_word: str, next_syllable: str, bot_word: str, next_bot_syllable: str) -> discord.Embed:
        description = (
            f"✨ Đường đi nước bước hoàn hảo! (+10 điểm tích lũy)\n"
            f"🌸 Từ vừa được hệ thống ghi nhận: **`{user_word.upper()}`**\n"
            f"🖤 Âm tiết bắt buộc cho lượt kế tiếp: **`{next_syllable.upper()}`**\n\n"
            f"🤖💗 **Phản đòn chớp nhoáng từ AI Bot:**\n\n"
            f"## {bot_word.upper()}\n\n"
            f"🌸 Lượt tiếp theo dành cho bạn, bắt đầu bằng: **`{next_bot_syllable.upper()}`**"
        )
        embed = discord.Embed(
            title="✨💗 [ LƯỢT ĐẤU HỢP LỆ THÀNH CÔNG ] 💗✨",
            description=description,
            color=0xFF69B4,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Black & Pink Word Chain System • Active Session.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_noitu_english_start(start_word: str, next_letter: str) -> discord.Embed:
        description = (
            f"✨ Welcome to the global English word chain battle arena!\n"
            f"🌸 Rule: Each word must connect using the last letter of the previous word.\n"
            f"🖤 Starting word provided by system:\n\n"
            f"## {start_word.upper()}\n\n"
            f"🌸 Required starting letter for next word: **`{next_letter.upper()}`**"
        )
        embed = discord.Embed(
            title="🇬🇧💗 [ ENGLISH WORD CHAIN MODE ] 💗🖤",
            description=description,
            color=0xFF69B4,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Hệ thống Black & Pink • Gõ ?huynoitu để dừng phiên chơi.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_vua_tieng_viet_start(scrambled_word: str) -> discord.Embed:
        description = (
            f"✨ Thử tài giải mã ngôn từ tiếng Việt cùng hệ thống!\n"
            f"🌸 Nhiệm vụ: Sắp xếp lại các âm tiết bên dưới để tạo thành từ có nghĩa:\n\n"
            f"## 🔀 {scrambled_word}\n\n"
            f"🖤 Gõ đáp án trực tiếp vào khung chat để giành chiến thắng."
        )
        embed = discord.Embed(
            title="👑💗 [ VUA TIẾNG VIỆT (XẾP CHỮ) ] 💗👑",
            description=description,
            color=0xFF69B4,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Thể loại: Giải đố ngôn ngữ • Black & Pink Edition.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_doan_quoc_gia_start(masked_hint: str) -> discord.Embed:
        description = (
            f"🌍 Thử tài hiểu biết về bản đồ thế giới và địa lý các nước!\n"
            f"🌸 Gợi ý từ khóa ký tự (Bao gồm khoảng trắng nếu có):\n\n"
            f"## 🗺️ {masked_hint}\n\n"
            f"🖤 Nhập tên quốc gia đầy đủ bằng tiếng Việt để trả lời."
        )
        embed = discord.Embed(
            title="🌍💗 [ THỬ TÀI ĐỊA LÝ QUỐC GIA ] 💗🌍",
            description=description,
            color=0xFF69B4,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Thể loại: Kiến thức chung • Black & Pink Edition.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_game_victory(winner_mention: str, correct_answer: str, game_name: str) -> discord.Embed:
        poetic_quote = PetalAesthetics.get_falling_petal_quote()
        description = (
            f"🎉 Xuất sắc! {winner_mention} đã tìm ra đáp án chính xác!\n\n"
            f"✨ **ĐÁP ÁN CHÍNH XÁC:** **`{correct_answer.upper()}`**\n\n"
            f"🌸 *{poetic_quote}*"
        )
        embed = discord.Embed(
            title=f"🏆💗 [ CHIẾN THẮNG: {game_name.upper()} ] 💗🏆",
            description=description,
            color=0xFF69B4,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Hệ thống trao thưởng danh dự • Black & Pink Edition.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_bot_victory(user_mention: str, missing_syllable: str, dict_size: int) -> discord.Embed:
        description = (
            f"🎉 Không thể tin được! {user_mention} đã đánh bại hoàn toàn Hệ Thống Bot!\n\n"
            f"🥀 Trí tuệ nhân tạo đã lùng sục **{dict_size:,}** từ vựng nhưng **KHÔNG THỂ** "
            f"tìm ra từ hợp lệ bắt đầu bằng âm tiết: **`{missing_syllable.upper()}`**\n\n"
            f"🖤 *Chính thức phong vương Bậc Thầy Nối Từ cho bạn!*"
        )
        embed = discord.Embed(
            title="🏆💗 [ NGƯỜI CHƠI ĐÁNH BẠI AI BOT ] 💗🏆",
            description=description,
            color=0xFF69B4,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Kết quả: Player Win • Black & Pink Edition.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

    @staticmethod
    def build_help_embed() -> discord.Embed:
        description = (
            f"💬 **Word Chain Ultimate Bot**\n"
            f"Chào mừng mấy dân chơi đã lạc vào con bot nối từ đỉnh nhất server. Đây là nơi để mấy ông so trình từ vựng, flex vốn từ và leo rank đến cùng trời cuối đất.\n"
            f"Hỗ trợ kho từ vựng khổng lồ Tiếng Việt & Tiếng Anh!\n\n"
            
            f"🇻🇳💗 **[ NỐI TỪ TIẾNG VIỆT ]** 💗🇻🇳\n"
            f"🌸 `{BotConfig.PREFIX}noitu` → Chơi chung kênh cùng bè lũ (PvP)\n"
            f"🖤 `{BotConfig.PREFIX}botnoitu` → Solo khô máu với Bot tiếng Việt\n\n"
            
            f"🇬🇧💗 **[ NỐI TỪ TIẾNG ANH ]** 💗🇬🇧\n"
            f"🌸 `{BotConfig.PREFIX}noituen` → Nối từ tiếng Anh PvP\n\n"
            
            f"👑💗 **[ TRÒ CHƠI KHÁC ]** 💗👑\n"
            f"🌸 `{BotConfig.PREFIX}vuatiengviet` → Sắp xếp lại từ xáo trộn\n"
            f"🖤 `{BotConfig.PREFIX}doanquocgia` → Đoán tên quốc gia qua gợi ý\n\n"
            
            f"⚙️💗 **[ QUẢN LÝ TRẬN ĐẤU & TIỆN ÍCH ]** 💗⚙️\n"
            f"🌸 `{BotConfig.PREFIX}huygame` → Hủy ván chơi hiện tại trong kênh\n"
            f"🖤 `{BotConfig.PREFIX}nghia [từ]` → Tra cứu từ điển\n"
            f"🌸 `{BotConfig.PREFIX}rank` → Xem cấp độ và XP\n"
            f"🖤 `{BotConfig.PREFIX}daily` → Điểm danh nhận thưởng mỗi ngày"
        )
        embed = discord.Embed(
            title="✨💗 [ HỆ THỐNG TRỢ GIÚP NỐI TỪ ] 💗✨",
            description=description,
            color=0xFF69B4,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Bot được tạo ra bởi dân chơi hệ logic.", icon_url=UIUtils.DEFAULT_FOOTER_ICON)
        return embed

# ====================================================================================================
# PHẦN 7: KHỞI TẠO DISCORD BOT & ĐĂNG KÝ SỰ KIỆN (BOT INITIALIZATION & EVENTS)
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
    logger.info("=" * 60)
    logger.info(f"✅ HỆ THỐNG SẴN SÀNG: Bot đăng nhập với tên {bot.user}")
    logger.info(f"✅ ID Ứng dụng: {bot.user.id}")
    logger.info(f"✅ Phủ sóng: {len(bot.guilds)} máy chủ (Guilds).")
    logger.info("=" * 60)
    
    activity = discord.Activity(
        type=discord.ActivityType.playing, 
        name=f"{BotConfig.PREFIX}help | Enterprise Logic"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_command_error(ctx: commands.Context, error: Exception) -> None:
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = UIUtils.create_embed(
            "⚠️ Thiếu Thông Tin Lệnh",
            f"Lệnh bạn vừa nhập đang thiếu tham số yêu cầu.\nVui lòng gõ `{BotConfig.PREFIX}help` để xem hướng dẫn chi tiết.",
            BotConfig.COLOR_WARNING
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandOnCooldown):
        embed = UIUtils.create_embed(
            "⏳ Thao Tác Quá Nhanh",
            f"Lệnh này đang trong thời gian chờ. Vui lòng thử lại sau **{round(error.retry_after, 1)}s**.",
            BotConfig.COLOR_WARNING
        )
        await ctx.send(embed=embed)
    else:
        logger.error(f"LỖI THỰC THI LỆNH (Context: {ctx.command}): {str(error)}")

# ====================================================================================================
# PHẦN 8: NHÓM LỆNH HỆ THỐNG VÀ THÔNG TIN (SYSTEM & INFO COMMANDS)
# ====================================================================================================

@bot.command(name="ping", aliases=["latency", "speed"])
async def sys_ping(ctx: commands.Context) -> None:
    bot_latency = round(bot.latency * 1000)
    color = BotConfig.COLOR_SUCCESS if bot_latency < 100 else (BotConfig.COLOR_WARNING if bot_latency < 300 else BotConfig.COLOR_ERROR)
    embed = UIUtils.create_embed(
        "🏓 Pong! Network Diagnostics",
        f"Độ trễ Gateway Discord: **{bot_latency}ms**",
        color
    )
    await ctx.send(embed=embed)

@bot.command(name="about", aliases=["info"])
async def sys_about(ctx: commands.Context) -> None:
    desc = (
        f"🤖 **Black & Pink Pure Fun (Phiên bản {BotConfig.VERSION})**\n\n"
        "**Kiến trúc:** Enterprise Scale\n"
        "**Cơ sở dữ liệu:**\n"
        f"• Tiếng Việt: {len(COMBINED_VIETNAMESE_DICTIONARY):,} từ\n"
        f"• Tiếng Anh: {len(ENGLISH_DICT):,} từ\n"
        f"• Quốc gia: {len(COUNTRIES_VN_DICT):,} quốc gia"
    )
    embed = UIUtils.create_embed("🖤💗 Về Kiến Trúc Hệ Thống", desc, BotConfig.COLOR_DEFAULT)
    await ctx.send(embed=embed)

@bot.command(name="help", aliases=["hướngdẫn", "menu"])
async def sys_help(ctx: commands.Context) -> None:
    embed = UIUtils.build_help_embed()
    await ctx.send(embed=embed)

# ====================================================================================================
# PHẦN 9: NHÓM LỆNH TRÒ CHƠI & ĐIỀU KHIỂN (GAME COMMANDS)
# ====================================================================================================

@bot.command(name="noitu")
async def cmd_noitu(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có một ván chơi hoạt động. Gõ `?huygame` để kết thúc."))
        return
    
    if not COMBINED_VIETNAMESE_DICTIONARY:
        await ctx.send(embed=UIUtils.build_error_embed(BotConfig.MSG_ERR_NO_DATA))
        return
        
    start_word = random.choice(list(COMBINED_VIETNAMESE_DICTIONARY))
    syllables = start_word.split()
    next_syl = syllables[-1] if syllables else start_word
    
    session.initialize_session(GameMode.PVP_VIETNAMESE, start_word=start_word)
    embed = UIUtils.build_noitu_pvp_start(start_word, next_syl)
    await ctx.send(embed=embed)

@bot.command(name="botnoitu")
async def cmd_botnoitu(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có một ván chơi hoạt động."))
        return
        
    if not COMBINED_VIETNAMESE_DICTIONARY:
        await ctx.send(embed=UIUtils.build_error_embed(BotConfig.MSG_ERR_NO_DATA))
        return
        
    start_word = random.choice(list(COMBINED_VIETNAMESE_DICTIONARY))
    syllables = start_word.split()
    next_syl = syllables[-1] if syllables else start_word
    
    session.initialize_session(GameMode.BOT_VIETNAMESE, start_word=start_word)
    embed = UIUtils.build_noitu_bot_start(start_word, next_syl)
    await ctx.send(embed=embed)

@bot.command(name="noituen")
async def cmd_noituen(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có một ván chơi hoạt động."))
        return
        
    if not ENGLISH_DICT:
        await ctx.send(embed=UIUtils.build_error_embed(BotConfig.MSG_ERR_NO_DATA))
        return
        
    start_word = random.choice(list(ENGLISH_DICT))
    next_letter = start_word[-1]
    
    session.initialize_session(GameMode.PVP_ENGLISH, start_word=start_word)
    embed = UIUtils.build_noitu_english_start(start_word, next_letter)
    await ctx.send(embed=embed)

@bot.command(name="vuatiengviet")
async def cmd_vuatiengviet(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có một ván chơi hoạt động."))
        return
    
    valid_phrases = [w for w in COMBINED_VIETNAMESE_DICTIONARY if len(w.split()) >= 2]
    if not valid_phrases:
        valid_phrases = list(BotConfig.FALLBACK_VIETNAMESE)
        
    target = random.choice(valid_phrases)
    scrambled = GameUtils.scramble_vietnamese_syllables(target)
    
    session.initialize_session(GameMode.VUA_TIENG_VIET, target=target)
    
    embed = UIUtils.build_vua_tieng_viet_start(scrambled)
    await ctx.send(embed=embed)

@bot.command(name="doanquocgia")
async def cmd_doanquocgia(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Đã có ván chơi", "Kênh này đang có một ván chơi hoạt động."))
        return
        
    countries = list(COUNTRIES_VN_DICT) if COUNTRIES_VN_DICT else list(BotConfig.FALLBACK_COUNTRIES)
    target = random.choice(countries)
    masked = GameUtils.generate_country_mask(target)
    
    session.initialize_session(GameMode.GUESS_COUNTRY, target=target)
    
    embed = UIUtils.build_doan_quoc_gia_start(masked)
    await ctx.send(embed=embed)

@bot.command(name="huygame", aliases=["huynoitu"])
async def cmd_huygame(ctx: commands.Context) -> None:
    session = global_session_manager.get_session(ctx.channel.id)
    if not session.is_active:
        await ctx.send(embed=UIUtils.build_warning_embed("Không có ván chơi", BotConfig.MSG_NO_ACTIVE_GAME))
        return
    session.reset()
    embed = UIUtils.create_embed("🚫 Đã Hủy Phiên Trò Chơi", BotConfig.MSG_GAME_CANCELLED, BotConfig.COLOR_WARNING)
    await ctx.send(embed=embed)

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
        desc += "❌ **Trạng thái:** Từ này không có trong từ điển hoặc chưa được cập nhật."
        
    embed = UIUtils.create_embed("📖 Tra Cứu Từ Điển", desc, BotConfig.COLOR_INFO)
    await ctx.send(embed=embed)

@bot.command(name="rank", aliases=["level"])
async def cmd_rank(ctx: commands.Context) -> None:
    u_data = get_user_data(ctx.author.id)
    desc = f"👤 **Thành viên:** {ctx.author.mention}\n⭐ **Cấp độ (Level):** {u_data['level']}\n✨ **Điểm kinh nghiệm (XP):** {u_data['xp']}"
    embed = UIUtils.create_embed("📊 Thẻ Xếp Hạng Cá Nhân", desc, BotConfig.COLOR_DEFAULT)
    await ctx.send(embed=embed)

@bot.command(name="daily")
async def cmd_daily(ctx: commands.Context) -> None:
    u_data = get_user_data(ctx.author.id)
    today_str = datetime.now().strftime("%Y-%m-%d")
    if u_data["last_daily"] == today_str:
        await ctx.send(embed=UIUtils.build_warning_embed("Điểm Danh", "Bạn đã điểm danh ngày hôm nay rồi. Hãy quay lại vào ngày mai nhé!"))
        return
    u_data["last_daily"] = today_str
    u_data["xp"] += 50
    embed = UIUtils.build_success_embed("Điểm Danh Thành Công", f"Bạn đã nhận được **+50 XP** tích lũy vào tài khoản!")
    await ctx.send(embed=embed)

# ====================================================================================================
# PHẦN 10: TRÌNH LẮNG NGHE SỰ KIỆN TIN NHẮN (GAMEPLAY MESSAGE LISTENER)
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
            return
            
        if content in session.used_words_history:
            await message.channel.send(BotConfig.MSG_ERR_ALREADY_USED)
            return
            
        if content not in COMBINED_VIETNAMESE_DICTIONARY:
            return
            
        current_syllables = session.current_word.split()
        required_syl = current_syllables[-1] if current_syllables else ""
        
        if syllables[0] != required_syl:
            return
            
        session.used_words_history.add(content)
        session.current_word = content
        next_syl = syllables[-1]
        session.turn_counter += 1
        
        u_data = get_user_data(message.author.id)
        u_data["xp"] += 10
        
        embed = UIUtils.build_success_embed(
            "Lượt Nối Từ Hợp Lệ",
            f"✨ Người chơi {message.author.mention} đã nối từ: **`{content.upper()}`**\n🌸 Âm tiết tiếp theo: **`{next_syl.upper()}`**"
        )
        await message.channel.send(embed=embed)

    # 4. Chế độ Đấu Với Bot (Bot Tiếng Việt)
    elif session.active_mode == GameMode.BOT_VIETNAMESE:
        syllables = content.split()
        if len(syllables) != 2:
            return
            
        if content in session.used_words_history:
            await message.channel.send(BotConfig.MSG_ERR_ALREADY_USED)
            return
            
        if content not in COMBINED_VIETNAMESE_DICTIONARY:
            return
            
        current_syllables = session.current_word.split()
        required_syl = current_syllables[-1] if current_syllables else ""
        
        if syllables[0] != required_syl:
            return
            
        session.used_words_history.add(content)
        user_next_syl = syllables[-1]
        
        possible_bot_words = [
            w for w in COMBINED_VIETNAMESE_DICTIONARY 
            if w.startswith(user_next_syl + " ") and w not in session.used_words_history
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
            return
            
        if word in session.used_words_history:
            await message.channel.send(BotConfig.MSG_ERR_ALREADY_USED)
            return
            
        if word not in ENGLISH_DICT:
            return
            
        required_letter = session.current_word[-1]
        if word[0] != required_letter:
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
