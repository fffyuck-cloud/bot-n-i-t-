import os
import ssl
import json
import urllib.request
import urllib.parse
import random
import re
import unicodedata
from datetime import datetime
import discord
from discord.ext import commands
from keep_alive import keep_alive

# --- 🎨 CẤU HÌNH GIAO DIỆN & BANNER ---
COLOR_THEME = 0xFF1493 # Hồng Cyberpunk
BANNER_URL = "https://cdn.discordapp.com/attachments/1398867543971946578/1405789128033099836/6ab3b622-3ac8-4d11-88e3-ede9d98f7f10.png" 

# Custom Emoji của bạn
EMOJI_TICK = "<:Screenshot20260812172055:1537043520790073424>"
EMOJI_CROSS = "<:Screenshot20260812173722:1537047895310602300>"

def norm(text: str) -> str:
    if not text: return ""
    text = unicodedata.normalize('NFC', str(text).lower().strip())
    return re.sub(r'\s+', ' ', text)

FALLBACK_VI_WORDS = [
    "đá banh", "đá bóng", "bàn học", "học sinh", "sinh viên", "viên bi", "bi ao",
    "ao cá", "cá chép", "chép phạt", "phạt góc", "học bài", "thể thao", "bóng đá",
    "ao làng", "làng quê", "quê hương", "hương thơm", "thơm ngon", "ngon ngọt"
]

