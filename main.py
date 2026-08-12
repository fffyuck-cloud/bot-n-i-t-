import os
import re
import ssl
import urllib.request
import random
import discord
from datetime import date
from discord.ext import commands
from pyvi import ViTokenizer
from keep_alive import keep_alive

dictionary_vi = set()
dictionary_en = set()

# Tải từ điển tiếng Việt
urls_vi = [
    "https://raw.githubusercontent.com/vietnamese-wordlist/vietnamese-wordlist/master/words.txt",
    "https://raw.githubusercontent.com/Khang-NT/vietnamese-dictionary/master/words.txt",
    "https://raw.githubusercontent.com/hoangviet/vietnamese-wordlist/master/words.txt"
]

for url_vi in urls_vi:
    try:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url_vi, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
            for line in content.splitlines():
                word = line.strip().lower()
                if word:
                    dictionary_vi.add(word)
        if len(dictionary_vi) > 0:
            print(f"Đã nạp thành công {len(dictionary_vi)} từ tiếng Việt!")
            break
    except Exception as e:
        print(f"Lỗi tải link TV ({url_vi}): {e}")

# Tải từ điển tiếng Anh
try:
    url_en = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url_en, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
        content = response.read().decode('utf-8', errors='ignore')
        dictionary_en = set(line.strip().lower() for line in content.splitlines() if line.strip())
    print(f"Đã nạp thành công {len(dictionary_en)} từ tiếng Anh!")
except Exception as e:
    print(f"Lỗi tải từ điển TA: {e}")

# Đọc thêm file words.txt cá nhân
try:
    with open("words.txt", "r", encoding="utf-8", errors="ignore") as f:
        dictionary_vi.update(set(line.strip().lower() for line in f if line.strip()))
except FileNotFoundError:
    pass

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)
games = {}

user_hints = {}        
user_daily_claimed = {} 

async def safe_delete(message, delay=0):
    try:
        await message.delete(delay=delay)
    except Exception:
        pass

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

def check_has_next_vi(last_syllable, used_words):
    prefix = last_syllable.lower().strip() + " "
    for w in dictionary_vi:
        if w.startswith(prefix) and w not in used_words:
            return True
    # Mẹo dự phòng kiểm tra từ ghép âm đơn hợp lệ
    return True

@bot.event
async def on_ready():
    print(f"{bot.user} bố online rồi các con")

@bot.command(name="help")
async def custom_help(ctx):
    embed = discord.Embed(
        title="🎮 LỆNH VÀ LUẬT CHƠI NỐI TỪ",
        description="Chào mừng bạn đến với Bot Nối Từ béo béo béo!",
        color=discord.Color.green()
    )
    embed.add_field(name="`?noitu`", value="Bắt đầu ván Nối Từ Tiếng Việt (2 từ)", inline=False)
    embed.add_field(name="`?noituen`", value="Bắt đầu ván Nối Từ Tiếng Anh (1 từ)", inline=False)
    embed.add_field(name="`?daily`", value="Điểm danh nhận 3 lượt gợi ý mỗi ngày", inline=False)
    embed.add_field(name="`?hint`", value="Tốn 1 lượt gợi ý để xem từ có thể nối", inline=False)
    embed.add_field(name="`?top`", value="Xem Bảng Xếp Hạng người nối nhiều từ nhất ván hiện tại", inline=False)
    embed.add_field(name="`?huynoitu`", value="Hủy ván game đang chơi", inline=False)
    embed.set_footer(text="Luật: Thay phiên nhau nối, không được tự nối 2 lần liên tiếp!")
    await ctx.send(embed=embed)

@bot.command(name="daily")
async def claim_daily(ctx):
    user_id = ctx.author.id
    today_str = str(date.today())

    if user_daily_claimed.get(user_id) == today_str:
        await ctx.send("⚠️ Hôm nay bạn đã điểm danh rồi, quay lại vào ngày mai nhé!")
        return

    user_hints[user_id] = 3
    user_daily_claimed[user_id] = today_str
    await ctx.send(f"🎁 **{ctx.author.display_name}** đã điểm danh thành công và nhận **3 lượt gợi ý** cho ngày hôm nay!")

