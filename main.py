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

# --- 🎨 BẢNG MÀU THEME & HÌNH ẢNH (ULTIMATE EDITION) ---
COLOR_BLACK     = 0x2B2D31 
COLOR_PINK      = 0xFF69B4 
COLOR_DEEP_PINK = 0xFF1493 
COLOR_RED       = 0xFF4747 
COLOR_SUCCESS   = 0x57F287 
COLOR_ERROR     = 0xED4245 

BANNER_HELP = "https://i.imgur.com/xT5l7Hn.gif" 

def norm(text: str) -> str:
    if not text: return ""
    text = unicodedata.normalize('NFC', str(text).lower().strip())
    return re.sub(r'\s+', ' ', text)

BAD_WORDS = {norm("ỉa")}
DEAD_END_WORDS = {norm(w) for w in ["vậy", "sao", "mà", "thì", "là", "nhé", "à", "nhỉ", "nè", "đâu", "đó", "nào", "đấy", "ư", "hử", "nha", "nghen", "ha", "kìa", "này", "chứ", "rồi"]}

EASY_VI_WORDS = ["đá banh", "đá bóng", "bàn học", "học sinh", "sinh viên", "viên bi", "bi ao", "ao cá", "cá chép", "chép phạt", "phạt góc", "học bài", "thể thao", "bóng đá", "cầu thủ"]
easy_en_words_set = {"apple", "banana", "cat", "dog", "elephant", "fish", "giraffe", "house", "ice", "jungle", "kite", "lemon", "monkey", "nest", "orange"}

# --- 🎭 KHO LỜI THOẠI KHI TRẢ LỜI SAI (ĐA DẠNG & CÀ KHỊA) ---
VI_ERROR_RESPONSES = [
    "Sai bét nhè rồi đại thần ơi! Từ này không hợp lệ hoặc sai vần.",
    "Ọt ẹc, tính lừa bot hả? Cố gắng đọc kỹ luật chơi lại xem nào!",
    "Đi lạc hướng rồi nha! Bộ não đang đình công hay gì thế?",
    "Giao thông bế tắc! Từ này không dùng được hoặc sai vần rồi.",
    "Sai hoàn toàn! Đừng để bot phải cười chê chứ lị.",
    "Ê ê, gõ nhầm bàn phím à? Từ này không nằm trong từ điển nối từ đâu!"
]

EN_ERROR_RESPONSES = [
    "Oops! That's completely wrong or already used. Try again!",
    "Nice try, but your English vocabulary needs a little upgrade!",
    "Nope! That word doesn't match the rules. Wake up!",
    "Grammar police says NO! Check your spelling or starting letter.",
    "Error 404: Valid English word not found in your typing."
]

def contains_bad_word(text):
    text_clean = norm(text)
    for word in text_clean.split():
        if word in BAD_WORDS: return True
    return text_clean in BAD_WORDS

def is_dead_end_word(word):
    word_clean = norm(word)
    syllables = word_clean.split()
    return len(syllables) == 2 and syllables[-1] in DEAD_END_WORDS

