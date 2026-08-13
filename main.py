import os
import ssl
import json
import urllib.request
import random
import re
import discord
from datetime import date
from discord.ext import commands
from keep_alive import keep_alive

# Custom Emoji của bạn
CUSTOM_TICK = "Screenshot20260812172055:1537043520790073424"
CUSTOM_CROSS = "Screenshot20260812173722:1537047895310602300"

NUMBER_EMOJIS = {
    1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
    6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
}

# 🚫 DANH SÁCH TỪ BẬY / THÔ TỤC (Tự động chặn)
BAD_WORDS = {
    "lồn", "cặc", "đéo", "đm", "đmá", "dmm", "dm", "buồi", "cặt", "phò", 
    "chịch", "xoạc", "địt", "đù", "vãi", "chó", "óc", "ngu",
    "fuck", "shit", "bitch", "cunt", "dick", "pussy", "asshole"
}

def contains_bad_word(text):
    """Kiểm tra xem câu/từ có chứa từ bậy hay không"""
    words = text.lower().strip().split()
    for word in words:
        if word in BAD_WORDS:
            return True
    return text.lower().strip() in BAD_WORDS

def prepare_dictionaries():
    words_vi = set()
    syllables_vi = set()
    words_en = set()
    
    urls_vi = [
        "https://raw.githubusercontent.com/vietnamese-wordlist/vietnamese-wordlist/master/words.txt",
        "https://raw.githubusercontent.com/Khang-NT/vietnamese-dictionary/master/words.txt"
    ]
    for url in urls_vi:
        try:
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
                content = response.read().decode('utf-8', errors='ignore')
                for line in content.splitlines():
                    word = line.strip().lower()
                    if word and len(word.split()) == 2 and not contains_bad_word(word):
                        words_vi.add(word)
                        for syllable in word.split():
                            syllables_vi.add(syllable)
        except Exception as e:
            print(f"Lỗi tải từ điển TV: {e}")

    try:
        url_en = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url_en, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            content = response.read().decode('utf-8', errors='ignore')
            words_en = set(
                line.strip().lower() for line in content.splitlines() 
                if line.strip() and len(line.strip()) > 1 and not contains_bad_word(line.strip())
            )
    except Exception as e:
        print(f"Lỗi tải từ điển TA: {e}")

    # Từ điển dự phòng
    if not words_vi:
        words_vi = {"mèo con", "bàn học", "xe máy", "học sinh", "cây cảnh", "sách vở"}
    if not words_en:
        words_en = {"apple", "banana", "cat", "dog", "elephant", "fish", "green"}

    return words_vi, syllables_vi, words_en

dictionary_vi, syllables_vi, dictionary_en = prepare_dictionaries()

VN_CHARS_REGEX = re.compile(r'^[a-zàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]+$')

def is_valid_vietnamese_word(text):
    text_clean = text.lower().strip()
    words = text_clean.split()
    if len(words) != 2:
        return False
    if not VN_CHARS_REGEX.match(text_clean):
        return False
    if len(syllables_vi) > 100:
        if text_clean in dictionary_vi:
            return True
        return (words[0] in syllables_vi) and (words[1] in syllables_vi)
    return True

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

def update_highscore_if_needed(mode, count):
    mode_key = "vi" if mode == "vi" else "en"
    current_hs = highscores.get(mode_key, {}).get("count", 0)
    if count > current_hs:
        highscores[mode_key] = {"count": count}
        save_highscore(highscores)
        return True
    return False

async def add_success_reactions(message, count):
    try:
        await message.add_reaction(CUSTOM_TICK)
    except Exception:
        await message.add_reaction("✅")

    try:
        if count in NUMBER_EMOJIS:
            await message.add_reaction(NUMBER_EMOJIS[count])
    except Exception as e:
        print(f"Lỗi thả emoji số: {e}")

async def add_fail_reaction(message):
    try:
        await message.add_reaction(CUSTOM_CROSS)
    except Exception:
        await message.add_reaction("❌")

@bot.event
async def on_ready():
    print(f"Bot {bot.user} đã sẵn sàng!")