# --- 📚 TẢI TỪ ĐIỂN TIẾNG VIỆT & ANH ---
def prepare_dictionaries():
    ctx = ssl._create_unverified_context()
    words_vi = set(norm(w) for w in FALLBACK_VI_WORDS)
    
    try:
        req = urllib.request.Request("https://raw.githubusercontent.com/NguyenAnhTuan1997/Vietnamese-Dictionary/master/words.txt", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            for line in response.read().decode('utf-8', errors='ignore').splitlines():
                word = norm(line.replace("_", " "))
                if word and len(word.split()) == 2: 
                    words_vi.add(word)
    except Exception as e:
        print(f"⚠️ Dùng từ điển dự phòng VN: {e}")

    words_en = set()
    try:
        req = urllib.request.Request("https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=12) as response:
            for line in response.read().decode('utf-8', errors='ignore').splitlines():
                w = line.strip().lower()
                if len(w) >= 2 and w.isalpha(): 
                    words_en.add(w)
    except Exception as e:
        print(f"⚠️ Lỗi tải từ điển Anh: {e}")
        
    print(f"✅ Đã nạp: {len(words_vi):,} từ TV | {len(words_en):,} từ TA.")
    return words_vi, words_en

dictionary_vi, dictionary_en = prepare_dictionaries()
VN_CHARS_REGEX = re.compile(r'^[a-zàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]+$')

# Vừa fix: Chỉ kiểm tra đúng 2 từ và là chữ VN hợp lệ, không ép người chơi phải nhập đúng từ trong từ điển nữa
def is_valid_vietnamese_word(text):
    text_clean = norm(text)
    return len(text_clean.split()) == 2 and bool(VN_CHARS_REGEX.match(text_clean))

def is_valid_english_word(text):
    return text.strip().lower() in dictionary_en

def pick_random_vi_word(prefix=None, used_words=None):
    used_words = {norm(w) for w in used_words} if used_words else set()
    prefix_norm = norm(prefix) if prefix else None
    all_w = [w for w in dictionary_vi if (not prefix_norm or norm(w).startswith(prefix_norm + " ")) and norm(w) not in used_words]
    return random.choice(all_w) if all_w else None

def pick_random_en_word(letter=None, used_words=None):
    used_words = {w.lower() for w in used_words} if used_words else set()
    letter = letter.lower() if letter else None
    all_candidates = [w for w in dictionary_en if (not letter or w.startswith(letter)) and w not in used_words]
    return random.choice(all_candidates) if all_candidates else None

# --- 💎 HÀM TẠO EMBED CHI TIẾT ---
def build_game_embed(game, title, last_player_name=None):
    embed = discord.Embed(color=COLOR_THEME, timestamp=datetime.now())
    embed.set_image(url=BANNER_URL)
    embed.set_author(name=f"❖ {title} ❖", icon_url="https://cdn-icons-png.flaticon.com/512/8066/8066804.png")
    
    used_list = list(game.get("history_list", []))
    history_str = " ➔ ".join([w.upper() for w in used_list[-5:]])
    embed.add_field(name="📜 LỊCH SỬ TỪ VỰNG (5 GẦN NHẤT)", value=f"```fix\n{history_str}\n```", inline=False)

    if game["mode"] == "vi":
        prev_last = norm(game["last_word"].split()[-1]).upper()
        target_word = f"# 🔠 Bắt đầu bằng: `{prev_last}`"
    else:
        last_char = game["last_word"][-1].upper()
        target_word = f"# 🔠 Bắt đầu bằng: `{last_char}`"

    combo = game.get('count', 1)
    bar = f"`[{'█'*min(10, combo)}{'░'*max(0, 10-combo)}]`"
    
    embed.add_field(name="🎯 MỤC TIÊU TỪ", value=target_word, inline=True)
    embed.add_field(name="🔥 LEVEL / COMBO", value=f"**Level {combo}**\n{bar}", inline=True)
    embed.add_field(name="📊 TỔNG SỐ TỪ", value=f"` {len(used_list)} từ đã nối `", inline=True)

    if last_player_name:
        embed.add_field(name="╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯", value=f"✨ Từ vừa nối: **`{used_list[-1].upper()}`**\n👤 Người chơi: **{last_player_name}**", inline=False)
    else:
        embed.add_field(name="╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯", value="> 💬 *Hãy chat từ tiếp theo trực tiếp vào kênh chat này.*\n> *Gõ `?huynoitu` nếu muốn dừng ván chơi.*", inline=False)

    return embed

# --- 🚀 KHỞI TẠO BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)
games = {}

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user.name} đã sẵn sàng hoạt động!")

@bot.command(name="help")
async def custom_help(ctx):
    embed = discord.Embed(color=COLOR_THEME)
    embed.set_image(url=BANNER_URL)
    embed.set_author(name="❖ HỆ THỐNG TRỢ GIÚP NỐI TỪ ❖", icon_url=bot.user.display_avatar.url)
    embed.description = ">>> 🎮 **Word Chain Ultimate Bot**\nHỗ trợ kho từ vựng khổng lồ Tiếng Việt & Tiếng Anh, chế độ chơi chung hoặc Solo Bot!"
    
    embed.add_field(name="🇻🇳 NỐI TỪ TIẾNG VIỆT", value="`?noitu` ➔ Chơi chung kênh\n`?noitubot` ➔ Solo với Bot", inline=True)
    embed.add_field(name="🇬🇧 NỐI TỪ TIẾNG ANH", value="`?noitueng` ➔ Chơi chung kênh\n`?noituboteng` ➔ Solo với Bot", inline=True)
    embed.add_field(name="⚙️ QUẢN LÝ TRẬN ĐẤU", value="`?huynoitu` ➔ Hủy ván chơi hiện tại\n`?nghia [từ]` ➔ Tra nghĩa từ điển Anh", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="huynoitu")
async def stop_game(ctx):
    if ctx.channel.id in games:
        del games[ctx.channel.id]
        embed = discord.Embed(title="🛑 ĐÃ HỦY VÁN NỐI TỪ", description="Trận đấu tại kênh này đã được kết thúc thành công.", color=0xED4245)
        embed.set_image(url=BANNER_URL)
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Không có trận đấu nào đang diễn ra tại kênh này.")

@bot.command(name="noitu")
async def start_game_vi(ctx):
    if ctx.channel.id in games: return await ctx.send("⚠️ Kênh đang có trận đấu diễn ra! Dùng `?huynoitu` nếu muốn hủy.")
    word = norm(pick_random_vi_word() or "đá bóng")
    games[ctx.channel.id] = {"mode": "vi", "vs_bot": False, "last_word": word, "count": 1, "used_words": {word}, "history_list": [word]}
    await ctx.send(embed=build_game_embed(games[ctx.channel.id], "NỐI TỪ TIẾNG VIỆT (MULTIPLAYER)"))

@bot.command(name="noitubot")
async def start_game_vi_bot(ctx):
    if ctx.channel.id in games: return await ctx.send("⚠️ Kênh đang có trận đấu diễn ra! Dùng `?huynoitu` nếu muốn hủy.")
    word = norm(pick_random_vi_word() or "đá bóng")
    games[ctx.channel.id] = {"mode": "vi", "vs_bot": True, "last_word": word, "count": 1, "used_words": {word}, "history_list": [word]}
    await ctx.send(embed=build_game_embed(games[ctx.channel.id], "NỐI TỪ TIẾNG VIỆT (VS BOT)"))

@bot.command(name="noitueng")
async def start_game_en(ctx):
    if ctx.channel.id in games: return await ctx.send("⚠️ Kênh đang có trận đấu diễn ra! Dùng `?huynoitu` nếu muốn hủy.")
    word = pick_random_en_word() or "apple"
    games[ctx.channel.id] = {"mode": "en", "vs_bot": False, "last_word": word, "count": 1, "used_words": {word}, "history_list": [word]}
    await ctx.send(embed=build_game_embed(games[ctx.channel.id], "ENGLISH WORD CHAIN (MULTIPLAYER)"))

@bot.command(name="noituboteng")
async def start_game_en_bot(ctx):
    if ctx.channel.id in games: return await ctx.send("⚠️ Kênh đang có trận đấu diễn ra! Dùng `?huynoitu` nếu muốn hủy.")
    word = pick_random_en_word() or "apple"
    games[ctx.channel.id] = {"mode": "en", "vs_bot": True, "last_word": word, "count": 1, "used_words": {word}, "history_list": [word]}
    await ctx.send(embed=build_game_embed(games[ctx.channel.id], "ENGLISH WORD CHAIN (VS BOT)"))

# --- 📩 XỬ LÝ LƯỢT CHƠI NỐI TỪ ---
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

        # Luật mới: Yêu cầu đúng 2 từ, chữ đầu khớp, chưa được dùng và là ký tự VN hợp lệ
        if len(words) != 2 or words[0] != prev_last or text in game["used_words"] or not is_valid_vietnamese_word(text):
            await message.add_reaction(EMOJI_CROSS)
            return

        game["used_words"].add(text)
        game["history_list"].append(text)
        game["last_word"] = text
        game["count"] += 1
        await message.add_reaction(EMOJI_TICK)

        if game["vs_bot"]:
            bot_word = pick_random_vi_word(prefix=words[-1], used_words=game["used_words"])
            if bot_word:
                game["used_words"].add(bot_word)
                game["history_list"].append(bot_word)
                game["last_word"] = bot_word
                game["count"] += 1
                await message.channel.send(embed=build_game_embed(game, "NỐI TỪ TIẾNG VIỆT (VS BOT)", last_player_name="🤖 Bot Trí Tuệ"))
            else:
                embed = discord.Embed(title="🏆 BẠN ĐÃ CHIẾN THẮNG BOT!", description="Bot đã cạn kiệt từ vựng tiếng Việt có thể nối tiếp!", color=0x57F287)
                embed.set_image(url=BANNER_URL)
                await message.channel.send(embed=embed)
                del games[message.channel.id]
        else:
            await message.channel.send(embed=build_game_embed(game, "NỐI TỪ TIẾNG VIỆT", last_player_name=message.author.display_name))

    elif game["mode"] == "en":
        last_char = game["last_word"][-1].lower()
        if not user_input.startswith(last_char) or user_input in game["used_words"] or not is_valid_english_word(user_input):
            await message.add_reaction(EMOJI_CROSS)
            return

        game["used_words"].add(user_input)
        game["history_list"].append(user_input)
        game["last_word"] = user_input
        game["count"] += 1
        await message.add_reaction(EMOJI_TICK)

        if game["vs_bot"]:
            bot_word = pick_random_en_word(letter=user_input[-1], used_words=game["used_words"])
            if bot_word:
                game["used_words"].add(bot_word)
                game["history_list"].append(bot_word)
                game["last_word"] = bot_word
                game["count"] += 1
                await message.channel.send(embed=build_game_embed(game, "ENGLISH WORD CHAIN (VS BOT)", last_player_name="🤖 English Bot"))
            else:
                embed = discord.Embed(title="🏆 YOU BEAT THE BOT!", description="The Bot ran out of English words!", color=0x57F287)
                embed.set_image(url=BANNER_URL)
                await message.channel.send(embed=embed)
                del games[message.channel.id]
        else:
            await message.channel.send(embed=build_game_embed(game, "ENGLISH WORD CHAIN", last_player_name=message.author.display_name))

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