# --- 📚 NẠP TỪ ĐIỂN ---
def prepare_dictionaries():
    ctx = ssl._create_unverified_context()
    words_vi = set(norm(w) for w in EASY_VI_WORDS)
    try:
        req = urllib.request.Request("https://raw.githubusercontent.com/NguyenAnhTuan1997/Vietnamese-Dictionary/master/words.txt", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            for line in response.read().decode('utf-8', errors='ignore').splitlines():
                word = norm(line.replace("_", " "))
                if word and len(word.split()) == 2 and not contains_bad_word(word): words_vi.add(word)
    except: pass

    words_en = set()
    try:
        req = urllib.request.Request("https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            for line in response.read().decode('utf-8', errors='ignore').splitlines():
                w = line.strip().lower()
                if len(w) >= 2 and w.isalpha(): words_en.add(w)
    except: pass
    print(f"✅ NẠP DATA: {len(words_vi):,} từ VN | {len(words_en):,} từ EN.")
    return words_vi, words_en

dictionary_vi, dictionary_en = prepare_dictionaries()
VN_CHARS_REGEX = re.compile(r'^[a-zàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]+$')

def is_valid_vietnamese_word(text):
    text_clean = norm(text)
    return len(text_clean.split()) == 2 and VN_CHARS_REGEX.match(text_clean) and text_clean in dictionary_vi

def is_valid_english_word(text):
    return text.strip().lower() in dictionary_en

def pick_random_vi_word(prefix=None, used_words=None):
    used_words = {norm(w) for w in used_words} if used_words else set()
    prefix_norm = norm(prefix) if prefix else None
    all_w = [w for w in dictionary_vi if (not prefix_norm or norm(w).startswith(prefix_norm + " ")) and norm(w) not in used_words and not is_dead_end_word(w)]
    return random.choice(all_w) if all_w else None

def pick_random_en_word(letter=None, used_words=None):
    used_words = {w.lower() for w in used_words} if used_words else set()
    letter = letter.lower() if letter else None
    all_candidates = [w for w in dictionary_en if (not letter or w.startswith(letter)) and w not in used_words]
    return random.choice(all_candidates) if all_candidates else None

# --- 💾 THỐNG KÊ (DATABASE) ---
STATS_FILE = "user_stats.json"

def load_json():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

user_stats = load_json()

def save_json():
    with open(STATS_FILE, "w", encoding="utf-8") as f: json.dump(user_stats, f, ensure_ascii=False, indent=4)

def update_user_stats(user_id, added_words=0, win=False, loss=False):
    u_id = str(user_id)
    if u_id not in user_stats: user_stats[u_id] = {"wins": 0, "losses": 0, "total_words": 0}
    user_stats[u_id]["total_words"] += added_words
    if win: user_stats[u_id]["wins"] += 1
    if loss: user_stats[u_id]["losses"] += 1
    save_json()

def get_user_title(total_words):
    if total_words >= 1000: return "🌟 CHÚA TỂ NGÔN TỪ"
    if total_words >= 500: return "👑 BẬC THẦY GIAO TIẾP"
    if total_words >= 200: return "🔥 CAO THỦ NỐI TỪ"
    if total_words >= 50: return "✨ TAY CHƠI TRIỂN VỌNG"
    return "🐣 TÂN THỦ NHẬP MÔN"

# --- 💎 PREMIUM EMBED BUILDER ---
def build_game_embed(game, title, color, author_user=None, last_player_name=None):
    embed = discord.Embed(color=color, timestamp=datetime.now())
    embed.set_author(name=f" ❖ {title} ❖", icon_url="https://cdn-icons-png.flaticon.com/512/8066/8066804.png")
    
    used_list = list(game.get("history_list", []))
    history_str = " ➔ ".join([w.upper() for w in used_list[-5:]])
    embed.add_field(name="╭━━━━━━━━ 📜 DÒNG CHẢY TỪ VỰNG ━━━━━━━━╮", value=f"```fix\n{history_str}\n```", inline=False)

    if game["mode"] == "vi":
        prev_last = norm(game["last_word"].split()[-1]).upper()
        target_word = f"# 🔠 {prev_last}"
    else:
        last_char = game["last_word"][-1].upper()
        target_word = f"# 🔠 {last_char}"

    combo = game.get('count', 1)
    bar = f"`[{'█'*min(10, combo)}{'░'*max(0, 10-combo)}]`"

    embed.add_field(name="🎯 **NỐI TIẾP BẰNG**", value=target_word, inline=True)
    embed.add_field(name="🔥 **CHUỖI COMBO**", value=f"**{combo}**\n{bar}", inline=True)

    if last_player_name:
        embed.add_field(name="╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯", value=f"✨ Lượt vừa nối: **{last_player_name}**", inline=False)
    else:
        embed.add_field(name="╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯", value="> 💬 *Chat trực tiếp từ nối vào kênh. Không cần dùng dấu `?`*", inline=False)

    flag = "https://cdn-icons-png.flaticon.com/512/197/197473.png" if game["mode"] == "vi" else "https://cdn-icons-png.flaticon.com/512/197/197374.png"
    embed.set_thumbnail(url=flag)
    embed.set_footer(text=f"Host: {author_user.display_name}" if author_user else "Word Chain Engine v2.0", icon_url=author_user.display_avatar.url if author_user else None)
    return embed

# --- 🖱️ HỆ THỐNG NÚT BẤM ---
class GameControlButtons(discord.ui.View):
    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="Cứu Viện (Gợi Ý)", emoji="🆘", style=discord.ButtonStyle.danger, custom_id="btn_hint")
    async def hint_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel_id = interaction.channel_id
        if channel_id not in games: return await interaction.response.send_message("❌ Trận đấu đã kết thúc!", ephemeral=True)
        user_id = interaction.user.id
        hints_left = user_hints.get(user_id, 0)
        if hints_left <= 0: return await interaction.response.send_message("❌ Cạn kiệt Lượt Gợi Ý! Gõ `?daily` để nhận thêm.", ephemeral=True)

        game = games[channel_id]
        if game["mode"] == "vi":
            suggested = pick_random_vi_word(prefix=norm(game["last_word"].split()[-1]), used_words=game["used_words"])
        else:
            suggested = pick_random_en_word(letter=game["last_word"][-1].lower(), used_words=game["used_words"])

        if suggested:
            user_hints[user_id] -= 1
            await interaction.response.send_message(f"💡 Hỗ trợ: **`{suggested.upper()}`** *(Còn {user_hints[user_id]} lượt)*", ephemeral=True)
        else:
            await interaction.response.send_message("💀 Chịu chết! Hệ thống cũng đã bí từ hợp lệ.", ephemeral=True)

    @discord.ui.button(label="Xem Hồ Sơ", emoji="💎", style=discord.ButtonStyle.primary, custom_id="btn_profile")
    async def profile_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        stats = user_stats.get(str(interaction.user.id), {"wins": 0, "losses": 0, "total_words": 0})
        await interaction.response.send_message(f"🏅 **Rank:** {get_user_title(stats['total_words'])}\n🧠 **Vốn từ:** `{stats['total_words']}` từ", ephemeral=True)

# --- 🚀 BOT INIT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)
games, user_hints, user_daily_claimed = {}, {}, {}

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user.name} online (Bản Chát Đa Dạng & Embed Đẹp)!")
    await bot.change_presence(activity=discord.Game(name="?help | Nối Từ Đỉnh Cao"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound): return 
    raise error 

# --- 📜 LỆNH CHỨC NĂNG ---
@bot.command(name="help", aliases=["trogiup", "menu"])
async def custom_help(ctx):
    embed = discord.Embed(color=COLOR_PINK)
    embed.set_author(name=" ❖ BẢNG ĐIỀU KHIỂN HỆ THỐNG NỐI TỪ ❖", icon_url=bot.user.display_avatar.url)
    embed.set_image(url=BANNER_HELP)
    embed.description = ">>> 🎮 **Word Chain Master V2**\nThử thách vốn từ vựng cực mạnh với kho lời thoại cực lầy lội!"
    
    embed.add_field(name="🇻🇳 TIẾNG VIỆT", value="`?noitu` ➔ Chơi chung\n`?noitubot` ➔ Solo Bot", inline=True)
    embed.add_field(name="🔤 TIẾNG ANH", value="`?noitueng` ➔ Chơi chung\n`?noituboteng` ➔ Solo Bot", inline=True)
    embed.add_field(name="\u200B", value="\u200B", inline=False)
    embed.add_field(name="⚙️ TIỆN ÍCH", value="`?daily` ➔ Điểm danh nhận Gợi ý\n`?profile` ➔ Xem thông số cá nhân\n`?huynoitu` ➔ Hủy ván", inline=False)
    
    embed.set_footer(text="Dev by Word Chain Master", icon_url="https://cdn-icons-png.flaticon.com/512/2069/2069581.png")
    await ctx.send(embed=embed)

@bot.command(name="profile")
async def show_profile(ctx, member: discord.Member = None):
    target = member or ctx.author
    stats = user_stats.get(str(target.id), {"wins": 0, "losses": 0, "total_words": 0})
    w, l, total = stats["wins"], stats["losses"], stats["total_words"]
    win_rate = round((w / (w + l) * 100), 1) if (w + l) > 0 else 0

    embed = discord.Embed(title=f"💎 HỒ SƠ NGƯỜI CHƠI", color=COLOR_BLACK)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="👤 Tên Tài Khoản", value=f"**{target.display_name}**", inline=True)
    embed.add_field(name="🏅 Danh Hiệu", value=f"**{get_user_title(total)}**", inline=True)
    embed.add_field(name="\u200B", value="\u200B", inline=False)
    embed.add_field(name="🧠 Vốn Từ (Kinh nghiệm)", value=f"```diff\n+ {total:,} từ chuẩn\n```", inline=True)
    embed.add_field(name="⚔️ Tỉ Lệ Thắng Bot", value=f"```ini\n[ {win_rate}% ] ({w} Thắng / {l} Thua)\n```", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="daily")
