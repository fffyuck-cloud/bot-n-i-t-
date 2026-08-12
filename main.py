import os
import re
import ssl
import urllib.request
import discord
from discord.ext import commands
from pyvi import ViTokenizer
from keep_alive import keep_alive

dictionary = set()

# 1. Tải bộ từ điển online
try:
    url = "https://raw.githubusercontent.com/duythinht/vietnamese-dictionary/master/words.txt"
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
        content = response.read().decode('utf-8')
        dictionary = set(line.strip().lower() for line in content.splitlines() if line.strip())
    print(f"Đã nạp thành công {len(dictionary)} từ tiếng Việt!")
except Exception as e:
    print(f"Lỗi tải từ điển online: {e}")

# 2. Đọc thêm từ file words.txt cá nhân nếu có
try:
    with open("words.txt", "r", encoding="utf-8") as f:
        local_words = set(line.strip().lower() for line in f if line.strip())
        dictionary.update(local_words)
except FileNotFoundError:
    pass

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)
games = {}

def is_valid_vietnamese_syllable(word):
    """Kiểm tra 1 từ đơn có phải là âm tiết Tiếng Việt chuẩn không."""
    word = word.lower().strip()
    if re.search(r'(.)\1{2,}', word):
        return False
    if re.search(r'[sfrxzjwkbdghqvl]$', word):
        return False
    vn_pattern = r'^[a-àáảãạăằắẳẵặâầấẩẫậbcdđeèéẻẽẹêềếểễệghiìíỉĩịklmnoòóỏõọôồốổỗộơờớởỡợpqrstuùúủũụưừứửữựvxyỳýỷỹỵ]+$'
    return bool(re.match(vn_pattern, word))

def is_valid_vietnamese_word(text):
    """Kiểm tra cụm 2 từ tiếng Việt hợp lệ."""
    text_clean = text.lower().strip()
    if text_clean in dictionary:
        return True
    tokenized = ViTokenizer.tokenize(text_clean)
    if "_" in tokenized:
        return True
    words = text_clean.split()
    if len(words) == 2:
        return is_valid_vietnamese_syllable(words[0]) and is_valid_vietnamese_syllable(words[1])
    return False

@bot.event
async def on_ready():
    print(f"{bot.user} bố online rồi các con")

@bot.command(name="noitu")
async def start_game(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("⚠️ Kênh này đang có trận diễn ra rồi, phiền bố m mute!")
        return

    games[channel_id] = {
        "last_word": None,
        "count": 0,
        "used_words": set(),
        "last_player": None
    }
    
    await ctx.send(
        "🎮 **Đã bắt trò chơi nối từ béo béo béo!**\n"
        "• đéo được nối 2 lần liên tiếp , thay phiên nhau mà nối.\n"
        "• Đúng chính xác 2 từ có nghĩa tiếng Việt.\n"
        "• Gõ `?huynoitu` để end."
    )

@bot.command(name="huynoitu")
async def stop_game(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        total_count = games[channel_id]["count"]
        del games[channel_id]
        await ctx.send(f"🛑 **Đã hủy con mẹ nó trận!** Tổng số từ nối thành công: **{total_count}** từ.")
    else:
        await ctx.send("❌ Kênh này hiện đéo có trận để huỷ đâu!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    channel_id = message.channel.id
    if channel_id not in games:
        return

    if message.content.startswith("?"):
        return

    text = message.content.strip().lower()
    words = text.split()

    if len(words) != 2:
        return

    game = games[channel_id]

    # 1. Kiểm tra luân phiên người chơi (Tự xóa thông báo lỗi sau 3 giây)
    if game["last_player"] == message.author.id:
        await message.reply("Đợi đứa khác nối đi thằng l..., đừng tự sướng!", delete_after=3)
        return

    # 2. Kiểm tra từ hợp lệ (Tự xóa thông báo lỗi sau 3 giây)
    if not is_valid_vietnamese_word(text):
        await message.reply("Từ này đéo có trong từ điển tiếng Việt!", delete_after=3)
        return

    # 3. Kiểm tra trùng lặp
    if text in game["used_words"]:
        return

    # 4. Kiểm tra quy tắc nối từ
    if game["last_word"] is not None:
        prev_last_single_word = game["last_word"].split()[-1]
        first_single_word = words[0]
        
        if first_single_word != prev_last_single_word:
            return

    # --- HỢP LỆ ---
    game["used_words"].add(text)
    game["last_word"] = text
    game["count"] += 1
    game["last_player"] = message.author.id

    next_start_word = words[-1] # Từ cần nối tiếp theo

    await message.add_reaction("✅")
    
    # Tin nhắn báo lượt + nhắc từ nối.
    # delete_after=5 : Tự động xóa tin nhắn này sau 5 giây (nếu không muốn xóa thì bỏ delete_after=5 đi)
    await message.reply(
        f"🎯 **#{game['count']}** | Đến lượt đứa tiếp theo! Nối từ chữ: **{next_start_word}**", 
        mention_author=False,
        delete_after=5
    )

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
