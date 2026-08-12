import os
import ssl
import json
import urllib.request
import random
import discord
from datetime import date
from discord.ext import commands
from keep_alive import keep_alive

# Cấu hình Emoji Custom của bạn
CUSTOM_EMOJI = "Screenshot20260812173722:1537047895310602300"

dictionary_vi = set()
dictionary_en = set()

# Tải từ điển tiếng Việt chuẩn
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

# Đọc thêm file words.txt cá nhân nếu có
try:
    with open("words.txt", "r", encoding="utf-8", errors="ignore") as f:
        dictionary_vi.update(set(line.strip().lower() for line in f if line.strip()))
except FileNotFoundError:
    pass

# Xử lý Lưu / Đọc Kỷ Lục Highscore
HIGHSCORE_FILE = "highscore.json"

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"vi": {"count": 0}, "en": {"count": 0}}
    return {"vi": {"count": 0}, "en": {"count": 0}}

def save_highscore(data):
    try:
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Lỗi lưu highscore: {e}")

highscores = load_highscore()

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

def is_valid_vietnamese_word(text):
    text_clean = text.lower().strip()
    words = text_clean.split()
    if len(words) != 2:
        return False
    
    if text_clean in dictionary_vi:
        return True

    w1, w2 = words[0], words[1]
    is_w1_valid = any(w == w1 or w.startswith(w1 + " ") or w.endswith(" " + w1) for w in dictionary_vi)
    is_w2_valid = any(w == w2 or w.startswith(w2 + " ") or w.endswith(" " + w2) for w in dictionary_vi)
    
    return is_w1_valid and is_w2_valid

def check_has_next_vi(last_syllable, used_words):
    prefix = last_syllable.lower().strip() + " "
    for w in dictionary_vi:
        if w.startswith(prefix) and w not in used_words:
            return True
    return True

def update_highscore_if_needed(mode, count):
    mode_key = "vi" if mode == "vi" else "en"
    current_hs = highscores.get(mode_key, {}).get("count", 0)
    if count > current_hs:
        highscores[mode_key] = {"count": count}
        save_highscore(highscores)
        return True
    return False

@bot.event
async def on_ready():
    print(f"{bot.user} bố online rồi các con")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⚠️ Bạn phải là **Administrator** mới có quyền bắt đầu hoặc kết thúc trò chơi!")
    else:
        raise error

@bot.command(name="help")
async def custom_help(ctx):
    embed = discord.Embed(
        title="🎮 LỆNH VÀ LUẬT CHƠI NỐI TỪ",
        description="Chào mừng bạn đến với Bot Nối Từ béo béo béo!",
        color=discord.Color.from_rgb(255, 20, 147)
    )
    embed.add_field(name="`?noitu` (Admin)", value="Bắt đầu ván Nối Từ Tiếng Việt (2 từ)", inline=False)
    embed.add_field(name="`?noituen` (Admin)", value="Bắt đầu ván Nối Từ Tiếng Anh (1 từ)", inline=False)
    embed.add_field(name="`?huynoitu` (Admin)", value="Hủy ván game đang chơi", inline=False)
    embed.add_field(name="`?daily`", value="Điểm danh nhận 3 lượt gợi ý mỗi ngày", inline=False)
    embed.add_field(name="`?hint`", value="Tốn 1 lượt gợi ý để xem từ có thể nối", inline=False)
    embed.add_field(name="`?top`", value="Xem Bảng Xếp Hạng người nối nhiều từ nhất ván hiện tại", inline=False)
    embed.add_field(name="`?highscore`", value="Xem kỷ lục chuỗi nối dài nhất của Server", inline=False)
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

@bot.command(name="highscore")
async def show_highscore(ctx):
    embed = discord.Embed(
        title="🏆 KỶ LỤC CAO NHẤT SERVER",
        color=discord.Color.gold()
    )
    embed.add_field(name="🇻🇳 Tiếng Việt", value=f"**{highscores.get('vi', {}).get('count', 0)}** từ", inline=False)
    embed.add_field(name="🇬🇧 Tiếng Anh", value=f"**{highscores.get('en', {}).get('count', 0)}** từ", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="noitu")
@commands.has_permissions(administrator=True)
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
        "• Gõ `?daily` | `?hint` | `?top` | `?highscore` | `?huynoitu`."
    )

@bot.command(name="noituen")
@commands.has_permissions(administrator=True)
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
        "• Gõ `?daily` | `?hint` | `?top` | `?highscore` | `?huynoitu`."
    )