async def claim_daily(ctx):
    user_id, today_str = ctx.author.id, str(date.today())
    if user_daily_claimed.get(user_id) == today_str: return await ctx.send("❌ Đừng tham lam! Bạn đã nhận thưởng hôm nay rồi.")
    user_hints[user_id] = 3
    user_daily_claimed[user_id] = today_str
    
    embed = discord.Embed(title="🎁 NHẬN THƯỞNG THÀNH CÔNG", description=f"> **{ctx.author.display_name}** đã được nạp **3 Lượt Cứu Viện** 🆘!", color=COLOR_SUCCESS)
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

# --- 🎮 LỆNH GAME ---
@bot.command(name="noitu")
async def start_game_vi(ctx):
    if ctx.channel.id in games: return await ctx.send("⚠️ Kênh này đang diễn ra một trận chiến rồi!")
    word = norm(pick_random_vi_word() or random.choice(EASY_VI_WORDS))
    games[ctx.channel.id] = {"mode": "vi", "vs_bot": False, "last_word": word, "count": 1, "used_words": {word}, "history_list": [word]}
    await ctx.send(embed=build_game_embed(games[ctx.channel.id], "NỐI TỪ TIẾNG VIỆT (MULTIPLAYER)", COLOR_BLACK, ctx.author), view=GameControlButtons(ctx.channel.id))

