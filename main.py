# =====================================================================
# BLACK & PINK PURE FUN - ULTIMATE ENTERPRISE (FULL FILE INTEGRATION)
# Tích hợp toàn bộ dữ liệu từ các file .txt trên GitHub repository.
# Không có hệ thống kinh tế (Không Coins, Shop, Rank, Cờ bạc).
# =====================================================================

import os
import random
import logging
import threading
from flask import Flask
import discord
from discord.ext import commands

# =====================================================================
# 1. CẤU HÌNH LOGGING & KEEP-ALIVE WEB SERVER
# =====================================================================

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("BlackPinkPureFunEnterprise")

app = Flask("KeepAliveServer")

@app.route('/')
def home():
    return "Black & Pink Pure Fun Bot is active and running 24/7!"

def run_flask():
    try:
        app.run(host='0.0.0.0', port=8080)
    except Exception as e:
        logger.error(f"Lỗi khởi chạy Web Server Keep-Alive: {e}")

threading.Thread(target=run_flask, daemon=True).start()

# =====================================================================
# 2. HỆ THỐNG NẠP DỮ LIỆU TỪ CÁC FILE .TXT TRÊN GITHUB
# =====================================================================

def load_words_from_file(filename, default_set):
    """Hàm đọc file .txt linh hoạt, tự động fallback nếu file trống hoặc lỗi."""
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                words = {line.strip().lower() for line in f if line.strip()}
            if words:
                logger.info(f"Đã nạp thành công {len(words)} dòng từ file: {filename}")
                return words
        except Exception as e:
            logger.error(f"Lỗi khi đọc file {filename}: {e}")
    logger.warning(f"Không tìm thấy hoặc file {filename} trống. Sử dụng dữ liệu dự phòng.")
    return default_set

# Dữ liệu dự phòng mặc định nếu file chưa được tạo kịp trên GitHub
DEFAULT_VIETNAMESE = {"học tập", "tập thể", "thể thao", "áo quần", "nước non", "non sông"}
DEFAULT_ENGLISH = {"learning code", "code python", "python bot", "discord api"}
DEFAULT_COUNTRIES_VN = {"việt nam", "pháp", "mỹ", "nhật bản", "hàn quốc", "anh", "đức"}
DEFAULT_COUNTRIES_EN = {"vietnam", "france", "usa", "japan", "south korea", "uk", "germany"}

# Nạp toàn bộ dữ liệu từ các file .txt của bạn
VIETNAMESE_DICT = load_words_from_file("tu dien.txt", DEFAULT_VIETNAMESE)
WORDS_DICT = load_words_from_file("words.txt", DEFAULT_VIETNAMESE)
ENGLISH_DICT = load_words_from_file("tu dien tieng anh.txt", DEFAULT_ENGLISH)
COUNTRIES_VN_DICT = load_words_from_file("quoc gia vn.txt", DEFAULT_COUNTRIES_VN)
COUNTRIES_EN_DICT = load_words_from_file("quoc gia en.txt", DEFAULT_COUNTRIES_EN)

# =====================================================================
# 3. QUẢN LÝ PHIÊN CHƠI (GAME SESSIONS)
# =====================================================================

class GameSession:
    def __init__(self):
        self.active = False
        self.mode = None  # 'pvp_vi', 'bot_vi', 'pvp_en', 'vua_vi', 'doan_quoc_gia'
        self.last_word = ""
        self.used_words = set()
        self.turn_count = 0
        self.scrambled_target = None
        self.secret_country = None

    def reset(self):
        self.active = False
        self.mode = None
        self.last_word = ""
        self.used_words.clear()
        self.turn_count = 0
        self.scrambled_target = None
        self.secret_country = None

channel_sessions = {}

def get_session(channel_id):
    if channel_id not in channel_sessions:
        channel_sessions[channel_id] = GameSession()
    return channel_sessions[channel_id]

# =====================================================================
# 4. HÀM TIỆN ÍCH & EMBED
# =====================================================================

def scramble_word(word):
    parts = word.split()
    if len(parts) > 1:
        shuffled = parts.copy()
        random.shuffle(shuffled)
        return " ".join(shuffled)
    return word

def create_embed(title, description, color=0xFF69B4):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="Black & Pink Pure Fun • Enterprise Edition")
    return embed

# =====================================================================
# 5. KHỞI TẠO DISCORD BOT & LỆNH HỆ THỐNG
# =====================================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)

