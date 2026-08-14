import os
import ssl
import json
import urllib.request
import urllib.parse
import random
import re
import unicodedata
from datetime import datetime, date
import discord
from discord.ext import commands
from keep_alive import keep_alive

# --- 🎨 THEME & BANNER & EMOJI ---
COLOR_THEME   = 0xFF1493 # Hồng đậm Cyberpunk
COLOR_SUCCESS = 0x57F287 
COLOR_ERROR   = 0xED4245 

# 👉 Dán link ảnh banner của bạn vào đây:
BANNER_URL = "URL_ANH_BANNER_CUA_BAN" 

# Custom Emoji của bạn
EMOJI_TICK = "<:Screenshot20260812172055:1537043520790073424>"
EMOJI_CROSS = "<:Screenshot20260812173722:1537047895310602300>"

def norm(text: str) -> str:
    if not text: return ""
    text = unicodedata.normalize('NFC', str(text).lower().strip())
    return re.sub(r'\s+', ' ', text)

DEAD_END_WORDS = {norm(w) for w in ["vậy", "sao", "mà", "thì", "là", "nhé", "à", "nhỉ", "nè", "đâu", "đó", "nào", "đấy", "ư", "hử", "nha", "nghen", "ha", "kìa", "này", "chứ", "rồi"]}
EASY_VI_WORDS = ["đá banh", "đá bóng", "bàn học", "học sinh", "sinh viên", "viên bi", "bi ao", "ao cá", "cá chép", "chép phạt", "phạt góc", "học bài", "thể thao", "bóng đá", "cầu thủ"]

def is_dead_end_word(word):
    word_clean = norm(word)
    syllables = word_clean.split()
    return len(syllables) == 2 and syllables[-1] in DEAD_END_WORDS

