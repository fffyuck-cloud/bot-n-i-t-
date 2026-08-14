import os
import ssl
import json
import urllib.request
import random
import re
import unicodedata
from datetime import datetime, date
import discord
from discord.ext import commands
from keep_alive import keep_alive

# --- 🎨 BẢNG MÀU THEME (ĐEN - HỒNG - ĐỎ) ---
COLOR_BLACK     = 0x111111
COLOR_PINK      = 0xFF69B4
COLOR_DEEP_PINK = 0xFF1493
COLOR_RED       = 0xFF0000
COLOR_DARK_RED  = 0xD32F2F

COLOR_VI_MULTI = COLOR_BLACK
COLOR_VI_BOT   = COLOR_PINK
COLOR_EN_MULTI = COLOR_DEEP_PINK
COLOR_EN_BOT   = COLOR_RED
COLOR_SUCCESS  = COLOR_PINK
COLOR_ERROR    = COLOR_DARK_RED

CUSTOM_TICK = "Screenshot20260812172055:1537043520790073424"
CUSTOM_CROSS = "Screenshot20260812173722:1537047895310602300"

NUMBER_EMOJIS = {
    1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
    6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
}

# --- 🛠️ CHUẨN HÓA UNICODE & TỪ CẤM ---
def norm(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize('NFC', str(text).lower().strip())
    return re.sub(r'\s+', ' ', text)

BAD_WORDS = {norm("ỉa")}
DEAD_END_WORDS = {
    norm(w) for w in [
        "vậy", "sao", "mà", "thì", "là", "nhé", "à", "nhỉ", "nè", "đâu", "đó",
        "nào", "đấy", "ư", "hử", "nha", "nghen", "ha", "kìa", "này", "chứ", "rồi"
    ]
}

EASY_VI_WORDS = [
    "đá banh", "đá bóng", "bàn học", "học sinh", "sinh viên", "viên bi", "bi ao", "ao cá", "cá chép", 
    "chép phạt", "phạt góc", "học bài", "học tập", "học hành", "bài học", "bài tập", "tập viết", 
    "viết sách", "sách vở", "vở kịch", "kịch bản", "bản đồ", "đồ chơi", "chơi game", "góc sân", 
    "sân trường", "trường học", "góc nhỏ", "phạt đền", "góc nhìn", "thể thao", "bóng đá", "cầu thủ"
]

easy_en_words_set = set([
    "apple", "banana", "cat", "dog", "elephant", "fish", "giraffe", "house",
    "ice", "jungle", "kite", "lemon", "monkey", "nest", "orange", "paper",
    "queen", "rabbit", "sun", "tree", "umbrella", "van", "water", "yellow", "zebra"
])

def contains_bad_word(text):
    text_clean = norm(text)
    words = text_clean.split()
    for word in words:
        if word in BAD_WORDS: return True
    return text_clean in BAD_WORDS

def is_dead_end_word(word):
    word_clean = norm(word)
    syllables = word_clean.split()
    return len(syllables) == 2 and syllables[-1] in DEAD_END_WORDS

# --- 📚 NẠP TỪ ĐIỂN FULL (FIX LINK KHÔNG CÒN 404) ---
def prepare_dictionaries():
    ctx = ssl._create_unverified_context()
    
    words_vi = set(norm(w) for w in EASY_VI_WORDS)
    urls_vi = [
        "https://raw.githubusercontent.com/duyvuleo/VNcoreNLP/master/words.txt",
        "https://raw.githubusercontent.com/NguyenAnhTuan1997/Vietnamese-Dictionary/master/words.txt",
        "https://raw.githubusercontent.com/stopwords/vietnamese-stopwords/master/vietnamese-stopwords.txt"
    ]
    for url in urls_vi:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                for line in content.splitlines():
                    word = norm(line.replace("_", " "))
                    if word and len(word.split()) == 2 and not contains_bad_word(word):
                        words_vi.add(word)
        except Exception as e:
            print(f"Lỗi nạp nguồn Tiếng Việt ({url}): {e}")

    words_en = set()
    urls_en_full = [
        "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt",
        "https://raw.githubusercontent.com/raun/Scrabble/master/words.txt"
    ]
    for url in urls_en_full:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                for line in content.splitlines():
                    w = line.strip().lower()
                    if len(w) >= 2 and w.isalpha():
                        words_en.add(w)
        except Exception as e:
            print(f"Lỗi nạp nguồn Tiếng Anh ({url}): {e}")

    try:
        url_common = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-no-swears.txt"
        req = urllib.request.Request(url_common, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
            for line in content.splitlines():
                w = line.strip().lower()
                if len(w) >= 2 and w.isalpha():
                    easy_en_words_set.add(w)
                    words_en.add(w)
    except Exception as e:
        print(f"Lỗi nạp từ phổ thông Tiếng Anh: {e}")

    print(f"✅ NẠP THÀNH CÔNG: {len(words_vi):,} từ Tiếng Việt | {len(words_en):,} từ Tiếng Anh.")
    return words_vi, words_en

dictionary_vi, dictionary_en = prepare_dictionaries()
VN_CHARS_REGEX = re.compile(r'^[a-zàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]+$')

def is_valid_vietnamese_word(text):
    text_clean = norm(text)
    words = text_clean.split()
    return len(words) == 2 and VN_CHARS_REGEX.match(text_clean) and text_clean in dictionary_vi

def is_valid_english_word(text):
    return text.strip().lower() in dictionary_en

def pick_random_vi_word(prefix=None, used_words=None):
    used_words = {norm(w) for w in used_words} if used_words else set()
    prefix_norm = norm(prefix) if prefix else None

    easy = [w for w in EASY_VI_WORDS if (not prefix_norm or norm(w).startswith(prefix_norm + " ")) and norm(w) not in used_words and not is_dead_end_word(w) and not contains_bad_word(w)]
    all_w = [w for w in dictionary_vi if (not prefix_norm or norm(w).startswith(prefix_norm + " ")) and norm(w) not in used_words and not is_dead_end_word(w) and not contains_bad_word(w)]

    if not all_w: return None
    return random.choice(easy) if (random.random() < 0.75 and easy) else random.choice(all_w)

def pick_random_en_word(letter=None, used_words=None):
    used_words = {w.lower() for w in used_words} if used_words else set()
    letter = letter.lower() if letter else None

    easy_candidates = [w for w in easy_en_words_set if (not letter or w.startswith(letter)) and w not in used_words]
    all_candidates = [w for w in dictionary_en if (not letter or w.startswith(letter)) and w not in used_words]

    if not all_candidates: return None
    return random.choice(easy_candidates) if (random.random() < 0.75 and easy_candidates) else random.choice(all_candidates)

# --- DATABASE STATS ---
STATS_FILE = "user_stats.json"

def load_json(file_path, default_data):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: return default_data
    return default_data

def save_json(file_path, data):
    try:
        with open(file_path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e: print(f"Lỗi lưu JSON: {e}")

user_stats = load_json(STATS_FILE, {})

def update_user_stats(user_id, added_words=0, win=False, loss=False):
    u_id = str(user_id)
    if u_id not in user_stats:
        user_stats[u_id] = {"wins": 0, "losses": 0, "total_words": 0}
    user_stats[u_id]["total_words"] += added_words
    if win: user_stats[u_id]["wins"] += 1
    if loss: user_stats[u_id]["losses"] += 1
    save_json(STATS_FILE, user_stats)

def make_progress_bar(val, total=100, length=10):
    if total <= 0: return "░" * length
    percent = min(1.0, max(0.0, val / total))
    filled = int(round(length * percent))
    return "█" * filled + "░" * (length - filled)

def get_user_title(total_words):
    if total_words >= 500: return "👑 Bậc Thầy Ngôn Ngữ"
    if total_words >= 200: return "🔥 Cao Thủ Nối Từ"
    if total_words >= 50: return "✨ Tay Chơi Triển Vọng"
    return "🐣 Tân Thủ Nối Từ"

def get_combo_title(count):
    if count >= 20: return f"👑 ULTRA COMBO ({count})"
    if count >= 10: return f"⚡ HYPER COMBO ({count})"
    if count >= 5:  return f"🔥 STREAK COMBO ({count})"
    return f"✨ COMBO ({count})"

# --- 🎨 EMBED BUILDER ---
CB = "```"

def build_game_embed(game, title, color, author_user=None, last_player_name=None):
    embed = discord.Embed(
        title=f"❖ ────── {title} ────── ❖",
        color=color,
        timestamp=datetime.now()
    )
    
    if author_user:
        embed.set_author(name=f"🎮 Trận đấu tạo bởi {author_user.display_name}", icon_url=author_user.display_avatar.url)

    used_list = list(game.get("history_list", []))
    recent_list = used_list[-5:]
    history_str = " ➔ ".join([w.upper() for w in recent_list])
    
    history_box = CB + "yaml\n" + history_str + "\n" + CB
    embed.add_field(
        name="📜 DÒNG CHẢY TỪ NỐI",
        value=history_box,
        inline=False
    )

    if game["mode"] == "vi":
        prev_last = norm(game["last_word"].split()[-1]).upper()
        target_info = f"👉 Bắt đầu bằng tiếng:\n# `  {prev_last}  `"
    else:
        last_char = game["last_word"][-1].upper()
        target_info = f"👉 Bắt đầu bằng chữ:\n# `  {last_char}  `"

    combo_info = f"**{get_combo_title(game.get('count', 1))}**\n`[{'█' * min(10, game.get('count', 1))}]`"

    embed.add_field(name="🎯 TỪ CẦN NỐI TIẾP", value=target_info, inline=True)
    embed.add_field(name="🔥 TRẠNG THÁI CHUỖI", value=combo_info, inline=True)
    
    if last_player_name:
        embed.add_field(name="👤 LƯỢT VỪA NỐI", value=f"**{last_player_name}**", inline=True)

    embed.add_field(
        name="‎",
        value="💬 *Gõ từ trực tiếp vào kênh để nối • Nhấn nút **💡 Gợi Ý** bên dưới nếu bị bí!*",
        inline=False
    )
    
    flag_thumb = "[https://cdn-icons-png.flaticon.com/512/197/197473.png](https://cdn-icons-png.flaticon.com/512/197/197473.png)" if game["mode"] == "vi" else "[https://cdn-icons-png.flaticon.com/512/197/197374.png](https://cdn-icons-png.flaticon.com/512/197/197374.png)"
    embed.set_thumbnail(url=flag_thumb)
    embed.set_footer(text="Word Chain Master Engine • Theme Đen - Hồng - Đỏ", icon_url="[https://cdn-icons-png.flaticon.com/512/2069/2069581.png](https://cdn-icons-png.flaticon.com/512/2069/2069581.png)")
    return embed

# --- INTERACTIVE BUTTONS UI ---
class GameControlButtons(discord.ui.View):
    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="💡 Gợi Ý Từ", style=discord.ButtonStyle.danger, custom_id="btn_game_hint")
    async def hint_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel_id = interaction.channel_id
        if channel_id not in games:
            await interaction.response.send_message("❌ Chưa có ván đấu nào đang chạy ở kênh này!", ephemeral=True)
            return

        user_id = interaction.user.id
        hints_left = user_hints.get(user_id, 0)
        if hints_left <= 0:
            await interaction.response.send_message("❌ Bạn đã hết lượt gợi ý! Gõ `?daily` để nhận **3 lượt mới** ngay.", ephemeral=True)
            return

        game = games[channel_id]
        if game["mode"] == "vi":
            prev_last = norm(game["last_word"].split()[-1])
            suggested = pick_random_vi_word(prefix=prev_last, used_words=game["used_words"])
            hint_msg = f"Từ Tiếng Việt gợi ý: **`{suggested.upper() if suggested else 'Bí từ'}`**"
        else:
            last_char = game["last_word"][-1].lower()
            suggested = pick_random_en_word(letter=last_char, used_words=game["used_words"])
            hint_msg = f"Từ Tiếng Anh gợi ý: **`{suggested.upper() if suggested else 'Bí từ'}`**"

        if suggested:
            user_hints[user_id] -= 1
            await interaction.response.send_message(f"💡 **GỢI Ý DÀNH CHO BẠN:**\n{hint_msg}\n*(Bạn còn **{user_hints[user_id]}/3** lượt gợi ý)*", ephemeral=True)
        else:
            await interaction.response.send_message("💡 Hệ thống đã bí từ hợp lệ cho lượt này!", ephemeral=True)

    @discord.ui.button(label="📊 Hồ Sơ", style=discord.ButtonStyle.secondary, custom_id="btn_game_profile")
    async def profile_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        u_id = str(interaction.user.id)
        stats = user_stats.get(u_id, {"wins": 0, "losses": 0, "total_words": 0})
        wins, losses = stats["wins"], stats["losses"]
        total = wins + losses
        win_rate = round((wins / total * 100), 1) if total > 0 else 0
        bar = make_progress_bar(wins, total if total > 0 else 1)
        title = get_user_title(stats["total_words"])

        embed = discord.Embed(title=f"📊 HỒ SƠ NGÔN NGỮ - {interaction.user.display_name}", color=COLOR_BLACK)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="🏅 Danh hiệu", value=f"**{title}**", inline=False)
        embed.add_field(name="🏆 Tỉ lệ Thắng (1v1 Bot)", value=f"`[{bar}]` **{win_rate}%**\n({wins} Thắng | {losses} Thua)", inline=True)
        embed.add_field(name="✍️ Tích lũy từ vựng", value=f"**{stats['total_words']}** từ chuẩn", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# --- BOT INIT ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)
games = {}
user_hints = {}        
user_daily_claimed = {} 

async def add_success_reactions(message, count):
    try: await message.add_reaction(CUSTOM_TICK)
    except Exception: await message.add_reaction("✅")
    try:
        if count in NUMBER_EMOJIS: await message.add_reaction(NUMBER_EMOJIS[count])
    except Exception: pass

async def add_fail_reaction(message):
    try: await message.add_reaction(CUSTOM_CROSS)
    except Exception: await message.add_reaction("❌")

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} đã sẵn sàng kết nối Discord!")

# --- 📜 LỆNH HELP / TROGIUP ---
@bot.command(name="help", aliases=["trogiup", "huongdan"])
async def custom_help(ctx):
    embed = discord.Embed(
        title="❖ ────── 📜 DANH SÁCH LỆNH BOT NỐI TỪ ────── ❖",
        description="Chào mừng bạn đến với **Word Chain Master**! Dưới đây là toàn bộ các lệnh bạn có thể sử dụng:",
        color=COLOR_PINK,
        timestamp=datetime.now()
    )
    if bot.user and bot.user.display_avatar:
        embed.set_thumbnail(url=bot.user.display_avatar.url)

    embed.add_field(
        name="🇻🇳 NỐI TỪ TIẾNG VIỆT",
        value="• `?noitu` ➔ Bắt đầu ván chơi nhóm (Server cùng chơi)\n• `?noitubot` ➔ Đấu 1v1 trực tiếp với Bot",
        inline=False
    )
    embed.add_field(
        name="🔤 ENGLISH WORD CHAIN",
        value="• `?noitueng` ➔ Bắt đầu ván Tiếng Anh nhóm\n• `?noituboteng` ➔ Đấu 1v1 Tiếng Anh với Bot",
        inline=False
    )
    embed.add_field(
        name="📊 TÍNH NĂNG & TIỆN ÍCH",
        value="• `?daily` ➔ Điểm danh hằng ngày (Nhận 3 lượt gợi ý)\n• `?profile` ➔ Xem hồ sơ & tỉ lệ thắng của bạn\n• `?profile @user` ➔ Xem hồ sơ người chơi khác\n• `?huynoitu` ➔ Hủy trận đấu ở kênh hiện tại",
        inline=False
    )
    embed.add_field(
        name="💡 LƯU Ý KHI CHƠI",
        value="* Khi trận đấu đã mở, bạn **không cần gõ `?`**, chỉ cần gõ trực tiếp từ nối vào kênh chat!\n* Nhấn nút **💡 Gợi Ý** trên Embed nếu bí từ.",
        inline=False
    )
    embed.set_footer(text="Gõ ?help hoặc ?trogiup bất kỳ lúc nào để xem lại bảng này!", icon_url="[https://cdn-icons-png.flaticon.com/512/2069/2069581.png](https://cdn-icons-png.flaticon.com/512/2069/2069581.png)")
    
    await ctx.send(embed=embed)

# --- 🎮 LỆNH CHƠI GAME ---
@bot.command(name="noitu")
async def start_game_vi(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("❌ Kênh này đang có trận đấu diễn ra rồi!")
        return

    start_word = norm(pick_random_vi_word() or random.choice(EASY_VI_WORDS))
    games[channel_id] = {
        "mode": "vi", "vs_bot": False, "last_word": start_word,
        "count": 1, "used_words": {start_word}, "history_list": [start_word]
    }

    embed = build_game_embed(games[channel_id], title="🖤 NỐI TỪ TIẾNG VIỆT", color=COLOR_VI_MULTI, author_user=ctx.author)
    view = GameControlButtons(channel_id)
    msg = await ctx.send(embed=embed, view=view)
    await add_success_reactions(msg, 1)

@bot.command(name="noitubot")
async def start_game_vi_bot(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("❌ Kênh này đang có trận đấu diễn ra rồi!")
        return

    start_word = norm(pick_random_vi_word() or random.choice(EASY_VI_WORDS))
    games[channel_id] = {
        "mode": "vi", "vs_bot": True, "last_word": start_word,
        "count": 1, "used_words": {start_word}, "history_list": [start_word]
    }

    embed = build_game_embed(games[channel_id], title="🩷 1v1 TIẾNG VIỆT VỚI BOT", color=COLOR_VI_BOT, author_user=ctx.author)
    view = GameControlButtons(channel_id)
    msg = await ctx.send(embed=embed, view=view)
    await add_success_reactions(msg, 1)

@bot.command(name="noitueng")
async def start_game_en(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("❌ Kênh này đang có trận đấu diễn ra rồi!")
        return

    start_word = pick_random_en_word() or "apple"
    games[channel_id] = {
        "mode": "en", "vs_bot": False, "last_word": start_word,
        "count": 1, "used_words": {start_word}, "history_list": [start_word]
    }

    embed = build_game_embed(games[channel_id], title="🩷 ENGLISH WORD CHAIN", color=COLOR_EN_MULTI, author_user=ctx.author)
    view = GameControlButtons(channel_id)
    msg = await ctx.send(embed=embed, view=view)
    await add_success_reactions(msg, 1)

@bot.command(name="noituboteng")
async def start_game_en_bot(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("❌ Kênh này đang có trận đấu diễn ra rồi!")
        return

    start_word = pick_random_en_word() or "apple"
    games[channel_id] = {
        "mode": "en", "vs_bot": True, "last_word": start_word,
        "count": 1, "used_words": {start_word}, "history_list": [start_word]
    }

    embed = build_game_embed(games[channel_id], title="❤️ 1v1 ENGLISH WITH BOT", color=COLOR_EN_BOT, author_user=ctx.author)
    view = GameControlButtons(channel_id)
    msg = await ctx.send(embed=embed, view=view)
    await add_success_reactions(msg, 1)

@bot.command(name="profile")
async def show_profile(ctx, member: discord.Member = None):
    target = member or ctx.author
    u_id = str(target.id)
    stats = user_stats.get(u
