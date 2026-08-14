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

try:
    from keep_alive import keep_alive
except ImportError:
    def keep_alive(): pass

# Đã sửa lại vị trí TICK và CROSS cho chuẩn xác
TICK = "<:Screenshot20260812173722:1537047895310602300>"
CROSS = "<:Screenshot20260812172055:1537043520790073424>"

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

def prepare_dictionaries():
    ctx = ssl._create_unverified_context()
    words_vi = {"đá bóng", "bóng đá", "học sinh", "sinh viên", "thể thao"}
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

user_profiles = {}
def get_user_data(user_id):
    if user_id not in user_profiles:
        user_profiles[user_id] = {"xp": 100, "level": 1, "rank": 1, "streak": 0, "last_daily": None}
    return user_profiles[user_id]

def get_background():
    try:
        bg = Image.open("d89db057-b415-48f7-8603-47052617b39e.png").convert("RGBA")
        return ImageOps.fit(bg, (600, 200), Image.Resampling.LANCZOS)
    except:
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
        draw.text((170, 100), "Mai quay lại nhận nhé", fill="#ffffff", font=font_medium)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return discord.File(buffer, filename="daily.png")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)
games = {}

@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} online")

@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(title="✦ HỆ THỐNG TRỢ GIÚP NỐI TỪ ULTIMATE ✦", color=0xFF007F)
    embed.description = (
        "💬 **Word Chain Ultimate Bot Core**\n"
        "Hệ thống trò chơi nối từ tích hợp bộ đếm số lượng từ và kiểm tra từ điển chuẩn xác."
    )
    embed.add_field(
        name="🎮 CÁC LỆNH TRÒ CHƠI",
        value=(
            "• `?noitu [vi/en]` → Khởi động bàn đấu chung.\n"
            "• `?noitueng` → Khởi động bàn đấu tiếng Anh nhanh.\n"
            "• `?noituubot` → Solo 1v1 với AI tiếng Việt.\n"
            "• `?noituuboteng` → Solo 1v1 với AI tiếng Anh.\n"
            "• `?huynoitu` → Hủy bỏ ván đấu hiện tại."
        ),
        inline=False
    )
    embed.add_field(
        name="📊 TIỆN ÍCH & TRA CỨU",
        value=(
            "• `?nghia [từ]` → Tra cứu từ điển Anh.\n"
            "• `?rank` → Xem thẻ cấp độ và thứ hạng.\n"
            "• `?daily` → Điểm danh nhận thưởng hằng ngày."
        ),
        inline=False
    )
    embed.set_footer(text="Hệ thống đã cập nhật sửa lỗi icon và bộ đếm số từ thành công!")
    await ctx.send(embed=embed)

@bot.command(name="rank")
async def rank_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = get_user_data(member.id)
    file = await create_rank_card(member, data)
    
    embed = discord.Embed(title=f"📊 HỒ SƠ XẾP HẠNG: {member.display_name.upper()}", color=0xFF007F)
    embed.add_field(name="⭐ Cấp Độ", value=f"Level **{data['level']}**", inline=True)
    embed.add_field(name="🏆 Vị Thế", value=f"Rank **#{data['rank']}**", inline=True)
    embed.add_field(name="⚡ Kinh Nghiệm", value=f"**{data['xp']}** / {data['level'] * 300} XP", inline=True)
    embed.add_field(name="🔥 Streak", value=f"**{data['streak']}** ngày", inline=True)
    await ctx.send(embed=embed, file=file)

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
        
    file = await create_daily_card(ctx.author, reward, claimed)
    embed = discord.Embed(title="🎁 ĐIỂM DANH HẰNG NGÀY", color=0x57F287 if claimed else 0xED4245)
    if claimed:
        embed.description = f"🎉 Chúc mừng {ctx.author.mention} điểm danh thành công!"
        embed.add_field(name="💰 Phần Thưởng", value=f"+**{reward}** XP", inline=True)
        embed.add_field(name="📈 Streak", value=f"**{data['streak']}** ngày", inline=True)
    else:
        embed.description = f"⚠️ {ctx.author.mention} đã điểm danh trong vòng 24 giờ qua rồi."
    icon = TICK if claimed else CROSS
    await ctx.send(f"{icon} Yêu cầu từ {ctx.author.mention}", embed=embed, file=file)

