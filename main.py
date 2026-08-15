# =====================================================================
# HỆ THỐNG DISCORD BOT NỐI TỪ & VUA TIẾNG VIỆT/ANH - BLACK & PINK EDITION
# =====================================================================

import os
import json
import random
import logging
import asyncio
from threading import Thread
from flask import Flask
import discord

# =====================================================================
# 1. CẤU HÌNH HỆ THỐNG LOGGING VÀ KEEP-ALIVE WEB SERVER
# =====================================================================

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("BlackPinkWordBot")

app = Flask("BlackPinkServer")

@app.route('/')
def home_route():
    return "Black & Pink Word Chain & Vua Tiếng Việt Bot is running smoothly!"

def run_web_server():
    try:
        app.run(host='0.0.0.0', port=8080)
    except Exception as e:
        logger.error(f"Lỗi khởi chạy Web Server Keep-Alive: {e}")

def initialize_keep_alive():
    logger.info("Đang khởi tạo tiến trình nền Keep-Alive Web Server...")
    server_thread = Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    logger.info("Tiến trình Keep-Alive đã hoạt động thành công trên cổng 8080.")

# =====================================================================
# 2. CẤU HÌNH MÀU SẮC ĐẶC TRƯNG (BLACK & PINK PALETTE)
# =====================================================================

COLOR_PINK_NEON = 0xFF69B4    # Hồng neon cá tính
COLOR_DARK_BLACK = 0x111111   # Đen huyền bí
COLOR_HOT_PINK = 0xFF1493     # Hồng đậm nổi bật
COLOR_GOLD_ACCENT = 0xFFD700 # Vàng điểm nhấn thành tích

# =====================================================================
# 3. HỆ THỐNG QUẢN LÝ DỮ LIỆU TỪ ĐIỂN VÀ LƯU TRỮ NGƯỜI DÙNG
# =====================================================================

STATS_STORAGE_FILE = "user_blackpink_stats.json"

def load_vocabulary_file(file_path):
    vocab_set = set()
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file_obj:
                for current_line in file_obj:
                    cleaned_word = current_line.strip().lower()
                    if cleaned_word:
                        vocab_set.add(cleaned_word)
            logger.info(f"Đã nạp thành công {len(vocab_set)} từ vựng từ tệp: {file_path}")
        else:
            logger.warning(f"Không tìm thấy tệp từ điển tại đường dẫn: {file_path}")
    except Exception as error_msg:
        logger.error(f"Xảy ra lỗi khi đọc tệp {file_path}: {error_msg}")
    return vocab_set

def load_english_dictionary_optimized(file_path):
    dict_by_letter = {}
    total_words = 0
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file_obj:
                for current_line in file_obj:
                    cleaned_word = current_line.strip().lower()
                    if cleaned_word and len(cleaned_word.split()) == 1:
                        first_char = cleaned_word[0]
                        if first_char not in dict_by_letter:
                            dict_by_letter[first_char] = set()
                        dict_by_letter[first_char].add(cleaned_word)
                        total_words += 1
            logger.info(f"Đã nạp và phân loại thành công {total_words} từ tiếng Anh từ tệp: {file_path}")
        else:
            logger.warning(f"Không tìm thấy tệp từ điển tại đường dẫn: {file_path}")
    except Exception as error_msg:
        logger.error(f"Xảy ra lỗi khi đọc tệp {file_path}: {error_msg}")
    
    full_set = {word for words in dict_by_letter.values() for word in words}
    return dict_by_letter, full_set

def load_user_statistics_database():
    if os.path.exists(STATS_STORAGE_FILE):
        try:
            with open(STATS_STORAGE_FILE, 'r', encoding='utf-8') as db_file:
                logger.info("Đã tải thành công cơ sở dữ liệu thống kê người dùng.")
                return json.load(db_file)
        except Exception as err:
            logger.error(f"Lỗi đọc cơ sở dữ liệu thống kê: {err}")
    return {}

