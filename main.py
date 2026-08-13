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

# --- 🎨 BẢNG MÀU UI EMBED ---
COLOR_BLACK = 0x1A1A1A  # Đen sang trọng
COLOR_PINK = 0xFF69B4   # Hồng nổi bật
COLOR_GOLD = 0xFFD700   # Vàng kim (Highscore / Victory)
COLOR_RED = 0xFF4757    # Đỏ (Cảnh báo / Lỗi)

# Custom Emoji
CUSTOM_TICK = "Screenshot20260812172055:1537043520790073424"
CUSTOM_CROSS = "Screenshot20260812173722:1537047895310602300"

NUMBER_EMOJIS = {
    1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
    6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
}

# --- 🛠️ CHUẨN HÓA UNICODE & DỮ LIỆU ---
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

EASY_EN_WORDS = [
    "apple", "banana", "cat", "dog", "elephant", "fish", "giraffe", "house",
    "ice", "jungle", "kite", "lemon", "monkey", "nest", "orange", "paper"
]

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

def prepare_dictionaries():
    words_vi = set(norm(w) for w in EASY_VI_WORDS)
    urls_vi = [
        "https://raw.githubusercontent.com/vinhjaxt/vietnamese-words/master/vietnamese-words.txt",
        "https://raw.githubusercontent.com/undertheseanlp/nlp/master/underthesea/word_tokenize/dicts/words.txt"
    ]
    for url in urls_vi:
        try:
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                for line in content.splitlines():
                    word = norm(line.replace("_", " "))
                    if word and len(word.split()) == 2 and not contains_bad_word(word):
                        words_vi.add(word)
        except Exception as e:
            print(f"Lỗi nạp từ điển Việt: {e}")

    words_en = set(EASY_EN_WORDS)
    try:
        url_en = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url_en, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
            for line in content.splitlines():
                w = line.strip().lower()
                if len(w) >= 2 and w.isalpha(): words_en.add(w)
    except Exception as e:
        print(f"Lỗi nạp từ điển Anh: {e}")

    print(f"✅ Đã nạp: {len(words_vi)} từ Tiếng Việt | {len(words_en)} từ Tiếng Anh.")
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
    return random.choice(easy) if (random.random() < 0.80 and easy) else random.choice(all_w)

def pick_random_en_word(letter=None, used_words=None):
    used_words = {w.lower() for w in used_words} if used_words else set()
    letter = letter.lower() if letter else None
    candidates = [w for w in dictionary_en if (not letter or w.startswith(letter)) and w not in used_words]
    return random.choice(candidates) if candidates else None

# --- DATABASE JSON ---
STATS_FILE = "user_stats.json"
HIGHSCORE_FILE = "highscore.json"

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
highscores = load_json(HIGHSCORE_FILE, {"vi": {"count": 0}, "en": {"count": 0}})

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
    if total_words >= 50: return "✨ Tay Chơi Hứa Hẹn"
    return "🐣 Tân Thủ Nối Từ"

# --- 🎨 HAM TẠO EMBED CHUYÊN NGHIỆP ---
def build_game_embed(game, title, description, color=COLOR_PINK, author_user=None):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    
    if author_user:
        embed.set_author(name=f"Yêu cầu bởi {author_user.display_name}", icon_url=author_user.display_avatar.url)

    # Hiển thị lịch sử 4 từ gần nhất
    used_list = list(game.get("history_list", []))
    if used_list:
        recent_4 = used_list[-4:]
        history_fmt = " ➔ ".join([f"`{w.upper()}`" for w in recent_4])
        embed.add_field(name="📜 Lịch sử nối từ gần nhất", value=history_fmt, inline=False)

    # Hiển thị thống kê lượt chơi
    embed.add_field(name="🔢 Tổng số từ đã nối", value=f"**{game.get('count', 1)}** từ", inline=True)
    
    if game["mode"] == "vi":
        prev_last = norm(game["last_word"].split()[-1])
        embed.add_field(name="👉 Tiếng phải nối tiếp", value=f"Bắt đầu bằng **'{prev_last.upper()}'**", inline=True)
    elif game["mode"] == "en":
        last_char = game["last_word"][-1].upper()
        embed.add_field(name="👉 Chữ cái phải nối", value=f"Bắt đầu bằng **'{last_char}'**", inline=True)

    embed.add_field(
        name="💡 Mẹo & Hướng dẫn", 
        value="• Nhập từ trực tiếp vào kênh mà không cần dùng lệnh.\n• Nối sai sẽ được cho **nối lại** (không bị tính thua).\n• Bấm nút **💡 Gợi ý** bên dưới nếu bị bí từ!",
        inline=False
    )
    
    embed.set_footer(text="Discord Word Chain Bot • Chúc bạn may mắn!", icon_url="https://cdn-icons-png.flaticon.com/512/2069/2069581.png")
    return embed

