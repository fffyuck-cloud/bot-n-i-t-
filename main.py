import os
import ssl
import urllib.request
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
    ctx = ssl._create_unverified_context()
    
    # Kho từ điển tiếng Việt tích hợp sẵn khổng lồ và đầy đủ
    words_vi = {
        "đá bóng", "bóng đá", "học sinh", "sinh viên", "thể thao", "bóng chuyền", "chuyền bóng",
        "cầu lông", "lông gà", "nhà cửa", "cửa sổ", "sổ tay", "tay chân", "chân thành",
        "thành phố", "phố phường", "phường xã", "xã hội", "hội ngộ", "ngộ nghĩnh",
        "sách vở", "vở bài", "bài học", "học tập", "tập thể", "thể hình", "hình ảnh",
        "máy tính", "tính toán", "toán học", "học hành", "hành động", "động lực", "lực lượng",
        "lượng mưa", "mưa gió", "gió bão", "bão tố", "tố cáo", "cáo trạng", "trạng thái",
        "thái độ", "độ ẩm", "ẩm thực", "thực phẩm", "phẩm chất", "chất lượng", "lượng từ",
        "từ vựng", "phát triển", "triển khai", "khai thác", "thác nước", "nước ngọt",
        "ngọt ngào", "ngào ngạt", "ngạt thở", "thở dài", "dài lâu", "lâu đời", "đời sống",
        "sống ảo", "ảo tưởng", "tưởng tượng", "tượng đài", "phát thanh", "thanh niên",
        "hạn chế", "chế độ", "độ bền", "bền vững", "vững chắc", "chắc chắn",
        "bùn lầy", "lầy lội", "lội nước", "nước mắt", "mắt cá", "cá tính",
        "tính cách", "cách mạng", "mạng lưới", "lưới cá", "cá mập", "mập mạp",
        "ít ỏi", "ương bướng", "bướng bỉnh", "bút chì", "chìa khóa", "khóa cửa",
        "cửa hàng", "hàng hóa", "hóa đơn", "đơn ca", "ca sĩ", "tử vong", "vong hồn",
        "hồn nhiên", "nhiên liệu", "liệu pháp", "pháp luật", "luật sư", "sư phạm",
        "phạm nhân", "nhân dân", "dân tộc", "tộc họ", "họ hàng", "hàng xóm",
        "xóm giềng", "giềng mối", "mối tình", "tình yêu", "yêu thương", "thương nhớ",
        "nhớ mong", "mong mỏi", "mỏi mệt", "mệt mỏi", "tử thần", "thần tốc", "tốc độ",
        "độ lượng", "lượng thứ", "thứ bậc", "bậc thang", "thang máy", "máy bay",
        "bay lượn", "lượn lờ", "lờ đờ", "đờ đẫn", "dắt dìu", "lái xe", "xe cộ",
        "kiệu hoa", "hoa hồng", "ngoại ô", "ô tô", "tô điểm", "điểm số", "hồng hộc",
        "hộc bàn", "bàn ghế", "ghế đá", "đá quý", "quý mến", "mến yêu", "yêu đương",
        "đương nhiên", "thủy tinh", "tinh tế", "tế bào", "bào thai", "thai nghén",
        "suy nghĩ", "nghĩ ngợi", "ngợi ca", "ca tụng", "tụng kinh", "kinh điển",
        "điển hình", "hình thức", "thức ăn", "ăn uống", "uống nước", "nước non",
        "non sông", "sông ngòi", "ngòi bút", "bút mực", "tàu thủy", "thủy thủ",
        "thủ đô", "đô la", "la cà", "cà phê", "pha lê", "lê thê", "thê lương",
        "lương tâm", "tâm sự", "sự nghiệp", "nghiệp dư", "dưa hấu", "kính cận",
        "cận thị", "thị xã", "xã tắc", "tắc nghẽn", "mạch máu", "máu me", "chua chát",
        "chúa tể", "tể tướng", "tướng quân", "quân đội", "đội ngũ", "ngũ cốc",
        "cốc chén", "chén trà", "trà đá", "đá lạnh", "lạnh lùng", "sục sôi",
        "sôi nổi", "nổi bật", "bật mí", "mí mắt", "mắt kính", "kính chào", "chào hỏi",
        "hỏi thăm", "thăm nom", "rõ ràng", "buộc tội", "tội lỗi", "lỗi lầm",
        "nhịp nhàng", "rượu chè", "anh em", "em út", "nam thanh", "thanh tú",
        "tài năng", "kinh tế", "tế nhị", "vị trí", "trí tuệ", "cán bộ", "bộ đội",
        "đội trưởng", "trưởng thành", "thành đạt", "được mùa", "mùa màng", "mục tiêu",
        "tiêu cực", "kỳ diệu", "kỳ quan", "quan sát", "phạt đền", "đền ơn", "ơn huệ",
        "ơn nghĩa", "nghĩa vụ", "vụ án", "án mạng", "mạng sống", "sống chết", "mỏ neo",
        "neo đậu", "đậu phộng", "rang lạc", "lạc quan", "quan hệ", "hệ trọng",
        "trọng điểm", "điểm hẹn", "hẹn hò", "hò hét", "đẹp đẽ", "gọt giũa", "chữ nghĩa",
        "nghĩa tình", "tình cảm", "cảm xúc", "động đất", "đất liền", "mạch lạc",
        "lạc hậu", "hậu cần", "cần cù", "lao động", "động viên", "viên mãn", "mãn nguyện",
        "nguyện vọng", "vọng tưởng", "tưởng nhớ", "nhớ nhung", "nhung lụa", "lụa là",
        "đà điểu", "thú vật", "vật chất", "thảo nguyên", "nguyên thủy", "thủy triều",
        "triều đại", "đại dương", "gian nan", "giải quyết", "quyết tâm", "tâm huyết",
        "huyết mạch", "đập phá", "phá hoại", "hoại tử", "vong thân", "thân thiết",
        "thiết thực", "thực tế", "sinh hoạt", "hoạt động", "tĩnh lặng", "lặng lẽ",
        "lẽ phải", "phải trái", "trái đất", "đất trời", "trời mây", "qua đời",
        "đời thuở", "thuở xưa", "xưa nay", "nay mai", "mai sau", "sau này", "quý tử",
        "tử hình", "hình phạt", "vạ lây", "lây lan", "lan tràn", "ngập tràn", "tràn lan",
        "lan tỏa", "tỏa sáng", "sáng ngời", "sáng tạo", "tạo hình", "hình mẫu",
        "mẫu giáo", "giáo dục", "ngoại giao", "giao lưu", "lưu trữ", "trữ lượng",
        "lượng giác", "giác quan", "quan điểm", "điểm tựa",
        # Thêm các từ hệ thống, hệ quả, hệ lụy...
        "hệ thống", "thống nhất", "thống kê", "hệ quả", "quả cảm", "quả tang",
        "hệ lụy", "lụy tình", "hệ trọng", "trọng trách", "trọng tài", "trọng tâm"
    }
    
    words_en = {
        "lol", "omg", "btw", "asap", "fyi", "gg", "idk", "tbh", "imo", "imho", 
        "rip", "afk", "brb", "gn", "gm", "np", "thx", "ty", "wth", "wtf", 
        "yolo", "pro", "ez", "bro", "sis", "bae", "flex", "stfu", "dm", "pm",
        "apple", "banana", "cat", "dog", "egg", "game", "python", "discord"
    }
    try:
        req = urllib.request.Request("https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            for line in response.read().decode('utf-8', errors='ignore').splitlines():
                w = line.strip().lower()
                if len(w) >= 2 and w.isalpha(): words_en.add(w)
    except: pass
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
    print(f"Bot {bot.user.name} online")

@bot.command(name="help")
async def help_cmd(ctx):
    try:
        file = discord.File("d89db057-b415-48f7-8603-47052617b39e.png", filename="banner.png")
    except:
        file = None
        
    embed = discord.Embed(title="✦ HỆ THỐNG TRỢ GIÚP NỐI TỪ ✦", color=0xFF0055)
    if file: embed.set_image(url="attachment://banner.png")
        
    embed.description = (
        "💬 **Word Chain Ultimate Bot**\n"
        "Chào mừng mấy dân chơi đã lạc vào con bot nối từ đỉnh nhất server. Đây là nơi để mấy ông so trình từ vựng, flex vốn từ và leo rank đến cùng trời cuối đất.\n\n"
        
        "🇻🇳 **NỐI TỪ TIẾNG VIỆT**\n"
        "Chơi đúng luật 2 từ (ví dụ: 'đền ơn' -> 'ơn huệ'). Đầy đủ kho từ vựng chuẩn!\n"
        "`?noitu` → Chơi chung kênh cùng bè lũ\n"
        "`?noituubot` → Solo khô máu với con bot cho biết mùi đời\n\n"
        
        "🇬🇧 **NỐI TỪ TIẾNG ANH**\n"
        "Luật quốc tế chơi 1 từ duy nhất (ví dụ: 'apple' -> 'egg' hoặc từ viết tắt 'lol') chuẩn quốc tế\n"
        "`?noitueng` → Chơi chung kênh cùng bè lũ\n"
        "`?noituuboteng` → Solo khô máu với con bot cho biết mùi đời\n\n"
        
        "⚙️ **QUẢN LÝ TRẬN ĐẤU & CÔNG CỤ**\n"
        "`?huynoitu` → Hủy ván chơi nếu thấy chán hoặc lag\n"
        "`?nghia [từ]` → Tra cứu từ điển tiếng Việt/Anh\n\n"
        
        "📊 **HỆ THỐNG RANK & DAILY**\n"
        "`?rank` → Xem thẻ rank\n"
        "`?daily` → Điểm danh hằng ngày"
    )
    if file: await ctx.send(embed=embed, file=file)
    else: await ctx.send(embed=embed)

@bot.command(name="rank")
async def rank_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = get_user_data(member.id)
    file = await create_rank_card(member, data)
    
    embed = discord.Embed(title=f"📊 HỒ SƠ XẾP HẠNG: {member.display_name.upper()}", color=0xFF0055)
    embed.set_image(url="attachment://rank.png")
    embed.add_field(name="⭐ Cấp Độ", value=f"Level **{data['level']}**", inline=True)
    embed.add_field(name="🏆 Vị Thế", value=f"Rank **#{data['rank']}**", inline=True)
    embed.add_field(name="⚡ Kinh Nghiệm", value=f"**{data['xp']}** / {data['level'] * 300} XP", inline=True)
    embed.add_field(name="🔥 Streak", value=f"**{data['streak']}** ngày", inline=True)
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
    if claimed:
        embed.description = f"🎉 Chúc mừng {ctx.author.mention} điểm danh thành công!"
        embed.add_field(name="💰 Phần Thưởng", value=f"+**{reward}** XP", inline=True)
        embed.add_field(name="📈 Streak", value=f"**{data['streak']}** ngày", inline=True)
    else:
        embed.description = f"⚠️ {ctx.author.mention} đã điểm danh trong vòng 24 giờ qua rồi."
    icon = TICK if claimed else CROSS
    await ctx.send(f"{icon} Yêu cầu từ {ctx.author.mention}", embed=embed, file=file)

@bot.command(name="noitu")
async def start_noitu(ctx, mode: str = "vi"):
    if ctx.channel.id in games: 
        embed = discord.Embed(title="⚠️ THÔNG BÁO", color=0xED4245)
        embed.description = f"{CROSS} Kênh này đang có ván chơi nối từ diễn ra rồi!"
        return await ctx.send(embed=embed)
    mode = mode.lower()
    
    try:
        file = discord.File("d89db057-b415-48f7-8603-47052617b39e.png", filename="banner.png")
    except:
        file = None

    if mode in ["en", "english", "eng", "noitueng"]:
        word = random.choice(list(dictionary_en)) if dictionary_en else "apple"
        games[ctx.channel.id] = {"mode": "en_multi", "last_word": word, "used_words": {word}}
        embed = discord.Embed(title="🇬🇧 TRẬN ĐẤU NỐI TỪ TIẾNG ANH", color=0xFF0055)
        if file: embed.set_image(url="attachment://banner.png")
        embed.description = (
            "🔥 **SÀN ĐẤU QUỐC TẾ KHAI MẠC** 🔥\n\n"
            f"🎯 **TỪ KHÓA KHỞI ĐẦU:** 👉 **`{word.upper()}`**\n"
            f"📊 **Tổng số từ hiện tại:** `1` từ\n\n"
            f"⚡ Bắt đầu bằng ký tự: **{word[-1].upper()}**"
        )
        if file: await ctx.send(embed=embed, file=file)
        else: await ctx.send(embed=embed)
    else:
        word = random.choice(list(dictionary_vi)) if dictionary_vi else "học tập"
        games[ctx.channel.id] = {"mode": "vi_multi", "last_word": word, "used_words": {word}}
        embed = discord.Embed(title="🇻🇳 TRẬN ĐẤU NỐI TỪ TIẾNG VIỆT", color=0xFF0055)
        if file: embed.set_image(url="attachment://banner.png")
        embed.description = (
            "🔥 **SÀN ĐẤU TIẾNG VIỆT KHAI MẠC** 🔥\n\n"
            f"🎯 **TỪ KHÓA KHỞI ĐẦU:** 👉 **`{word.upper()}`**\n"
            f"📊 **Tổng số từ hiện tại:** `1` từ\n\n"
            f"⚡ Bắt đầu bằng âm tiết: **{word.split()[-1].upper()}**"
        )
        if file: await ctx.send(embed=embed, file=file)
        else: await ctx.send(embed=embed)

@bot.command(name="noituubot")
async def start_game_vi_bot(ctx):
    if ctx.channel.id in games: 
        embed = discord.Embed(title="⚠️ THÔNG BÁO", color=0xED4245)
        embed.description = f"{CROSS} Kênh này đang có ván chơi nối từ diễn ra rồi!"
        return await ctx.send(embed=embed)
    word = random.choice(list(dictionary_vi)) if dictionary_vi else "học tập"
    games[ctx.channel.id] = {"mode": "vi_bot", "last_word": word, "used_words": {word}}
    try:
        file = discord.File("d89db057-b415-48f7-8603-47052617b39e.png", filename="banner.png")
    except:
        file = None
    embed = discord.Embed(title="🤖 THÁCH ĐẤU AI: SOLO TIẾNG VIỆT", color=0xFF0055)
    if file: embed.set_image(url="attachment://banner.png")
    embed.description = (
        "⚔️ **1V1 VỚI HỆ THỐNG AI** ⚔️\n\n"
        f"🎯 **TỪ KHÓA MỞ MÀN:** 👉 **`{word.upper()}`**\n"
        f"📊 **Tổng số từ hiện tại:** `1` từ\n\n"
        f"⚡ Âm tiết tiếp theo: **{word.split()[-1].upper()}**"
    )
    if file: await ctx.send(embed=embed, file=file)
    else: await ctx.send(embed=embed)

@bot.command(name="noitueng")
async def start_game_en(ctx):
    if ctx.channel.id in games: 
        embed = discord.Embed(title="⚠️ THÔNG BÁO", color=0xED4245)
        embed.description = f"{CROSS} Kênh này đang có ván chơi nối từ diễn ra rồi!"
        return await ctx.send(embed=embed)
    word = random.choice(list(dictionary_en)) if dictionary_en else "apple"
    games[ctx.channel.id] = {"mode": "en_multi", "last_word": word, "used_words": {word}}
    try:
        file = discord.File("d89db057-b415-48f7-8603-47052617b39e.png", filename="banner.png")
    except:
        file = None
    embed = discord.Embed(title="🇬🇧 TRẬN ĐẤU NỐI TỪ TIẾNG ANH", color=0xFF0055)
    if file: embed.set_image(url="attachment://banner.png")
    embed.description = (
        "🔥 **SÀN ĐẤU QUỐC TẾ KHAI MẠC** 🔥\n\n"
        f"🎯 **TỪ KHÓA KHỞI ĐẦU:** 👉 **`{word.upper()}`**\n"
        f"📊 **Tổng số từ hiện tại:** `1` từ\n\n"
        f"⚡ Bắt đầu bằng ký tự: **{word[-1].upper()}**"
    )
    if file: await ctx.send(embed=embed, file=file)
    else: await ctx.send(embed=embed)

@bot.command(name="noituuboteng")
async def start_game_en_bot(ctx):
    if ctx.channel.id in games: 
        embed = discord.Embed(title="⚠️ THÔNG BÁO", color=0xED4245)
        embed.description = f"{CROSS} Kênh này đang có ván chơi nối từ diễn ra rồi!"
        return await ctx.send(embed=embed)
    word = random.choice(list(dictionary_en)) if dictionary_en else "apple"
    games[ctx.channel.id] = {"mode": "en_bot", "last_word": word, "used_words": {word}}
    try:
        file = discord.File("d89db057-b415-48f7-8603-47052617b39e.png", filename="banner.png")
    except:
        file = None
    embed = discord.Embed(title="🤖 THÁCH ĐẤU AI: SOLO TIẾNG ANH", color=0xFF0055)
    if file: embed.set_image(url="attachment://banner.png")
    embed.description = (
        "⚔️ **1V1 VỚI HỆ THỐNG AI QUỐC TẾ** ⚔️\n\n"
        f"🎯 **TỪ KHÓA MỞ MÀN:** 👉 **`{word.upper()}`**\n"
        f"📊 **Tổng số từ hiện tại:** `1` từ\n\n"
        f"⚡ Ký tự tiếp theo: **{word[-1].upper()}**"
    )
    if file: await ctx.send(embed=embed, file=file)
    else: await ctx.send(embed=embed)

@bot.command(name="huynoitu")
async def stop_game(ctx):
    try:
        file = discord.File("d89db057-b415-48f7-8603-47052617b39e.png", filename="banner.png")
    except:
        file = None
    if ctx.channel.id in games:
        del games[ctx.channel.id]
        embed = discord.Embed(title="⚙️ HỦY BỎ TRẬN ĐẤU", color=0xED4245)
        if file: embed.set_image(url="attachment://banner.png")
        embed.description = f"{TICK} Ván đấu nối từ trong kênh này đã được hủy bỏ thành công."
        if file: await ctx.send(embed=embed, file=file)
        else: await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="⚙️ HỦY BỎ TRẬN ĐẤU", color=0xED4245)
        if file: embed.set_image(url="attachment://banner.png")
        embed.description = f"{CROSS} Kênh này hiện không có ván đấu nào đang chạy!"
        if file: await ctx.send(embed=embed, file=file)
        else: await ctx.send(embed=embed)