@bot.command(name="noitu")
@commands.has_permissions(administrator=True)
async def start_game_vi(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("⚠️ Kênh này đang có trận diễn ra rồi!")
        return

    start_word = random.choice(list(dictionary_vi))
    last_syllable = start_word.split()[-1]

    games[channel_id] = {
        "mode": "vi",
        "last_word": start_word,
        "count": 1,
        "used_words": {start_word},
        "last_player": bot.user.id,
        "scores": {}
    }

    msg = await ctx.send(
        f"🎮 **Đã bắt đầu trò chơi nối từ! (Tiếng Việt)**\n"
        f"• Từ mở màn ngẫu nhiên của Bot: **{start_word.upper()}**\n"
        f"👉 Mọi người hãy nối tiếp từ bắt đầu bằng: **'{last_syllable}'** (chỉ tính từ **2 chữ**)."
    )
    await add_success_reactions(msg, 1)

@bot.command(name="noituen")
@commands.has_permissions(administrator=True)
async def start_game_en(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("⚠️ Kênh này đang có trận diễn ra rồi!")
        return

    start_word = random.choice(list(dictionary_en))
    last_char = start_word[-1]

    games[channel_id] = {
        "mode": "en",
        "last_word": start_word,
        "count": 1,
        "used_words": {start_word},
        "last_player": bot.user.id,
        "scores": {}
    }

    msg = await ctx.send(
        f"🔤 **Đã bắt đầu trò chơi nối từ! (Tiếng Anh)**\n"
        f"• Từ mở màn ngẫu nhiên của Bot: **{start_word.upper()}**\n"
        f"👉 Mọi người hãy nối từ tiếp theo bắt đầu bằng chữ: **'{last_char.upper()}'**."
    )
    await add_success_reactions(msg, 1)

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

@bot.command(name="hint")
async def get_hint(ctx):
    channel_id = ctx.channel.id
    user_id = ctx.author.id

    if channel_id not in games:
        await ctx.send("⚠️ Chưa có game đang chạy!")
        return

    hints_left = user_hints.get(user_id, 0)
    if hints_left <= 0:
        await ctx.send("⚠️ Bạn đã hết lượt gợi ý hôm nay rồi. Gõ `?daily` để nhận lượt mới!")
        return

    game = games[channel_id]

    if game["mode"] == "en":
        last_char = game["last_word"][-1]
        valid_words = [w for w in dictionary_en if w.startswith(last_char) and w not in game["used_words"] and not contains_bad_word(w)]
        if valid_words:
            user_hints[user_id] -= 1
            suggested = random.choice(valid_words)
            await ctx.send(f"💡 **Gợi ý TA:** Từ bắt đầu bằng **'{last_char.upper()}'**: **{suggested}** *(Còn {user_hints[user_id]}/3 lượt)*")
        else:
            await ctx.send("💡 Hết từ nối rồi!")

    elif game["mode"] == "vi":
        prev_last = game["last_word"].split()[-1]
        prefix = prev_last + " "
        valid_words = [w for w in dictionary_vi if w.startswith(prefix) and w not in game["used_words"] and not contains_bad_word(w)]
        if valid_words:
            user_hints[user_id] -= 1
            suggested = random.choice(valid_words)
            await ctx.send(f"💡 **Gợi ý TV:** Từ bắt đầu bằng **'{prev_last}'**: **{suggested}** *(Còn {user_hints[user_id]}/3 lượt)*")
        else:
            await ctx.send(f"💡 Cố tìm từ bắt đầu bằng **'{prev_last}'** nhé!")

@bot.command(name="top")
async def show_top(ctx):
    channel_id = ctx.channel.id
    if channel_id not in games:
        await ctx.send("⚠️ Chưa có trận đấu nào đang diễn ra!")
        return

    scores = games[channel_id]["scores"]
    if not scores:
        await ctx.send("📊 Chưa có ai ghi điểm trong ván này!")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    msg = "🏆 **BẢNG XẾP HẠNG VÁN HIỆN TẠI** 🏆\n"
    for idx, (user_id, count) in enumerate(sorted_scores, 1):
        user = await bot.fetch_user(user_id)
        msg += f"**#{idx}** {user.display_name}: **{count}** từ\n"

    await ctx.send(msg)

@bot.command(name="highscore")
async def show_highscore(ctx):
    embed = discord.Embed(title="🏆 KỶ LỤC CAO NHẤT SERVER", color=discord.Color.gold())
    embed.add_field(name="🇻🇳 Tiếng Việt", value=f"**{highscores.get('vi', {}).get('count', 0)}** từ", inline=False)
    embed.add_field(name="🇬🇧 Tiếng Anh", value=f"**{highscores.get('en', {}).get('count', 0)}** từ", inline=False)
    await ctx.send(embed=embed)

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
        await ctx.send(f"🛑 Trận đấu đã dừng! Tổng số từ nối được: **{total_count}**{hs_msg}")
    else:
        await ctx.send("⚠️ Kênh này chưa có ván đấu nào!")

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

    # --- NỐI TỪ TIẾNG VIỆT ---
    if game["mode"] == "vi":
        words = text.split()
        if len(words) != 2:
            return

        prev_last = game["last_word"].split()[-1]

        # 🚫 Kiểm tra từ bậy/thô tục
        if contains_bad_word(text):
            await add_fail_reaction(message)
            await message.reply(f"🚫 Từ ngữ bậy bạ/không phù hợp không được tính! Từ tiếp theo phải bắt đầu bằng **'{prev_last}'**.", mention_author=False)
            return

        if game["last_player"] == message.author.id:
            await add_fail_reaction(message)
            await message.reply(f"❌ Bạn không được nối 2 lần liên tiếp! Hãy chờ người khác nối từ tiếp theo bắt đầu bằng **'{prev_last}'**.", mention_author=False)
            return

        if text in game["used_words"]:
            await add_fail_reaction(message)
            await message.reply(f"❌ Từ **'{text}'** đã được dùng rồi! Từ tiếp theo phải bắt đầu bằng **'{prev_last}'**.", mention_author=False)
            return

        if not is_valid_vietnamese_word(text):
            await add_fail_reaction(message)
            await message.reply(f"❌ **'{text}'** không phải từ tiếng Việt hợp lệ! Từ tiếp theo phải bắt đầu bằng **'{prev_last}'**.", mention_author=False)
            return

        if words[0] != prev_last:
            await add_fail_reaction(message)
            await message.reply(f"❌ Sai từ nối! Từ tiếp theo phải bắt đầu bằng từ **'{prev_last}'**.", mention_author=False)
            return

        game["used_words"].add(text)
        game["last_word"] = text
        game["count"] += 1
        game["last_player"] = message.author.id
        game["scores"][message.author.id] = game["scores"].get(message.author.id, 0) + 1

        await add_success_reactions(message, game["count"])
        return

    # --- NỐI TỪ TIẾNG ANH ---
    if game["mode"] == "en":
        words = text.split()
        if len(words) != 1:
            return

        last_char = game["last_word"][-1]

        # 🚫 Kiểm tra từ bậy/thô tục
        if contains_bad_word(text):
            await add_fail_reaction(message)
            await message.reply(f"🚫 Từ ngữ bậy bạ/không phù hợp không được tính! Từ tiếp theo phải bắt đầu bằng chữ **'{last_char.upper()}'**.", mention_author=False)
            return

        if game["last_player"] == message.author.id:
            await add_fail_reaction(message)
            await message.reply(f"❌ Bạn không được nối 2 lần liên tiếp! Hãy chờ người khác nối từ bắt đầu bằng chữ **'{last_char.upper()}'**.", mention_author=False)
            return

        if len(dictionary_en) > 100 and text not in dictionary_en:
            await add_fail_reaction(message)
            await message.reply(f"❌ **'{text}'** không có trong từ điển! Từ tiếp theo phải bắt đầu bằng chữ **'{last_char.upper()}'**.", mention_author=False)
            return

        if text in game["used_words"]:
            await add_fail_reaction(message)
            await message.reply(f"❌ Từ **'{text}'** đã dùng rồi! Từ tiếp theo phải bắt đầu bằng chữ **'{last_char.upper()}'**.", mention_author=False)
            return

        if text[0] != last_char:
            await add_fail_reaction(message)
            await message.reply(f"❌ Sai chữ nối! Từ tiếp theo phải bắt đầu bằng chữ **'{last_char.upper()}'**.", mention_author=False)
            return

        game["used_words"].add(text)
        game["last_word"] = text
        game["count"] += 1
        game["last_player"] = message.author.id
        game["scores"][message.author.id] = game["scores"].get(message.author.id, 0) + 1

        await add_success_reactions(message, game["count"])
        return

try:
    keep_alive()
except Exception:
    pass

TOKEN = os.getenv("DISCORD_TOKEN", "DÁN_TOKEN_DISCORD_CỦA_BẠN_VÀO_ĐÂY")
bot.run(TOKEN)
