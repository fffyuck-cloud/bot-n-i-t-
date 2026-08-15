import os
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

TICK = "<:Screenshot20260812172055:1537043520790073424>"
CROSS = "<:Screenshot20260812173722:1537047895310602300>"

try:
    font_large = ImageFont.load_default(size=22)
    font_medium = ImageFont.load_default(size=18)
    font_small = ImageFont.load_default(size=14)
except Exception:
    font_large = font_medium = font_small = ImageFont.load_default()

def norm(text: str) -> str:
    if not text: return ""
    text = unicodedata.normalize('NFC', str(text).lower().strip())
    text = re.sub(r'[^\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def prepare_dictionaries():
    default_words_vi = {
        "học sinh", "sinh viên", "sinh hoạt", "sinh học", "bài học", "bài tập", "bài bản",
        "thể thao", "thể hình", "bóng đá", "đá bóng", "bóng chuyền", "chuyền bóng",
        "cầu lông", "lông gà", "nhà cửa", "cửa sổ", "sổ tay", "tay chân", "chân thành", 
        "thành phố", "phố phường", "phường xã", "xã hội", "hội ngộ", "ngộ nghĩnh", 
        "sách vở", "vở bài", "ghi bàn", "bàn ghế", "ghế đá", "tập thể", "hình ảnh", 
        "máy tính", "tính toán", "toán học", "học hành", "hành động", "động lực", 
        "lực lượng", "lượng mưa", "mưa gió", "gió bão", "bão tố", "tố cáo", "cáo trạng", 
        "trạng thái", "thái độ", "độ ẩm", "ẩm thực", "thực phẩm", "phẩm chất", "chất lượng", 
        "lượng từ", "từ vựng", "phát triển", "triển khai", "khai thác", "thác nước", 
        "nước ngọt", "ngọt ngào", "ngào ngạt", "ngạt thở", "thở dài", "dài lâu", "lâu đời", 
        "đời sống", "sống ảo", "ảo tưởng", "tưởng tượng", "tượng đài", "phát thanh", 
        "thanh niên", "hạn chế", "chế độ", "độ bền", "bền vững", "vững chắc", "chắc chắn", 
        "rõ ràng", "ràng buộc", "buộc tội", "tội lỗi", "lỗi lầm", "nhịp nhàng", "anh em", 
        "em út", "nam thanh", "thanh tú", "tài năng", "kinh tế", "tế nhị", "vị trí", 
        "trí tuệ", "cán bộ", "bộ đội", "đội trưởng", "trưởng thành", "thành đạt", 
        "được mùa", "mùa màng", "mục tiêu", "tiêu cực", "kỳ diệu", "kỳ quan", "quan sát", 
        "phạt đền", "đền ơn", "ơn huệ", "ơn nghĩa", "nghĩa vụ", "vụ án", "án mạng", 
        "mạng sống", "sống chết", "mỏ neo", "neo đậu", "đậu phộng", "rang lạc", "lạc quan", 
        "quan hệ", "hệ trọng", "trọng điểm", "trọng trách", "trọng tài", "trọng tâm", 
        "trọng đại", "tiểu đường", "đường đi", "đi đứng", "đương thời", "hệ lụy", "lụy tình", 
        "hệ thống", "thống nhất", "thống kê", "hệ quả", "quả cảm", "quả tang", "khoa học", 
        "địa lý", "lịch sử", "tự nhiên", "văn hóa", "giáo dục", "y tế", "kho tàng", 
        "ông bà", "cha mẹ", "mẹ hiền", "mẹ ghẻ", "mẹ đẻ", "mẹ con", "bạn bè", "thầy cô", 
        "trường lớp", "cây cối", "hoa quả", "động vật", "thực vật", "mây gió", "núi non", 
        "biển cả", "mặt trời", "mặt trăng", "ngôi sao", "không gian", "thời gian", "quá khứ", 
        "tương lai", "hiện tại", "ngày đêm", "năm tháng", "tuần lễ", "buổi sáng", "trưa chiều", 
        "tối đêm", "mùa xuân", "mùa hạ", "mùa thu", "mùa đông"
    }

    words_vi = set(default_words_vi)
    if os.path.exists("words.txt"):
        try:
            with open("words.txt", "r", encoding="utf-8") as f:
                for line in f:
                    w = norm(line.replace("_", " "))
                    if w: words_vi.add(w)
            print(f"Đã nạp {len(words_vi)} từ tiếng Việt từ file.")
        except Exception as e:
            print(f"Lỗi đọc file words.txt: {e}")
    else:
        try:
            with open("words.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(sorted(words_vi)))
        except: pass

    words_en = {"lol", "omg", "btw", "asap", "fyi", "gg", "idk", "tbh", "imo", "imho", 
                "rip", "afk", "brb", "gn", "gm", "np", "thx", "ty", "wth", "wtf", 
                "yolo", "pro", "ez", "bro", "sis", "bae", "flex", "stfu", "dm", "pm",
                "apple", "banana", "cat", "dog", "egg", "game", "python", "discord",
                "network", "system", "coding", "server", "channel", "message", "bot"}
    
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
    draw.rectangle([5, 5, 595, 195], outline="#FF0055", width=3)
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
    draw.ellipse((38, 43, 152, 157), outline="#FF0055", width=4)
    draw.text((170, 45), f"{member.display_name}", fill="#ffffff", font=font_large)
    draw.text((170, 75), f"@{member.user.username}", fill="#a0a0ab", font=font_small)
    draw.text((450, 45), f"RANK #{data['rank']}", fill="#FF0055", font=font_large)
    draw.text((450, 75), f"LVL {data['level']}", fill="#ffffff", font=font_medium)
    xp_needed = data["level"] * 300
    progress = min(data["xp"] / xp_needed, 1.0)
    draw.rounded_rectangle([170, 120, 560, 142], radius=11, fill="#1a1a24")
    if progress > 0:
        draw.rounded_rectangle([170, 120, 170 + int(390 * progress), 142], radius=11, fill="#FF0055")
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
    draw.rectangle([5, 5, 595, 195], outline="#FF0055", width=3)
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
    print(f"Bot {bot.user.name} online!")

@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(title="✦ HỆ THỐNG TRỢ GIÚP NỐI TỪ ✦", color=0xFF0055)
    embed.description = (
        "💬 **Word Chain Ultimate Bot**\n\n"
        "🇻🇳 **NỐI TỪ TIẾNG VIỆT (2 TỪ)**\n"
        "`?noitu` → Chơi chung kênh\n"
        "`?noituubot` → Solo với AI\n\n"
        "🇬🇧 **NỐI TỪ TIẾNG ANH (1 TỪ)**\n"
        "`?noitueng` → Chơi chung kênh tiếng Anh\n"
        "`?noituuboteng` → Solo tiếng Anh với AI\n\n"
        "⚙️ **CÔNG CỤ**\n"
        "`?huynoitu` → Hủy ván chơi\n"
        "`?nghia [từ]` → Tra cứu từ điển\n"
        "`?rank` & `?daily` → Xem cấp độ & điểm danh"
    )
    await ctx.send(embed=embed)

@bot.command(name="rank")
async def rank_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = get_user_data(member.id)
    file = await create_rank_card(member, data)
    embed = discord.Embed(title=f"📊 HỒ SƠ XẾP HẠNG: {member.display_name.upper()}", color=0xFF0055)
    embed.set_image(url="attachment://rank.png")
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
    embed = discord.Embed(title="🎁 ĐIỂM DANH HẰNG NGÀY", color=0xFF0055)
    embed.set_image(url="attachment://daily.png")
    await ctx.send(embed=embed, file=file)

@bot.command(name="noitu")
async def start_noitu(ctx):
    if ctx.channel.id in games: 
        return await ctx.send(embed=discord.Embed(title="⚠️ THÔNG BÁO", description=f"{CROSS} Kênh này đang có ván chơi diễn ra rồi!", color=0xED4245))
    word = random.choice(list(dictionary_vi))
    games[ctx.channel.id] = {"mode": "vi_multi", "last_word": word, "used_words": {word}}
    embed = discord.Embed(title="🇻🇳 NỐI TỪ TIẾNG VIỆT", color=0xFF0055)
    embed.description = f"🎯 **TỪ KHÓA:** 👉 **`{word.upper()}`**\n⚡ Âm tiết tiếp theo: **{word.split()[-1].upper()}**"
    await ctx.send(embed=embed)

@bot.command(name="noituubot")
async def start_game_vi_bot(ctx):
    if ctx.channel.id in games: 
        return await ctx.send(embed=discord.Embed(title="⚠️ THÔNG BÁO", description=f"{CROSS} Kênh này đang có ván chơi diễn ra rồi!", color=0xED4245))
    word = random.choice(list(dictionary_vi))
    games[ctx.channel.id] = {"mode": "vi_bot", "last_word": word, "used_words": {word}}
    embed = discord.Embed(title="🤖 SOLO TIẾNG VIỆT VỚI AI", color=0xFF0055)
    embed.description = f"🎯 **TỪ KHÓA:** 👉 **`{word.upper()}`**\n⚡ Âm tiết tiếp theo: **{word.split()[-1].upper()}**"
    await ctx.send(embed=embed)

@bot.command(name="noitueng")
async def start_game_en(ctx):
    if ctx.channel.id in games: 
        return await ctx.send(embed=discord.Embed(title="⚠️ THÔNG BÁO", description=f"{CROSS} Kênh này đang có ván chơi diễn ra rồi!", color=0xED4245))
    word = random.choice(list(dictionary_en))
    games[ctx.channel.id] = {"mode": "en_multi", "last_word": word, "used_words": {word}}
    embed = discord.Embed(title="🇬🇧 NỐI TỪ TIẾNG ANH", color=0xFF0055)
    embed.description = f"🎯 **TỪ KHÓA:** 👉 **`{word.upper()}`**\n⚡ Ký tự tiếp theo: **{word[-1].upper()}**"
    await ctx.send(embed=embed)

@bot.command(name="noituuboteng")
async def start_game_en_bot(ctx):
    if ctx.channel.id in games: 
        return await ctx.send(embed=discord.Embed(title="⚠️ THÔNG BÁO", description=f"{CROSS} Kênh này đang có ván chơi diễn ra rồi!", color=0xED4245))
    word = random.choice(list(dictionary_en))
    games[ctx.channel.id] = {"mode": "en_bot", "last_word": word, "used_words": {word}}
    embed = discord.Embed(title="🤖 SOLO TIẾNG ANH VỚI AI", color=0xFF0055)
    embed.description = f"🎯 **TỪ KHÓA:** 👉 **`{word.upper()}`**\n⚡ Ký tự tiếp theo: **{word[-1].upper()}**"
    await ctx.send(embed=embed)

@bot.command(name="huynoitu")
async def stop_game(ctx):
    if ctx.channel.id in games:
        del games[ctx.channel.id]
        await ctx.send(embed=discord.Embed(title="⚙️ HỦY BỎ TRẬN ĐẤU", description=f"{TICK} Đã hủy ván chơi.", color=0xED4245))
    else:
        await ctx.send(embed=discord.Embed(title="⚙️ HỦY BỎ TRẬN ĐẤU", description=f"{CROSS} Không có ván nào đang chạy!", color=0xED4245))

@bot.command(name="nghia")
async def nghia_cmd(ctx, *, word: str = None):
    if not word: return await ctx.send("Vui lòng nhập từ cần tra!")
    w = word.strip().lower()
    if w in dictionary_vi or w in dictionary_en:
        await ctx.send(f"{TICK} Từ **`{w}`** hợp lệ và có trong từ điển!")
    else:
        await ctx.send(f"{CROSS} Không tìm thấy từ **`{w}`** trong hệ thống!")

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
            return await message.add_reaction(CROSS)
            
        game["used_words"].add(user_input)
        game["last_word"] = user_input
        await message.add_reaction(TICK)
        
        if mode == "vi_bot":
            last_syllable = user_input.split()[-1]
            possible_words = [w for w in dictionary_vi if w.startswith(last_syllable + " ") and w not in game["used_words"]]
            if not possible_words:
                await message.channel.send(f"🏆 {message.author.mention} chiến thắng bot vì bot đã bí từ!")
                del games[message.channel.id]
            else:
                bot_word = random.choice(possible_words)
                game["used_words"].add(bot_word)
                game["last_word"] = bot_word
                await message.channel.send(f"🤖 Bot nối tiếp: 👉 **`{bot_word.upper()}`**")

    elif mode in ["en_multi", "en_bot"]:
        w = user_input
        prev_char = game["last_word"][-1]
        if len(w.split()) != 1 or not (w.isascii() and w.isalpha()) or w[0] != prev_char or w in game["used_words"] or w not in dictionary_en:
            return await message.add_reaction(CROSS)
            
        game["used_words"].add(w)
        game["last_word"] = w
        await message.add_reaction(TICK)
        
        if mode == "en_bot":
            last_char = w[-1]
            possible_words = [word for word in dictionary_en if word.startswith(last_char) and word not in game["used_words"]]
            if possible_words:
                bot_word = random.choice(possible_words)
                game["used_words"].add(bot_word)
                game["last_word"] = bot_word
                await message.channel.send(f"🤖 Bot nối tiếp: 👉 **`{bot_word.upper()}`**")
            else:
                await message.channel.send(f"🏆 {message.author.mention} chiến thắng bot vì hết từ tiếng Anh!")
                del games[message.channel.id]

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
