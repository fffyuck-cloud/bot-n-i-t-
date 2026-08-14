import os
import ssl
import json
import urllib.request
import urllib.parse
import random
import re
import unicodedata
from datetime import datetime, date
import discord
from discord.ext import commands
from keep_alive import keep_alive

# --- 🎨 CẤU HÌNH ---
COLOR_THEME = 0xFF1493
BANNER_URL = "https://cdn.discordapp.com/attachments/1398867543971946578/1405789128033099836/6ab3b622-3ac8-4d11-88e3-ede9d98f7f10.png"
EMOJI_TICK = "<:Screenshot20260812172055:1537043520790073424>"
EMOJI_CROSS = "<:Screenshot20260812173722:1537047895310602300>"

def norm(text: str) -> str:
    if not text: return ""
    text = unicodedata.normalize('NFC', str(text).lower().strip())
    return re.sub(r'\s+', ' ', text)

# Dữ liệu dự phòng
FALLBACK_VI_WORDS = ["đá banh", "đá bóng", "bàn học", "học sinh", "sinh viên", "viên bi", "bi ao", "ao cá", "cá chép", "chép phạt", "phạt góc"]

def prepare_dictionaries():
    ctx = ssl._create_unverified_context()
    words_vi = set(norm(w) for w in FALLBACK_VI_WORDS)
    try:
        req = urllib.request.Request("https://raw.githubusercontent.com/NguyenAnhTuan1997/Vietnamese-Dictionary/master/words.txt", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            for line in response.read().decode('utf-8', errors='ignore').splitlines():
                word = norm(line.replace("_", " "))
                if word and len(word.split()) == 2: words_vi.add(word)
    except: pass
    
    words_en = set()
    try:
        req = urllib.request.Request("https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            for line in response.read().decode('utf-8', errors='ignore').splitlines():
                w = line.strip().lower()
                if len(w) >= 2 and w.isalpha(): words_en.add(w)
    except: pass
    return words_vi, words_en

dictionary_vi, dictionary_en = prepare_dictionaries()
VN_CHARS_REGEX = re.compile(r'^[a-zàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờờớởợùúủũụưừứửữựỳýỷỹỵđ\s]+$')

# --- 💎 HÀM TẠO EMBED GỌN GÀNG ---
def build_game_embed(game, title, last_player_name=None):
    embed = discord.Embed(color=COLOR_THEME, timestamp=datetime.now())
    embed.set_image(url=BANNER_URL) # <--- Banner nằm trong Embed
    embed.set_author(name=f"❖ {title} ❖", icon_url="https://cdn-icons-png.flaticon.com/512/8066/8066804.png")
    
    used_list = list(game.get("history_list", []))
    history_str = " ➔ ".join([w.upper() for w in used_list[-5:]])
    embed.add_field(name="📜 LỊCH SỬ (5 TỪ GẦN NHẤT)", value=f"```fix\n{history_str}\n```", inline=False)

    if game["mode"] == "vi":
        target_word = f"# 🔠 Bắt đầu bằng: `{norm(game['last_word'].split()[-1]).upper()}`"
    else:
        target_word = f"# 🔠 Bắt đầu bằng: `{game['last_word'][-1].upper()}`"

    embed.add_field(name="🎯 CẦN NỐI", value=target_word, inline=True)
    embed.add_field(name="📊 TỔNG TỪ", value=f"` {len(used_list)} từ `", inline=True)

    if game.get("is_duel"):
        p1 = game.get("p1_name"); p2 = game.get("p2_name"); turn = p1 if game["turn_idx"] == 0 else p2
        embed.add_field(name="⚔️ ĐẤU TRƯỜNG", value=f"**{p1}** vs **{p2}**\n👉 Lượt của: **{turn}**", inline=False)
    elif last_player_name:
        embed.add_field(name="✨ NGƯỜI CHƠI", value=f"**{last_player_name}** vừa nối: `{used_list[-1].upper()}`", inline=False)
    return embed

# --- 🚀 BỘ BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)
games = {}

@bot.command(name="help")
async def custom_help(ctx):
    embed = discord.Embed(title="❖ HỆ THỐNG TRỢ GIÚP ❖", color=COLOR_THEME)
    embed.set_image(url=BANNER_URL)
    embed.add_field(name="🇻🇳 Tiếng Việt", value="`?noitu` (Chung)\n`?noitubot` (Solo)", inline=True)
    embed.add_field(name="🇬🇧 Tiếng Anh", value="`?noitueng` (Chung)\n`?noituboteng` (Solo)", inline=True)
    embed.add_field(name="⚙️ Khác", value="`?thachdau @user` | `?profile` | `?nghia [từ]`", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="profile")
async def show_profile(ctx, member: discord.Member = None):
    target = member or ctx.author
    embed = discord.Embed(title=f"💎 HỒ SƠ: {target.display_name}", color=COLOR_THEME)
    embed.set_image(url=BANNER_URL)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.description = "Dữ liệu được lưu tại hệ thống."
    await ctx.send(embed=embed)

# --- XỬ LÝ GAME (Mẫu 1 lệnh, các lệnh khác copy tương tự) ---
@bot.command(name="noitu")
async def start_game_vi(ctx):
    word = "đá bóng"
    games[ctx.channel.id] = {"mode": "vi", "vs_bot": False, "is_duel": False, "last_word": word, "count": 1, "used_words": {word}, "history_list": [word]}
    await ctx.send(embed=build_game_embed(games[ctx.channel.id], "NỐI TỪ TIẾNG VIỆT"))

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    # ... logic nối từ ... (bạn giữ phần logic cũ ở đây)

try: keep_alive()
except: pass
bot.run(os.getenv("DISCORD_TOKEN"))