@bot.command(name="noitu")
async def start_game_vi(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("⚠️ Kênh này đang có trận diễn ra rồi, phiền bố m mute!")
        return

    games[channel_id] = {
        "mode": "vi",
        "last_word": None,
        "count": 0,
        "used_words": set(),
        "last_player": None,
        "scores": {}
    }
    await ctx.send(
        "🎮 **Đã bắt trò chơi nối từ béo béo béo! (Tiếng Việt)**\n"
        "• Đéo được nối 2 lần liên tiếp, thay phiên nhau mà nối.\n"
        "• Đúng chính xác 2 từ có nghĩa tiếng Việt.\n"
        "• Gõ `?daily` điểm danh | `?hint` gợi ý | `?top` BXH | `?huynoitu` end."
    )

@bot.command(name="noituen")
async def start_game_en(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("⚠️ Kênh này đang có trận diễn ra rồi, phiền bố m mute!")
        return

    games[channel_id] = {
        "mode": "en",
        "last_word": None,
        "count": 0,
        "used_words": set(),
        "last_player": None,
        "scores": {}
    }
    await ctx.send(
        "🔤 **Nối từ tiếng anh béo béo đã xuất hiện!!!!**\n"
        "• Mỗi thằng chỉ được nối đúng 1 từ, thay phiên nhau mà nói.\n"
        "• Gõ `?daily` điểm danh | `?hint` gợi ý | `?top` BXH | `?huynoitu` end."
    )

@bot.command(name="hint")
async def get_hint(ctx):
    channel_id = ctx.channel.id
    user_id = ctx.author.id

    if channel_id not in games:
        await ctx.send("<:Screenshot20260812173722:1537047895310602300> Đã có game đ đâu mà gợi ý hả thằng nqu!")
        return

    hints_left = user_hints.get(user_id, 0)
    if hints_left <= 0:
        await ctx.send("<:Screenshot20260812173722:1537047895310602300> Mệt mày quá! Bạn đã hết lượt gợi ý hôm nay rồi. Gõ `?daily` để nhận (nếu chưa điểm danh) hoặc đợi ngày mai!")
        return

    game = games[channel_id]
    
    if game["last_word"] is None:
        await ctx.send("💡 Lượt đầu tiên đánh đại đi còn xin gợi ý!")
        return

    if game["mode"] == "en":
        last_char = game["last_word"][-1]
        valid_words = [w for w in dictionary_en if w.startswith(last_char) and w not in game["used_words"]]
        if valid_words:
            user_hints[user_id] -= 1
            suggested = random.choice(valid_words)
            await ctx.send(f"💡 **Gợi ý Tiếng Anh:** Từ bắt đầu bằng **'{last_char.upper()}'** có thể dùng: **{suggested}**\n*(Bạn còn {user_hints[user_id]}/3 lượt gợi ý)*")
        else:
            await ctx.send("💡 Hết từ nối rồi, chịu thua đi!")

    elif game["mode"] == "vi":
        prev_last = game["last_word"].split()[-1]
        prefix = prev_last + " "
        valid_words = [w for w in dictionary_vi if w.startswith(prefix) and w not in game["used_words"]]
        if valid_words:
            user_hints[user_id] -= 1
            suggested = random.choice(valid_words)
            await ctx.send(f"💡 **Gợi ý Tiếng Việt:** Từ bắt đầu bằng **'{prev_last}'** có thể dùng: **{suggested}**\n*(Bạn còn {user_hints[user_id]}/3 lượt gợi ý)*")
        else:
            await ctx.send(f"💡 Cố tìm từ bắt đầu bằng **'{prev_last}'** nhé!")

@bot.command(name="top")
async def show_top(ctx):
    channel_id = ctx.channel.id
    if channel_id not in games:
        await ctx.send("<:Screenshot20260812173722:1537047895310602300> Có trận đ đâu mà xem điểm!")
        return

    scores = games[channel_id]["scores"]
    if not scores:
        await ctx.send("📊 Chưa có ai ghi điểm trong ván này cả!")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    msg = "🏆 **BẢNG XẾP HẠNG VÁN HIỆN TẠI** 🏆\n"
    for idx, (user_id, count) in enumerate(sorted_scores, 1):
        user = await bot.fetch_user(user_id)
        msg += f"**#{idx}** {user.display_name}: **{count}** từ\n"

    await ctx.send(msg)

@bot.command(name="huynoitu")
async def stop_game(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        total_count = games[channel_id]["count"]
        del games[channel_id]
        await ctx.send(f"🛑 **Thua rồi mấy thằng nhóc con, trình độ m chắc chắc còn non: **{total_count}**")
    else:
        await ctx.send("<:Screenshot20260812173722:1537047895310602300> Có trận đ đâu mà huỷ v thằng nqu")

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

    # --- NỐI TỪ TIẾNG ANH ---
    if game["mode"] == "en":
        words = text.split()
        if len(words) != 1:
            return

        if game["last_player"] == message.author.id:
            await message.add_reaction("Screenshot20260812173722:1537047895310602300")
            await message.reply("Óc c mù, bố kêu thay phiên mà nói", delete_after=3)
            await safe_delete(message, delay=3)
            return

        if text not in dictionary_en:
            await message.add_reaction("Screenshot20260812173722:1537047895310602300")
            await message.reply("Từ này là tiếng anh à thằng óc?", delete_after=3)
            await safe_delete(message, delay=3)
            return

        if text in game["used_words"]:
            await message.add_reaction("Screenshot20260812173722:1537047895310602300")
            await message.reply("Từ này sử dụng rồi m êiii", delete_after=3)
            await safe_delete(message, delay=3)
            return

        if game["last_word"] is not None:
            last_char = game["last_word"][-1]
            if text[0] != last_char:
                await message.add_reaction("Screenshot20260812173722:1537047895310602300")
                await message.reply(f"Mắt mù à, từ phải bắt đầu bằng chữ **{last_char.upper()}**!", delete_after=3)
                await safe_delete(message, delay=3)
                return

        game["used_words"].add(text)
        game["last_word"] = text
        game["count"] += 1
        game["last_player"] = message.author.id
        game["scores"][message.author.id] = game["scores"].get(message.author.id, 0) + 1

        await message.add_reaction("Screenshot20260812172055:1537043520790073424")

        next_char = text[-1]
        has_next_word = any(w.startswith(next_char) and w not in game["used_words"] for w in dictionary_en)
        if not has_next_word:
            await message.reply(f"🏆 Hết từ nối chữ '{next_char.upper()}'. Tổng: **{game['count']}**. Reset game!", mention_author=False)
            game.update({"last_word": None, "count": 0, "used_words": set(), "last_player": None, "scores": {}})
            return

        await message.reply(
            f"<:Screenshot20260812172055:1537043520790073424> 🎯 **Word #{game['count']}** | Next: **{text[-1].upper()}**", 
            mention_author=False, delete_after=5
        )
        return

    # --- NỐI TỪ TIẾNG VIỆT ---
    if game["mode"] == "vi":
        words = text.split()
        if len(words) != 2:
            return

        if game["last_player"] == message.author.id:
            await message.add_reaction("Screenshot20260812173722:1537047895310602300")
            await message.reply("Đợi đứa khác nối đi thằng l..., đừng tự sướng!", delete_after=3)
            await safe_delete(message, delay=3)
            return

        if not is_valid_vietnamese_word(text):
            await message.add_reaction("Screenshot20260812173722:1537047895310602300")
            await message.reply("Từ này đéo có trong từ điển tiếng Việt!", delete_after=3)
            await safe_delete(message, delay=3)
            return

        if text in game["used_words"]:
            await message.add_reaction("Screenshot20260812173722:1537047895310602300")
            await message.reply("Từ này nối rồi con gà!", delete_after=3)
            await safe_delete(message, delay=3)
            return

        if game["last_word"] is not None:
            prev_last = game["last_word"].split()[-1]
            if words[0] != prev_last:
                await message.add_reaction("Screenshot20260812173722:1537047895310602300")
                await message.reply(f"Từ phải bắt đầu bằng **{prev_last}**!", delete_after=3)
                await safe_delete(message, delay=3)
                return

        game["used_words"].add(text)
        game["last_word"] = text
        game["count"] += 1
        game["last_player"] = message.author.id
        game["scores"][message.author.id] = game["scores"].get(message.author.id, 0) + 1

        await message.add_reaction("Screenshot20260812172055:1537043520790073424")

        if not check_has_next_vi(words[-1], game["used_words"]):
            await message.reply(f"🏆 Hết từ nối chữ '{words[-1].upper()}'. Tổng: **{game['count']}**. Reset game!", mention_author=False)
            game.update({"last_word": None, "count": 0, "used_words": set(), "last_player": None, "scores": {}})
            return

        await message.reply(
            f"<:Screenshot20260812172055:1537043520790073424> 🎯 **#{game['count']}** | Nối: **{words[-1]}**", 
            mention_author=False, delete_after=5
        )

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
