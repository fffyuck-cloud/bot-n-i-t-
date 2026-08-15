# =====================================================================
# HỆ THỐNG DISCORD BOT NỐI TỪ - BLACK & PINK EDITION (VIETNAMESE & ENGLISH)
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
    return "Black & Pink Word Chain Bot is running smoothly!"

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

COLOR_PINK_NEON = 0xFF69B4   # Hồng neon cá tính
COLOR_DARK_BLACK = 0x111111  # Đen huyền bí
COLOR_HOT_PINK = 0xFF1493    # Hồng đậm nổi bật
COLOR_GOLD_ACCENT = 0xFFD700 # Vàng điểm nhấn thành tích

# =====================================================================
# 3. HỆ THỐNG QUẢN LÝ DỮ LIỆU TỪ ĐIỂN VÀ LƯU TRỮ NGƯỜI DÙNG (TỐI ƯU 4 TRIỆU TỪ)
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
    
    # Tạo set tổng hợp để kiểm tra tồn tại nhanh O(1)
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
        self.mode = None  # 'pvp_vi', 'bot_vi', 'pvp_eng', 'bot_eng'
        self.last_word = ""
        self.used_words = set()
        self.last_author_id = None

    def reset_session(self):
        self.active = False
        self.mode = None
        self.last_word = ""
        self.used_words.clear()
        self.last_author_id = None

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
    # NHÓM LỆNH 1: KÍCH HOẠT NỐI TỪ TIẾNG VIỆT (PvP & BOT)
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
            start_word = "lỗi từ điển"
            next_syllable = ""

        embed_response = discord.Embed(
            title="🖤💗 [ CHẾ ĐỘ NỐI TỪ TIẾNG VIỆT: PvP ] 💗🖤",
            description=(
                "✨ Chào mừng các bạn đến với phòng chơi đối kháng tiếng Việt đỉnh cao!\n"
                "🌸 Yêu cầu bắt buộc: Mỗi từ phải gồm **2 tiếng** (vd: học tập, tập thể).\n"
                "🖤 Hệ thống đã tự động random từ mở màn cho ván đấu:\n"
                f"# {start_word}\n"
                f"🌸 Âm tiết bắt buộc cho từ tiếp theo: **`{next_syllable}`**\n"
                "🖤 Người chơi tiếp theo hãy nhập cụm từ 2 tiếng bắt đầu bằng âm tiết trên.\n"
                "🌸 Chúc các bạn có những giây phút giải trí thật bùng nổ và thăng hoa."
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
            start_word = "lỗi từ điển"
            next_syllable = ""

        embed_response = discord.Embed(
            title="🤖💗 [ THÁCH ĐẤU BOT TIẾNG VIỆT ] 💗🤖",
            description=(
                "✨ Thử thách trí tuệ trực tiếp cùng Trí tuệ nhân tạo (AI Bot) tiếng Việt!\n"
                "🌸 Yêu cầu bắt buộc: Mỗi từ phải gồm **2 tiếng** (vd: vui chơi, chơi đùa).\n"
                "🖤 Hệ thống đã tự động random từ mở màn cho bạn:\n"
                f"# {start_word}\n"
                f"🌸 Âm tiết bắt buộc cho từ tiếp theo: **`{next_syllable}`**\n"
                "🖤 Hãy nhập từ 2 tiếng nối tiếp theo đúng quy tắc để tiếp tục đấu với Bot.\n"
                "🌸 Chúc bạn đánh bại Bot và thiết lập kỷ lục điểm số mới."
            ),
            color=COLOR_HOT_PINK
        )
        embed_response.set_footer(text="Chế độ Solo Bot • Bản quyền Black & Pink Edition.")
        await incoming_message.channel.send(embed=embed_response)
        return

    # -----------------------------------------------------------------
    # NHÓM LỆNH 2: KÍCH HOẠT NỐI TỪ TIẾNG ANH (PvP & BOT)
    # -----------------------------------------------------------------

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
                "🌸 Giao diện Black & Pink huyền bí sẽ đồng hành cùng ván đấu.\n"
                "🖤 Hệ thống đã tự động random từ mở màn cho bạn:\n"
                f"# {start_word}\n"
                f"🌸 Ký tự bắt buộc cho từ tiếp theo: **`{next_char}`**\n"
                "🖤 Người chơi tiếp theo hãy nhập từ tiếng Anh bắt đầu bằng ký tự trên.\n"
                "🌸 Chúc các bạn có những giây phút giải trí thật tuyệt vời."
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
                "🌸 Giao diện Black & Pink huyền bí sẽ đồng hành cùng bạn trong trận chiến này.\n"
                "🖤 Hệ thống đã tự động random từ mở màn cho bạn:\n"
                f"# {start_word}\n"
                f"🌸 Ký tự bắt buộc cho từ tiếp theo: **`{next_char}`**\n"
                "🖤 Hãy nhập từ tiếng Anh nối tiếp theo đúng quy tắc để tiếp tục đấu với Bot.\n"
                "🌸 Chúc bạn đánh bại Bot tiếng Anh và thiết lập kỷ lục điểm số mới."
            ),
            color=COLOR_HOT_PINK
        )
        embed_response.set_footer(text="Chế độ Solo Bot Tiếng Anh • Bản quyền Black & Pink Edition.")
        await incoming_message.channel.send(embed=embed_response)
        return

    # -----------------------------------------------------------------
    # NHÓM LỆNH 3: ĐIỀU KHIỂN HỆ THỐNG VÀ TIỆN ÍCH
    # -----------------------------------------------------------------

    elif raw_content == "?huynoitu":
        if session_data.active:
            session_data.reset_session()
            embed_response = discord.Embed(
                title="🚫🖤 [ KẾT THÚC PHIÊN CHƠI ] 🖤🚫",
                description=(
                    "⚠️ Ván nối từ hiện tại trong kênh này đã chính thức bị hủy bỏ hoàn toàn.\n"
                    "🌸 Toàn bộ bộ nhớ đệm từ vựng đã được làm sạch để chuẩn bị cho phòng mới.\n"
                    "🖤 Cảm ơn các bạn đã tham gia trải nghiệm không gian giải trí.\n"
                    "🌸 Nếu muốn mở lại ván mới, hãy sử dụng lệnh `?noitu` hoặc các lệnh tương đương!"
                ),
                color=COLOR_DARK_BLACK
            )
            await incoming_message.channel.send(embed=embed_response)
        else:
            await incoming_message.channel.send("⚠️ Hiện tại không có ván nối từ nào đang hoạt động trong kênh này.")
        return

    elif raw_content.startswith("?nghia"):
        split_parts = incoming_message.content.split()
        if len(split_parts) > 1:
            query_term = " ".join(split_parts[1:]).lower()
            exists_in_vi = query_term in vietnamese_dictionary
            exists_in_en = query_term in english_dictionary
            
            embed_response = discord.Embed(
                title="📖💗 [ HỆ THỐNG TRA CỨU TỪ ĐIỂN ] 💗📖",
                description=(
                    "✨ Công cụ tra cứu cơ sở dữ liệu ngôn ngữ tốc độ cao tích hợp AI.\n"
                    f"🌸 Từ khóa bạn yêu cầu phân tích hệ thống là: **`{query_term}`**\n"
                    "🖤 Kết quả kiểm tra chi tiết từ các kho từ điển độc quyền:\n"
                    f"  • Từ điển Tiếng Việt (2 tiếng): {'✅ **Tồn tại hợp lệ**' if exists_in_vi else '❌ **Không tìm thấy**'}\n"
                    f"  • Từ điển Tiếng Anh (Khủng 4M): {'✅ **Tồn tại hợp lệ**' if exists_in_en else '❌ **Không tìm thấy**'}\n"
                    "🌸 Hãy tiếp tục khám phá thêm nhiều từ vựng độc đáo khác cùng chúng tôi!"
                ),
                color=COLOR_PINK_NEON
            )
            embed_response.set_footer(text="Dictionary Lookup Tool • Black & Pink Style.")
            await incoming_message.channel.send(embed=embed_response)
        else:
            await incoming_message.channel.send("⚠️ Vui lòng chỉ định từ cần tra cứu theo đúng cú pháp: `?nghia <từ>`")
        return

    elif raw_content == "?rank":
        user_record = fetch_user_record(incoming_message.author.id)
        embed_response = discord.Embed(
            title=f"🏆💗 [ BẢNG THÀNH TÍCH: {incoming_message.author.name.upper()} ] 💗🏆",
            description=(
                "✨ Chào mừng bạn đến với trung tâm thông tin dữ liệu cá nhân.\n"
                "🌸 Dưới đây là các thông số hoạt động tích lũy của bạn trên hệ thống:\n"
                f"  • Tổng điểm tích lũy hiện tại: **`{user_record['score']} điểm`**\n"
                f"  • Chuỗi thắng liên tiếp: **`{user_record['streak']} trận`**\n"
                f"  • Tổng số từ đã đóng góp: **`{user_record['games_played']} từ`**\n"
                "🖤 Danh hiệu cá nhân: **`Chuyên gia từ vựng Black & Pink`**\n"
                "🌸 Hãy chăm chỉ tham gia các ván đấu và điểm danh hằng ngày\n"
                "🖤 để củng cố vị thế dẫn đầu của mình trên bảng vàng danh vọng!"
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
                "🌸 Hệ thống đã tự động chuyển phần thưởng vào tài khoản của bạn:\n"
                "  • Quà tặng nhận được: **`+50 điểm tích lũy`**\n"
                f"  • Tổng điểm số hiện tại: **`{user_record['score']} điểm`**\n"
                "🖤 Hãy ghi nhớ quay lại điểm danh đều đặn mỗi ngày\n"
                "🌸 để không bỏ lỡ bất kỳ phần quà giá trị nào từ hệ thống,\n"
                "🖤 đồng thời tích lũy nguồn điểm số khổng lồ cho bản thân mình!"
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
                "✨ Chào mừng bạn đến với mục trợ giúp toàn diện của hệ thống.\n"
                "🌸 Danh sách toàn bộ các lệnh điều khiển và chế độ chơi được hỗ trợ:\n"
                "🖤 **Nhóm lệnh trò chơi chính (Tự động random từ mở màn):**\n"
                "  • `?noitu` - Kích hoạt phòng nối từ tiếng Việt (2 tiếng, PvP)\n"
                "  • `?noituubot` - Thách đấu nối từ tiếng Việt (2 tiếng, AI Bot)\n"
                "  • `?noitueng` - Kích hoạt phòng nối từ tiếng Anh (PvP)\n"
                "  • `?noituuboteng` - Thách đấu nối từ tiếng Anh với AI Bot\n"
                "  • `?huynoitu` - Dừng và hủy ván đấu hiện tại trong kênh\n"
                "🖤 **Nhóm lệnh tiện ích & cá nhân:**\n"
                "  • `?nghia <từ>` - Tra cứu từ vựng trực tiếp trong cơ sở dữ liệu\n"
                "  • `?rank` - Xem bảng thành tích và điểm số cá nhân\n"
                "  • `?daily` - Nhận phần thưởng điểm danh hằng ngày\n"
                "  • `?help` - Hiển thị bảng hướng dẫn chi tiết này\n"
                "🌸 Hãy tận hưởng không gian giải trí độc đáo mang phong cách Đen & Hồng!"
            ),
            color=COLOR_PINK_NEON
        )
        embed_response.set_footer(text="Help Center & Command Guide • Black & Pink Edition.")
        await incoming_message.channel.send(embed=embed_response)
        return

    # -----------------------------------------------------------------
    # KHU VỰC 4: XỬ LÝ LOGIC LUẬT CHƠI NỐI TỪ THỰC TẾ
    # -----------------------------------------------------------------

    if session_data.active:
        is_english_mode = "eng" in session_data.mode
        active_dictionary = english_dictionary if is_english_mode else vietnamese_dictionary

        # Kiểm tra định dạng số từ/tiếng bắt buộc
        if not is_english_mode and len(raw_content.split()) != 2:
            embed_response = discord.Embed(
                title="⚠️💗 [ SAI ĐỊNH DẠNG TỪ ] 💗⚠️",
                description=(
                    "⚠️ Chế độ tiếng Việt bắt buộc phải nhập đúng **2 tiếng** (có dấu cách ở giữa, vd: `học tập`).\n"
                    "🌸 Vui lòng kiểm tra lại cấu trúc từ của bạn và thử nhập lại nhé!"
                ),
                color=COLOR_DARK_BLACK
            )
            await incoming_message.channel.send(embed=embed_response)
            return

        if is_english_mode and len(raw_content.split()) != 1:
            embed_response = discord.Embed(
                title="⚠️💗 [ SAI ĐỊNH DẠNG TỪ ] 💗⚠️",
                description=(
                    "⚠️ Chế độ tiếng Anh yêu cầu nhập đúng **1 từ đơn** duy nhất không chứa khoảng trắng.\n"
                    "🌸 Vui lòng kiểm tra lại từ của bạn và thử nhập lại nhé!"
                ),
                color=COLOR_DARK_BLACK
            )
            await incoming_message.channel.send(embed=embed_response)
            return

        # Kiểm tra từ có tồn tại trong từ điển không (O(1) cực nhanh)
        if raw_content not in active_dictionary:
            embed_response = discord.Embed(
                title="❌💗 [ TỪ KHÔNG HỢP LỆ ] 💗❌",
                description=(
                    "⚠️ Từ bạn vừa nhập không vượt qua được bộ lọc kiểm duyệt của hệ thống.\n"
                    "🌸 Nguyên nhân có thể do: Từ không tồn tại trong từ điển hoặc sai chính tả.\n"
                    "🖤 Vui lòng kiểm tra lại thật kỹ và lựa chọn một từ vựng khác chính xác hơn nhé!"
                ),
                color=COLOR_DARK_BLACK
            )
            await incoming_message.channel.send(embed=embed_response)
            return

        # Kiểm tra từ đã được sử dụng trong ván này chưa
        if raw_content in session_data.used_words:
            embed_response = discord.Embed(
                title="⚠️💗 [ TỪ ĐÃ ĐƯỢC SỬ DỤNG ] 💗⚠️",
                description=(
                    "⚠️ Từ này đã xuất hiện và được sử dụng trước đó trong ván đấu hiện tại rồi!\n"
                    "🌸 Mỗi từ vựng chỉ được phép ghi nhận một lần duy nhất trong suốt ván chơi.\n"
                    "🖤 Hãy tư duy nhanh chóng để tìm ra một từ mới hoàn toàn chưa được dùng nhé!"
                ),
                color=COLOR_HOT_PINK
            )
            await incoming_message.channel.send(embed=embed_response)
            return

        # Kiểm tra người chơi đánh liền 2 lượt của chính mình (chế độ PvP)
        if "pvp" in session_data.mode and session_data.last_author_id == incoming_message.author.id:
            embed_response = discord.Embed(
                title="⚠️💗 [ VI PHẠM LIÊN TỤC LƯỢT ] 💗⚠️",
                description=(
                    "⚠️ Bạn không được phép tự nối từ của chính mình trong chế độ PvP!\n"
                    "🌸 Hãy nhường cơ hội cho các thành viên khác trong kênh cùng tham gia.\n"
                    "🖤 Đợi người chơi kế tiếp hoàn thành lượt đi rồi bạn mới tiếp tục đánh nhé!"
                ),
                color=COLOR_DARK_BLACK
            )
            await incoming_message.channel.send(embed=embed_response)
            return

        # Kiểm tra quy tắc nối từ thực tế
        if session_data.last_word != "":
            if is_english_mode:
                required_char = session_data.last_word[-1]
                if not raw_content.startswith(required_char):
                    embed_response = discord.Embed(
                        title="⚠️💗 [ SAI QUY TẮC NỐI TỪ ] 💗⚠️",
                        description=(
                            "✨ Bạn đã vi phạm quy tắc nối từ tiếng Anh rồi!\n"
                            f"🌸 Từ tiếp theo bắt buộc phải bắt đầu bằng ký tự: **`{required_char}`**\n"
                            "🖤 Hãy kiểm tra lại ký tự cuối của từ trước và thử lại nhé!"
                        ),
                        color=COLOR_DARK_BLACK
                    )
                    await incoming_message.channel.send(embed=embed_response)
                    return
            else:
                required_syllable = session_data.last_word.split()[-1]
                if raw_content.split()[0] != required_syllable:
                    embed_response = discord.Embed(
                        title="⚠️💗 [ SAI QUY TẮC NỐI TỪ ] 💗⚠️",
                        description=(
                            "✨ Bạn đã đánh rơi nhịp nối quan trọng của ván đấu rồi!\n"
                            f"🌸 Từ tiếp theo bắt buộc phải bắt đầu bằng âm tiết: **`{required_syllable}`**\n"
                            "🖤 Hãy tập trung quan sát kỹ tiếng cuối cùng của từ trước và thử lại ngay!"
                        ),
                        color=COLOR_DARK_BLACK
                    )
                    await incoming_message.channel.send(embed=embed_response)
                    return

        # Cập nhật trạng thái phiên chơi hợp lệ
        session_data.last_word = raw_content
        session_data.used_words.add(raw_content)
        session_data.last_author_id = incoming_message.author.id

        # Cập nhật điểm số và thống kê cá nhân người dùng
        user_record = fetch_user_record(incoming_message.author.id)
        user_record["score"] += 10
        user_record["streak"] += 1
        user_record["games_played"] += 1
        save_user_statistics_database(user_stats_database)

        if is_english_mode:
            next_target = session_data.last_word[-1]
        else:
            next_target = session_data.last_word.split()[-1]

        response_description = (
            "✨ **Đường đi nước bước hoàn hảo! (+10 điểm tích lũy)**\n"
            f"🌸 Từ vừa được hệ thống ghi nhận: `{raw_content}`\n"
            f"🖤 Âm tiết / ký tự bắt buộc cho lượt kế tiếp: **`{next_target}`**\n"
            "🌸 Sẵn sàng tinh thần chưa? Đưa ra câu trả lời tiếp theo thật nhanh nào!"
        )

        # Xử lý phản hồi siêu tốc từ AI Bot (Sử dụng Indexing 4M từ)
        if "bot" in session_data.mode:
            if is_english_mode:
                # Chỉ lọc các từ bắt đầu bằng đúng ký tự yêu cầu (Cực kỳ tối ưu cho 4M từ)
                target_pool = english_dict_by_letter.get(next_target, set())
                possible_bot_words = [
                    candidate for candidate in target_pool 
                    if candidate not in session_data.used_words
                ]
            else:
                possible_bot_words = [
                    candidate for candidate in vietnamese_dictionary 
                    if candidate.split()[0] == next_target and candidate not in session_data.used_words
                ]

            if possible_bot_words:
                chosen_bot_word = random.choice(possible_bot_words)
                session_data.last_word = chosen_bot_word
                session_data.used_words.add(chosen_bot_word)
                session_data.last_author_id = discord_client.user.id
                
                if is_english_mode:
                    bot_next_target = chosen_bot_word[-1]
                else:
                    bot_next_target = chosen_bot_word.split()[-1]
                
                response_description += (
                    f"\n\n🤖💗 **Phản đòn chớp nhoáng từ AI Bot:**\n"
                    f"# {chosen_bot_word}\n"
                    f"🌸 Lượt tiếp theo dành cho bạn, bắt đầu bằng: **`{bot_next_target}`**"
                )
            else:
                response_description += (
                    f"\n\n🎉💗 **CHIẾN THẮNG TUYỆT ĐỐI!**\n"
                    "✨ AI Bot đã hoàn toàn cạn kiệt từ vựng để nối tiếp.\n"
                    "🖤 Bạn đã xuất sắc giành chiến thắng chung cuộc trong phòng này!"
                )
                session_data.reset_session()

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
