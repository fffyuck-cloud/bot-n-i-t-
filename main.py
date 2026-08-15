# =====================================================================
# BLACK & PINK DISCORD BOT - FULL ENTERPRISE ULTIMATE EDITION (1000+ LINES STYLE)
# Tích hợp: Nối từ (PvP & Bot), Vua Tiếng Việt, Hệ thống Kinh tế, Shop,
# Inventory, Daily, Work, Leaderboard, Quản lý Session, Logging & Flask Keep-Alive.
# =====================================================================

import os
import json
import random
import logging
import threading
from datetime import datetime, timedelta
from flask import Flask
import discord
from discord.ext import commands

# =====================================================================
# 1. CẤU HÌNH HỆ THỐNG LOGGING VÀ KEEP-ALIVE WEB SERVER
# =====================================================================

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("BlackPinkUltimateEnterpriseBot")

app = Flask("BlackPinkKeepAliveUltimateEnterprise")

@app.route('/')
def home_route():
    return "Black & Pink Ultimate Enterprise Bot is active and running 24/7!"

@app.route('/health')
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

def run_web_server():
    try:
        app.run(host='0.0.0.0', port=8080)
    except Exception as e:
        logger.error(f"Lỗi khởi chạy Web Server Keep-Alive: {e}")

def initialize_keep_alive():
    logger.info("Đang khởi tạo tiến trình nền Keep-Alive Web Server...")
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    logger.info("Tiến trình Keep-Alive đã hoạt động thành công trên cổng 8080.")

# =====================================================================
# 2. HỆ THỐNG CƠ SỞ DỮ LIỆU NÂNG CAO (DATABASE MANAGER)
# =====================================================================

DATABASE_FILE = "bot_database_ultimate_enterprise.json"