@bot.event
async def on_ready():
    logger.info(f"Bot đã đăng nhập thành công: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="?help | Nối từ & Trò chơi"))

@bot.command(name="ping")
async def cmd_ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(embed=create_embed("🏓 Pong!", f"Độ trễ hệ thống: **{latency}ms**", 0x00FF00))

@bot.command(name="about")
async def cmd_about(ctx):
    desc = (
        "🤖 **Black & Pink Pure Fun Bot**\n"
        "Phiên bản tối ưu hóa sử dụng dữ liệu trực tiếp từ các tệp `.txt`.\n"
        "Hoàn toàn tập trung vào giải trí, không có hệ thống tiền tệ hay cờ bạc."
    )
    await ctx.send(embed=create_embed("🖤💗 Về Bot", desc))

@bot.command(name="help")
async def cmd_help(ctx):
    help_text = (
        "**🎮 Nhóm Trò Chơi Nối Từ & Từ Vựng:**\n"
        "`?noitu` - Nối từ Tiếng Việt (PvP dùng `tu dien.txt`)\n"
        "`?botnoitu` - Đấu Nối Từ Tiếng Việt với Bot\n"
        "`?noituen` - Nối từ Tiếng Anh (dùng `tu dien tieng anh.txt`)\n"
        "`?vuatiengviet` - Trò chơi Vua Tiếng Việt\n"
        "`?doanquocgia` - Đoán tên quốc gia (dùng `quoc gia vn.txt`)\n\n"
        "**⚙️ Lệnh Điều Khiển:**\n"
        "`?huygame` - Dừng phiên chơi hiện tại trong kênh\n"
        "`?ping` - Kiểm tra tốc độ bot"
    )
    await ctx.send(embed=create_embed("📖 Menu Trợ Giúp", help_text))

# =====================================================================
# 6. CÁC LỆNH KHỞI TẠO TRÒ CHƠI
# =====================================================================

@bot.command(name="noitu")
async def cmd_noitu(ctx):
    session = get_session(ctx.channel.id)
    session.reset()
    session.active = True
    session.mode = "pvp_vi"
    session.last_word = random.choice(list(VIETNAMESE_DICT))
    session.used_words.add(session.last_word)
    session.turn_count = 1

    msg = (
        f"✅ **Bắt đầu Nối Từ Tiếng Việt (PvP)!**\n"
        f"📌 Từ mở màn (`tu dien.txt`): **{session.last_word}**\n"
        f"🌸 Âm tiết tiếp theo: **`{session.last_word.split()[-1]}`**"
    )
    await ctx.send(embed=create_embed("🎮 Nối Từ Tiếng Việt", msg))

@bot.command(name="botnoitu")
async def cmd_botnoitu(ctx):
    session = get_session(ctx.channel.id)
    session.reset()
    session.active = True
    session.mode = "bot_vi"
    session.last_word = random.choice(list(VIETNAMESE_DICT))
    session.used_words.add(session.last_word)
    session.turn_count = 1

    msg = (
        f"🤖 **Đấu Nối Từ với Bot!**\n"
        f"📌 Từ mở màn: **{session.last_word}**\n"
        f"🌸 Lượt của bạn bắt đầu với âm tiết: **`{session.last_word.split()[-1]}`**"
    )
    await ctx.send(embed=create_embed("🤖 Đấu Với Bot", msg))

@bot.command(name="noituen")
async def cmd_noituen(ctx):
    session = get_session(ctx.channel.id)
    session.reset()
    session.active = True
    session.mode = "pvp_en"
    session.last_word = random.choice(list(ENGLISH_DICT))
    session.used_words.add(session.last_word)
    session.turn_count = 1

    msg = (
        f"🇬🇧 **English Word Chain (PvP)!**\n"
        f"📌 Start Word (`tu dien tieng anh.txt`): **{session.last_word}**\n"
        f"🔤 Next word must start with letter: **`{session.last_word[-1]}`**"
    )
    await ctx.send(embed=create_embed("🇬🇧 English Word Chain", msg))

@bot.command(name="vuatiengviet")
async def cmd_vuatiengviet(ctx):
    session = get_session(ctx.channel.id)
    session.reset()
    session.active = True
    session.mode = "vua_vi"
    session.scrambled_target = random.choice(list(VIETNAMESE_DICT))
    
    puzzle = scramble_word(session.scrambled_target)
    msg = (
        f"👑 **Vua Tiếng Việt đã bắt đầu!**\n"
        f"Hãy sắp xếp lại các tiếng sau thành từ có nghĩa:\n\n"
        f"# 🔀 `{puzzle}`"
    )
    await ctx.send(embed=create_embed("👑 Vua Tiếng Việt", msg, 0xFFD700))

@bot.command(name="doanquocgia")
async def cmd_doanquocgia(ctx):
    session = get_session(ctx.channel.id)
    session.reset()
    session.active = True
    session.mode = "doan_quoc_gia"
    
    countries = list(COUNTRIES_VN_DICT)
    session.secret_country = random.choice(countries)
    hint = session.secret_country[0].upper() + " _ " * (len(session.secret_country) - 1)

    msg = (
        f"🌍 **Trò chơi Đoán Tên Quốc Gia!** (`quoc gia vn.txt`)\n"
        f"Gợi ý từ khóa: **`{hint}`**\n"
        f"Hãy gõ tên quốc gia đầy đủ vào kênh để chiến thắng!"
    )
    await ctx.send(embed=create_embed("🌍 Đoán Quốc Gia", msg))

@bot.command(name="huygame")
async def cmd_huygame(ctx):
    get_session(ctx.channel.id).reset()
    await ctx.send(embed=create_embed("🚫 Đã hủy", "Phiên chơi trong kênh này đã được kết thúc."))

# =====================================================================
# 7. XỬ LÝ SỰ KIỆN TIN NHẮN (GAME ENGINE)
# =====================================================================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    session = get_session(message.channel.id)
    if not session.active:
        return

    content = message.content.lower().strip()

    # 1. Mode: Vua Tiếng Việt
    if session.mode == "vua_vi":
        if content == session.scrambled_target:
            await message.channel.send(embed=create_embed("✅ Chính xác!", f"✨ Chúc mừng {message.author.mention} đã giải đúng từ: **`{session.scrambled_target}`**!", 0x00FF00))
            session.reset()
        else:
            await message.add_reaction("❌")

    # 2. Mode: Đoán Quốc Gia
    elif session.mode == "doan_quoc_gia":
        if content == session.secret_country:
            await message.channel.send(embed=create_embed("🌍 CHIẾN THẮNG!", f"✨ {message.author.mention} đã đoán đúng quốc gia: **`{session.secret_country.upper()}`**!", 0x00FF00))
            session.reset()
        else:
            await message.add_reaction("❌")

    # 3. Mode: Nối từ Tiếng Việt (PvP)
    elif session.mode == "pvp_vi":
        if len(content.split()) != 2:
            return
        if content in session.used_words:
            await message.channel.send("❌ Từ này đã được sử dụng rồi!")
            return
        required = session.last_word.split()[-1]
        if content.split()[0] != required:
            await message.channel.send(f"❌ Từ phải bắt đầu bằng âm tiết: **`{required}`**")
            return

        session.last_word = content
        session.used_words.add(content)
        session.turn_count += 1
        await message.channel.send(f"✅ Hợp lệ (Lượt {session.turn_count})! Tiếp theo: **`{content.split()[-1]}`**")

    # 4. Mode: Đấu với Bot Tiếng Việt
    elif session.mode == "bot_vi":
        if len(content.split()) != 2:
            return
        if content in session.used_words:
            await message.channel.send("❌ Từ này đã được sử dụng rồi!")
            return
        required = session.last_word.split()[-1]
        if content.split()[0] != required:
            await message.channel.send(f"❌ Từ phải bắt đầu bằng âm tiết: **`{required}`**")
            return

        session.last_word = content
        session.used_words.add(content)
        session.turn_count += 1

        user_next = content.split()[-1]
        possible_bot_words = [w for w in VIETNAMESE_DICT if w.split()[0] == user_next and w not in session.used_words]

        if possible_bot_words:
            bot_word = random.choice(possible_bot_words)
            session.last_word = bot_word
            session.used_words.add(bot_word)
            session.turn_count += 1
            await message.channel.send(
                f"🤖 **Bot nối:** `{bot_word}`\n"
                f"🌸 Lượt tiếp theo của bạn bắt đầu bằng: **`{bot_word.split()[-1]}`**"
            )
        else:
            await message.channel.send(f"🎉 Chúc mừng {message.author.mention}! Bot đã cạn từ vựng và chịu thua.")
            session.reset()

    # 5. Mode: Nối từ Tiếng Anh (English Word Chain)
    elif session.mode == "pvp_en":
        if not content.isalpha():
            return
        if content in session.used_words:
            await message.channel.send("❌ Word already used!")
            return
        required_char = session.last_word[-1]
        if content[0] != required_char:
            await message.channel.send(f"❌ Word must start with letter: **`{required_char.upper()}`**")
            return

        session.last_word = content
        session.used_words.add(content)
        session.turn_count += 1
        await message.channel.send(f"✅ Valid! Next word must start with letter: **`{content[-1].upper()}`**")

# =====================================================================
# 8. KHỞI CHẠY CHƯƠNG TRÌNH
# =====================================================================

if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        logger.critical("LỖI: Không tìm thấy biến môi trường DISCORD_TOKEN.")