@bot.command(name="noitu")
async def start_noitu(ctx, mode: str = "vi"):
    if ctx.channel.id in games: 
        return await ctx.send("Kênh đang có ván chơi rồi!")
    mode = mode.lower()
    
    if mode in ["en", "english", "eng", "noitueng"]:
        word = "apple"
        games[ctx.channel.id] = {"mode": "en_multi", "last_word": word, "used_words": {word}}
        embed = discord.Embed(title="🇬🇧 TRẬN ĐẤU NỐI TỪ TIẾNG ANH", color=0xFF007F)
        embed.description = (
            "🔥 **SÀN ĐẤU QUỐC TẾ KHAI MẠC** 🔥\n\n"
            f"🎯 **TỪ KHÓA KHỞI ĐẦU:** 👉 **`{word.upper()}`**\n"
            f"📊 **Tổng số từ hiện tại:** `1` từ\n\n"
            f"⚡ Bắt đầu bằng ký tự: **{word[-1].upper()}**"
        )
        await ctx.send(embed=embed)
    else:
        word = "đá bóng"
        games[ctx.channel.id] = {"mode": "vi_multi", "last_word": word, "used_words": {word}}
        embed = discord.Embed(title="🇻🇳 TRẬN ĐẤU NỐI TỪ TIẾNG VIỆT", color=0xFF007F)
        embed.description = (
            "🔥 **SÀN ĐẤU TIẾNG VIỆT KHAI MẠC** 🔥\n\n"
            f"🎯 **TỪ KHÓA KHỞI ĐẦU:** 👉 **`{word.upper()}`**\n"
            f"📊 **Tổng số từ hiện tại:** `1` từ\n\n"
            f"⚡ Bắt đầu bằng âm tiết: **{word.split()[-1].upper()}**"
        )
        await ctx.send(embed=embed)

@bot.command(name="noituubot")
async def start_game_vi_bot(ctx):
    if ctx.channel.id in games: return await ctx.send("Kênh đang có ván chơi rồi!")
    word = "đá bóng"
    games[ctx.channel.id] = {"mode": "vi_bot", "last_word": word, "used_words": {word}}
    embed = discord.Embed(title="🤖 THÁCH ĐẤU AI: SOLO TIẾNG VIỆT", color=0xFF007F)
    embed.description = (
        "⚔️ **1V1 VỚI HỆ THỐNG AI** ⚔️\n\n"
        f"🎯 **TỪ KHÓA MỞ MÀN:** 👉 **`{word.upper()}`**\n"
        f"📊 **Tổng số từ hiện tại:** `1` từ\n\n"
        f"⚡ Âm tiết tiếp theo: **{word.split()[-1].upper()}**"
    )
    await ctx.send(embed=embed)

@bot.command(name="noitueng")
async def start_game_en(ctx):
    if ctx.channel.id in games: return await ctx.send("Kênh đang có ván chơi rồi!")
    word = "apple"
    games[ctx.channel.id] = {"mode": "en_multi", "last_word": word, "used_words": {word}}
    embed = discord.Embed(title="🇬🇧 TRẬN ĐẤU NỐI TỪ TIẾNG ANH", color=0xFF007F)
    embed.description = (
        "🔥 **SÀN ĐẤU QUỐC TẾ KHAI MẠC** 🔥\n\n"
        f"🎯 **TỪ KHÓA KHỞI ĐẦU:** 👉 **`{word.upper()}`**\n"
        f"📊 **Tổng số từ hiện tại:** `1` từ\n\n"
        f"⚡ Bắt đầu bằng ký tự: **{word[-1].upper()}**"
    )
    await ctx.send(embed=embed)

@bot.command(name="noituuboteng")
async def start_game_en_bot(ctx):
    if ctx.channel.id in games: return await ctx.send("Kênh đang có ván chơi rồi!")
    word = "apple"
    games[ctx.channel.id] = {"mode": "en_bot", "last_word": word, "used_words": {word}}
    embed = discord.Embed(title="🤖 THÁCH ĐẤU AI: SOLO TIẾNG ANH", color=0xFF007F)
    embed.description = (
        "⚔️ **1V1 VỚI HỆ THỐNG AI QUỐC TẾ** ⚔️\n\n"
        f"🎯 **TỪ KHÓA MỞ MÀN:** 👉 **`{word.upper()}`**\n"
        f"📊 **Tổng số từ hiện tại:** `1` từ\n\n"
        f"⚡ Ký tự tiếp theo: **{word[-1].upper()}**"
    )
    await ctx.send(embed=embed)