# --- 📚 NẠP TỪ ĐIỂN TIẾNG VIỆT & ANH ---
def prepare_dictionaries():
    ctx = ssl._create_unverified_context()
    words_vi = set(norm(w) for w in EASY_VI_WORDS)
    try:
        req = urllib.request.Request("https://raw.githubusercontent.com/NguyenAnhTuan1997/Vietnamese-Dictionary/master/words.txt", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            for line in response.read().decode('utf-8', errors='ignore').splitlines():
                word = norm(line.replace("_", " "))
                if word and len(word.split()) == 2: words_vi.add(word)
    except: pass

    words_en = set()
    try:
        req = urllib.request.Request("https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            for line in response.read().decode('utf-8', errors='ignore').splitlines():
                w = line.strip().lower()
                if len(w) >= 2 and w.isalpha(): words_en.add(w)
    except: pass
    print(f"✅ NẠP DATA THÀNH CÔNG: {len(words_vi):,} từ VN | {len(words_en):,} từ EN.")
    return words_vi, words_en

dictionary_vi, dictionary_en = prepare_dictionaries()
VN_CHARS_REGEX = re.compile(r'^[a-zàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]+$')

def is_valid_vietnamese_word(text):
    text_clean = norm(text)
    return len(text_clean.split()) == 2 and VN_CHARS_REGEX.match(text_clean) and text_clean in dictionary_vi

def is_valid_english_word(text):
    return text.strip().lower() in dictionary_en

def pick_random_vi_word(prefix=None, used_words=None):
    used_words = {norm(w) for w in used_words} if used_words else set()
    prefix_norm = norm(prefix) if prefix else None
    all_w = [w for w in dictionary_vi if (not prefix_norm or norm(w).startswith(prefix_norm + " ")) and norm(w) not in used_words and not is_dead_end_word(w)]
    return random.choice(all_w) if all_w else None

def pick_random_en_word(letter=None, used_words=None):
    used_words = {w.lower() for w in used_words} if used_words else set()
    letter = letter.lower() if letter else None
    all_candidates = [w for w in dictionary_en if (not letter or w.startswith(letter)) and w not in used_words]
    return random.choice(all_candidates) if all_candidates else None

# --- 💾 THỐNG KÊ NGƯỜI CHƠI ---
STATS_FILE = "user_stats.json"
def load_json():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

user_stats = load_json()
def save_json():
    with open(STATS_FILE, "w", encoding="utf-8") as f: json.dump(user_stats, f, ensure_ascii=False, indent=4)

def update_user_stats(user_id, added_words=0, win=False, loss=False):
    u_id = str(user_id)
    if u_id not in user_stats: user_stats[u_id] = {"wins": 0, "losses": 0, "total_words": 0}
    user_stats[u_id]["total_words"] += added_words
    if win: user_stats[u_id]["wins"] += 1
    if loss: user_stats[u_id]["losses"] += 1
    save_json()

def get_user_title(total_words):
    if total_words >= 1000: return "🌟 CHÚA TỂ NGÔN TỪ"
    if total_words >= 500: return "👑 BẬC THẦY GIAO TIẾP"
    if total_words >= 200: return "🔥 CAO THỦ NỐI TỪ"
    return "🐣 TÂN THỦ NHẬP MÔN"

# --- 💎 GIAO DIỆN EMBED ---
def build_game_embed(game, title, last_player_name=None):
    embed = discord.Embed(color=COLOR_THEME, timestamp=datetime.now())
    embed.set_author(name=f"❖ {title} ❖", icon_url="https://cdn-icons-png.flaticon.com/512/8066/8066804.png")
    
    used_list = list(game.get("history_list", []))
    history_str = " ➔ ".join([w.upper() for w in used_list[-5:]])
    embed.add_field(name="╭━━━━━━━━ 📜 LỊCH SỬ TỪ VỰNG ━━━━━━━━╮", value="```fix\n" + history_str + "\n```", inline=False)

    if game["mode"] == "vi":
        prev_last = norm(game["last_word"].split()[-1]).upper()
        target_word = f"# 🔠 {prev_last}"
    else:
        last_char = game["last_word"][-1].upper()
        target_word = f"# 🔠 {last_char}"

    combo = game.get('count', 1)
    bar = f"`[{'█'*min(10, combo)}{'░'*max(0, 10-combo)}]`"
    embed.add_field(name="🎯 **NỐI TIẾP BẰNG**", value=target_word, inline=True)
    embed.add_field(name="🔥 **CHUỖI COMBO**", value=f"**{combo}**\n{bar}", inline=True)

    if game.get("is_duel"):
        p1_name = game.get("p1_name", "P1")
        p2_name = game.get("p2_name", "P2")
        current_turn = p1_name if game["turn_idx"] == 0 else p2_name
        embed.add_field(name="╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯", value=f"⚔️ **Đấu 1v1**: `{p1_name}` vs `{p2_name}`\n⏳ Lượt đi của: **{current_turn}**", inline=False)
    elif last_player_name:
        embed.add_field(name="╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯", value=f"✨ Vừa nối bởi: **{last_player_name}**", inline=False)
    else:
        embed.add_field(name="╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯", value="> 💬 *Chat trực tiếp từ nối vào kênh.*", inline=False)

    return embed

# --- 🖱️ NÚT BẤM TIỆN ÍCH ---
class GameControlButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Gợi Ý (Cứu Viện)", emoji="🆘", style=discord.ButtonStyle.danger, custom_id="btn_hint")
    async def hint_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel_id = interaction.channel_id
        if channel_id not in games: return await interaction.response.send_message("❌ Trận đấu không tồn tại!", ephemeral=True)
        game = games[channel_id]
        if game["mode"] == "vi":
            suggested = pick_random_vi_word(prefix=norm(game["last_word"].split()[-1]), used_words=game["used_words"])
        else:
            suggested = pick_random_en_word(letter=game["last_word"][-1].lower(), used_words=game["used_words"])
        await interaction.response.send_message(f"💡 Gợi ý cho bạn: **`{suggested.upper() if suggested else 'Không tìm thấy từ phù hợp'}`**", ephemeral=True)

# --- ⚔️ THÁCH ĐẤU 1V1 ---
class ChallengeView(discord.ui.View):
    def __init__(self, challenger, target):
        super().__init__(timeout=30)
        self.challenger = challenger
        self.target = target

    @discord.ui.button(label="Chấp Nhận Thách Đấu", emoji="⚔️", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id: return await interaction.response.send_message("❌ Bạn không phải là người được thách đấu!", ephemeral=True)
        channel_id = interaction.channel_id
        if channel_id in games: return await interaction.response.send_message("⚠️ Kênh đang có trận đấu khác!", ephemeral=True)
        
        for child in self.children: child.disabled = True
        await interaction.response.edit_message(content=f"⚔️ **{self.target.display_name}** đã chấp nhận chiến thư từ **{self.challenger.display_name}**!", view=self)
        
        word = norm(pick_random_vi_word() or "đá bóng")
        games[channel_id] = {
            "mode": "vi", "vs_bot": False, "is_duel": True, "players": [self.challenger.id, self.target.id],
            "p1_name": self.challenger.display_name, "p2_name": self.target.display_name,
            "turn_idx": 0, "last_word": word, "count": 1, "used_words": {word}, "history_list": [word]
        }
        
        if BANNER_URL and BANNER_URL != "URL_ANH_BANNER_CUA_BAN":
            await interaction.channel.send(BANNER_URL)
        await interaction.channel.send(embed=build_game_embed(games[channel_id], "⚔️ ĐẠI CHIẾN NỐI TỪ 1V1"))
        self.stop()

    @discord.ui.button(label="Từ Chối", emoji="🛑", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id: return await interaction.response.send_message("❌ Bạn không liên quan!", ephemeral=True)
        for child in self.children: child.disabled = True
        await interaction.response.edit_message(content=f"🛑 **{self.target.display_name}** đã từ chối thách đấu.", view=self)
        self.stop()

# --- 🚀 KHỞI TẠO BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)
games, user_hints, user_daily_claimed = {}, {}, {}

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user.name} đã sẵn sàng chinh chiến!")

@bot.command(name="help", aliases=["trogiup"])
async def custom_help(ctx):
    if BANNER_URL and BANNER_URL != "URL_ANH_BANNER_CUA_BAN":
        await ctx.send(BANNER_URL)
        
    embed = discord.Embed(color=COLOR_THEME)
    embed.set_author(name="❖ HỆ THỐNG TRỢ GIÚP NỐI TỪ ❖", icon_url=bot.user.display_avatar.url)
    embed.description = ">>> 🎮 **Word Chain Ultimate**\nHỗ trợ cả Tiếng Việt & Tiếng Anh, chế độ Solo Bot và Thách Đấu 1v1 đỉnh cao!"
    
    embed.add_field(name="🇻🇳 NỐI TỪ TIẾNG VIỆT", value="`?noitu` ➔ Chơi chung\n`?noitubot` ➔ Solo với Bot", inline=True)
    embed.add_field(name="🇬🇧 NỐI TỪ TIẾNG ANH", value="`?noitueng` ➔ Chơi chung\n`?noituboteng` ➔ Solo với Bot", inline=True)
    embed.add_field(name="⚔️ TÍNH NĂNG KHÁC", value="`?thachdau @user` ➔ Thách đấu 1v1 trực tiếp\n`?nghia [từ]` ➔ Tra nghĩa từ tiếng Anh\n`?profile` ➔ Xem hồ sơ cá nhân\n`?daily` ➔ Nhận lượt cứu viện\n`?huynoitu` ➔ Hủy ván chơi", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="nghia", aliases=["define"])
async def define_word(ctx, word: str = None):
    if not word:
        return await ctx.send("❌ Vui lòng nhập từ tiếng Anh cần tra! Ví dụ: `?nghia apple`")
    
    clean_w = word.strip().lower()
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(clean_w)}"
    ctx_ssl = ssl._create_unverified_context()
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx_ssl, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if not data or not isinstance(data, list):
                return await ctx.send(f"❌ Không tìm thấy định nghĩa cho từ **`{clean_w}`**.")
            
            entry = data[0]
            word_name = entry.get('word', clean_w).capitalize()
            phonetic = entry.get('phonetic', '')
            if not phonetic and entry.get('phonetics'):
                for p in entry.get('phonetics'):
                    if p.get('text'):
                        phonetic = p.get('text')
                        break
            
            embed = discord.Embed(title=f"📖 TRA TỪ ĐIỂN: {word_name}", description=f"**Phát âm:** `{phonetic}`" if phonetic else "", color=COLOR_THEME)
            
            meanings = entry.get('meanings', [])
            count = 0
            for meaning in meanings:
                if count >= 3: break
                part_of_speech = meaning.get('partOfSpeech', '')
                definitions = meaning.get('definitions', [])
                if definitions:
                    def_text = definitions[0].get('definition', '')
                    example = definitions[0].get('example', '')
                    val = f"• **Định nghĩa:** {def_text}"
                    if example:
                        val += f"\n• **Ví dụ:** *\"{example}\"* "
                    embed.add_field(name=f"📌 Loại từ: ({part_of_speech})", value=val, inline=False)
                    count += 1
            
            if BANNER_URL and BANNER_URL != "URL_ANH_BANNER_CUA_BAN":
                await ctx.send(BANNER_URL)
            await ctx.send(embed=embed)
    except Exception:
        await ctx.send(f"❌ Không tìm thấy từ **`{clean_w}`** trong cơ sở dữ liệu từ điển!")

@bot.command(name="thachdau")
async def challenge_user(ctx, member: discord.Member = None):
    if not member or member.bot or member == ctx.author: return await ctx.send("❌ Hãy tag một người chơi hợp lệ để thách đấu!")
    if ctx.channel.id in games: return await ctx.send("⚠️ Kênh này đang có trận đấu diễn ra!")
    
    if BANNER_URL and BANNER_URL != "URL_ANH_BANNER_CUA_BAN":
        await ctx.send(BANNER_URL)
    await ctx.send(content=member.mention, embed=discord.Embed(title="⚔️ LỜI THÁCH ĐẤU 1V1!", description=f"> **{ctx.author.display_name}** vừa thách đấu {member.mention}!", color=COLOR_THEME), view=ChallengeView(ctx.author, member))

@bot.command(name="profile")
async def show_profile(ctx, member: discord.Member = None):
    target = member or ctx.author
    stats = user_stats.get(str(target.id), {"wins": 0, "losses": 0, "total_words": 0})
    w, l, total = stats["wins"], stats["losses"], stats["total_words"]
    win_rate = round((w / (w + l) * 100), 1) if (w + l) > 0 else 0

    if BANNER_URL and BANNER_URL != "URL_ANH_BANNER_CUA_BAN":
        await ctx.send(BANNER_URL)

    embed = discord.Embed(title=f"💎 HỒ SƠ: {target.display_name}", color=COLOR_THEME)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="🏅 Danh Hiệu", value=f"**{get_user_title(total)}**", inline=True)
    embed.add_field(name="🧠 Vốn Từ Tích Lũy", value=f"**{total:,}** từ", inline=True)
    embed.add_field(name="⚔️ Tỉ Lệ Thắng", value=f"**{win_rate}%** ({w} Thắng / {l} Thua)", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="daily")
async def claim_daily(ctx):
    user_id, today_str = ctx.author.id, str(date.today())
    if user_daily_claimed.get(user_id) == today_str: return await ctx.send("❌ Bạn đã nhận lượt cứu viện hôm nay rồi!")
    user_hints[user_id] = 3
    user_daily_claimed[user_id] = today_str
    await ctx.send(embed=discord.Embed(title="🎁 NHẬN THƯỞNG THÀNH CÔNG", description="Bạn đã nhận được quyền trợ giúp cứu viện!", color=COLOR_SUCCESS))

@bot.command(name="noitu")
async def start_game_vi(ctx):
    if ctx.channel.id in games: return await ctx.send("⚠️ Kênh đang có trận đấu!")
    word = norm(pick_random_vi_word() or "đá bóng")
    games[ctx.channel.id] = {"mode": "vi", "vs_bot": False, "is_duel": False, "last_word": word, "count": 1, "used_words": {word}, "history_list": [word]}
    
    if BANNER_URL and BANNER_URL != "URL_ANH_BANNER_CUA_BAN":
        await ctx.send(BANNER_URL)
    await ctx.send(embed=build_game_embed(games[ctx.channel.id], "NỐI TỪ TIẾNG VIỆT (MULTIPLAYER)"), view=GameControlButtons())

@bot.command(name="noitubot")
async def start_game_vi_bot(ctx):
    if ctx.channel.id in games: return await ctx.send("⚠️ Kênh đang có trận đấu!")
    word = norm(pick_random_vi_word() or "đá bóng")
    games[ctx.channel.id] = {"mode": "vi", "vs_bot": True, "is_duel": False, "last_word": word, "count": 1, "used_words": {word}, "history_list": [word]}
    
    if BANNER_URL and BANNER_URL != "URL_ANH_BANNER_CUA_BAN":
        await ctx.send(BANNER_URL)
    await ctx.send(embed=build_game_embed(games[ctx.channel.id], "NỐI TỪ TIẾNG VIỆT (VS BOT)"), view=GameControlButtons())

@bot.command(name="noitueng")
async def start_game_en(ctx):
    if ctx.channel.id in games: return await ctx.send("⚠️ Kênh đang có trận đấu!")
    word = pick_random_en_word() or "apple"
    games[ctx.channel.id] = {"mode": "en", "vs_bot": False, "is_duel": False, "last_word": word, "count": 1, "used_words": {word}, "history_list": [word]}
    
    if BANNER_URL and BANNER_URL != "URL_ANH_BANNER_CUA_BAN":
        await ctx.send(BANNER_URL)
    await ctx.send(embed=build_game_embed(games[ctx.channel.id], "ENGLISH WORD CHAIN (MULTIPLAYER)"), view=GameControlButtons())

@bot.command(name="noituboteng")
async def start_game_en_bot(ctx):
    if ctx.channel.id in games: return await ctx.send("⚠️ Kênh đang có trận đấu!")
    word = pick_random_en_word() or "apple"
    games[ctx.channel.id] = {"mode": "en", "vs_bot": True, "is_duel": False, "last_word": word, "count": 1, "used_words": {word}, "history_list": [word]}
    
    if BANNER_URL and BANNER_URL != "URL_ANH_BANNER_CUA_BAN":
        await ctx.send(BANNER_URL)
    await ctx.send(embed=build_game_embed(games[ctx.channel.id], "ENGLISH WORD CHAIN (VS BOT)"), view=GameControlButtons())

@bot.command(name="huynoitu")
async def stop_game(ctx):
    if ctx.channel.id in games:
        del games[ctx.channel.id]
        await ctx.send(embed=discord.Embed(description="🛑 Đã hủy trận đấu tại kênh này.", color=COLOR_ERROR))
    else:
        await ctx.send("❌ Không có trận đấu nào đang diễn ra ở kênh này.")

# --- 📩 XỬ LÝ SỰ KIỆN TIN NHẮN ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    await bot.process_commands(message)
    if message.channel.id not in games or message.content.startswith("?"): return
    
    game = games[message.channel.id]
    user_input = message.content.strip().lower()

    if game.get("is_duel"):
        players = game["players"]
        if message.author.id != players[game["turn_idx"]]: return
        text = norm(user_input)
        words = text.split()
        prev_last = norm(game["last_word"].split()[-1])

        if len(words) != 2 or words[0] != prev_last or text in game["used_words"] or not is_valid_vietnamese_word(text):
            loser_name = message.author.display_name
            winner_name = game["p2_name"] if game["turn_idx"] == 0 else game["p1_name"]
            winner_id = players[1 - game["turn_idx"]]
            update_user_stats(message.author.id, loss=True)
            update_user_stats(winner_id, win=True)
            await message.channel.send(embed=discord.Embed(title=f"🏆 {winner_name.upper()} CHIẾN THẮNG 1V1!", description=f"`- {loser_name} đã gõ sai từ!`", color=COLOR_SUCCESS))
            del games[message.channel.id]
            return

        game["used_words"].add(text); game["history_list"].append(text); game["last_word"] = text; game["count"] += 1
        update_user_stats(message.author.id, added_words=1)
        game["turn_idx"] = 1 - game["turn_idx"]
        await message.channel.send(embed=build_game_embed(game, "⚔️ ĐẠI CHIẾN NỐI TỪ 1V1"))
        return

    if game["mode"] == "vi":
        text = norm(user_input)
        words = text.split()
        prev_last = norm(game["last_word"].split()[-1])

        if len(words) != 2 or words[0] != prev_last or text in game["used_words"] or not is_valid_vietnamese_word(text):
            await message.add_reaction(EMOJI_CROSS)
            return

        game["used_words"].add(text); game["history_list"].append(text); game["last_word"] = text; game["count"] += 1
        update_user_stats(message.author.id, added_words=1)
        await message.add_reaction(EMOJI_TICK)

        if game["vs_bot"]:
            bot_word = pick_random_vi_word(prefix=words[-1], used_words=game["used_words"])
            if bot_word:
                game["used_words"].add(bot_word); game["history_list"].append(bot_word); game["last_word"] = bot_word; game["count"] += 1
                await message.channel.send(embed=build_game_embed(game, "NỐI TỪ TIẾNG VIỆT (VS BOT)", last_player_name="🤖 Bot Trí Tuệ"))
            else:
                update_user_stats(message.author.id, win=True)
                await message.channel.send(embed=discord.Embed(title="🏆 BẠN ĐÃ THẮNG BOT!", description="Bot đã cạn kiệt từ vựng!", color=COLOR_SUCCESS))
                del games[message.channel.id]
        else:
            await message.channel.send(embed=build_game_embed(game, "NỐI TỪ TIẾNG VIỆT", last_player_name=message.author.display_name))

    elif game["mode"] == "en":
        last_char = game["last_word"][-1].lower()
        if not user_input.startswith(last_char) or user_input in game["used_words"] or not is_valid_english_word(user_input):
            await message.add_reaction(EMOJI_CROSS)
            return

        game["used_words"].add(user_input); game["history_list"].append(user_input); game["last_word"] = user_input; game["count"] += 1
        update_user_stats(message.author.id, added_words=1)
        await message.add_reaction(EMOJI_TICK)

        if game["vs_bot"]:
            bot_word = pick_random_en_word(letter=user_input[-1], used_words=game["used_words"])
            if bot_word:
                game["used_words"].add(bot_word); game["history_list"].append(bot_word); game["last_word"] = bot_word; game["count"] += 1
                await message.channel.send(embed=build_game_embed(game, "ENGLISH WORD CHAIN (VS BOT)", last_player_name="🤖 English Bot"))
            else:
                update_user_stats(message.author.id, win=True)
                await message.channel.send(embed=discord.Embed(title="🏆 YOU BEAT THE BOT!", description="Bot ran out of English words!", color=COLOR_SUCCESS))
                del games[message.channel.id]
        else:
            await message.channel.send(embed=build_game_embed(game, "ENGLISH WORD CHAIN", last_player_name=message.author.display_name))

try: keep_alive()
except: pass
bot.run(os.getenv("DISCORD_TOKEN"))
