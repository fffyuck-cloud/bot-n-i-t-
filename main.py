import os
import ssl
import urllib.request
import random
import re
import unicodedata
from datetime import datetime, timedelta
import io

import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageOps, ImageFont

# Khởi tạo Web Server để Render không bị sập
try:
    from keep_alive import keep_alive
except ImportError:
    def keep_alive(): pass # Fallback nếu đéo có file keep_alive.py

# --- 🎨 CẤU HÌNH EMOJI VÀ MÀU SẮC ---
TICK = "<:Screenshot20260812172055:1537043520790073424>"
CROSS = "<:Screenshot20260812173722:1537047895310602300>"
COLOR_THEME = 0xFF007F

# --- HỖ TRỢ FONT CHỮ TRÁNH LỖI PILLOW ---
try:
    font_large = ImageFont.load_default(size=22)
    font_medium = ImageFont.load_default(size=18)
    font_small = ImageFont.load_default(size=14)
except Exception:
    font_large = font_medium = font_small = ImageFont.load_default()

def norm(text: str) -> str:
    if not text: return ""
    text = unicodedata.normalize('NFC', str(text).lower().strip())
    return re.sub(r'\s+', ' ', text)

# --- 📚 TẢI TỪ ĐIỂN ---
FALLBACK_VI_WORDS = ["đá bóng", "bóng đá", "học sinh", "sinh viên", "thể thao"]
def prepare_dictionaries():
    ctx = ssl._create_unverified_context()
    words_vi = set(norm(w) for w in FALLBACK_VI_WORDS)
    try:
        req = urllib.request.Request("https://raw.githubusercontent.com/NguyenAnhTuan1997/Vietnamese-Dictionary/master/words.txt", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            for line in response.read().decode('utf-8', errors='ignore').splitlines():
                word = norm(line.replace("_", " "))
                if word and len(word.split()) == 2: words_vi.add(word)
    except: pass
    
    words_en = set()
    try:
        req = urllib.request.Request("https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            for line in response.read().decode('utf-8', errors='ignore').splitlines():
                w = line.strip().lower()
                if len(w) >= 2 and w.isalpha(): words_en.add(w)
    except: pass
    return words_vi, words_en

dictionary_vi, dictionary_en = prepare_dictionaries()
VN_CHARS_REGEX = re.compile(r'^[a-zàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]+$')

def is_valid_vietnamese_word(text): return len(norm(text).split()) == 2 and bool(VN_CHARS_REGEX.match(norm(text)))
def is_valid_english_word(text): return text.strip().lower() in dictionary_en

# --- 📊 DATABASE USER & HÀM VẼ ẢNH ---
user_profiles = {}
def get_user_data(user_id):
    if user_id not in user_profiles:
        user_profiles[user_id] = {"xp": 100, "level": 1, "rank": 1, "streak": 0, "last_daily": None}
    return user_profiles[user_id]

def get_background():
    try:
        bg = Image.open("d89db057-b415-48f7-8603-47052617b39e.png").convert("RGBA")
        return ImageOps.fit(bg, (600, 200), Image.Resampling.LANCZOS)
    except Exception as e:
        print(f"⚠️ Đéo thấy file nền: {e}")
        return Image.new("RGBA", (600, 200), "#0b0b0e")

async def create_rank_card(member, data):
    image = get_background()
    draw = ImageDraw.Draw(image)
    
    overlay = Image.new("RGBA", (600, 200), (0, 0, 0, 140))
    image.alpha_composite(overlay)
    draw.rectangle([5, 5, 595, 195], outline="#ff007f", width=3)
    
    try:
        avatar_url = member.display_avatar.with_size(128).url
        req = urllib.request.Request(avatar_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            avatar_img = Image.open(io.BytesIO(resp.read())).convert("RGBA")
            avatar_img = avatar_img.resize((110, 110))
            mask = Image.new("L", (110, 110), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 110, 110), fill=255)
            image.paste(avatar_img, (40, 45), mask)
    except: pass
        
    draw.ellipse((38, 43, 152, 157), outline="#ff007f", width=4)
    
    draw.text((170, 45), f"{member.display_name}", fill="#ffffff", font=font_large)
    draw.text((170, 75), f"@{member.user.username}", fill="#a0a0ab", font=font_small)
    draw.text((450, 45), f"RANK #{data['rank']}", fill="#ff007f", font=font_large)
    draw.text((450, 75), f"LVL {data['level']}", fill="#ffffff", font=font_medium)
    
    xp_needed = data["level"] * 300
    progress = min(data["xp"] / xp_needed, 1.0)
    draw.rounded_rectangle([170, 120, 560, 142], radius=11, fill="#1a1a24")
    if progress > 0:
        draw.rounded_rectangle([170, 120, 170 + int(390 * progress), 142], radius=11, fill="#ff007f")
    draw.text((180, 124), f"XP: {data['xp']} / {xp_needed}", fill="#ffffff", font=font_small)
    
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return discord.File(buffer, filename="rank.png")

async def create_daily_card(member, reward, success):
    image = get_background()
    draw = ImageDraw.Draw(image)
    overlay = Image.new("RGBA", (600, 200), (0, 0, 0, 160))
    image.alpha_composite(overlay)
    
    draw.rectangle([5, 5, 595, 195], outline="#ff007f", width=3)
    
    status_text = "ĐIỂM DANH THÀNH CÔNG" if success else "ĐÃ ĐIỂM DANH RỒI"
    color = "#57F287" if success else "#ED4245"
    
    draw.text((170, 60), status_text, fill=color, font=font_large)
    if success:
        draw.text((170, 100), f"Phần thưởng: {reward} XP", fill="#ffffff", font=font_medium)
    else:
        draw.text((170, 100), "Mai quay lại nhận nhé!", fill="#ffffff", font=font_medium)
    
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return discord.File(buffer, filename="daily.png")

# --- 🚀 KHỞI TẠO BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)
games = {}

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user.name} đã sẵn sàng bão táp!")

@bot.command(name="rank")
async def rank_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = get_user_data(member.id)
    file = await create_rank_card(member, data)
    await ctx.send(file=file)

@bot.command(name="daily")
async def daily_cmd(ctx):
    user_id = ctx.author.id
    data = get_user_data(user_id)
    now = datetime.now()
    claimed = True
    reward = 100 * (data["streak"] + 1)

    if data["last_daily"]:
        last_time = datetime.fromisoformat(data["last_daily"])
        if now - last_time < timedelta(hours=24): claimed = False

    if claimed:
        data["last_daily"] = now.isoformat()
        data["streak"] += 1
        data["xp"] += reward
        
    icon = TICK if claimed else CROSS
    file = await create_daily_card(ctx.author, reward, claimed)
    await ctx.send(f"{icon} Yêu cầu của {ctx.author.mention}:", file=file)

@bot.command(name="noitu")
async def start_game_vi(ctx):
    if ctx.channel.id in games: return await ctx.send("⚠️ Kênh đang có ván chơi rồi!")
    word = "đá bóng"
    games[ctx.channel.id] = {"mode": "vi", "last_word": word, "used_words": {word}}
    await ctx.send(f"🎮 **NỐI TỪ TIẾNG VIỆT** bắt đầu! Từ đầu tiên: **`{word.upper()}`**")

@bot.command(name="huynoitu")
async def stop_game(ctx):
    if ctx.channel.id in games:
        del games[ctx.channel.id]
        await ctx.send(f"{TICK} Đã hủy ván đấu!")

@bot.event
async def on_message(message):
    if message.author.bot: return
    await bot.process_commands(message)
    if message.channel.id not in games or message.content.startswith("?"): return
    
    game = games[message.channel.id]
    user_input = norm(message.content)
    
    if game["mode"] == "vi":
        words = user_input.split()
        prev_last = game["last_word"].split()[-1]
        
        if len(words) != 2 or words[0] != prev_last or user_input in game["used_words"] or not is_valid_vietnamese_word(user_input):
            await message.add_reaction(CROSS)
            return
            
        game["used_words"].add(user_input)
        game["last_word"] = user_input
        await message.add_reaction(TICK)
        
        # Cộng điểm
        data = get_user_data(message.author.id)
        data["xp"] += 25
        if data["xp"] >= data["level"] * 300:
            data["xp"] -= data["level"] * 300
            data["level"] += 1
            await message.channel.send(f"🎉 Ê {message.author.mention}, m vừa lên Level {data['level']}! Dùng `?rank` xem thẻ!")

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