@bot.command(name="noitubot")
async def start_game_vi_bot(ctx):
    if ctx.channel.id in games: return await ctx.send("⚠️ Kênh này đang giao tranh rồi!")
    word = norm(pick_random_vi_word() or random.choice(EASY_VI_WORDS))
    games[ctx.channel.id] = {"mode": "vi", "vs_bot": True, "last_word": word, "count": 1, "used_words": {word}, "history_list": [word]}
    await ctx.send(embed=build_game_embed(games[ctx.channel.id], "NỐI TỪ TIẾNG VIỆT (VS BOT)", COLOR_PINK, ctx.author), view=GameControlButtons(ctx.channel.id))

@bot.command(name="noitueng")
async def start_game_en(ctx):
    if ctx.channel.id in games: return await ctx.send("⚠️ Kênh này đang giao tranh rồi!")
    word = pick_random_en_word() or "apple"
    games[ctx.channel.id] = {"mode": "en", "vs_bot": False, "last_word": word, "count": 1, "used_words": {word}, "history_list": [word]}
    await ctx.send(embed=build_game_embed(games[ctx.channel.id], "ENGLISH WORD CHAIN (MULTIPLAYER)", COLOR_DEEP_PINK, ctx.author), view=GameControlButtons(ctx.channel.id))

@bot.command(name="noituboteng")
async def start_game_en_bot(ctx):
    if ctx.channel.id in games: return await ctx.send("⚠️ Kênh này đang giao tranh rồi!")
    word = pick_random_en_word() or "apple"
    games[ctx.channel.id] = {"mode": "en", "vs_bot": True, "last_word": word, "count": 1, "used_words": {word}, "history_list": [word]}
    await ctx.send(embed=build_game_embed(games[ctx.channel.id], "ENGLISH WORD CHAIN (VS BOT)", COLOR_RED, ctx.author), view=GameControlButtons(ctx.channel.id))

@bot.command(name="huynoitu")
async def stop_game(ctx):
    if ctx.channel.id in games:
        del games[ctx.channel.id]
        await ctx.message.add_reaction("✅")
        await ctx.send(embed=discord.Embed(description="🛑 Đã đình chỉ trận đấu tại kênh này.", color=COLOR_ERROR))
    else:
        await ctx.send("❌ Ở đây làm gì có trận nào đang chạy mà hủy?")

