import os
import json
import random
import logging
import asyncio
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands

# =====================================================================
# 1. CẤU HÌNH HỆ THỐNG & LOGGING
# =====================================================================

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("WordChainBot")

# Khởi động server phụ để giữ bot chạy 24/7 (nếu dùng Replit/Render)
app = Flask("")

@app.route('/')
def home():
    return "Bot Nối Từ đang hoạt động trực tuyến!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    logger.info("Đã kích hoạt Keep-Alive Web Server thành công.")

# =====================================================================
# 2. QUẢN LÝ DỮ LIỆU TỪ ĐIỂN VÀ THỐNG KÊ NGƯỜI DÙNG
# =====================================================================

STATS_FILE = "user_stats.json"

def load_vocabulary(file_path):
    """Đọc và chuẩn hóa toàn bộ từ vựng từ tệp văn bản"""
    words = set()
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    cleaned = line.strip().lower()
                    if cleaned:
                        words.add(cleaned)
            logger.info(f"Đã nạp thành công {len(words)} từ từ {file_path}")
        else:
            logger.warning(f"Không tìm thấy tệp dữ liệu: {file_path}")
    except Exception as e:
        logger.error(f"Lỗi khi đọc tệp {file_path}: {e}")
    return words

def load_user_stats():
    """Tải dữ liệu điểm số người dùng từ tệp JSON"""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Lỗi đọc file thống kê: {e}")
    return {}

def save_user_stats(stats):
    """Lưu dữ liệu điểm số người dùng vào tệp JSON"""
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Lỗi lưu file thống kê: {e}")

# Tải từ điển vào bộ nhớ RAM
vietnam_dict = load_vocabulary('tu dien.txt')
vietnam_dict.update(load_vocabulary('words.txt'))
english_dict = load_vocabulary('words_en.txt')

user_stats_db = load_user_stats()

# =====================================================================
# 3. LỚP QUẢN LÝ PHIÊN CHƠI (SESSION MANAGER)
# =====================================================================

class GameSession:
    def __init__(self):
        self.active = False
        self.mode = None  # 'pvp_vi', 'bot_vi', 'pvp_eng', 'bot_eng'
        self.last_word = ""
        self.used_words = set()
        self.last_author_id = None

    def reset(self):
        self.active = False
        self.mode = None
        self.last_word = ""
        self.used_words.clear()
        self.last_author_id = None

channel_sessions = {}

def get_session(channel_id):
    if channel_id not in channel_sessions:
        channel_sessions[channel_id] = GameSession()
    return channel_sessions[channel_id]

def get_user_data(user_id):
    uid_str = str(user_id)
    if uid_str not in user_stats_db:
        user_stats_db[uid_str] = {
            "score": 0,
            "streak": 0,
            "games_played": 0,
            "last_daily": ""
        }
    return user_stats_db[uid_str]

# =====================================================================
# 4. KHỞI TẠO DISCORD BOT CLIENT
# =====================================================================

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logger.info(f"Bot đã đăng nhập thành công với tài khoản: {client.user}")
    await client.change_presence(activity=discord.Game(name="?help | Trò chơi Nối Từ"))

# =====================================================================
# 5. XỬ LÝ SỰ KIỆN TIN NHẮN & CÁC LỆNH TRÒ CHƠI
# =====================================================================

