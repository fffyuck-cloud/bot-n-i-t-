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

# MÀU SẮC THEME ĐEN HỒNG
COLOR_BLACK = 0x1A1A1A  
COLOR_PINK = 0xFF69B4   
COLOR_HOT_PINK = 0xFF1493 

# Custom Emoji của bạn
CUSTOM_TICK = "Screenshot20260812172055:1537043520790073424"
CUSTOM_CROSS = "Screenshot20260812173722:1537047895310602300"

NUMBER_EMOJIS = {
    1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
    6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
}

# DANH SÁCH BỊ CHẶN (Chỉ chặn từ "ỉa")
BAD_WORDS = {"ỉa"}

def contains_bad_word(text):
    words = text.lower().strip().split()
    for word in words:
        if word in BAD_WORDS:
            return True
    return text.lower().strip() in BAD_WORDS

# --- TẢI TỪ ĐIỂN CHUẨN TỪ GITHUB ---
def prepare_dictionaries():
    words_vi = set()
    words_en = set()
    
    urls_vi = [
        "https://raw.githubusercontent.com/vietnamese-wordlist/vietnamese-wordlist/master/words.txt",
        "https://raw.githubusercontent.com/Khang-NT/vietnamese-dictionary/master/words.txt"
    ]
    for url in urls_vi:
        try:
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                for line in content.splitlines():
                    word = line.strip().lower()
                    # Chỉ lấy từ ghép 2 chữ chuẩn
                    if word and len(word.split()) == 2 and not contains_bad_word(word):
                        words_vi.add(word)
        except Exception as e:
            print(f"Lỗi tải từ điển TV từ {url}: {e}")

    try:
        url_en = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url_en, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
            words_en = set(
                line.strip().lower() for line in content.splitlines() 
                if line.strip() and len(line.strip()) > 1 and not contains_bad_word(line.strip())
            )
    except Exception as e:
        print(f"Lỗi tải từ điển TA: {e}")

    # Từ điển dự phòng nếu không tải được web
    if not words_vi:
        words_vi = {"bàn học", "học sinh", "sinh viên", "viên bi", "bi ao", "ao cá", "cá chép", "chép phạt"}
    if not words_en:
        words_en = {"apple", "banana", "cat", "dog", "elephant", "fish", "green"}

    return words_vi, words_en

dictionary_vi, dictionary_en = prepare_dictionaries()

VN_CHARS_REGEX = re.compile(r'^[a-zàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]+$')

# BẮT BUỘC: Từ phải nằm trong từ điển Tiếng Việt!
def is_valid_vietnamese_word(text):
    text_clean = text.lower().strip()
    words = text_clean.split()
    if len(words) != 2:
        return False
    if not VN_CHARS_REGEX.match(text_clean):
        return False
    return text_clean in dictionary_vi

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

async def check_and_send_streak(channel, count):
    if count > 0 and count % 10 == 0:
        embed1 = discord.Embed(title="COMBO STREAK CỰC CHẤT!", color=COLOR_BLACK)
        embed2 = discord.Embed(description=f"**XỊN XÒ!** Trận đấu đã cán mốc **{count} TỪ NỐI LIÊN TIẾP**!", color=COLOR_PINK)
        embed2.set_footer(text="Tiếp tục giữ phong độ nhé!")
        await channel.send(embeds=[embed1, embed2])

@bot.event
async def on_ready():
    print(f"Bot {bot.user} đã sẵn sàng! Kho TV có {len(dictionary_vi)} từ.")

