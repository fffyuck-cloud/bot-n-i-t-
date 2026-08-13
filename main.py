import os
import ssl
import json
import urllib.request
import random
import re
import unicodedata
import discord
from datetime import date
from discord.ext import commands
from keep_alive import keep_alive

# MÀU SẮC THEME ĐEN HỒNG
COLOR_BLACK = 0x1A1A1A  
COLOR_PINK = 0xFF69B4   

# Custom Emoji
CUSTOM_TICK = "Screenshot20260812172055:1537043520790073424"
CUSTOM_CROSS = "Screenshot20260812173722:1537047895310602300"

NUMBER_EMOJIS = {
    1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
    6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
}

# --- 🛠️ HÀM CHUẨN HÓA UNICODE TRIỆT ĐỂ (NFC) ---
def norm(text: str) -> str:
    """Chuyển toàn bộ chuỗi về NFC Unicode, viết thường và xóa khoảng trắng thừa."""
    if not text:
        return ""
    # Chuẩn hóa về NFC
    text = unicodedata.normalize('NFC', str(text).lower().strip())
    # Xóa nhiều khoảng trắng liên tiếp thành 1 khoảng trắng
    return re.sub(r'\s+', ' ', text)

BAD_WORDS = {norm("ỉa")}
DEAD_END_WORDS = {
    norm(w) for w in [
        "vậy", "sao", "mà", "thì", "là", "nhé", "à", "nhỉ", "nè", "đâu", "đó",
        "nào", "đấy", "ư", "hử", "nha", "nghen", "ha", "kìa", "này", "chứ", "rồi",
        "chăng", "vơi", "vâng", "ôi", "uôi", "hế", "hèn"
    ]
}

EASY_VI_WORDS = [
    "đá banh", "đá bóng", "bàn học", "học sinh", "sinh viên", "viên bi", "bi ao", "ao cá", "cá chép", 
    "chép phạt", "phạt góc", "học bài", "học tập", "học hành", "bài học", "bài tập", "tập viết", 
    "viết sách", "sách vở", "vở kịch", "kịch bản", "bản đồ", "đồ chơi", "chơi game", "góc sân", 
    "sân trường", "trường học", "góc nhỏ", "phạt đền", "góc nhìn", "thể thao", "bóng đá", "cầu thủ", 
    "thủ môn", "môn học", "thời gian", "gian hàng", "mặt trời", "mặt đất", "thời tiết", "máy tính", 
    "điện thoại", "xe máy", "xe đạp", "bạn bè", "thầy cô", "gia đình", "âm nhạc", "ca sĩ", "bài hát", 
    "mưa rào", "nắng ấm", "cây xanh", "hoa hồng", "quần áo", "màu sắc", "vui vẻ", "hạnh phúc", 
    "thành công", "cố gắng", "nỗ lực", "học hỏi", "kiến thức", "tương lai"
]

def contains_bad_word(text):
    text_clean = norm(text)
    words = text_clean.split()
    for word in words:
        if word in BAD_WORDS:
            return True
    return text_clean in BAD_WORDS

def is_dead_end_word(word):
    word_clean = norm(word)
    syllables = word_clean.split()
    if len(syllables) == 2 and syllables[-1] in DEAD_END_WORDS:
        return True
    return False

# --- TẢI VÀ NẠP TỪ ĐIỂN ---
def prepare_dictionaries():
    words_vi = set(norm(w) for w in EASY_VI_WORDS)
    words_en = set()

    urls_vi = [
        "https://raw.githubusercontent.com/vinhjaxt/vietnamese-words/master/vietnamese-words.txt",
        "https://raw.githubusercontent.com/undertheseanlp/nlp/master/underthesea/word_tokenize/dicts/words.txt",
        "https://raw.githubusercontent.com/stopwords-iso/stopwords-vi/master/stopwords-vi.txt"
    ]
    
    for url in urls_vi:
        try:
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                for line in content.splitlines():
                    word = norm(line.replace("_", " "))
                    if word and len(word.split()) == 2 and not contains_bad_word(word):
                        words_vi.add(word)
        except Exception as e:
            print(f"Không thể nạp nguồn {url}: {e}")

    try:
        url_en = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url_en, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
            for line in content.splitlines():
                w = norm(line)
                if w and len(w) > 1 and not contains_bad_word(w):
                    words_en.add(w)
    except Exception as e:
        print(f"Lỗi tải từ điển Anh: {e}")

    if not words_en:
        words_en = {"apple", "banana", "cat", "dog", "elephant", "fish", "green"}

    print(f"✅ Đã nạp thành công: {len(words_vi)} từ Tiếng Việt và {len(words_en)} từ Tiếng Anh (Đã chuẩn hóa NFC).")
    return words_vi, words_en