@bot.command(name="huynoitu")
async def stop_game(ctx):
    if ctx.channel.id in games:
        del games[ctx.channel.id]
        embed = discord.Embed(title="⚙️ HỦY BỎ TRẬN ĐẤU", color=0xED4245)
        embed.description = "🛑 Ván đấu nối từ trong kênh này đã được hủy bỏ thành công."
        await ctx.send(embed=embed)
    else:
        await ctx.send("Kênh này hiện không có ván đấu nào đang chạy!")

@bot.command(name="nghia")
async def nghia_cmd(ctx, word: str = None):
    if not word: return await ctx.send("Vui lòng nhập từ cần tra cứu! Ví dụ: `?nghia apple`")
    w = word.strip().lower()
    if w in dictionary_en:
        await ctx.send(f"{TICK} Từ **`{w}`** có nghĩa và hợp lệ trong từ điển tiếng Anh!")
    else:
        await ctx.send(f"{CROSS} Từ **`{w}`** không tìm thấy trong từ điển tiếng Anh!")

@bot.event
async def on_message(message):
    if message.author.bot: return
    await bot.process_commands(message)
    if message.channel.id not in games or message.content.startswith("?"): return
    
    game = games[message.channel.id]
    user_input = norm(message.content)
    mode = game["mode"]
    
    if mode in ["vi_multi", "vi_bot"]:
        words = user_input.split()
        prev_last = game["last_word"].split()[-1]
        if len(words) != 2 or words[0] != prev_last or user_input in game["used_words"] or user_input not in dictionary_vi:
            await message.add_reaction(CROSS)
            return
        game["used_words"].add(user_input)
        game["last_word"] = user_input
        current_count = len(game["used_words"])
        await message.add_reaction(TICK)
        
        data = get_user_data(message.author.id)
        data["xp"] += 25
        if data["xp"] >= data["level"] * 300:
            data["xp"] -= data["level"] * 300
            data["level"] += 1
            await message.channel.send(f"🎉 {message.author.mention} vừa lên level {data['level']}")

        if mode == "vi_bot":
            last_syllable = user_input.split()[-1]
            possible_words = [w for w in dictionary_vi if w.startswith(last_syllable + " ") and w not in game["used_words"]]
            if possible_words:
                bot_word = random.choice(possible_words)
                game["used_words"].add(bot_word)
                game["last_word"] = bot_word
                current_count = len(game["used_words"])
                await message.channel.send(f"🤖 Bot nối tiếp: **`{bot_word.upper()}`** (Tổng số từ: `{current_count}`) {TICK}")
            else:
                await message.channel.send(f"🏆 {message.author.mention} đã chiến thắng bot vì bot đã cạn kiệt từ vựng!")
                del games[message.channel.id]
        else:
            await message.channel.send(f"📊 Tổng số từ đã nối: **`{current_count}`** từ")

    elif mode in ["en_multi", "en_bot"]:
        w = user_input
        prev_char = game["last_word"][-1]
        if len(w.split()) != 1 or w[0] != prev_char or w in game["used_words"] or w not in dictionary_en:
            await message.add_reaction(CROSS)
            return
        game["used_words"].add(w)
        game["last_word"] = w
        current_count = len(game["used_words"])
        await message.add_reaction(TICK)
        
        data = get_user_data(message.author.id)
        data["xp"] += 25
        if data["xp"] >= data["level"] * 300:
            data["xp"] -= data["level"] * 300
            data["level"] += 1
            await message.channel.send(f"🎉 {message.author.mention} vừa lên level {data['level']}")

        if mode == "en_bot":
            last_char = w[-1]
            possible_words = [word for word in dictionary_en if word.startswith(last_char) and word not in game["used_words"]]
            if possible_words:
                bot_word = random.choice(possible_words)
                game["used_words"].add(bot_word)
                game["last_word"] = bot_word
                current_count = len(game["used_words"])
                await message.channel.send(f"🤖 Bot nối tiếp: **`{bot_word.upper()}`** (Tổng số từ: `{current_count}`) {TICK}")
            else:
                await message.channel.send(f"🏆 {message.author.mention} đã chiến thắng bot vì bot đã cạn kiệt từ vựng!")
                del games[message.channel.id]
        else:
            await message.channel.send(f"📊 Tổng số từ đã nối: **`{current_count}`** từ")

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