def save_user_statistics_database(stats_data):
    try:
        with open(STATS_STORAGE_FILE, 'w', encoding='utf-8') as db_file:
            json.dump(stats_data, db_file, ensure_ascii=False, indent=4)
    except Exception as err:
        logger.error(f"Lỗi khi ghi dữ liệu thống kê: {err}")

# Nạp từ điển Tiếng Việt (bắt buộc đúng 2 tiếng)
raw_vi_dict = load_vocabulary_file('tu dien.txt')
raw_vi_dict.update(load_vocabulary_file('words.txt'))
vietnamese_dictionary = {w for w in raw_vi_dict if len(w.split()) == 2}

# Nạp từ điển Tiếng Anh siêu tốc (Phân nhóm chữ cái + Set tổng hợp)
english_dict_by_letter, english_dictionary = load_english_dictionary_optimized('tu dien tieng anh.txt')

user_stats_database = load_user_statistics_database()

# =====================================================================
# 4. LỚP QUẢN LÝ PHIÊN CHƠI TRÊN TỪNG KÊNH (SESSION MANAGER)
# =====================================================================

class ChannelGameSession:
    def __init__(self):
        self.active = False
        self.mode = None  # 'pvp_vi', 'bot_vi', 'pvp_eng', 'bot_eng', 'vua_vi', 'vua_eng'
        self.last_word = ""
        self.used_words = set()
        self.last_author_id = None
        # Dành riêng cho minigame Vua Tiếng Việt / Vua Tiếng Anh (giải đố xáo trộn chữ)
        self.scrambled_target = None

    def reset_session(self):
        self.active = False
        self.mode = None
        self.last_word = ""
        self.used_words.clear()
        self.last_author_id = None
        self.scrambled_target = None

channel_game_sessions = {}

def get_channel_session(channel_id):
    if channel_id not in channel_game_sessions:
        channel_game_sessions[channel_id] = ChannelGameSession()
    return channel_game_sessions[channel_id]

def fetch_user_record(user_id):
    uid_str = str(user_id)
    if uid_str not in user_stats_database:
        user_stats_database[uid_str] = {
            "score": 0,
            "streak": 0,
            "games_played": 0,
            "last_daily": ""
        }
    return user_stats_database[uid_str]

def scramble_word(word):
    """Hàm xáo trộn các ký tự hoặc các tiếng trong từ để làm minigame giải đố"""
    parts = word.split()
    if len(parts) > 1:
        # Xáo trộn các tiếng nếu là cụm từ (ví dụ: 'học tập' -> 'tập học')
        shuffled = parts.copy()
        while shuffled == parts:
            random.shuffle(shuffled)
        return " ".join(shuffled)
    else:
        # Xáo trộn các chữ cái bên trong từ đơn tiếng Anh
        chars = list(word)
        if len(chars) <= 1:
            return word
        while chars == list(word):
            random.shuffle(chars)
        return "".join(chars)

# =====================================================================
# 5. KHỞI TẠO DISCORD CLIENT VÀ CÁC INTENTS
# =====================================================================

bot_intents = discord.Intents.default()
bot_intents.message_content = True
bot_intents.guilds = True

discord_client = discord.Client(intents=bot_intents)

@discord_client.event
async def on_ready():
    logger.info(f"Bot đã đăng nhập thành công dưới tên tài khoản: {discord_client.user}")
    await discord_client.change_presence(
        activity=discord.Game(name="?help | Black & Pink Word Chain")
    )
    logger.info("Trạng thái hoạt động của Bot đã được thiết lập hoàn tất.")

# =====================================================================
# 6. HỆ THỐNG XỬ LÝ SỰ KIỆN TIN NHẮN VÀ ĐIỀU HƯỚNG LỆNH
# =====================================================================