dictionary_vi, dictionary_en = prepare_dictionaries()
VN_CHARS_REGEX = re.compile(r'^[a-zàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]+$')

def is_valid_vietnamese_word(text):
    text_clean = norm(text)
    words = text_clean.split()
    if len(words) != 2 or not VN_CHARS_REGEX.match(text_clean):
        return False
    return text_clean in dictionary_vi

def pick_random_vi_word(prefix=None, used_words=None):
    if used_words is None:
        used_words = set()
    else:
        used_words = {norm(w) for w in used_words}

    prefix_norm = norm(prefix) if prefix else None

    easy_candidates = [
        w for w in EASY_VI_WORDS
        if (not prefix_norm or norm(w).startswith(prefix_norm + " ")) 
        and norm(w) not in used_words and not is_dead_end_word(w) and not contains_bad_word(w)
    ]
    all_candidates = [
        w for w in dictionary_vi
        if (not prefix_norm or norm(w).startswith(prefix_norm + " ")) 
        and norm(w) not in used_words and not is_dead_end_word(w) and not contains_bad_word(w)
    ]

    if not all_candidates:
        return None

    if random.random() < 0.80 and easy_candidates:
        return random.choice(easy_candidates)
    return random.choice(all_candidates)

# --- QUẢN LÝ DATABASE THỐNG KÊ (JSON) ---
STATS_FILE = "user_stats.json"
HIGHSCORE_FILE = "highscore.json"

def load_json(file_path, default_data):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_data
    return default_data

def save_json(file_path, data):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Lỗi lưu {file_path}: {e}")

user_stats = load_json(STATS_FILE, {})
highscores = load_json(HIGHSCORE_FILE, {"vi": {"count": 0}, "en": {"count": 0}})

def update_user_stats(user_id, added_words=0, win=False, loss=False):
    u_id = str(user_id)
    if u_id not in user_stats:
        user_stats[u_id] = {"wins": 0, "losses": 0, "total_words": 0}
    user_stats[u_id]["total_words"] += added_words
    if win:
        user_stats[u_id]["wins"] += 1
    if loss:
        user_stats[u_id]["losses"] += 1
    save_json(STATS_FILE, user_stats)

def update_highscore_if_needed(mode, count):
    mode_key = "vi" if mode == "vi" else "en"
    current_hs = highscores.get(mode_key, {}).get("count", 0)
    if count > current_hs:
        highscores[mode_key] = {"count": count}
        save_json(HIGHSCORE_FILE, highscores)
        return True
    return False