# --- NÚT BẤM INTERACTIVE UI ---
class GameControlButtons(discord.ui.View):
    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="💡 Gợi ý", style=discord.ButtonStyle.primary, custom_id="btn_game_hint")
    async def hint_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel_id = interaction.channel_id
        if channel_id not in games:
            await interaction.response.send_message("❌ Chưa có ván đấu nào đang diễn ra ở kênh này!", ephemeral=True)
            return

        user_id = interaction.user.id
        hints_left = user_hints.get(user_id, 0)
        if hints_left <= 0:
            await interaction.response.send_message("❌ Bạn đã dùng hết lượt gợi ý. Hãy gõ lệnh `?daily` để nhận thêm 3 lượt mới!", ephemeral=True)
            return

        game = games[channel_id]
        if game["mode"].startswith("vi"):
            prev_last = norm(game["last_word"].split()[-1])
            suggested = pick_random_vi_word(prefix=prev_last, used_words=game["used_words"])
            hint_msg = f"Từ Tiếng Việt bắt đầu bằng **'{prev_last}'**: **{suggested.upper() if suggested else 'Hết từ'}**"
        else:
            last_char = game["last_word"][-1].lower()
            suggested = pick_random_en_word(letter=last_char, used_words=game["used_words"])
            hint_msg = f"Từ Tiếng Anh bắt đầu bằng chữ **'{last_char.upper()}'**: **{suggested.upper() if suggested else 'Hết từ'}**"

        if suggested:
            user_hints[user_id] -= 1
            await interaction.response.send_message(f"💡 **GỢI Ý TỪ BOT:**\n{hint_msg}\n*(Bạn còn lại **{user_hints[user_id]}/3** lượt gợi ý hôm nay)*", ephemeral=True)
        else:
            await interaction.response.send_message("💡 Đã hết từ phù hợp trong hệ thống từ điển!", ephemeral=True)

    @discord.ui.button(label="📊 Hồ sơ", style=discord.ButtonStyle.secondary, custom_id="btn_game_profile")
    async def profile_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        u_id = str(interaction.user.id)
        stats = user_stats.get(u_id, {"wins": 0, "losses": 0, "total_words": 0})
        wins, losses = stats["wins"], stats["losses"]
        total = wins + losses
        win_rate = round((wins / total * 100), 1) if total > 0 else 0
        bar = make_progress_bar(wins, total if total > 0 else 1)
        title = get_user_title(stats["total_words"])

        embed = discord.Embed(title=f"📊 HỒ SƠ TÀI KHOẢN - {interaction.user.display_name}", color=COLOR_BLACK)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="🏅 Danh hiệu", value=f"**{title}**", inline=False)
        embed.add_field(name="🏆 Tỉ lệ thắng", value=f"`[{bar}]` **{win_rate}%**\n({wins} Thắng / {losses} Thua)", inline=True)
        embed.add_field(name="✍️ Tổng từ đã nối", value=f"**{stats['total_words']}** từ chuẩn", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# --- BOT INITIALIZATION ---
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
    print(f"Bot {bot.user} đã sẵn sàng với hệ thống Embed nâng cấp!")

# --- 🎮 CÁC LỆNH BẮT ĐẦU VÁN ĐẤU ---

# 1. Nối từ Tiếng Việt Thường
@bot.command(name="noitu")
@commands.has_permissions(administrator=True)
async def start_game_vi(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("❌ Kênh này đang có một ván đấu đang chạy!")
        return

    start_word = norm(pick_random_vi_word() or random.choice(EASY_VI_WORDS))
    games[channel_id] = {
        "mode": "vi", "vs_bot": False, "last_word": start_word,
        "count": 1, "used_words": {start_word}, "history_list": [start_word]
    }

    embed = build_game_embed(
        games[channel_id],
        title="🇻🇳 TRÒ CHƠI NỐI TỪ TIẾNG VIỆT",
        description=f"Ván đấu nối từ nhiều người đã bắt đầu!\nTừ mở màn: **{start_word.upper()}**",
        color=COLOR_BLACK,
        author_user=ctx.author
    )
    view = GameControlButtons(channel_id)
    msg = await ctx.send(embed=embed, view=view)
    await add_success_reactions(msg, 1)

# 2. Nối từ Tiếng Việt 1v1 với Bot
@bot.command(name="noitubot")
async def start_game_vi_bot(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("❌ Kênh này đang có ván đấu diễn ra rồi!")
        return

    start_word = norm(pick_random_vi_word() or random.choice(EASY_VI_WORDS))
    games[channel_id] = {
        "mode": "vi", "vs_bot": True, "last_word": start_word,
        "count": 1, "used_words": {start_word}, "history_list": [start_word]
    }

    embed = build_game_embed(
        games[channel_id],
        title="🤖 1v1 NỐI TỪ VỚI BOT",
        description=f"Bot mở màn trận đấu bằng từ: **{start_word.upper()}**\nHãy thách thức trí nhớ từ vựng của bạn nào!",
        color=COLOR_PINK,
        author_user=ctx.author
    )
    view = GameControlButtons(channel_id)
    msg = await ctx.send(embed=embed, view=view)
    await add_success_reactions(msg, 1)

# 3. Nối từ Tiếng Anh
@bot.command(name="noitueng")
async def start_game_en(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("❌ Kênh này đang có ván đấu diễn ra!")
        return

    start_word = pick_random_en_word() or "apple"
    games[channel_id] = {
        "mode": "en", "vs_bot": False, "last_word": start_word,
        "count": 1, "used_words": {start_word}, "history_list": [start_word]
    }

    embed = build_game_embed(
        games[channel_id],
        title="🇬🇧 ENGLISH WORD CHAIN GAME",
        description=f"The game has started!\nStarting word: **{start_word.upper()}**",
        color=COLOR_GOLD,
        author_user=ctx.author
    )
    view = GameControlButtons(channel_id)
    msg = await ctx.send(embed=embed, view=view)
    await add_success_reactions(msg, 1)

# --- 📊 LỆNH XEM PROFILE & DAILY ---
@bot.command(name="profile")
async def show_profile(ctx, member: discord.Member = None):
    target = member or ctx.author
    u_id = str(target.id)
    stats = user_stats.get(u_id, {"wins": 0, "losses": 0, "total_words": 0})
    wins, losses = stats["wins"], stats["losses"]
    total = wins + losses
    win_rate = round((wins / total * 100), 1) if total > 0 else 0
    bar = make_progress_bar(wins, total if total > 0 else 1)
    title = get_user_title(stats["total_words"])

    embed = discord.Embed(title=f"📊 HỒ SƠ THỐNG KÊ CHI TIẾT", color=COLOR_BLACK, timestamp=datetime.now())
    embed.set_author(name=target.display_name, icon_url=target.display_avatar.url)
    embed.set_thumbnail(url=target.display_avatar.url)
    
    embed.add_field(name="🏅 Danh hiệu Ngôn ngữ", value=f"**{title}**", inline=False)
    embed.add_field(name="🏆 Tỉ lệ Thắng / Thua", value=f"`[{bar}]` **{win_rate}%**\n({wins} Thắng | {losses} Thua)", inline=True)
    embed.add_field(name="✍️ Tổng từ chuẩn đã nối", value=f"**{stats['total_words']}** từ", inline=True)
    
    embed.set_footer(text="Discord Word Chain Bot", icon_url="https://cdn-icons-png.flaticon.com/512/2069/2069581.png")
    await ctx.send(embed=embed)

@bot.command(name="daily")
async def claim_daily(ctx):
    user_id = ctx.author.id
    today_str = str(date.today())
    if user_daily_claimed.get(user_id) == today_str:
        embed = discord.Embed(description="❌ Hôm nay bạn đã nhận lượt gợi ý rồi. Hãy quay lại vào ngày mai nhé!", color=COLOR_RED)
        await ctx.send(embed=embed)
        return

    user_hints[user_id] = 3
    user_daily_claimed[user_id] = today_str

    embed = discord.Embed(
        title="🎁 ĐIỂM DANH HẰNG NGÀY THÀNH CÔNG",
        description=f"Chúc mừng **{ctx.author.display_name}** đã nhận được **3 lượt gợi ý** `?hint` cho ngày hôm nay!",
        color=COLOR_GOLD,
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="huynoitu")
@commands.has_permissions(administrator=True)
async def stop_game(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        del games[channel_id]
        embed = discord.Embed(description="✅ Đã hủy trận đấu nối từ trên kênh này thành công.", color=COLOR_BLACK)
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Kênh này hiện không có ván đấu nào đang chạy!")

# --- 📩 XỬ LÝ LƯỢT CHƠI CỦA NGƯỜI DÙNG ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

    channel_id = message.channel.id
    if channel_id not in games or message.content.startswith("?"):
        return

    game = games[channel_id]
    user_input = message.content.strip().lower()

    # --- MODE TIẾNG VIỆT ---
    if game["mode"] == "vi":
        text = norm(user_input)
        words = text.split()
        prev_last = norm(game["last_word"].split()[-1])

        # Từ không hợp lệ -> Báo lỗi & Cho gõ lại
        if contains_bad_word(text) or len(words) != 2 or words[0] != prev_last or text in game["used_words"] or not is_valid_vietnamese_word(text):
            await add_fail_reaction(message)
            embed_err = discord.Embed(
                description=f"❌ **Từ không hợp lệ hoặc đã sử dụng!**\nVui lòng gõ lại từ Tiếng Việt (2 chữ) bắt đầu bằng tiếng **'{prev_last.upper()}'**.",
                color=COLOR_RED
            )
            await message.reply(embed=embed_err, mention_author=False)
            return

        # Nối từ hợp lệ
        game["used_words"].add(text)
        game["history_list"].append(text)
        game["last_word"] = text
        game["count"] += 1
        update_user_stats(message.author.id, added_words=1)
        await add_success_reactions(message, game["count"])

        if game["vs_bot"]:
            bot_word = pick_random_vi_word(prefix=words[-1], used_words=game["used_words"])
            if bot_word:
                bot_word_norm = norm(bot_word)
                game["used_words"].add(bot_word_norm)
                game["history_list"].append(bot_word_norm)
                game["last_word"] = bot_word_norm
                game["count"] += 1
                
                next_s = bot_word_norm.split()[-1]
                recent_history = " ➔ ".join([f"`{w.upper()}`" for w in game["history_list"][-4:]])
                
                embed_bot = discord.Embed(
                    title="🤖 LƯỢT ĐI CỦA BOT",
                    description=f"Bot nối từ: **{bot_word_norm.upper()}**\n📜 Lịch sử: {recent_history}",
                    color=COLOR_PINK
                )
                embed_bot.add_field(name="👉 Đến lượt bạn", value=f"Nối từ bắt đầu bằng tiếng **'{next_s.upper()}'**", inline=True)
                embed_bot.add_field(name="🔢 Tổng chuỗi từ", value=f"**{game['count']}** từ", inline=True)
                
                view = GameControlButtons(channel_id)
                msg = await message.channel.send(embed=embed_bot, view=view)
                await add_success_reactions(msg, game["count"])
            else:
                update_user_stats(message.author.id, win=True)
                embed_win = discord.Embed(
                    title="🎉 BẠN ĐÃ CHIẾN THẮNG BOT!",
                    description=f"Bot đã bí từ Tiếng Việt bắt đầu bằng tiếng **'{words[-1].upper()}'**!\n🏆 Tổng số từ nối được: **{game['count']}** từ.",
                    color=COLOR_GOLD,
                    timestamp=datetime.now()
                )
                embed_win.set_thumbnail(url=message.author.display_avatar.url)
                await message.channel.send(embed=embed_win)
                del games[channel_id]

    # --- MODE TIẾNG ANH ---
    elif game["mode"] == "en":
        last_char = game["last_word"][-1].lower()

        if not user_input.startswith(last_char) or user_input in game["used_words"] or not is_valid_english_word(user_input):
            await add_fail_reaction(message)
            embed_err = discord.Embed(
                description=f"❌ **Invalid English word!**\nPlease try again with a word starting with letter **'{last_char.upper()}'**.",
                color=COLOR_RED
            )
            await message.reply(embed=embed_err, mention_author=False)
            return

        game["used_words"].add(user_input)
        game["history_list"].append(user_input)
        game["last_word"] = user_input
        game["count"] += 1
        update_user_stats(message.author.id, added_words=1)
        await add_success_reactions(message, game["count"])

try:
    keep_alive()
except Exception:
    pass

TOKEN = os.getenv("DISCORD_TOKEN", "DÁN_TOKEN_DISCORD_CỦA_BẠN_VÀO_ĐÂY")
bot.run(TOKEN)