@bot.command(name="hint")
async def get_hint(ctx):
    channel_id = ctx.channel.id
    user_id = ctx.author.id

    if channel_id not in games:
        await ctx.send("⚠️ Đã có game đ đâu mà gợi ý hả thằng nqu!")
        return

    hints_left = user_hints.get(user_id, 0)
    if hints_left <= 0:
        await ctx.send("⚠️ Mệt mày quá! Bạn đã hết lượt gợi ý hôm nay rồi. Gõ `?daily` để nhận (nếu chưa điểm danh) hoặc đợi ngày mai!")
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
        await ctx.send("⚠️ Có trận đ đâu mà xem điểm!")
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
@commands.has_permissions(administrator=True)
async def stop_game(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        game = games[channel_id]
        total_count = game["count"]
        is_new_hs = update_highscore_if_needed(game["mode"], total_count)
        hs_msg = "\n🎉 **KỶ LỤC MỚI CỦA SERVER!**" if is_new_hs else ""
        del games[channel_id]
        await ctx.send(f"🛑 **Thua rồi mấy thằng nhóc con, trình độ m chắc chắc còn non: **{total_count}**{hs_msg}")
    else:
        await ctx.send("⚠️ Có trận đ đâu mà huỷ v thằng nqu")

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
            await message.reply("Óc c mù, bố kêu thay phiên mà nói", delete_after=3)
            await safe_delete(message, delay=3)
            return

        if text not in dictionary_en:
            await message.reply("Từ này là tiếng anh à thằng óc?", delete_after=3)
            await safe_delete(message, delay=3)
            return

        if text in game["used_words"]:
            await message.reply("Từ này sử dụng rồi m êiii", delete_after=3)
            await safe_delete(message, delay=3)
            return

        if game["last_word"] is not None:
            last_char = game["last_word"][-1]
            if text[0] != last_char:
                await message.reply(f"Mắt mù à, từ phải bắt đầu bằng chữ **{last_char.upper()}**!", delete_after=3)
                await safe_delete(message, delay=3)
                return

        # Thả custom emoji
        try:
            await message.add_reaction(CUSTOM_EMOJI)
        except Exception:
            pass

        game["used_words"].add(text)
        game["last_word"] = text
        game["count"] += 1
        game["last_player"] = message.author.id
        game["scores"][message.author.id] = game["scores"].get(message.author.id, 0) + 1

        next_char = text[-1]
        has_next_word = any(w.startswith(next_char) and w not in game["used_words"] for w in dictionary_en)
        if not has_next_word:
            is_new_hs = update_highscore_if_needed("en", game["count"])
            hs_msg = "\n🎉 **KỶ LỤC MỚI CỦA SERVER!**" if is_new_hs else ""
            await message.reply(f"🏆 Hết từ nối chữ '{next_char.upper()}'. Tổng: **{game['count']}**.{hs_msg}\nReset game!", mention_author=False)
            game.update({"last_word": None, "count": 0, "used_words": set(), "last_player": None, "scores": {}})
            return
        return

    # --- NỐI TỪ TIẾNG VIỆT ---
    if game["mode"] == "vi":
        words = text.split()
        if len(words) != 2:
            return

        if game["last_player"] == message.author.id:
            await message.reply("Đợi đứa khác nối đi thằng l..., đừng tự sướng!", delete_after=3)
            await safe_delete(message, delay=3)
            return

        if not is_valid_vietnamese_word(text):
            await message.reply("Từ này đéo có trong từ điển tiếng Việt!", delete_after=3)
            await safe_delete(message, delay=3)
            return

        if text in game["used_words"]:
            await message.reply("Từ này nối rồi con gà!", delete_after=3)
            await safe_delete(message, delay=3)
            return

        if game["last_word"] is not None:
            prev_last = game["last_word"].split()[-1]
            if words[0] != prev_last:
                await message.reply(f"Từ phải bắt đầu bằng **{prev_last}**!", delete_after=3)
                await safe_delete(message, delay=3)
                return

        # Thả custom emoji
        try:
            await message.add_reaction(CUSTOM_EMOJI)
        except Exception:
            pass

        game["used_words"].add(text)
        game["last_word"] = text
        game["count"] += 1
        game["last_player"] = message.author.id
        game["scores"][message.author.id] = game["scores"].get(message.author.id, 0) + 1

        if not check_has_next_vi(words[-1], game["used_words"]):
            is_new_hs = update_highscore_if_needed("vi", game["count"])
            hs_msg = "\n🎉 **KỶ LỤC MỚI CỦA SERVER!**" if is_new_hs else ""
            await message.reply(f"🏆 Hết từ nối chữ '{words[-1].upper()}'. Tổng: **{game['count']}**.{hs_msg}\nReset game!", mention_author=False)
            game.update({"last_word": None, "count": 0, "used_words": set(), "last_player": None, "scores": {}})
            return

try:
    keep_alive()
except Exception:
    pass

TOKEN = os.getenv("DISCORD_TOKEN", "DÁN_TOKEN_DISCORD_CỦA_BẠN_VÀO_ĐÂY")
bot.run(TOKEN)