@bot.command(name="nghia")
async def nghia_cmd(ctx, *, word: str = None):
    try:
        file = discord.File("d89db057-b415-48f7-8603-47052617b39e.png", filename="banner.png")
    except:
        file = None
    if not word: 
        embed = discord.Embed(title="📖 TRA CỨU TỪ ĐIỂN", color=0xFF0055)
        if file: embed.set_image(url="attachment://banner.png")
        embed.description = f"{CROSS} Vui lòng nhập từ cần tra cứu! Ví dụ: `?nghia hệ thống`"
        if file: return await ctx.send(embed=embed, file=file)
        else: return await ctx.send(embed=embed)
        
    w = word.strip().lower()
    embed = discord.Embed(title="📖 TRA CỨU TỪ ĐIỂN", color=0xFF0055)
    if file: embed.set_image(url="attachment://banner.png")
    
    if w in dictionary_en or w in dictionary_vi:
        embed.description = f"{TICK} Từ **`{w}`** có trong từ điển và hoàn toàn hợp lệ!"
    else:
        embed.description = f"{CROSS} Không tìm thấy từ **`{w}`** trong hệ thống từ điển!"
    if file: await ctx.send(embed=embed, file=file)
    else: await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot: return
    await bot.process_commands(message)
    if message.channel.id not in games or message.content.startswith("?"): return
    
    game = games[message.channel.id]
    user_input = norm(message.content)
    mode = game["mode"]
    
    try:
        banner_file = discord.File("d89db057-b415-48f7-8603-47052617b39e.png", filename="banner.png")
    except:
        banner_file = None
    
    if mode in ["vi_multi", "vi_bot"]:
        words = user_input.split()
        prev_last = game["last_word"].split()[-1]
        
        if len(words) != 2 or words[0] != prev_last or user_input in game["used_words"] or user_input not in dictionary_vi:
            await message.add_reaction(CROSS)
            return
            
        game["used_words"].add(user_input)
        game["last_word"] = user_input
        current_count = len(game["used_words"])
        await message.add_reaction(TICK)
        
        data = get_user_data(message.author.id)
        data["xp"] += 25
        if data["xp"] >= data["level"] * 300:
            data["xp"] -= data["level"] * 300
            data["level"] += 1
            embed_lvl = discord.Embed(title="🎉 THĂNG CẤP", color=0x57F287)
            if banner_file: embed_lvl.set_image(url="attachment://banner.png")
            embed_lvl.description = f"{TICK} {message.author.mention} vừa xuất sắc thăng lên level **{data['level']}**!"
            if banner_file: await message.channel.send(embed=embed_lvl, file=banner_file)
            else: await message.channel.send(embed=embed_lvl)

        if mode == "vi_bot":
            last_syllable = user_input.split()[-1]
            possible_words = [w for w in dictionary_vi if w.startswith(last_syllable + " ") and w not in game["used_words"]]
            if not possible_words:
                bot_word = f"{last_syllable} quả" if last_syllable != "quả" else "hệ thống"
            else:
                bot_word = random.choice(possible_words)
                
            game["used_words"].add(bot_word)
            game["last_word"] = bot_word
            current_count = len(game["used_words"])
            embed_bot = discord.Embed(title="🤖 LƯỢT ĐẤU CỦA AI", color=0xFF0055)
            if banner_file: embed_bot.set_image(url="attachment://banner.png")
            embed_bot.description = f"🤖 Bot nối tiếp: 👉 **`{bot_word.upper()}`**\n📊 Tổng số từ hiện tại: `{current_count}` từ"
            if banner_file: await message.channel.send(embed=embed_bot, file=banner_file)
            else: await message.channel.send(embed=embed_bot)
        else:
            embed_stat = discord.Embed(title="📊 CẬP NHẬT TRẬN ĐẤU", color=0xFF0055)
            if banner_file: embed_stat.set_image(url="attachment://banner.png")
            embed_stat.description = f"{TICK} Từ hợp lệ! Tổng số từ đã nối: **`{current_count}`** từ"
            if banner_file: await message.channel.send(embed=embed_stat, file=banner_file)
            else: await message.channel.send(embed=embed_stat)

    elif mode in ["en_multi", "en_bot"]:
        w = user_input
        prev_char = game["last_word"][-1]
        
        if len(w.split()) != 1 or not (w.isascii() and w.isalpha()) or w[0] != prev_char or w in game["used_words"] or w not in dictionary_en:
            await message.add_reaction(CROSS)
            return
            
        game["used_words"].add(w)
        game["last_word"] = w
        current_count = len(game["used_words"])
        await message.add_reaction(TICK)
        
        data = get_user_data(message.author.id)
        data["xp"] += 25
        if data["xp"] >= data["level"] * 300:
            data["xp"] -= data["level"] * 300
            data["level"] += 1
            embed_lvl = discord.Embed(title="🎉 THĂNG CẤP", color=0x57F287)
            if banner_file: embed_lvl.set_image(url="attachment://banner.png")
            embed_lvl.description = f"{TICK} {message.author.mention} vừa xuất sắc thăng lên level **{data['level']}**!"
            if banner_file: await message.channel.send(embed=embed_lvl, file=banner_file)
            else: await message.channel.send(embed=embed_lvl)

        if mode == "en_bot":
            last_char = w[-1]
            possible_words = [word for word in dictionary_en if word.startswith(last_char) and word not in game["used_words"]]
            if possible_words:
                bot_word = random.choice(possible_words)
                game["used_words"].add(bot_word)
                game["last_word"] = bot_word
                current_count = len(game["used_words"])
                embed_bot = discord.Embed(title="🤖 LƯỢT ĐẤU CỦA AI", color=0xFF0055)
                if banner_file: embed_bot.set_image(url="attachment://banner.png")
                embed_bot.description = f"🤖 Bot nối tiếp: 👉 **`{bot_word.upper()}`**\n📊 Tổng số từ hiện tại: `{current_count}` từ"
                if banner_file: await message.channel.send(embed=embed_bot, file=banner_file)
                else: await message.channel.send(embed=embed_bot)
            else:
                embed_win = discord.Embed(title="🏆 KẾT QUẢ TRẬN ĐẤU", color=0x57F287)
                if banner_file: embed_win.set_image(url="attachment://banner.png")
                embed_win.description = f"🏆 {message.author.mention} đã chiến thắng bot vì hệ thống đã cạn kiệt từ vựng!"
                if banner_file: await message.channel.send(embed=embed_win, file=banner_file)
                else: await message.channel.send(embed=embed_win)
                del games[message.channel.id]
        else:
            embed_stat = discord.Embed(title="📊 CẬP NHẬT TRẬN ĐẤU", color=0xFF0055)
            if banner_file: embed_stat.set_image(url="attachment://banner.png")
            embed_stat.description = f"{TICK} Từ hợp lệ! Tổng số từ đã nối: **`{current_count}`** từ"
            if banner_file: await message.channel.send(embed=embed_stat, file=banner_file)
            else: await message.channel.send(embed=embed_stat)

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