@discord_client.event
async def on_message(incoming_message):
    if incoming_message.author.bot:
        return

    channel_identifier = incoming_message.channel.id
    raw_content = incoming_message.content.lower().strip()
    session_data = get_channel_session(channel_identifier)

    # -----------------------------------------------------------------
    # NHÓM LỆNH 1: KÍCH HOẠT NỐI TỪ TIẾNG VIỆT & TIẾNG ANH
    # -----------------------------------------------------------------

    if raw_content == "?noitu":
        session_data.reset_session()
        session_data.active = True
        session_data.mode = "pvp_vi"
        
        if vietnamese_dictionary:
            start_word = random.choice(list(vietnamese_dictionary))
            session_data.last_word = start_word
            session_data.used_words.add(start_word)
            next_syllable = start_word.split()[-1]
        else:
            start_word = "học tập"
            session_data.last_word = start_word
            session_data.used_words.add(start_word)
            next_syllable = "tập"

        embed_response = discord.Embed(
            title="🖤💗 [ CHẾ ĐỘ NỐI TỪ TIẾNG VIỆT: PvP ] 💗🖤",
            description=(
                "✨ Chào mừng các bạn đến với phòng chơi đối kháng tiếng Việt đỉnh cao!\n"
                "🌸 Yêu cầu bắt buộc: Mỗi từ phải gồm đúng **2 tiếng** (vd: học tập, tập thể).\n"
                "🖤 Hệ thống đã tự động random từ mở màn cho ván đấu:\n"
                f"# {start_word}\n"
                f"🌸 Âm tiết bắt buộc cho từ tiếp theo: **`{next_syllable}`**\n"
                "🖤 Người chơi tiếp theo hãy nhập cụm từ 2 tiếng bắt đầu bằng âm tiết trên."
            ),
            color=COLOR_PINK_NEON
        )
        embed_response.set_footer(text="Hệ thống Black & Pink • Gõ ?huynoitu để dừng phiên chơi.")
        await incoming_message.channel.send(embed=embed_response)
        return

    elif raw_content == "?noituubot":
        session_data.reset_session()
        session_data.active = True
        session_data.mode = "bot_vi"
        
        if vietnamese_dictionary:
            start_word = random.choice(list(vietnamese_dictionary))
            session_data.last_word = start_word
            session_data.used_words.add(start_word)
            next_syllable = start_word.split()[-1]
        else:
            start_word = "vui chơi"
            session_data.last_word = start_word
            session_data.used_words.add(start_word)
            next_syllable = "chơi"

        embed_response = discord.Embed(
            title="🤖💗 [ THÁCH ĐẤU BOT TIẾNG VIỆT ] 💗🤖",
            description=(
                "✨ Thử thách trí tuệ trực tiếp cùng Trí tuệ nhân tạo (AI Bot) tiếng Việt!\n"
                "🌸 Yêu cầu bắt buộc: Mỗi từ phải gồm đúng **2 tiếng** (vd: vui chơi, chơi đùa).\n"
                "🖤 Hệ thống đã tự động random từ mở màn cho bạn:\n"
                f"# {start_word}\n"
                f"🌸 Âm tiết bắt buộc cho từ tiếp theo: **`{next_syllable}`**\n"
                "🖤 Hãy nhập từ 2 tiếng nối tiếp theo đúng quy tắc để tiếp tục đấu với Bot."
            ),
            color=COLOR_HOT_PINK
        )
        embed_response.set_footer(text="Chế độ Solo Bot • Bản quyền Black & Pink Edition.")
        await incoming_message.channel.send(embed=embed_response)
        return

    elif raw_content == "?noitueng":
        session_data.reset_session()
        session_data.active = True
        session_data.mode = "pvp_eng"
        
        if english_dictionary:
            start_word = random.choice(list(english_dictionary))
            session_data.last_word = start_word
            session_data.used_words.add(start_word)
            next_char = start_word[-1]
        else:
            start_word = "error"
            next_char = ""

        embed_response = discord.Embed(
            title="🇬🇧💗 [ NỐI TỪ TIẾNG ANH: PvP ] 💗🇬🇧",
            description=(
                "✨ Chào mừng các bạn đến với phòng đấu kháng từ vựng tiếng Anh đỉnh cao!\n"
                "🖤 Hệ thống đã tự động random từ mở màn cho bạn:\n"
                f"# {start_word}\n"
                f"🌸 Ký tự bắt buộc cho từ tiếp theo: **`{next_char}`**\n"
                "🖤 Người chơi tiếp theo hãy nhập từ tiếng Anh bắt đầu bằng ký tự trên."
            ),
            color=COLOR_PINK_NEON
        )
        embed_response.set_footer(text="Phòng PvP Tiếng Anh • Gõ ?huynoitu để dừng phiên chơi.")
        await incoming_message.channel.send(embed=embed_response)
        return

    elif raw_content == "?noituuboteng":
        session_data.reset_session()
        session_data.active = True
        session_data.mode = "bot_eng"
        
        if english_dictionary:
            start_word = random.choice(list(english_dictionary))
            session_data.last_word = start_word
            session_data.used_words.add(start_word)
            next_char = start_word[-1]
        else:
            start_word = "error"
            next_char = ""

        embed_response = discord.Embed(
            title="🤖🇬🇧 [ THÁCH ĐẤU BOT TIẾNG ANH ] 🇬🇧🤖",
            description=(
                "✨ Thử thách trí tuệ trực tiếp cùng Trí tuệ nhân tạo (AI Bot) tiếng Anh!\n"
                "🖤 Hệ thống đã tự động random từ mở màn cho bạn:\n"
                f"# {start_word}\n"
                f"🌸 Ký tự bắt buộc cho từ tiếp theo: **`{next_char}`**\n"
                "🖤 Hãy nhập từ tiếng Anh nối tiếp theo đúng quy tắc để tiếp tục đấu với Bot."
            ),
            color=COLOR_HOT_PINK
        )
        embed_response.set_footer(text="Chế độ Solo Bot Tiếng Anh • Bản quyền Black & Pink Edition.")
        await incoming_message.channel.send(embed=embed_response)
        return

    # -----------------------------------------------------------------
    # NHÓM LỆNH 2: VUA TIẾNG VIỆT & VUA TIẾNG ANH (GIẢI ĐỐ XÁO TRỘN CHỮ)
    # -----------------------------------------------------------------

    elif raw_content == "?vuatiengviet":
        session_data.reset_session()
        session_data.active = True
        session_data.mode = "vua_vi"
        
        if vietnamese_dictionary:
            target_word = random.choice(list(vietnamese_dictionary))
        else:
            target_word = "chúc mừng"
            
        session_data.scrambled_target = target_word
        puzzle_display = scramble_word(target_word)

        embed_response = discord.Embed(
            title="👑🇻🇳 [ THỬ THÁCH: VUA TIẾNG VIỆT ] 🇻🇳👑",
            description=(
                "✨ Chào mừng bạn đến với minigame sắp xếp từ tiếng Việt cực hack não!\n"
                "🌸 Nhiệm vụ: Hãy sắp xếp lại các tiếng bị xáo trộn dưới đây thành một cụm từ **2 tiếng** có nghĩa hoàn chỉnh:\n\n"
                f"# 🔀 `{puzzle_display}`\n\n"
                "🖤 Gõ trực tiếp đáp án của bạn vào kênh để ghi điểm ngay lập tức!"
            ),
            color=COLOR_GOLD_ACCENT
        )
        embed_response.set_footer(text="Vua Tiếng Việt Minigame • Gõ ?huynoitu để dừng.")
        await incoming_message.channel.send(embed=embed_response)
        return

    elif raw_content == "?vuatienganh":
        session_data.reset_session()
        session_data.active = True
        session_data.mode = "vua_eng"
        
        if english_dictionary:
            target_word = random.choice(list(english_dictionary))
            while len(target_word) < 4:  # Đảm bảo từ tiếng Anh đủ độ dài để xáo trộn
                target_word = random.choice(list(english_dictionary))
        else:
            target_word = "python"
            
        session_data.scrambled_target = target_word
        puzzle_display = scramble_word(target_word)

        embed_response = discord.Embed(
            title="👑🇬🇧 [ THỬ THÁCH: VUA TIẾNG ANH ] 🇬🇧👑",
            description=(
                "✨ Chào mừng bạn đến với minigame giải đố từ vựng tiếng Anh!\n"
                "🌸 Nhiệm vụ: Hãy sắp xếp lại các chữ cái bị đảo lộn dưới đây thành một từ tiếng Anh chính xác:\n\n"
                f"# 🔀 `{puzzle_display}`\n\n"
                "🖤 Gõ trực tiếp đáp án của bạn vào kênh để ghi điểm ngay lập tức!"
            ),
            color=COLOR_GOLD_ACCENT
        )
        embed_response.set_footer(text="Vua Tiếng Anh Minigame • Gõ ?huynoitu để dừng.")
        await incoming_message.channel.send(embed=embed_response)
        return

    # -----------------------------------------------------------------
    # NHÓM LỆNH 3: ĐIỀU KHIỂN HỆ THỐNG VÀ TIỆN ÍCH (TRA CỨU / RANK / DAILY)
    # -----------------------------------------------------------------

    elif raw_content == "?huynoitu":
        if session_data.active:
            session_data.reset_session()
            embed_response = discord.Embed(
                title="🚫🖤 [ KẾT THÚC PHIÊN CHƠI ] 🖤🚫",
                description=(
                    "⚠️ Ván chơi hiện tại trong kênh này đã chính thức bị hủy bỏ hoàn toàn.\n"
                    "🌸 Toàn bộ bộ nhớ đệm đã được làm sạch để chuẩn bị cho phòng mới."
                ),
                color=COLOR_DARK_BLACK
            )
            await incoming_message.channel.send(embed=embed_response)
        else:
            await incoming_message.channel.send("⚠️ Hiện tại không có ván chơi nào đang hoạt động trong kênh này.")
        return

    elif raw_content.startswith("?nghia"):
        split_parts = incoming_message.content.split()
        if len(split_parts) > 1:
            query_term = " ".join(split_parts[1:]).lower()
            word_count = len(query_term.split())
            is_english = query_term in english_dictionary

            embed_response = discord.Embed(
                title="📖💗 [ KIỂM TRA TRẠNG THÁI TỪ VỰNG ] 💗📖",
                description=(
                    f"🌸 Từ khóa kiểm tra: **`{query_term}`**\n\n"
                    f"  • Tiếng Việt (chuẩn 2 tiếng): {'✅ **Hợp lệ chơi nối từ**' if word_count == 2 else '⚠️ **Không phải 2 tiếng**'}\n"
                    f"  • Tiếng Anh (kho từ điển): {'✅ **Tồn tại trong cơ sở dữ liệu**' if is_english else '❌ **Không tìm thấy**'}\n"
                ),
                color=COLOR_PINK_NEON
            )
            embed_response.set_footer(text="Dictionary Status Check • Black & Pink Style.")
            await incoming_message.channel.send(embed=embed_response)
        else:
            await incoming_message.channel.send("⚠️ Vui lòng chỉ định từ cần kiểm tra theo đúng cú pháp: `?nghia <từ>`")
        return

    elif raw_content == "?rank":
        user_record = fetch_user_record(incoming_message.author.id)
        embed_response = discord.Embed(
            title=f"🏆💗 [ BẢNG THÀNH TÍCH: {incoming_message.author.name.upper()} ] 💗🏆",
            description=(
                "✨ Trung tâm thông tin dữ liệu cá nhân:\n"
                f"  • Tổng điểm tích lũy hiện tại: **`{user_record['score']} điểm`**\n"
                f"  • Chuỗi thắng liên tiếp: **`{user_record['streak']} trận`**\n"
                f"  • Tổng số từ đã đóng góp: **`{user_record['games_played']} từ`**\n"
                "🖤 Danh hiệu cá nhân: **`Chuyên gia từ vựng Black & Pink`**"
            ),
            color=COLOR_GOLD_ACCENT
        )
        embed_response.set_thumbnail(url=incoming_message.author.display_avatar.url)
        embed_response.set_footer(text="User Leaderboard Profile • Black & Pink Edition.")
        await incoming_message.channel.send(embed=embed_response)
        return

    elif raw_content == "?daily":
        user_record = fetch_user_record(incoming_message.author.id)
        user_record["score"] += 50
        save_user_statistics_database(user_stats_database)
        
        embed_response = discord.Embed(
            title="🎁💗 [ QUÀ TẶNG ĐIỂM DANH HÀNG NGÀY ] 💗🎁",
            description=(
                "✨ Tuyệt vời! Bạn đã hoàn thành thủ tục điểm danh ngày hôm nay.\n"
                "  • Quà tặng nhận được: **`+50 điểm tích lũy`**\n"
                f"  • Tổng điểm số hiện tại: **`{user_record['score']} điểm`**"
            ),
            color=COLOR_HOT_PINK
        )
        embed_response.set_footer(text="Daily Check-in Reward • Black & Pink Theme.")
        await incoming_message.channel.send(embed=embed_response)
        return

    elif raw_content == "?help":
        embed_response = discord.Embed(
            title="📖💗 [ TRUNG TÂM HƯỚNG DẪN BLACK & PINK BOT ] 💗📖",
            description=(
                "✨ Danh sách toàn bộ các lệnh điều khiển và chế độ chơi được hỗ trợ:\n"
                "🖤 **Nhóm lệnh Nối Từ:**\n"
                "  • `?noitu` - Nối từ tiếng Việt (Đúng 2 tiếng, PvP)\n"
                "  • `?noituubot` - Thách đấu nối từ tiếng Việt với AI Bot\n"
                "  • `?noitueng` - Nối từ tiếng Anh (PvP)\n"
                "  • `?noituuboteng` - Thách đấu nối từ tiếng Anh với AI Bot\n"
                "🖤 **Nhóm lệnh Vua Tiếng Việt / Tiếng Anh (Giải đố):**\n"
                "  • `?vuatiengviet` - Minigame sắp xếp từ tiếng Việt chính xác\n"
                "  • `?vuatienganh` - Minigame giải mã từ tiếng Anh xáo trộn\n"
                "🖤 **Nhóm lệnh chung:**\n"
                "  • `?huynoitu` - Dừng ván đấu hiện tại\n"
                "  • `?nghia <từ>` - Kiểm tra từ vựng\n"
                "  • `?rank` - Xem bảng thành tích cá nhân\n"
                "  • `?daily` - Điểm danh nhận quà hằng ngày"
            ),
            color=COLOR_PINK_NEON
        )
        embed_response.set_footer(text="Help Center & Command Guide • Black & Pink Edition.")
        await incoming_message.channel.send(embed=embed_response)
        return

    # -----------------------------------------------------------------
    # KHU VỰC 4: XỬ LÝ LOGIC TRÒ CHƠI THỰC TẾ (NỐI TỪ HOẶC VUA TIẾNG VIỆT/ANH)
    # -----------------------------------------------------------------

    if session_data.active:
        # XỬ LÝ CHO CHẾ ĐỘ VUA TIẾNG VIỆT / VUA TIẾNG ANH
        if session_data.mode in ["vua_vi", "vua_eng"]:
            if raw_content == session_data.scrambled_target:
                # Cập nhật điểm số người chơi thắng giải đố
                user_record = fetch_user_record(incoming_message.author.id)
                user_record["score"] += 20
                user_record["streak"] += 1
                user_record["games_played"] += 1
                save_user_statistics_database(user_stats_database)

                correct_word = session_data.scrambled_target
                
                # Tự động tạo câu đố tiếp theo liền mạch (chuẩn phong cách bot Neko/Mimi)
                if session_data.mode == "vua_vi":
                    if vietnamese_dictionary:
                        next_target = random.choice(list(vietnamese_dictionary))
                    else:
                        next_target = "thông minh"
                else:
                    if english_dictionary:
                        next_target = random.choice(list(english_dictionary))
                        while len(next_target) < 4:
                            next_target = random.choice(list(english_dictionary))
                    else:
                        next_target = "discord"

                session_data.scrambled_target = next_target
                puzzle_display = scramble_word(next_target)

                embed_response = discord.Embed(
                    title="🎉👑 [ ĐÁP ÁN CHÍNH XÁC! (+20 điểm) ] 👑🎉",
                    description=(
                        f"✨ Chúc mừng **{incoming_message.author.mention}** đã giải mã thành công từ: **`{correct_word}`**!\n\n"
                        "🌸 **Vòng đấu tiếp theo bắt đầu ngay lập tức:**\n"
                        f"# 🔀 `{puzzle_display}`\n\n"
                        "🖤 Hãy nhanh tay gõ đáp án tiếp theo vào kênh!"
                    ),
                    color=COLOR_GOLD_ACCENT
                )
                embed_response.set_footer(text="Vua Tiếng Việt / Anh • Continuous Mode.")
                await incoming_message.channel.send(embed=embed_response)
            return

        # XỬ LÝ CHO CHẾ ĐỘ NỐI TỪ TRUYỀN THỐNG
        if session_data.mode in ["pvp_vi", "bot_vi"]:
            if len(raw_content.split()) != 2:
                embed_response = discord.Embed(
                    title="⚠️💗 [ SAI ĐỊNH DẠNG TỪ ] 💗⚠️",
                    description="⚠️ Chế độ tiếng Việt bắt buộc phải nhập đúng **2 tiếng**.",
                    color=COLOR_DARK_BLACK
                )
                await incoming_message.channel.send(embed=embed_response)
                return
            vietnamese_dictionary.add(raw_content)

        # Kiểm tra từ tồn tại trong từ điển tiếng Anh
        if session_data.mode in ["pvp_eng", "bot_eng"] and raw_content not in english_dictionary:
            embed_response = discord.Embed(
                title="❌💗 [ TỪ KHÔNG HỢP LỆ ] ❌",
                description="⚠️ Từ bạn vừa nhập không có trong cơ sở dữ liệu tiếng Anh.",
                color=COLOR_DARK_BLACK
            )
            await incoming_message.channel.send(embed=embed_response)
            return

        # Kiểm tra từ đã được sử dụng chưa
        if raw_content in session_data.used_words:
            embed_response = discord.Embed(
                title="⚠️💗 [ TỪ ĐÃ ĐƯỢC SỬ DỤNG ] 💗⚠️",
                description="⚠️ Từ này đã xuất hiện trước đó trong ván đấu hiện tại rồi!",
                color=COLOR_HOT_PINK
            )
            await incoming_message.channel.send(embed=embed_response)
            return

        # Kiểm tra quy tắc PvP (không đánh liền 2 lượt)
        if "pvp" in session_data.mode and session_data.last_author_id == incoming_message.author.id:
            embed_response = discord.Embed(
                title="⚠️💗 [ VI PHẠM LIÊN TỤC LƯỢT ] 💗⚠️",
                description="⚠️ Bạn không được phép tự nối từ của chính mình trong chế độ PvP!",
                color=COLOR_DARK_BLACK
            )
            await incoming_message.channel.send(embed=embed_response)
            return

        # Kiểm tra quy tắc nối ký tự / âm tiết
        if session_data.last_word != "":
            if session_data.mode in ["pvp_eng", "bot_eng"]:
                required_char = session_data.last_word[-1]
                if not raw_content.startswith(required_char):
                    embed_response = discord.Embed(
                        title="⚠️💗 [ SAI QUY TẮC NỐI TỪ ] 💗⚠️",
                        description=f"🌸 Từ tiếp theo bắt buộc phải bắt đầu bằng ký tự: **`{required_char}`**",
                        color=COLOR_DARK_BLACK
                    )
                    await incoming_message.channel.send(embed=embed_response)
                    return
            else:
                required_syllable = session_data.last_word.split()[-1]
                first_syllable_user = raw_content.split()[0]
                if first_syllable_user != required_syllable:
                    embed_response = discord.Embed(
                        title="⚠️💗 [ SAI QUY TẮC NỐI TỪ ] 💗⚠️",
                        description=f"🌸 Từ tiếp theo bắt buộc phải bắt đầu bằng âm tiết: **`{required_syllable}`**",
                        color=COLOR_DARK_BLACK
                    )
                    await incoming_message.channel.send(embed=embed_response)
                    return

        # Cập nhật trạng thái phiên nối từ hợp lệ
        session_data.last_word = raw_content
        session_data.used_words.add(raw_content)
        session_data.last_author_id = incoming_message.author.id

        user_record = fetch_user_record(incoming_message.author.id)
        user_record["score"] += 10
        user_record["streak"] += 1
        user_record["games_played"] += 1
        save_user_statistics_database(user_stats_database)

        if session_data.mode in ["pvp_eng", "bot_eng"]:
            next_target = session_data.last_word[-1]
        else:
            next_target = session_data.last_word.split()[-1]

        response_description = (
            "✨ **Đường đi nước bước hoàn hảo! (+10 điểm tích lũy)**\n"
            f"🌸 Từ vừa được hệ thống ghi nhận: `{raw_content}`\n"
            f"🖤 Âm tiết / ký tự bắt buộc cho lượt kế tiếp: **`{next_target}`**"
        )

        # Xử lý phản hồi từ AI Bot trong chế độ nối từ với Bot
        if "bot" in session_data.mode:
            if session_data.mode == "bot_eng":
                target_pool = english_dict_by_letter.get(next_target, set())
                possible_bot_words = [c for c in target_pool if c not in session_data.used_words]
            else:
                possible_bot_words = [c for c in vietnamese_dictionary if c.split()[0] == next_target and c not in session_data.used_words]

            if possible_bot_words:
                chosen_bot_word = random.choice(possible_bot_words)
            else:
                common_syllables = ["sống", "vui", "học", "nhà", "nước", "đường", "thời", "gian"]
                chosen_bot_word = f"{next_target} {random.choice(common_syllables)}"
                while chosen_bot_word in session_data.used_words:
                    chosen_bot_word = f"{next_target} {random.choice(common_syllables)}"

            session_data.last_word = chosen_bot_word
            session_data.used_words.add(chosen_bot_word)
            session_data.last_author_id = discord_client.user.id
            vietnamese_dictionary.add(chosen_bot_word)
            
            bot_next_target = chosen_bot_word[-1] if session_data.mode == "bot_eng" else chosen_bot_word.split()[-1]
            
            response_description += (
                f"\n\n🤖💗 **Phản đòn chớp nhoáng từ AI Bot:**\n"
                f"# {chosen_bot_word}\n"
                f"🌸 Lượt tiếp theo dành cho bạn, bắt đầu bằng: **`{bot_next_target}`**"
            )

        embed_response = discord.Embed(
            title="✨💗 [ LƯỢT ĐẤU HỢP LỆ THÀNH CÔNG ] 💗✨",
            description=response_description,
            color=COLOR_PINK_NEON
        )
        embed_response.set_footer(text="Black & Pink Word Chain System • Active Session.")
        await incoming_message.channel.send(embed=embed_response)

# =====================================================================
# 7. ĐIỂM KHỞI CHẠY CHƯƠNG TRÌNH CHÍNH
# =====================================================================

if __name__ == "__main__":
    logger.info("Đang tiến hành khởi động ứng dụng Discord Bot...")
    bot_discord_token = os.environ.get('DISCORD_TOKEN')
    
    if not bot_discord_token:
        logger.critical("LỖI NGHIÊM TRỌNG: Không tìm thấy biến môi trường DISCORD_TOKEN.")
    else:
        initialize_keep_alive()
        logger.info("Đang kết nối Discord Client tới máy chủ Discord...")
        try:
            discord_client.run(bot_discord_token)
        except Exception as startup_error:
            logger.critical(f"Không thể khởi chạy Discord Client do lỗi: {startup_error}")