@client.event
async def on_message(message):
    if message.author.bot:
        return

    channel_id = message.channel.id
    msg = message.content.lower().strip()
    session = get_session(channel_id)

    # -----------------------------------------------------------------
    # KHU VỰC ĐIỀU KHIỂN LỆNH HỆ THỐNG
    # -----------------------------------------------------------------

    if msg == "?noitu":
        session.reset()
        session.active = True
        session.mode = "pvp_vi"
        embed = discord.Embed(
            title="🎮 BẮT ĐẦU NỐI TỪ TIẾNG VIỆT (PvP)",
            description="Phòng chơi giữa người với người đã được kích hoạt!\nHãy nhập từ tiếng Việt hợp lệ đầu tiên.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Gõ ?huynoitu để kết thúc trận đấu.")
        await message.channel.send(embed=embed)
        return

    elif msg == "?noituubot":
        session.reset()
        session.active = True
        session.mode = "bot_vi"
        embed = discord.Embed(
            title="🤖 ĐẤU NỐI TỪ VỚI BOT (TIẾNG VIỆT)",
            description="Chế độ thách đấu Bot tiếng Việt đã sẵn sàng!\nHãy nhập từ đầu tiên để bắt đầu.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Chúc bạn may mắn khi đấu với trí tuệ nhân tạo!")
        await message.channel.send(embed=embed)
        return

    elif msg == "?noitueng":
        session.reset()
        session.active = True
        session.mode = "pvp_eng"
        embed = discord.Embed(
            title="🇬🇧 ENGLISH WORD CHAIN (PvP)",
            description="English player-vs-player mode is active!\nType the first English word.",
            color=discord.Color.purple()
        )
        embed.set_footer(text="Type ?huynoitu to stop the game.")
        await message.channel.send(embed=embed)
        return

    elif msg == "?noituuboteng":
        session.reset()
        session.active = True
        session.mode = "bot_eng"
        embed = discord.Embed(
            title="🤖🇬🇧 ENGLISH VS BOT",
            description="English bot challenge mode is active!\nType the first English word.",
            color=discord.Color.orange()
        )
        embed.set_footer(text="Show your vocabulary skills against the bot!")
        await message.channel.send(embed=embed)
        return

    elif msg == "?huynoitu":
        if session.active:
            session.reset()
            embed = discord.Embed(
                title="🚫 ĐÃ HỦY TRẬN ĐẤU",
                description="Ván nối từ trong kênh này đã được dừng lại.",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("⚠️ Hiện tại không có ván nối từ nào đang diễn ra trong kênh này.")
        return

    elif msg.startswith("?nghia"):
        parts = message.content.split()
        if len(parts) > 1:
            query_word = parts[1].lower()
            found_vi = query_word in vietnam_dict
            found_en = query_word in english_dict
            
            embed = discord.Embed(title="📖 TRA CỨU TỪ ĐIỂN HỆ THỐNG", color=discord.Color.gold())
            embed.add_field(name="Từ cần tra", value=parts[1], inline=False)
            embed.add_field(name="Từ điển Tiếng Việt", value="✅ Tồn tại" if found_vi else "❌ Không có", inline=True)
            embed.add_field(name="Từ điển Tiếng Anh", value="✅ Tồn tại" if found_en else "❌ Không có", inline=True)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("⚠️ Vui lòng chỉ định từ cần tra cứu theo cú pháp: `?nghia <từ>`")
        return

    elif msg == "?rank":
        user_data = get_user_data(message.author.id)
        embed = discord.Embed(title=f"🏆 THÀNH TÍCH CỦA {message.author.name.upper()}", color=discord.Color.gold())
        embed.add_field(name="Điểm tích lũy", value=f"`{user_data['score']} điểm`", inline=True)
        embed.add_field(name="Chuỗi thắng", value=f"`{user_data['streak']} trận`", inline=True)
        embed.add_field(name="Đã tham gia", value=f"`{user_data['games_played']} từ`", inline=True)
        embed.set_thumbnail(url=message.author.display_avatar.url)
        await message.channel.send(embed=embed)
        return

    elif msg == "?daily":
        user_data = get_user_data(message.author.id)
        user_data["score"] += 50
        save_user_stats(user_stats_db)
        
        embed = discord.Embed(
            title="🎁 ĐIỂM DANH HÀNG NGÀY THÀNH CÔNG",
            description="Bạn đã nhận được phần thưởng điểm danh hôm nay!",
            color=discord.Color.teal()
        )
        embed.add_field(name="Phần thưởng", value="`+50 điểm`", inline=True)
        embed.add_field(name="Tổng điểm hiện tại", value=f"`{user_data['score']} điểm`", inline=True)
        await message.channel.send(embed=embed)
        return

    elif msg == "?help":
        embed = discord.Embed(
            title="📖 TRUNG TÂM HƯỚNG DẪN BOT NỐI TỪ",
            description="Danh sách toàn bộ các lệnh và chế độ chơi được hỗ trợ:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🎮 Chế độ chơi",
            value=(
                "• `?noitu` - Chơi nối từ tiếng Việt (PvP)\n"
                "• `?noituubot` - Đấu nối từ tiếng Việt với Bot\n"
                "• `?noitueng` - Chơi nối từ tiếng Anh (PvP)\n"
                "• `?noituuboteng` - Đấu nối từ tiếng Anh với Bot\n"
                "• `?huynoitu` - Dừng trận đấu hiện tại"
            ),
            inline=False
        )
        embed.add_field(
            name="🛠️ Tiện ích & Thống kê",
            value=(
                "• `?nghia <từ>` - Tra cứu từ vựng trong hệ thống\n"
                "• `?rank` - Xem bảng điểm và thứ hạng cá nhân\n"
                "• `?daily` - Nhận thưởng điểm danh hằng ngày\n"
                "• `?help` - Hiển thị bảng trợ giúp này"
            ),
            inline=False
        )
        embed.set_footer(text="Hệ thống cơ sở dữ liệu tích hợp tự động cập nhật liên tục.")
        await message.channel.send(embed=embed)
        return

    # -----------------------------------------------------------------
    # KHU VỰC XỬ LÝ LOGIC LUẬT CHƠI NỐI TỪ
    # -----------------------------------------------------------------

    if session.active:
        is_english = "eng" in session.mode
        current_dict = english_dict if is_english else vietnam_dict

        # Kiểm tra từ có tồn tại trong từ điển không
        if msg not in current_dict:
            embed = discord.Embed(
                description=f"❌ **Từ này không có trong từ điển hệ thống!**",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
            return

        # Kiểm tra từ đã được sử dụng trong ván này chưa
        if msg in session.used_words:
            embed = discord.Embed(
                description=f"⚠️ **Từ này đã được sử dụng trước đó trong ván rồi!**",
                color=discord.Color.orange()
            )
            await message.channel.send(embed=embed)
            return

        # Kiểm tra người chơi có đánh liền 2 từ của chính mình không (trong chế độ PvP)
        if "pvp" in session.mode and session.last_author_id == message.author.id:
            embed = discord.Embed(
                description=f"⚠️ **Bạn không được tự nối từ của chính mình!** Hãy đợi người chơi khác.",
                color=discord.Color.orange()
            )
            await message.channel.send(embed=embed)
            return

        # Kiểm tra quy tắc nối từ (ký tự bắt đầu phải trùng với ký tự kết thúc từ trước)
        if session.last_word != "":
            last_part = session.last_word.split()[-1]
            if not msg.startswith(last_part):
                embed = discord.Embed(
                    description=f"⚠️ **Sai quy tắc nối từ!** Từ phải bắt đầu bằng: **'{last_part}'**",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
                return

        # Cập nhật trạng thái hợp lệ
        session.last_word = msg
        session.used_words.add(msg)
        session.last_author_id = message.author.id

        # Cập nhật điểm số và thống kê người dùng
        user_data = get_user_data(message.author.id)
        user_data["score"] += 10
        user_data["streak"] += 1
        user_data["games_played"] += 1
        save_user_stats(user_stats_db)

        next_required = msg.split()[-1]
        response_desc = f"✅ **Hợp lệ!** (+10 điểm)\n👉 Từ tiếp theo phải bắt đầu bằng: **'{next_required}'**"

        # Xử lý phản hồi tự động từ Bot nếu là chế độ Đấu với Bot
        if "bot" in session.mode:
            possible_words = [w for w in current_dict if w.startswith(next_required) and w not in session.used_words]
            if possible_words:
                bot_choice = random.choice(possible_words)
                session.last_word = bot_choice
                session.used_words.add(bot_choice)
                session.last_author_id = client.user.id
                bot_next = bot_choice.split()[-1]
                response_desc += f"\n\n🤖 **Bot đáp trả:** `{bot_choice}`\n👉 Tới lượt bạn, từ phải bắt đầu bằng: **'{bot_next}'**"
            else:
                response_desc += f"\n\n🎉 **Chúc mừng bạn!** Bot không còn từ nào để nối tiếp, bạn đã giành chiến thắng tuyệt đối!"
                session.reset()

        embed = discord.Embed(description=response_desc, color=discord.Color.green())
        await message.channel.send(embed=embed)

# =====================================================================
# 6. KHỞI CHẠY CHƯƠNG TRÌNH CHÍNH
# =====================================================================

if __name__ == "__main__":
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        logger.critical("Lỗi nghiêm trọng: Không tìm thấy biến môi trường DISCORD_TOKEN.")
    else:
        keep_alive()
        logger.info("Đang khởi chạy Discord Bot Client...")
        client.run(token)
