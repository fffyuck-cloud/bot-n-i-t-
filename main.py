import os
import re
import ssl
import urllib.request
import discord
from discord.ext import commands
from pyvi import ViTokenizer
from keep_alive import keep_alive

dictionary_vi = set()
dictionary_en = set()

# 1. Tải từ điển Tiếng Việt (40.000+ từ)
try:
    url_vi = "https://raw.githubusercontent.com/duythinht/vietnamese-dictionary/master/words.txt"
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url_vi, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
        content = response.read().decode('utf-8')
        dictionary_vi = set(line.strip().lower() for line in content.splitlines() if line.strip())
    print(f"Đã nạp {len(dictionary_vi)} từ tiếng Việt!")
except Exception as e:
    print(f"Lỗi tải từ điển tiếng Việt: {e}")

# 2. Tải từ điển Tiếng Anh chuẩn (370.000+ từ)
try:
    url_en = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url_en, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
        content = response.read().decode('utf-8')
        dictionary_en = set(line.strip().lower() for line in content.splitlines() if line.strip())
    print(f"Đã nạp {len(dictionary_en)} từ tiếng Anh!")
except Exception as e:
    print(f"Lỗi tải từ điển tiếng Anh: {e}")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)
games = {}

def is_valid_vietnamese_syllable(word):
    word = word.lower().strip()
    if re.search(r'(.)\1{2,}', word) or re.search(r'[sfrxzjwkbdghqvl]$', word):
        return False
    vn_pattern = r'^[a-àáảãạăằắẳẵặâầấẩẫậbcdđeèéẻẽẹêềếểễệghiìíỉĩịklmnoòóỏõọôồốổỗộơờớởỡợpqrstuùúủũụưừứửữựvxyỳýỷỹỵ]+$'
    return bool(re.match(vn_pattern, word))

def is_valid_vietnamese_word(text):
    text_clean = text.lower().strip()
    if text_clean in dictionary_vi or "_" in ViTokenizer.tokenize(text_clean):
        return True
    words = text_clean.split()
    if len(words) == 2:
        return is_valid_vietnamese_syllable(words[0]) and is_valid_vietnamese_syllable(words[1])
    return False

@bot.event
async def on_ready():
    print(f"{bot.user} online rồi các con")

# Lệnh bắt đầu nối từ TIẾNG VIỆT
@bot.command(name="noitu")
async def start_game_vi(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("⚠️ Kênh này đang có trận diễn ra rồi!")
        return

    games[channel_id] = {
        "mode": "vi",
        "last_word": None,
        "count": 0,
        "used_words": set(),
        "last_player": None
    }
    await ctx.send(
        "🎮 **Bắt đầu Nối Từ Tiếng Việt!**\n"
        "• Thay phiên nhau nối cụm 2 từ có nghĩa.\n"
        "• Gõ `?huynoitu` để hủy."
    )

# Lệnh bắt đầu nối từ TIẾNG ANH
@bot.command(name="noituen")
async def start_game_en(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("⚠️ Kênh này đang có trận diễn ra rồi!")
        return

    games[channel_id] = {
        "mode": "en",
        "last_word": None,
        "count": 0,
        "used_words": set(),
        "last_player": None
    }
    await ctx.send(
        "🔤 **Nối từ tiếng anh béo béo béo đã bắt đầu!!**\n"
        "• Nối chữ cái cuối của từ trước nghen mấy con (Ví dụ: appl**e** -> **e**lephan**t**).\n"
        "• Chỉ dùng từ tiếng anh hợp lệ, k được thì tại m ngu.\n"
        "• Gõ `?huynoitu` để hủy."
    )

@bot.command(name="huynoitu")
async def stop_game(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        total_count = games[channel_id]["count"]
        del games[channel_id]
        await ctx.send(f"🛑 **Đã hủy con mẹ nó trận!** Tổng số từ nối thành công: **{total_count}**")
    else:
        await ctx.send("❌ Kênh này hiện đéo có trận nào đâu mấy thằng óc!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    channel_id = message.channel.id
    if channel_id not in games or message.content.startswith("?"):
        return

    text = message.content.strip().lower()
    game = games[channel_id]

    # --- XỬ LÝ NỐI TỪ TIẾNG ANH ---
    if game["mode"] == "en":
        words = text.split()
        if len(words) != 1:  # Tiếng Anh chỉ chấp nhận 1 từ đơn
            return

        if game["last_player"] == message.author.id:
            await message.reply("Đợi ng khác nối đi , k đợi thì cúc!", delete_after=3)
            return

        if text not in dictionary_en:
            await message.reply("Từ này không có trong từ điển tiếng anh đâu . bố lạy con", delete_after=3)
            return

        if text in game["used_words"]:
            await message.reply("Từ này đã dùng rồi hihi!", delete_after=3)
            return

        if game["last_word"] is not None:
            last_char = game["last_word"][-1]
            if text[0] != last_char:
                await message.reply(f"Từ phải bắt đầu bằng chữ **{last_char.upper()}**!", delete_after=3)
                return

        # Hợp lệ
        game["used_words"].add(text)
        game["last_word"] = text
        game["count"] += 1
        game["last_player"] = message.author.id

        await message.add_reaction("✅")
        await message.reply(
            f"🎯 **#{game['count']}** | Bắt đầu bằng chữ: **{text[-1].upper()}**",
            mention_author=False,
            delete_after=5
        )
        return

    # --- XỬ LÝ NỐI TỪ TIẾNG VIỆT ---
    if game["mode"] == "vi":
        words = text.split()
        if len(words) != 2:
            return

        if game["last_player"] == message.author.id:
            await message.reply("Đợi người khác nối đi!", delete_after=3)
            return

        if not is_valid_vietnamese_word(text):
            await message.reply("Từ này đéo có trong từ điển tiếng Việt!", delete_after=3)
            return

        if text in game["used_words"]:
            return

        if game["last_word"] is not None:
            if words[0] != game["last_word"].split()[-1]:
                return

        game["used_words"].add(text)
        game["last_word"] = text
        game["count"] += 1
        game["last_player"] = message.author.id

        await message.add_reaction("✅")
        await message.reply(
            f"🎯 **#{game['count']}** | Nối từ chữ: **{words[-1]}**",
            mention_author=False,
            delete_after=5
        )

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
