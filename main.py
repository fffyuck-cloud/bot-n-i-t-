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

# Tải và khởi tạo từ điển
def prepare_dictionaries():
    words_vi = set()
    syllables_vi = set()
    words_en = set()
    
    # 1. Thử tải từ điển Tiếng Việt từ GitHub
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
                    if word:
                        words_vi.add(word)
                        for syllable in word.split():
                            syllables_vi.add(syllable)
        except Exception as e:
            print(f"Không tải được từ điển online ({url}): {e}")

    # 2. Tải từ điển Tiếng Anh
    try:
        url_en = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url_en, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            content = response.read().decode('utf-8', errors='ignore')
            words_en = set(line.strip().lower() for line in content.splitlines() if line.strip())
    except Exception as e:
        print(f"Không tải được từ điển TA: {e}")

    print(f"-> Đã nạp: {len(words_vi)} từ TV ghép, {len(syllables_vi)} tiếng đơn TV, {len(words_en)} từ TA.")
    return words_vi, syllables_vi, words_en

dictionary_vi, syllables_vi, dictionary_en = prepare_dictionaries()

# Kiểm tra cấu trúc vần/ký tự tiếng Việt cơ bản (Fallback dự phòng)
VN_CHARS_REGEX = re.compile(r'^[a-zàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]+$')

def is_valid_vietnamese_word(text):
    text_clean = text.lower().strip()
    words = text_clean.split()
    
    # Bắt buộc đúng 2 từ
    if len(words) != 2:
        return False

    # Kiểm tra ký tự tiếng Việt hợp lệ
    if not VN_CHARS_REGEX.match(text_clean):
        return False

    # Nếu từ điển online tải thành công -> kiểm tra theo từ điển
    if len(syllables_vi) > 100:
        if text_clean in dictionary_vi:
            return True
        return (words[0] in syllables_vi) and (words[1] in syllables_vi)

    # Nếu từ điển rỗng (do lỗi mạng) -> Chấp nhận mọi cụm 2 từ tiếng Việt có ký tự hợp lệ
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

    games[channel_id] = {
        "mode": "vi",
        "last_word": None,
        "count": 0,
        "used_words": set(),
        "last_player": None,
        "scores": {}
    }
    await ctx.send(
        "🎮 **Đã bắt trò chơi nối từ! (Tiếng Việt)**\n"
        "• Không được nối 2 lần liên tiếp, thay phiên nhau mà nối.\n"
        "• Đúng chính xác 2 từ có nghĩa tiếng Việt.\n"
        "• Gõ `?daily` | `?hint` | `?top` | `?highscore` | `?huynoitu`."
    )

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

    # NỐI TỪ TIẾNG VIỆT
    if game["mode"] == "vi":
        words = text.split()
        if len(words) != 2:
            return

        # Kiểm tra tự nối 2 lần liên tiếp
        if game["last_player"] == message.author.id:
            await add_fail_reaction(message)
            return

        # Kiểm tra tính hợp lệ & trùng lặp
        if not is_valid_vietnamese_word(text) or text in game["used_words"]:
            await add_fail_reaction(message)
            return

        # Kiểm tra chữ đầu nối với chữ cuối từ trước
        if game["last_word"] is not None:
            prev_last = game["last_word"].split()[-1]
            if words[0] != prev_last:
                await add_fail_reaction(message)
                return

        game["used_words"].add(text)
        game["last_word"] = text
        game["count"] += 1
        game["last_player"] = message.author.id
        game["scores"][message.author.id] = game["scores"].get(message.author.id, 0) + 1

        # Thả Tick + Emoji số
        await add_success_reactions(message, game["count"])

try:
    keep_alive()
except Exception:
    pass

TOKEN = os.getenv("DISCORD_TOKEN", "DÁN_TOKEN_DISCORD_CỦA_BẠN_VÀO_ĐÂY")
bot.run(TOKEN)