# --- 🎮 BẮT ĐẦU GAME NHIỀU NGƯỜI CHƠI ---
@bot.command(name="noitu")
@commands.has_permissions(administrator=True)
async def start_game_vi(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("Kênh này đang có trận diễn ra rồi nha!")
        return

    start_word = random.choice(list(dictionary_vi))
    last_syllable = start_word.split()[-1]

    games[channel_id] = {
        "mode": "vi",
        "vs_bot": False,
        "last_word": start_word,
        "count": 1,
        "used_words": {start_word},
        "last_player": bot.user.id,
        "scores": {}
    }

    embed1 = discord.Embed(title="TRÒ CHƠI NỐI TỪ (Tiếng Việt)", color=COLOR_BLACK)
    embed1.add_field(name="Từ mở màn", value=f"**{start_word.upper()}**", inline=False)
    
    embed2 = discord.Embed(color=COLOR_PINK)
    embed2.add_field(name="Từ tiếp theo", value=f"👉 Bắt đầu bằng tiếng **'{last_syllable}'** (Bắt buộc từ chuẩn từ điển 2 chữ)", inline=False)
    embed2.set_footer(text="Không nối 2 lần liên tiếp | Gõ ?hint để xin gợi ý")
    
    msg = await ctx.send(embeds=[embed1, embed2])
    await add_success_reactions(msg, 1)

@bot.command(name="noituen")
@commands.has_permissions(administrator=True)
async def start_game_en(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("Kênh này đang có trận diễn ra rồi nha!")
        return

    start_word = random.choice(list(dictionary_en))
    last_char = start_word[-1]

    games[channel_id] = {
        "mode": "en",
        "vs_bot": False,
        "last_word": start_word,
        "count": 1,
        "used_words": {start_word},
        "last_player": bot.user.id,
        "scores": {}
    }

    embed1 = discord.Embed(title="ENGLISH WORD CHAIN", color=COLOR_BLACK)
    embed1.add_field(name="Starting Word", value=f"**{start_word.upper()}**", inline=False)
    
    embed2 = discord.Embed(color=COLOR_PINK)
    embed2.add_field(name="Next Letter", value=f"👉 Starts with letter **'{last_char.upper()}'**", inline=False)
    embed2.set_footer(text="Take turns connecting words | Type ?hint for help")

    msg = await ctx.send(embeds=[embed1, embed2])
    await add_success_reactions(msg, 1)

# --- 🤖 CHẾ ĐỘ 1v1 ĐẤU VỚI BOT ---
@bot.command(name="noitubot")
async def start_game_vi_bot(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("Kênh này đang có trận diễn ra rồi nha!")
        return

    start_word = random.choice(list(dictionary_vi))
    last_syllable = start_word.split()[-1]

    games[channel_id] = {
        "mode": "vi",
        "vs_bot": True,
        "last_word": start_word,
        "count": 1,
        "used_words": {start_word},
        "last_player": bot.user.id,
        "scores": {}
    }

    embed1 = discord.Embed(title="🤖 1v1 NỐI TỪ CHUẨN VỚI BOT", color=COLOR_BLACK)
    embed1.add_field(name="Bot mở màn bằng từ", value=f"**{start_word.upper()}**", inline=False)
    
    embed2 = discord.Embed(color=COLOR_PINK)
    embed2.add_field(name="Lượt của bạn", value=f"Hãy nhập từ 2 chữ có thật trong từ điển bắt đầu bằng **'{last_syllable}'**", inline=False)
    embed2.set_footer(text="✨ Bot sẽ nối chuẩn từ điển với bạn tới khi hết từ!")

    msg = await ctx.send(embeds=[embed1, embed2])
    await add_success_reactions(msg, 1)

@bot.command(name="noituboten")
async def start_game_en_bot(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("Kênh này đang có trận diễn ra rồi nha!")
        return

    start_word = random.choice(list(dictionary_en))
    last_char = start_word[-1]

    games[channel_id] = {
        "mode": "en",
        "vs_bot": True,
        "last_word": start_word,
        "count": 1,
        "used_words": {start_word},
        "last_player": bot.user.id,
        "scores": {}
    }

    embed1 = discord.Embed(title="🤖 1v1 WORD CHAIN WITH BOT", color=COLOR_BLACK)
    embed1.add_field(name="Bot Starting Word", value=f"**{start_word.upper()}**", inline=False)
    
    embed2 = discord.Embed(color=COLOR_PINK)
    embed2.add_field(name="Your Turn", value=f"Enter word starting with **'{last_char.upper()}'**", inline=False)

    msg = await ctx.send(embeds=[embed1, embed2])
    await add_success_reactions(msg, 1)

# --- 🎁 TIỆN ÍCH & LỆNH PHỤ ---
@bot.command(name="daily")
async def claim_daily(ctx):
    user_id = ctx.author.id
    today_str = str(date.today())

    if user_daily_claimed.get(user_id) == today_str:
        await ctx.send("Hôm nay bạn đã điểm danh rồi, quay lại vào ngày mai nhé!")
        return

    user_hints[user_id] = 3
    user_daily_claimed[user_id] = today_str
    
    embed1 = discord.Embed(title="🎁 ĐIỂM DANH HÀNG NGÀY", color=COLOR_BLACK)
    embed2 = discord.Embed(description=f"Chúc mừng **{ctx.author.display_name}** nhận được **3 lượt gợi ý** `?hint` hôm nay! ✨", color=COLOR_PINK)
    await ctx.send(embeds=[embed1, embed2])

@bot.command(name="hint")
async def get_hint(ctx):
    channel_id = ctx.channel.id
    user_id = ctx.author.id

    if channel_id not in games:
        await ctx.send("Chưa có trận nào đang chạy hết nha!")
        return

    hints_left = user_hints.get(user_id, 0)
    if hints_left <= 0:
        await ctx.send("Bạn hết lượt gợi ý rồi. Gõ `?daily` để nhận lượt mới nhé!")
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
            await ctx.send("💡 Hết từ để gợi ý rồi!")

    elif game["mode"] == "vi":
        prev_last = game["last_word"].split()[-1]
        prefix = prev_last + " "
        valid_words = [w for w in dictionary_vi if w.startswith(prefix) and w not in game["used_words"] and not contains_bad_word(w)]
        if valid_words:
            user_hints[user_id] -= 1
            suggested = random.choice(valid_words)
            await ctx.send(f"💡 **Gợi ý TV:** Từ bắt đầu bằng **'{prev_last}'**: **{suggested}** *(Còn {user_hints[user_id]}/3 lượt)*")
        else:
            await ctx.send(f"💡 Hết từ chuẩn trong từ điển bắt đầu bằng **'{prev_last}'** rồi!")

@bot.command(name="top")
async def show_top(ctx):
    channel_id = ctx.channel.id
    if channel_id not in games:
        await ctx.send("Chưa có trận đấu nào đang diễn ra!")
        return

    scores = games[channel_id]["scores"]
    if not scores:
        await ctx.send("📊 Chưa có ai ghi điểm trong ván này!")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    embed1 = discord.Embed(title="BẢNG XẾP HẠNG VÁN HIỆN TẠI", color=COLOR_BLACK)
    desc = ""
    for idx, (user_id, count) in enumerate(sorted_scores, 1):
        badge = f"**#{idx}**"
        user = await bot.fetch_user(user_id)
        desc += f"{badge} **{user.display_name}**: `{count}` từ\n"

    embed2 = discord.Embed(description=desc, color=COLOR_PINK)
    await ctx.send(embeds=[embed1, embed2])

@bot.command(name="highscore")
async def show_highscore(ctx):
    embed1 = discord.Embed(title="🏆 KỶ LỤC CAO NHẤT SERVER", color=COLOR_BLACK)
    embed1.add_field(name="🇻🇳 Tiếng Việt", value=f"**{highscores.get('vi', {}).get('count', 0)}** từ nối", inline=False)
    
    embed2 = discord.Embed(color=COLOR_PINK)
    embed2.add_field(name="🇬🇧 Tiếng Anh", value=f"**{highscores.get('en', {}).get('count', 0)}** từ nối", inline=False)
    await ctx.send(embeds=[embed1, embed2])

@bot.command(name="huynoitu")
@commands.has_permissions(administrator=True)
async def stop_game(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        game = games[channel_id]
        total_count = game["count"]
        is_new_hs = update_highscore_if_needed(game["mode"], total_count)
        
        embed1 = discord.Embed(title="TRẬN ĐẤU ĐÃ DỪNG", color=COLOR_BLACK)
        embed1.add_field(name="Tổng số từ đạt được", value=f"**{total_count}** từ", inline=False)
        
        embed2 = discord.Embed(color=COLOR_PINK)
        if is_new_hs:
            embed2.add_field(name="Kỷ lục", value="✨ **XÁC LẬP KỶ LỤC MỚI CỦA SERVER!**", inline=False)
        else:
            embed2.description = "Trận đấu đã kết thúc thành công."
        
        del games[channel_id]
        await ctx.send(embeds=[embed1, embed2])
    else:
        await ctx.send("Kênh này chưa có ván đấu nào!")

# --- ⚙️ BOT TÌM TỪ TỪ TỪ ĐIỂN VÀ PHẢN HỒI ---
async def bot_make_turn(channel, game):
    if game["mode"] == "vi":
        prev_last = game["last_word"].split()[-1]
        prefix = prev_last + " "
        
        # Bot lọc các từ CHUẨN từ điển bắt đầu bằng âm tiết của bạn và chưa sử dụng
        valid_words = [w for w in dictionary_vi if w.startswith(prefix) and w not in game["used_words"] and not contains_bad_word(w)]
        
        if valid_words:
            bot_word = random.choice(valid_words)
            game["used_words"].add(bot_word)
            game["last_word"] = bot_word
            game["count"] += 1
            game["last_player"] = bot.user.id
            
            next_syllable = bot_word.split()[-1]
            msg = await channel.send(f"🤖 **Bot:** `{bot_word.upper()}` *(Tổng: {game['count']} từ)* | Đến lượt bạn: **'{next_syllable}'**")
            await add_success_reactions(msg, game["count"])
            await check_and_send_streak(channel, game["count"])
        else:
            # Hết từ trong từ điển -> Bạn thắng!
            is_new_hs = update_highscore_if_needed("vi", game["count"])
            embed1 = discord.Embed(title="🎉 BẠN ĐÃ THẮNG BOT!", color=COLOR_BLACK)
            embed1.description = f"Bot đã cạn sạch từ chuẩn trong từ điển bắt đầu bằng **'{prev_last}'** rồi!\n🏆 Tổng số từ đạt được: **{game['count']}** từ."
            
            embed2 = discord.Embed(color=COLOR_PINK)
            if is_new_hs:
                embed2.add_field(name="Kỷ lục", value="✨ **KỶ LỤC MỚI SERVER!**", inline=False)
            else:
                embed2.description = "Đỉnh thật! Bạn đã hạ gục từ điển của bot!"
                
            await channel.send(embeds=[embed1, embed2])
            del games[channel.id]

    elif game["mode"] == "en":
        last_char = game["last_word"][-1]
        valid_words = [w for w in dictionary_en if w.startswith(last_char) and w not in game["used_words"] and not contains_bad_word(w)]
        
        if valid_words:
            bot_word = random.choice(valid_words)
            game["used_words"].add(bot_word)
            game["last_word"] = bot_word
            game["count"] += 1
            game["last_player"] = bot.user.id
            
            next_char = bot_word[-1]
            msg = await channel.send(f"🤖 **Bot:** `{bot_word.upper()}` *(Total: {game['count']})* | Your turn: **'{next_char.upper()}'**")
            await add_success_reactions(msg, game["count"])
            await check_and_send_streak(channel, game["count"])
        else:
            is_new_hs = update_highscore_if_needed("en", game["count"])
            embed1 = discord.Embed(title="🎉 YOU BEAT THE BOT!", color=COLOR_BLACK)
            embed1.description = f"Bot ran out of dictionary words!\n🏆 Total words: **{game['count']}**."
            
            embed2 = discord.Embed(color=COLOR_PINK)
            if is_new_hs:
                embed2.add_field(name="Highscore", value="✨ **NEW SERVER HIGHSCORE!**", inline=False)
            else:
                embed2.description = "Thanks for playing!"
                
            await channel.send(embeds=[embed1, embed2])
            del games[channel.id]

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

        # 1. Chặn từ "ỉa"
        if contains_bad_word(text):
            await add_fail_reaction(message)
            await message.reply(f"🚫 Từ này bị cấm nha! Nối tiếp từ: **'{prev_last}'**.", mention_author=False)
            return

        # 2. Không nối 2 lần liên tiếp (ở chế độ nhiều người)
        if not game["vs_bot"] and game["last_player"] == message.author.id:
            await add_fail_reaction(message)
            await message.reply(f"Bạn không được nối 2 lần liên tiếp! Chờ người khác nối từ bắt đầu bằng **'{prev_last}'** nhé.", mention_author=False)
            return

        # 3. Trùng từ
        if text in game["used_words"]:
            await add_fail_reaction(message)
            await message.reply(f"❌ Từ **'{text}'** đã dùng rồi! Nối tiếp từ bắt đầu bằng **'{prev_last}'** nha.", mention_author=False)
            return

        # 4. Kiểm tra từ chuẩn từ điển Tiếng Việt
        if not is_valid_vietnamese_word(text):
            await add_fail_reaction(message)
            await message.reply(f"❌ **'{text}'** không có trong từ điển tiếng Việt! Nhập từ chuẩn khác nhé.", mention_author=False)
            return

        # 5. Khớp từ nối
        if words[0] != prev_last:
            await add_fail_reaction(message)
            await message.reply(f"❌ Sai từ nối rồi! Từ tiếp theo phải bắt đầu bằng **'{prev_last}'**.", mention_author=False)
            return

        # Nối thành công!
        game["used_words"].add(text)
        game["last_word"] = text
        game["count"] += 1
        game["last_player"] = message.author.id
        game["scores"][message.author.id] = game["scores"].get(message.author.id, 0) + 1

        await add_success_reactions(message, game["count"])
        await check_and_send_streak(message.channel, game["count"])

        if game["vs_bot"]:
            await bot_make_turn(message.channel, game)
        return

    # --- NỐI TỪ TIẾNG ANH ---
    if game["mode"] == "en":
        words = text.split()
        if len(words) != 1:
            return

        last_char = game["last_word"][-1]

        if contains_bad_word(text):
            await add_fail_reaction(message)
            await message.reply(f"🚫 Từ này bị cấm nha! Nối tiếp chữ: **'{last_char.upper()}'**.", mention_author=False)
            return

        if not game["vs_bot"] and game["last_player"] == message.author.id:
            await add_fail_reaction(message)
            await message.reply(f"You can't play twice in a row! Wait for others to match **'{last_char.upper()}'**.", mention_author=False)
            return

        if len(dictionary_en) > 100 and text not in dictionary_en:
            await add_fail_reaction(message)
            await message.reply(f"❌ **'{text}'** không có trong từ điển! Từ tiếp theo phải bắt đầu bằng chữ **'{last_char.upper()}'**.", mention_author=False)
            return

        if text in game["used_words"]:
            await add_fail_reaction(message)
            await message.reply(f"❌ Từ **'{text}'** đã dùng rồi! Nối tiếp chữ **'{last_char.upper()}'** nha.", mention_author=False)
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
        await check_and_send_streak(message.channel, game["count"])

        if game["vs_bot"]:
            await bot_make_turn(message.channel, game)
        return

try:
    keep_alive()
except Exception:
    pass

TOKEN = os.getenv("DISCORD_TOKEN", "DÁN_TOKEN_DISCORD_CỦA_BẠN_VÀO_ĐÂY")
bot.run(TOKEN)