# --- 📩 XỬ LÝ LOGIC NỐI TỪ & THÔNG BÁO SAI SIÊU ĐẸP ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    await bot.process_commands(message)
    if message.channel.id not in games or message.content.startswith("?"): return
    
    game = games[message.channel.id]
    user_input = message.content.strip().lower()

    if game["mode"] == "vi":
        text = norm(user_input)
        words = text.split()
        prev_last = norm(game["last_word"].split()[-1])

        if len(words) != 2 or words[0] != prev_last or text in game["used_words"] or not is_valid_vietnamese_word(text):
            await message.add_reaction("❌")
            # Chọn ngẫu nhiên một câu thoại cà khịa lỗi
            funny_msg = random.choice(VI_ERROR_RESPONSES)
            err_embed = discord.Embed(
                title="⚠️ TỪ KHÔNG HỢP LỆ!",
                description=f"> **{funny_msg}**\n\n📌 Từ tiếp theo bắt buộc phải bắt đầu bằng: **`{prev_last.upper()}`** (Gồm 2 âm tiết)",
                color=COLOR_ERROR
            )
            return await message.reply(embed=err_embed, delete_after=7)

        game["used_words"].add(text)
        game["history_list"].append(text)
        game["last_word"] = text
        game["count"] += 1
        update_user_stats(message.author.id, added_words=1)
        await message.add_reaction("✅")

        if game["vs_bot"]:
            bot_word = pick_random_vi_word(prefix=words[-1], used_words=game["used_words"])
            if bot_word:
                game["used_words"].add(bot_word)
                game["history_list"].append(bot_word)
                game["last_word"] = bot_word
                game["count"] += 1
                await message.channel.send(embed=build_game_embed(game, "ĐẾN LƯỢT BOT ĐÁP TRẢ", COLOR_PINK, last_player_name="🤖 Trí Tuệ Nhân Tạo"), view=GameControlButtons(message.channel.id))
            else:
                update_user_stats(message.author.id, win=True)
                embed_win = discord.Embed(title="🏆 CHIẾN THẮNG ÁP ĐẢO!", description=f"```diff\n+ Bot đã cạn kiệt từ vựng trước bộ não của {message.author.display_name}!\n+ Tích lũy trận này: {game['count']} từ.\n```", color=COLOR_SUCCESS)
                await message.channel.send(embed=embed_win)
                del games[message.channel.id]

    elif game["mode"] == "en":
        last_char = game["last_word"][-1].lower()
        if not user_input.startswith(last_char) or user_input in game["used_words"] or not is_valid_english_word(user_input):
            await message.add_reaction("❌")
            funny_msg_en = random.choice(EN_ERROR_RESPONSES)
            err_embed_en = discord.Embed(
                title="⚠️ INVALID WORD!",
                description=f"> **{funny_msg_en}**\n\n📌 Must start with letter: **`{last_char.upper()}`**",
                color=COLOR_ERROR
            )
            return await message.reply(embed=err_embed_en, delete_after=7)

        game["used_words"].add(user_input)
        game["history_list"].append(user_input)
        game["last_word"] = user_input
        game["count"] += 1
        update_user_stats(message.author.id, added_words=1)
        await message.add_reaction("✅")

        if game["vs_bot"]:
            bot_word = pick_random_en_word(letter=user_input[-1], used_words=game["used_words"])
            if bot_word:
                game["used_words"].add(bot_word)
                game["history_list"].append(bot_word)
                game["last_word"] = bot_word
                game["count"] += 1
                await message.channel.send(embed=build_game_embed(game, "BOT'S TURN (ENGLISH)", COLOR_RED, last_player_name="🤖 English Bot"), view=GameControlButtons(message.channel.id))
            else:
                update_user_stats(message.author.id, win=True)
                embed_win = discord.Embed(title="🏆 YOU BEAT THE SYSTEM!", description=f"```diff\n+ The bot is out of words starting with {user_input[-1].upper()}!\n+ Total streak: {game['count']} words.\n```", color=COLOR_SUCCESS)
                await message.channel.send(embed=embed_win)
                del games[message.channel.id]

try: keep_alive()
except: pass
bot.run(os.getenv("DISCORD_TOKEN"))