# --- NÚT BẤM INTERACTIVE UI ---
class GameControlButtons(discord.ui.View):
    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="💡 Gợi ý", style=discord.ButtonStyle.primary, custom_id="btn_game_hint")
    async def hint_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel_id = interaction.channel_id
        if channel_id not in games:
            await interaction.response.send_message("Chưa có trận nào đang chạy nha!", ephemeral=True)
            return

        user_id = interaction.user.id
        hints_left = user_hints.get(user_id, 0)
        if hints_left <= 0:
            await interaction.response.send_message("Bạn hết lượt gợi ý rồi. Gõ `?daily` để nhận lượt mới nhé!", ephemeral=True)
            return

        game = games[channel_id]
        if game["mode"] in ["vi", "vi_pvp"]:
            prev_last = norm(game["last_word"].split()[-1])
            suggested = pick_random_vi_word(prefix=prev_last, used_words=game["used_words"])
            if suggested:
                user_hints[user_id] -= 1
                await interaction.response.send_message(f"💡 **Gợi ý:** Từ bắt đầu bằng **'{prev_last}'**: **{suggested}** *(Còn {user_hints[user_id]}/3 lượt)*", ephemeral=True)
            else:
                await interaction.response.send_message(f"💡 Hết từ chuẩn bắt đầu bằng **'{prev_last}'** rồi!", ephemeral=True)
        elif game["mode"] == "en":
            last_char = norm(game["last_word"])[-1]
            valid_words = [w for w in dictionary_en if norm(w).startswith(last_char) and norm(w) not in game["used_words"]]
            if valid_words:
                user_hints[user_id] -= 1
                suggested = random.choice(valid_words)
                await interaction.response.send_message(f"💡 **Gợi ý TA:** Từ bắt đầu bằng **'{last_char.upper()}'**: **{suggested}** *(Còn {user_hints[user_id]}/3 lượt)*", ephemeral=True)
            else:
                await interaction.response.send_message("💡 Hết từ để gợi ý rồi!", ephemeral=True)

    @discord.ui.button(label="📊 Hồ sơ", style=discord.ButtonStyle.secondary, custom_id="btn_game_profile")
    async def profile_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        u_id = str(interaction.user.id)
        stats = user_stats.get(u_id, {"wins": 0, "losses": 0, "total_words": 0})
        wins, losses = stats["wins"], stats["losses"]
        total = wins + losses
        win_rate = round((wins / total * 100), 1) if total > 0 else 0
        
        msg = f"📊 **Hồ Sơ {interaction.user.display_name}**:\n🏆 Thành tích: `{wins}` Thắng | `{losses}` Thua (Tỉ lệ: `{win_rate}%`)\n✍️ Tổng số từ đã nối: `{stats['total_words']}` từ"
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.ui.button(label="🏆 Highscore", style=discord.ButtonStyle.success, custom_id="btn_game_hs")
    async def highscore_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vi_hs = highscores.get('vi', {}).get('count', 0)
        en_hs = highscores.get('en', {}).get('count', 0)
        await interaction.response.send_message(f"🏆 **Kỷ Lục Server:**\n🇻🇳 Tiếng Việt: `{vi_hs}` từ\n🇬🇧 Tiếng Anh: `{en_hs}` từ", ephemeral=True)