class DatabaseManager:
    def __init__(self, filename=DATABASE_FILE):
        self.filename = filename
        self.data = self._load_database()

    def _load_database(self):
        if not os.path.exists(self.filename):
            initial_data = {
                "users": {},
                "guilds": {},
                "statistics": {"total_games": 0, "total_words_played": 0, "total_transactions": 0}
            }
            self._save_database(initial_data)
            return initial_data
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Lỗi đọc cơ sở dữ liệu: {e}")
            return {"users": {}, "guilds": {}, "statistics": {"total_games": 0, "total_words_played": 0, "total_transactions": 0}}

    def _save_database(self, data_to_save):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Lỗi ghi cơ sở dữ liệu: {e}")

    def get_user_profile(self, user_id):
        uid_str = str(user_id)
        if uid_str not in self.data["users"]:
            self.data["users"][uid_str] = {
                "balance": 300,
                "level": 1,
                "xp": 0,
                "streak": 0,
                "games_played": 0,
                "inventory": [],
                "last_daily": "",
                "last_work": "",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self._save_database(self.data)
        return self.data["users"][uid_str]

    def update_user_profile(self, user_id, balance_change=0, xp_change=0, games_increment=0):
        profile = self.get_user_profile(user_id)
        profile["balance"] += balance_change
        profile["xp"] += xp_change
        profile["games_played"] += games_increment

        required_xp = profile["level"] * 100
        if profile["xp"] >= required_xp:
            profile["xp"] -= required_xp
            profile["level"] += 1

        self.data["statistics"]["total_games"] += games_increment
        self._save_database(self.data)
        return profile

    def add_item_to_inventory(self, user_id, item_name):
        profile = self.get_user_profile(user_id)
        if item_name not in profile["inventory"]:
            profile["inventory"].append(item_name)
            self._save_database(self.data)
            return True
        return False

    def get_top_users(self, limit=10):
        users = self.data["users"]
        sorted_users = sorted(users.items(), key=lambda x: x[1]["balance"], reverse=True)
        return sorted_users[:limit]

db_manager = DatabaseManager()

# =====================================================================
# 3. QUẢN LÝ PHIÊN CHƠI VÀ KHO TỪ ĐIỂN KHỔNG LỒ TIẾNG VIỆT
# =====================================================================

class ChannelGameSession:
    def __init__(self):
        self.active = False
        self.mode = None  # 'pvp_vi', 'vua_vi', 'bot_vi'
        self.last_word = ""
        self.used_words = set()
        self.turn_count = 0
        self.last_author_id = None
        self.scrambled_target = None
        self.start_time = None

    def reset_session(self):
        self.active = False
        self.mode = None
        self.last_word = ""
        self.used_words.clear()
        self.turn_count = 0
        self.last_author_id = None
        self.scrambled_target = None
        self.start_time = None

channel_game_sessions = {}

def get_channel_session(channel_id):
    if channel_id not in channel_game_sessions:
        channel_game_sessions[channel_id] = ChannelGameSession()
    return channel_game_sessions[channel_id]

# Bộ từ điển tiếng Việt mở rộng quy mô lớn (hơn 100 từ chuẩn 2 tiếng)
vietnamese_dictionary = {
    "học tập", "tập thể", "thể thao", "áo quần", "nước non",
    "non sông", "sông núi", "núi cao", "cao cấp", "cấp tốc",
    "tốc độ", "độ lượng", "lượng từ", "từ ngữ", "ngữ pháp",
    "pháp luật", "luật sư", "sư phạm", "phạm vi", "vi tính",
    "tính toán", "toán học", "học hỏi", "hỏi han", "hanh thông",
    "thông minh", "minh bạch", "bạch tuộc", "tuộc vòi", "vòi sen",
    "sen hồng", "hồng ngoại", "ngoại ngữ", "ngữ nghĩa", "nghĩa trang",
    "trang hoàng", "hoàng hôn", "hôn lễ", "lễ vật", "vật chất",
    "chất lượng", "lượng giá", "giá trị", "trị giá", "giá cả",
    "cả thể", "thể hình", "hình ảnh", "ảnh hưởng", "hưởng thụ",
    "thụ động", "động lực", "lực lượng", "lượng cư", "cư trú",
    "trú ngụ", "ngụ ngôn", "ngôn ngữ", "ngữ âm", "âm thanh",
    "thanh niên", "niên thiếu", "thiếu niên", "niên giám", "giám đốc",
    "đốc công", "công nhân", "nhân dân", "dân tộc", "tộc họ",
    "họ hàng", "hàng hóa", "hóa đơn", "đơn ca", "ca sĩ",
    "sĩ quan", "quan lại", "lại lịch", "lịch sử", "sử sách",
    "sách vở", "vở bài", "bài tập", "tập trung", "chung kết",
    "kết quả", "quả đất", "đất nước", "nước ngọt", "ngọt ngào",
    "ngào ngạt", "ngạt thở", "thở dài", "dài lâu", "lâu năm",
    "năm tháng", "tháng ngày", "ngày đêm", "đêm khuya", "khuya khoắt",
    "khoắt khoeo", "khoe mẽ", "mẽ đẹp", "đẹp đẽ", "đẽ gọt",
    "gọt đũa", "đũa ngọc", "ngọc ngà", "ngà voi", "voi rừng",
    "rừng rậm", "rậm rạp", "rạp hát", "hát ca", "ca khúc",
    "khúc nhạc", "nhạc cụ", "cụ già", "già làng", "làng bản",
    "bản sắc", "sắc màu", "màu mè", "mè xửng", "xử lý",
    "lý do", "do dự", "dự án", "án mạng", "mạng lưới",
    "lưới cá", "cá tính", "tính nết", "nết na", "na ná",
    "náo nhiệt", "nhiệt huyết", "huyết mạch", "mạch lạc", "lạc quan",
    "quan điểm", "điểm số", "số lượng", "lượng tiền", "tiền tài",
    "tài sản", "sản phẩm", "phẩm chất", "chất phác", "phác thảo",
    "thảo nguyên", "nguyên vẹn", "vẹn toàn", "toàn diện", "diện tích",
    "tích cực", "cực nhọc", "nhọc nhằn", "nhằn nhặn", "nhặn xị",
    "xị rượu", "rượu chè", "chè chén", "chén bát", "bát đĩa",
    "đĩa bay", "bay lượn", "lượn lờ", "lờ mờ", "mờ ảo",
    "ảo ảnh", "ảnh hưởng", "hưởng ứng", "ứng xử", "xử trí",
    "trí tuệ", "tuệ mẫn", "mẫn cảm", "cảm xúc", "xúc động",
    "động đất", "đất liền", "liền mạch", "mạch nước", "nước mát"
}

def scramble_vietnamese_word(word):
    parts = word.split()
    if len(parts) > 1:
        shuffled = parts.copy()
        while shuffled == parts:
            random.shuffle(shuffled)
        return " ".join(shuffled)
    return word

SHOP_ITEMS = {
    "vip_badge": {"name": "Huy hiệu VIP Black & Pink", "price": 500, "desc": "Huy hiệu danh giá hiển thị trong hồ sơ người dùng."},
    "double_xp": {"name": "Gói Nhân Đôi XP (1h)", "price": 300, "desc": "Tăng tốc độ cày cấp độ cực kỳ nhanh chóng."},
    "lucky_box": {"name": "Hộp Quà May Mắn", "price": 150, "desc": "Mở ra phần thưởng Coins ngẫu nhiên từ 50 đến 500."},
    "special_crown": {"name": "Vương Miện Hoàng Gia", "price": 1000, "desc": "Vật phẩm tối thượng thể hiện sự giàu có và đẳng cấp."}
}

# =====================================================================
# 4. KHỞI TẠO DISCORD BOT VÀ CÁC LỆNH HỆ THỐNG
# =====================================================================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="?", intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Bot đã đăng nhập thành công dưới tên: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="?help | Black & Pink Ultimate Enterprise"))

@bot.command(name="noitu")
async def cmd_noitu(ctx):
    session = get_channel_session(ctx.channel.id)
    session.reset_session()
    session.active = True
    session.mode = "pvp_vi"
    session.start_time = datetime.now()
    
    start_word = random.choice(list(vietnamese_dictionary))
    session.last_word = start_word
    session.used_words.add(start_word)
    session.turn_count = 1

    embed = discord.Embed(
        title="🖤💗 [ PHIÊN NỐI TỪ TIẾNG VIỆT: PvP ULTIMATE ] 💗🖤",
        description=(
            f"✅ **Lượt thứ: {session.turn_count}**\n"
            "✨ Yêu cầu: Cụm từ gồm đúng **2 tiếng**.\n"
            f"📌 Từ mở màn:\n# {start_word}\n"
            f"🌸 Âm tiết tiếp theo bắt buộc: **`{start_word.split()[-1]}`**"
        ),
        color=0xFF69B4
    )
    embed.set_footer(text="Black & Pink Ultimate Word Chain • Gõ ?huynoitu để dừng.")
    await ctx.send(embed=embed)

@bot.command(name="botnoitu")
async def cmd_botnoitu(ctx):
    session = get_channel_session(ctx.channel.id)
    session.reset_session()
    session.active = True
    session.mode = "bot_vi"
    session.start_time = datetime.now()
    
    start_word = random.choice(list(vietnamese_dictionary))
    session.last_word = start_word
    session.used_words.add(start_word)
    session.turn_count = 1

    embed = discord.Embed(
        title="🤖💗 [ NỐI TỪ ĐẤU VỚI BOT: ULTIMATE ] 💗🤖",
        description=(
            f"✅ **Lượt thứ: {session.turn_count}**\n"
            "✨ Đấu trí trực tiếp với Bot Black & Pink Enterprise!\n"
            f"📌 Từ mở màn:\n# {start_word}\n"
            f"🌸 Âm tiết tiếp theo của bạn: **`{start_word.split()[-1]}`**"
        ),
        color=0xFF69B4
    )
    embed.set_footer(text="Bot Battle Mode • Gõ ?huynoitu để dừng.")
    await ctx.send(embed=embed)

@bot.command(name="vuatiengviet")
async def cmd_vuatiengviet(ctx):
    session = get_channel_session(ctx.channel.id)
    session.reset_session()
    session.active = True
    session.mode = "vua_vi"
    session.start_time = datetime.now()
    
    target = random.choice(list(vietnamese_dictionary))
    session.scrambled_target = target
    session.turn_count = 1
    puzzle = scramble_vietnamese_word(target)

    embed = discord.Embed(
        title="👑🇻🇳 [ THỬ THÁCH: VUA TIẾNG VIỆT ULTIMATE ] 🇻🇳👑",
        description=(
            f"✅ **Lượt câu đố số: {session.turn_count}**\n"
            "✨ Hãy sắp xếp lại các tiếng sau thành cụm từ 2 tiếng có nghĩa:\n\n"
            f"# 🔀 `{puzzle}`\n\n"
            "🖤 Gõ trực tiếp đáp án vào kênh để ghi điểm!"
        ),
        color=0xFFD700
    )
    embed.set_footer(text="Vua Tiếng Việt Minigame • Black & Pink Edition.")
    await ctx.send(embed=embed)

@bot.command(name="huynoitu")
async def cmd_huynoitu(ctx):
    session = get_channel_session(ctx.channel.id)
    if session.active:
        session.reset_session()
        embed = discord.Embed(
            title="🚫🖤 [ KẾT THÚC PHIÊN CHƠI ] 🖤🚫",
            description="❌ Ván chơi trong kênh này đã được hủy bỏ thành công.",
            color=0x111111
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Hiện tại không có ván chơi nào đang hoạt động trong kênh này.")

@bot.command(name="daily")
async def cmd_daily(ctx):
    profile = db_manager.get_user_profile(ctx.author.id)
    now = datetime.now()
    
    if profile["last_daily"]:
        last_date = datetime.strptime(profile["last_daily"], "%Y-%m-%d %H:%M:%S")
        if now - last_date < timedelta(hours=24):
            remaining = timedelta(hours=24) - (now - last_date)
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            embed = discord.Embed(
                title="⏳💗 [ ĐÃ NHẬN QUÀ HÔM NAY ] 💗⏳",
                description=f"❌ Bạn đã điểm danh rồi! Vui lòng quay lại sau **{hours} giờ {minutes} phút**.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

    reward = 150
    profile["last_daily"] = now.strftime("%Y-%m-%d %H:%M:%S")
    db_manager.update_user_profile(ctx.author.id, balance_change=reward)
    
    embed = discord.Embed(
        title="🎁✨ [ ĐIỂM DANH HÀNG NGÀY THÀNH CÔNG! ] ✨🎁",
        description=f"✨ Chúc mừng {ctx.author.mention} đã nhận được **{reward} Coins** miễn phí hôm nay!",
        color=0x00FFCC
    )
    await ctx.send(embed=embed)

@bot.command(name="work")
async def cmd_work(ctx):
    profile = db_manager.get_user_profile(ctx.author.id)
    now = datetime.now()

    if profile["last_work"]:
        last_date = datetime.strptime(profile["last_work"], "%Y-%m-%d %H:%M:%S")
        if now - last_date < timedelta(minutes=30):
            remaining = timedelta(minutes=30) - (now - last_date)
            minutes, seconds = divmod(int(remaining.total_seconds()), 60)
            embed = discord.Embed(
                title="⏳💗 [ ĐANG TRONG THỜI GIAN NGHỈ NGƠI ] 💗⏳",
                description=f"❌ Bạn vừa mới làm việc xong! Hãy nghỉ ngơi thêm **{minutes} phút {seconds} giây**.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

    earned = random.choice([50, 75, 100, 120, 150, 200])
    profile["last_work"] = now.strftime("%Y-%m-%d %H:%M:%S")
    db_manager.update_user_profile(ctx.author.id, balance_change=earned, xp_change=25)

    embed = discord.Embed(
        title="💼💰 [ LÀM VIỆC KIẾM TIỀN THÀNH CÔNG ] 💰💼",
        description=f"✨ {ctx.author.mention} đã hoàn thành ca làm việc và nhận được **{earned} Coins** cùng **25 XP**!",
        color=0xFFD700
    )
    await ctx.send(embed=embed)

@bot.command(name="rank")
async def cmd_rank(ctx):
    profile = db_manager.get_user_profile(ctx.author.id)
    inventory_str = ", ".join(profile["inventory"]) if profile["inventory"] else "Trống"
    embed = discord.Embed(
        title=f"🏆💗 [ HỒ SƠ THÀNH TÍCH: {ctx.author.name.upper()} ] 💗🏆",
        description=(
            f"⭐ Cấp độ hiện tại: **Level {profile['level']}**\n"
            f"📈 Điểm kinh nghiệm XP: **{profile['xp']} XP**\n"
            f"💰 Số dư tài khoản: **{profile['balance']} Coins**\n"
            f"🎮 Tổng số từ đã chơi: **{profile['games_played']} từ**\n"
            f"🎒 Túi đồ vật phẩm: `{inventory_str}`\n"
            f"📅 Ngày tham gia: `{profile['created_at']}`"
        ),
        color=0xFFD700
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_footer(text="Black & Pink Ultimate Enterprise Economy System.")
    await ctx.send(embed=embed)

@bot.command(name="shop")
async def cmd_shop(ctx):
    embed = discord.Embed(
        title="🛍️💗 [ CỬA HÀNG VẬT PHẨM BLACK & PINK ] 💗🛍️",
        description="Sử dụng lệnh `?buy <ma_vat_pham>` để mua sắm các vật phẩm độc quyền!",
        color=0xFF69B4
    )
    for key, item in SHOP_ITEMS.items():
        embed.add_field(
            name=f"📌 {item['name']} (`{key}`)",
            value=f"💵 Giá: **{item['price']} Coins**\n📝 Mô tả: {item['desc']}",
            inline=False
        )
    embed.set_footer(text="Ultimate Enterprise Shop System.")
    await ctx.send(embed=embed)

@bot.command(name="buy")
async def cmd_buy(ctx, item_key: str = None):
    if not item_key or item_key not in SHOP_ITEMS:
        embed = discord.Embed(
            title="❌💗 [ LỖI MUA HÀNG ] 💗❌",
            description="❌ Vui lòng nhập đúng mã vật phẩm. Gõ `?shop` để xem danh sách.",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
        return

    item = SHOP_ITEMS[item_key]
    profile = db_manager.get_user_profile(ctx.author.id)

    if profile["balance"] < item["price"]:
        embed = discord.Embed(
            title="❌💗 [ KHÔNG ĐỦ TIỀN ] 💗❌",
            description=f"❌ Bạn cần **{item['price']} Coins** nhưng chỉ có **{profile['balance']} Coins**.",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
        return

    success = db_manager.add_item_to_inventory(ctx.author.id, item["name"])
    if success:
        db_manager.update_user_profile(ctx.author.id, balance_change=-item["price"])
        embed = discord.Embed(
            title="✅🛍️ [ MUA HÀNG THÀNH CÔNG! ] 🛍️✅",
            description=f"✨ Chúc mừng bạn đã sở hữu thành công: **{item['name']}**!",
            color=0x00FFCC
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="⚠️💗 [ ĐÃ SỞ HỮU ] 💗⚠️",
            description="⚠️ Bạn đã có vật phẩm này trong túi đồ rồi!",
            color=0xFFA500
        )
        await ctx.send(embed=embed)

@bot.command(name="leaderboard")
async def cmd_leaderboard(ctx):
    top_users = db_manager.get_top_users(10)
    description_lines = []
    for rank_idx, (uid, data) in enumerate(top_users, 1):
        try:
            user_obj = await bot.fetch_user(int(uid))
            username = user_obj.name
        except:
            username = f"User ID: {uid}"
        
        medal = "🥇" if rank_idx == 1 else "🥈" if rank_idx == 2 else "🥉" if rank_idx == 3 else f"`#{rank_idx}`"
        description_lines.append(f"{medal} **{username}** — 💰 **{data['balance']} Coins** (Level {data['level']})")

    embed = discord.Embed(
        title="🏆📊 [ BẢNG XẾP HẠNG GIÀU CÓ NHẤT ] 📊🏆",
        description="\n".join(description_lines) if description_lines else "Chưa có dữ liệu bảng xếp hạng.",
        color=0xFFD700
    )
    embed.set_footer(text="Ultimate Enterprise Leaderboard System.")
    await ctx.send(embed=embed)

# =====================================================================
# 5. XỬ LÝ SỰ KIỆN TIN NHẮN (GAME LOGIC TRỰC TIẾP)
# =====================================================================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    session = get_channel_session(message.channel.id)
    if not session.active:
        return

    content = message.content.lower().strip()

    # Xử lý chế độ Vua Tiếng Việt
    if session.mode == "vua_vi":
        if content == session.scrambled_target:
            session.turn_count += 1
            db_manager.update_user_profile(message.author.id, balance_change=30, xp_change=25, games_increment=1)
            
            correct_word = session.scrambled_target
            next_target = random.choice(list(vietnamese_dictionary))
            session.scrambled_target = next_target
            puzzle = scramble_vietnamese_word(next_target)

            embed = discord.Embed(
                title="✅👑 [ ĐÁP ÁN CHÍNH XÁC! (+30 Coins) ] 👑✅",
                description=(
                    f"✨ Chúc mừng {message.author.mention} đã giải mã đúng từ: **`{correct_word}`**!\n"
                    f"🔢 Lượt tiếp theo: **{session.turn_count}** ✅\n\n"
                    f"# 🔀 `{puzzle}`"
                ),
                color=0xFFD700
            )
            await message.channel.send(embed=embed)
        return

    # Xử lý chế độ Nối Từ PvP
    if session.mode == "pvp_vi":
        if len(content.split()) != 2:
            embed = discord.Embed(
                title="❌💗 [ SAI ĐỊNH DẠNG TỪ ] 💗❌",
                description="❌ Từ bắt buộc phải gồm đúng **2 tiếng**.",
                color=0xFF0000
            )
            await message.channel.send(embed=embed)
            return

        if content in session.used_words:
            embed = discord.Embed(
                title="❌💗 [ TỪ ĐÃ ĐƯỢC SỬ DỤNG ] 💗❌",
                description="❌ Từ này đã xuất hiện trước đó trong ván đấu!",
                color=0xFF0000
            )
            await message.channel.send(embed=embed)
            return

        if session.last_author_id == message.author.id:
            embed = discord.Embed(
                title="❌💗 [ VI PHẠM LUẬT LƯỢT ] 💗❌",
                description="❌ Bạn không thể tự nối từ của chính mình liên tiếp.",
                color=0xFF0000
            )
            await message.channel.send(embed=embed)
            return

        required_syllable = session.last_word.split()[-1]
        if content.split()[0] != required_syllable:
            embed = discord.Embed(
                title="❌💗 [ SAI QUY TẮC NỐI TỪ ] 💗❌",
                description=f"❌ Từ phải bắt đầu bằng âm tiết: **`{required_syllable}`**",
                color=0xFF0000
            )
            await message.channel.send(embed=embed)
            return

        session.turn_count += 1
        session.last_word = content
        session.used_words.add(content)
        session.last_author_id = message.author.id
        vietnamese_dictionary.add(content)

        db_manager.update_user_profile(message.author.id, balance_change=15, xp_change=15, games_increment=1)
        next_syllable = content.split()[-1]

        embed = discord.Embed(
            title="✅✨ [ LƯỢT ĐẤU HỢP LỆ ] ✨✅",
            description=(
                f"🔢 **Lượt thứ: {session.turn_count}** ✅\n"
                f"✨ Người chơi: {message.author.mention} (+15 Coins)\n"
                f"📌 Từ ghi nhận: `{content}`\n"
                f"🌸 Âm tiết cần nối tiếp: **`{next_syllable}`**"
            ),
            color=0xFF69B4
        )
        await message.channel.send(embed=embed)

    # Xử lý chế độ Đấu với Bot
    elif session.mode == "bot_vi":
        if len(content.split()) != 2:
            embed = discord.Embed(
                title="❌💗 [ SAI ĐỊNH DẠNG TỪ ] 💗❌",
                description="❌ Từ bắt buộc phải gồm đúng **2 tiếng**.",
                color=0xFF0000
            )
            await message.channel.send(embed=embed)
            return

        if content in session.used_words:
            embed = discord.Embed(
                title="❌💗 [ TỪ ĐÃ ĐƯỢC SỬ DỤNG ] 💗❌",
                description="❌ Từ này đã xuất hiện trước đó trong ván đấu!",
                color=0xFF0000
            )
            await message.channel.send(embed=embed)
            return

        required_syllable = session.last_word.split()[-1]
        if content.split()[0] != required_syllable:
            embed = discord.Embed(
                title="❌💗 [ SAI QUY TẮC NỐI TỪ ] 💗❌",
                description=f"❌ Từ phải bắt đầu bằng âm tiết: **`{required_syllable}`**",
                color=0xFF0000
            )
            await message.channel.send(embed=embed)
            return

        session.turn_count += 1
        session.last_word = content
        session.used_words.add(content)
        db_manager.update_user_profile(message.author.id, balance_change=15, xp_change=15, games_increment=1)

        user_next_syllable = content.split()[-1]
        
        # Tìm từ cho Bot phản đòn
        possible_bot_words = [w for w in vietnamese_dictionary if w.split()[0] == user_next_syllable and w not in session.used_words]
        
        description_text = (
            f"🔢 **Lượt người chơi (Lượt thứ: {session.turn_count})** ✅\n"
            f"✨ {message.author.mention} đã nối: `{content}` (+15 Coins)"
        )

        if possible_bot_words:
            bot_word = random.choice(possible_bot_words)
            session.turn_count += 1
            session.last_word = bot_word
            session.used_words.add(bot_word)
            bot_next_syllable = bot_word.split()[-1]
            
            description_text += (
                f"\n\n🤖💗 **Phản đòn từ Bot (Lượt thứ {session.turn_count}):**\n"
                f"# {bot_word}\n"
                f"🌸 Lượt tiếp theo của bạn bắt đầu bằng: **`{bot_next_syllable}`** ✅"
            )
        else:
            description_text += "\n\n🎉 **Bot đã cạn từ vựng! Bạn đã giành chiến thắng tuyệt đối!** 👑"
            session.reset_session()

        embed = discord.Embed(
            title="✅✨ [ ĐẤU TRÍ BOT: HIỆP HỢP LỆ ] ✨✅",
            description=description_text,
            color=0xFF69B4
        )
        await message.channel.send(embed=embed)

# =====================================================================
# 6. ĐIỂM KHỞI CHẠY CHƯƠNG TRÌNH ULTIMATE ENTERPRISE
# =====================================================================

if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        logger.critical("LỖI NGHIÊM TRỌNG: Không tìm thấy biến môi trường DISCORD_TOKEN.")
    else:
        initialize_keep_alive()
        logger.info("Đang khởi động kết nối Discord Bot phiên bản Ultimate Enterprise...")
        bot.run(token)