# --- NÚT XÁC NHẬN THÁCH ĐẤU PvP 1v1 ---
class PvPChallengeView(discord.ui.View):
    def __init__(self, challenger, opponent):
        super().__init__(timeout=60)
        self.challenger = challenger
        self.opponent = opponent
        self.accepted = None

    @discord.ui.button(label="⚔️ Chấp Nhận", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.opponent.id:
            await interaction.response.send_message("Lời thách đấu này không dành cho bạn!", ephemeral=True)
            return
        self.accepted = True
        self.stop()
        await interaction.response.send_message(f"⚔️ **{self.opponent.display_name}** đã chấp nhận lời thách đấu!")

    @discord.ui.button(label="✖️ Từ Chối", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.opponent.id:
            await interaction.response.send_message("Lời thách đấu này không dành cho bạn!", ephemeral=True)
            return
        self.accepted = False
        self.stop()
        await interaction.response.send_message(f"❌ **{self.opponent.display_name}** đã từ chối lời thách đấu.")

# --- INITIALIZE BOT ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)
games = {}
user_hints = {}        
user_daily_claimed = {} 

async def add_success_reactions(message, count):
    try: await message.add_reaction(CUSTOM_TICK)
    except Exception: await message.add_reaction("✅")
    try:
        if count in NUMBER_EMOJIS: await message.add_reaction(NUMBER_EMOJIS[count])
    except Exception: pass

async def add_fail_reaction(message):
    try: await message.add_reaction(CUSTOM_CROSS)
    except Exception: await message.add_reaction("❌")

async def check_and_send_streak(channel, count):
    if count > 0 and count % 10 == 0:
        embed1 = discord.Embed(title="COMBO STREAK CỰC CHẤT!", color=COLOR_BLACK)
        embed2 = discord.Embed(description=f"**XỊN XÒ!** Trận đấu đã cán mốc **{count} TỪ NỐI LIÊN TIẾP**!", color=COLOR_PINK)
        await channel.send(embeds=[embed1, embed2])

@bot.event
async def on_ready():
    print(f"Bot {bot.user} đã sẵn sàng hoạt động!")

# --- 🎮 LỆNH BẮT ĐẦU GAME ---
@bot.command(name="noitu")
@commands.has_permissions(administrator=True)
async def start_game_vi(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("Kênh này đang có trận diễn ra rồi nha!")
        return

    start_word = norm(pick_random_vi_word() or random.choice(EASY_VI_WORDS))
    last_syllable = start_word.split()[-1]

    games[channel_id] = {
        "mode": "vi", "vs_bot": False, "last_word": start_word,
        "count": 1, "used_words": {start_word}, "last_player": bot.user.id, "scores": {}
    }

    embed1 = discord.Embed(title="TRÒ CHƠI NỐI TỪ (Tiếng Việt)", color=COLOR_BLACK)
    embed1.add_field(name="Từ mở màn", value=f"**{start_word.upper()}**", inline=False)
    embed2 = discord.Embed(color=COLOR_PINK)
    embed2.add_field(name="Từ tiếp theo", value=f"👉 Bắt đầu bằng tiếng **'{last_syllable}'**", inline=False)
    
    view = GameControlButtons(channel_id)
    msg = await ctx.send(embeds=[embed1, embed2], view=view)
    await add_success_reactions(msg, 1)

@bot.command(name="noitubot")
async def start_game_vi_bot(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("Kênh này đang có trận diễn ra rồi nha!")
        return

    start_word = norm(pick_random_vi_word() or random.choice(EASY_VI_WORDS))
    last_syllable = start_word.split()[-1]

    games[channel_id] = {
        "mode": "vi", "vs_bot": True, "last_word": start_word,
        "count": 1, "used_words": {start_word}, "last_player": bot.user.id, "scores": {}
    }

    embed1 = discord.Embed(title="🤖 1v1 NỐI TỪ CHUẨN VỚI BOT", color=COLOR_BLACK)
    embed1.add_field(name="Bot mở màn bằng từ", value=f"**{start_word.upper()}**", inline=False)
    embed2 = discord.Embed(color=COLOR_PINK)
    embed2.add_field(name="Lượt của bạn", value=f"Hãy nhập từ 2 chữ bắt đầu bằng **'{last_syllable}'**", inline=False)

    view = GameControlButtons(channel_id)
    msg = await ctx.send(embeds=[embed1, embed2], view=view)
    await add_success_reactions(msg, 1)

# --- ⚔️ LỆNH THÁCH ĐẤU PvP 1v1 ---
@bot.command(name="pvp")
async def pvp_challenge(ctx, opponent: discord.Member):
    if opponent.bot or opponent.id == ctx.author.id:
        await ctx.send("Bạn không thể thách đấu chính mình hoặc Bot!")
        return
    
    channel_id = ctx.channel.id
    if channel_id in games:
        await ctx.send("Kênh này đang có trận đấu diễn ra rồi!")
        return

    view = PvPChallengeView(ctx.author, opponent)
    embed = discord.Embed(
        title="⚔️ LỜI THÁCH ĐẤU NỐI TỪ 1v1",
        description=f"**{ctx.author.display_name}** thách đấu **{opponent.mention}** một trận đối kháng!\nBạn có nhận lời không?",
        color=COLOR_PINK
    )
    await ctx.send(content=opponent.mention, embed=embed, view=view)
    await view.wait()

    if view.accepted:
        start_word = norm(pick_random_vi_word() or random.choice(EASY_VI_WORDS))
        last_syllable = start_word.split()[-1]
        
        games[channel_id] = {
            "mode": "vi_pvp", "vs_bot": False,
            "p1": ctx.author.id, "p2": opponent.id, "turn": ctx.author.id,
            "last_word": start_word, "count": 1, "used_words": {start_word},
            "scores": {ctx.author.id: 0, opponent.id: 0}
        }

        embed1 = discord.Embed(title="⚔️ TRẬN ĐẤU ĐỐI KHÁNG 1v1 BẮT ĐẦU", color=COLOR_BLACK)
        embed1.add_field(name="Từ mở màn", value=f"**{start_word.upper()}**", inline=False)
        embed2 = discord.Embed(description=f"👉 Lượt đi đầu tiên: {ctx.author.mention}\nNối từ bắt đầu bằng tiếng **'{last_syllable}'**", color=COLOR_PINK)
        
        game_view = GameControlButtons(channel_id)
        await ctx.send(embeds=[embed1, embed2], view=game_view)

# --- 📊 LỆNH XEM HỒ SƠ THỐNG KÊ ---
@bot.command(name="profile")
async def show_profile(ctx, member: discord.Member = None):
    target = member or ctx.author
    u_id = str(target.id)
    stats = user_stats.get(u_id, {"wins": 0, "losses": 0, "total_words": 0})
    
    wins, losses = stats["wins"], stats["losses"]
    total = wins + losses
    win_rate = round((wins / total * 100), 1) if total > 0 else 0
    
    embed1 = discord.Embed(title=f"📊 HỒ SƠ THỐNG KÊ - {target.display_name}", color=COLOR_BLACK)
    embed1.set_thumbnail(url=target.display_avatar.url)
    
    embed2 = discord.Embed(color=COLOR_PINK)
    embed2.add_field(name="🏆 Lịch sử Thắng / Thua", value=f"`{wins}` Thắng | `{losses}` Thua (Tỉ lệ: `{win_rate}%`)", inline=False)
    embed2.add_field(name="✍️ Tổng số từ đã nối", value=f"`{stats['total_words']}` từ chuẩn", inline=False)
    
    await ctx.send(embeds=[embed1, embed2])

# --- 🎁 DAILY, HINT, HIGHSCORE & CANCEL ---
@bot.command(name="daily")
async def claim_daily(ctx):
    user_id = ctx.author.id
    today_str = str(date.today())
    if user_daily_claimed.get(user_id) == today_str:
        await ctx.send("Hôm nay bạn đã điểm danh rồi, quay lại vào ngày mai nhé!")
        return
    user_hints[user_id] = 3
    user_daily_claimed[user_id] = today_str
    await ctx.send(f"🎁 Chúc mừng **{ctx.author.display_name}** nhận được **3 lượt gợi ý** `?hint` hôm nay! ✨")

@bot.command(name="highscore")
async def show_highscore(ctx):
    embed1 = discord.Embed(title="🏆 KỶ LỤC CAO NHẤT SERVER", color=COLOR_BLACK)
    embed1.add_field(name="🇻🇳 Tiếng Việt", value=f"**{highscores.get('vi', {}).get('count', 0)}** từ", inline=False)
    await ctx.send(embed=embed1)

@bot.command(name="huynoitu")
@commands.has_permissions(administrator=True)
async def stop_game(ctx):
    channel_id = ctx.channel.id
    if channel_id in games:
        del games[channel_id]
        await ctx.send("Trận đấu nối từ đã bị hủy thành công.")
    else:
        await ctx.send("Kênh này chưa có ván đấu nào!")

# --- ⚙️ LƯỢT ĐI CỦA BOT ---
async def bot_make_turn(channel, game):
    prev_last = norm(game["last_word"].split()[-1])
    bot_word = pick_random_vi_word(prefix=prev_last, used_words=game["used_words"])
    
    if bot_word:
        bot_word_norm = norm(bot_word)
        game["used_words"].add(bot_word_norm)
        game["last_word"] = bot_word_norm
        game["count"] += 1
        game["last_player"] = bot.user.id
        
        next_syllable = bot_word_norm.split()[-1]
        view = GameControlButtons(channel.id)
        msg = await channel.send(f"🤖 **Bot:** `{bot_word_norm.upper()}` *(Tổng: {game['count']} từ)* | Đến lượt bạn: **'{next_syllable}'**", view=view)
        await add_success_reactions(msg, game["count"])
        await check_and_send_streak(channel, game["count"])
    else:
        is_new_hs = update_highscore_if_needed("vi", game["count"])
        
        last_player_id = game.get("last_human_player")
        if last_player_id:
            update_user_stats(last_player_id, win=True)

        embed = discord.Embed(title="🎉 BẠN ĐÃ THẮNG BOT!", description=f"Bot đã bí từ bắt đầu bằng **'{prev_last}'**!\n🏆 Tổng số từ: **{game['count']}** từ.", color=COLOR_PINK)
        await channel.send(embed=embed)
        del games[channel.id]

# --- 📩 XỬ LÝ TIN NHẮN TỪ NGƯỜI CHƠI ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

    channel_id = message.channel.id
    if channel_id not in games or message.content.startswith("?"):
        return

    # Chuẩn hóa tin nhắn nhập vào của người chơi
    text = norm(message.content)
    game = games[channel_id]

    # --- CHẾ ĐỘ 1v1 PvP ĐỐI KHÁNG ---
    if game["mode"] == "vi_pvp":
        if message.author.id != game["turn"]:
            return

        words = text.split()
        prev_last = norm(game["last_word"].split()[-1])
        opponent_id = game["p2"] if message.author.id == game["p1"] else game["p1"]

        if len(words) != 2 or words[0] != prev_last or text in game["used_words"] or not is_valid_vietnamese_word(text) or contains_bad_word(text):
            await add_fail_reaction(message)
            
            update_user_stats(message.author.id, added_words=game["scores"].get(message.author.id, 0), loss=True)
            update_user_stats(opponent_id, added_words=game["scores"].get(opponent_id, 0), win=True)

            winner = await bot.fetch_user(opponent_id)
            embed = discord.Embed(
                title="🏆 TRẬN ĐẤU KẾT THÚC!",
                description=f"**{message.author.display_name}** đã đưa ra từ không hợp lệ!\n🎉 **{winner.mention}** đã giành chiến thắng chung cuộc!",
                color=COLOR_PINK
            )
            await message.channel.send(embed=embed)
            del games[channel_id]
            return

        game["used_words"].add(text)
        game["last_word"] = text
        game["count"] += 1
        game["scores"][message.author.id] = game["scores"].get(message.author.id, 0) + 1
        game["turn"] = opponent_id

        update_user_stats(message.author.id, added_words=1)
        await add_success_reactions(message, game["count"])
        
        next_syllable = words[-1]
        opponent_user = await bot.fetch_user(opponent_id)
        view = GameControlButtons(channel_id)
        await message.channel.send(f"👉 Đến lượt **{opponent_user.mention}**: Nối từ bắt đầu bằng **'{next_syllable}'**", view=view)
        return

    # --- CHẾ ĐỘ CHƠI THƯỜNG / VỚI BOT ---
    if game["mode"] == "vi":
        words = text.split()
        if len(words) != 2: return
        prev_last = norm(game["last_word"].split()[-1])

        if contains_bad_word(text) or words[0] != prev_last or text in game["used_words"] or not is_valid_vietnamese_word(text):
            await add_fail_reaction(message)
            if game["vs_bot"]:
                update_user_stats(message.author.id, loss=True)
                await message.reply(f"❌ Từ không hợp lệ! Bạn đã thua Bot trong ván này.", mention_author=False)
                del games[channel_id]
            return

        game["used_words"].add(text)
        game["last_word"] = text
        game["count"] += 1
        game["last_player"] = message.author.id
        game["last_human_player"] = message.author.id

        update_user_stats(message.author.id, added_words=1)
        await add_success_reactions(message, game["count"])
        await check_and_send_streak(message.channel, game["count"])

        if game["vs_bot"]:
            await bot_make_turn(message.channel, game)

try:
    keep_alive()
except Exception:
    pass

TOKEN = os.getenv("DISCORD_TOKEN", "DÁN_TOKEN_DISCORD_CỦA_BẠN_VÀO_ĐÂY")
bot.run(TOKEN)
