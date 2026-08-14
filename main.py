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
    return re.sub(r'\s+', ' ', text)

def prepare_dictionaries():
    ctx = ssl._create_unverified_context()
    words_vi = {"đá bóng", "bóng đá", "học sinh", "sinh viên", "thể thao"}
    try:
        req = urllib.request.Request("https://raw.githubusercontent.com/NguyenAnhTuan1997/Vietnamese-Dictionary/master/words.txt", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            for line in response.read().decode('utf-8', errors='ignore').splitlines():
                word = norm(line.replace("_", " "))
                if word and len(word.split()) == 2: words_vi.add(word)
    except: pass
    
    words_en = set()
    try:
        req = urllib.request.Request("https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            for line in response.read().decode('utf-8', errors='ignore').splitlines():
                w = line.strip().lower()
                if len(w) >= 2 and w.isalpha(): words_en.add(w)
    except: pass
    return words_vi, words_en

dictionary_vi, dictionary_en = prepare_dictionaries()
VN_CHARS_REGEX = re.compile(r'^[a-zàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]+$')

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
    draw.rectangle([5, 5, 595, 195], outline="#ff007f", width=3)
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
    draw.ellipse((38, 43, 152, 157), outline="#ff007f", width=4)
    draw.text((170, 45), f"{member.display_name}", fill="#ffffff", font=font_large)
    draw.text((170, 75), f"@{member.user.username}", fill="#a0a0ab", font=font_small)
    draw.text((450, 45), f"RANK #{data['rank']}", fill="#ff007f", font=font_large)
    draw.text((450, 75), f"LVL {data['level']}", fill="#ffffff", font=font_medium)
    xp_needed = data["level"] * 300
    progress = min(data["xp"] / xp_needed, 1.0)
    draw.rounded_rectangle([170, 120, 560, 142], radius=11, fill="#1a1a24")
    if progress > 0:
        draw.rounded_rectangle([170, 120, 170 + int(390 * progress), 142], radius=11, fill="#ff007f")
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
    draw.rectangle([5, 5, 595, 195], outline="#ff007f", width=3)
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
    embed = discord.Embed(title="✦ HỆ THỐNG TRỢ GIÚP NỐI TỪ ULTIMATE ✦", color=0xFF007F)
    embed.description = (
        "💬 **Word Chain Ultimate Bot Core**\n"
        "Chào mừng các dân chơi đã truy cập vào hệ thống trò chơi trí tuệ đỉnh cao nhất server. "
        "Bot được tích hợp kho từ vựng khổng lồ cả tiếng Việt lẫn tiếng Anh, hỗ trợ đa chế độ từ chiến đấu tập thể đến solo khô máu với AI.\n"
        "Hãy tham khảo chi tiết toàn bộ danh sách lệnh vận hành dưới đây để làm chủ cuộc chơi!"
    )
    embed.add_field(
        name="🇻🇳 HỆ THỐNG NỐI TỪ TIẾNG VIỆT",
        value=(
            "• `?noitu` hoặc `?noitu vi` → Khởi động bàn đấu chung tiếng Việt (quy chuẩn 2 từ).\n"
            "• `?noituubot` → Thách đấu solo trực tiếp với AI thông minh ở thể loại tiếng Việt."
        ),
        inline=False
    )
    embed.add_field(
        name="🇬🇧 HỆ THỐNG NỐI TỪ TIẾNG ANH",
        value=(
            "• `?noitu en` (hoặc `?noitu eng`) → Khởi động bàn đấu chung tiếng Anh chuẩn quốc tế.\n"
            "• `?noituuboteng` → Thách đấu solo trực tiếp với AI thông minh ở thể loại tiếng Anh."
        ),
        inline=False
    )
    embed.add_field(
        name="⚙️ QUẢN LÝ TRẬN ĐẤU & TRA CỨU",
        value=(
            "• `?huynoitu` → Hủy bỏ ngay lập tức ván đấu đang diễn ra trong kênh hiện tại.\n"
            "• `?nghia [từ]` → Tra cứu từ điển Anh chi tiết để kiểm tra tính hợp lệ của từ vựng."
        ),
        inline=False
    )
    embed.add_field(
        name="📊 HỆ THỐNG CÁ NHÂN HÓA & XQ",
        value=(
            "• `?rank [tag]` → Hiển thị thẻ cấp độ, thanh tiến trình XP và thứ hạng siêu đẹp.\n"
            "• `?daily` → Điểm danh hằng ngày nhận phần thưởng nóng hổi để đua top."
        ),
        inline=False
    )
    embed.set_footer(text="Hệ thống vận hành mượt mà 24/7 • Chúc các dân chơi có những giây phút đấu trí bùng nổ!")
    await ctx.send(embed=embed)

@bot.command(name="rank")
async def rank_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = get_user_data(member.id)
    file = await create_rank_card(member, data)
    
    embed = discord.Embed(title=f"📊 HỒ SƠ XẾP HẠNG CÁ NHÂN: {member.display_name.upper()}", color=0xFF007F)
    embed.description = (
        f"Hồ sơ năng lực của thành viên {member.mention} trong hệ thống trò chơi nối từ.\n"
        "Toàn bộ thông số cấp độ, kinh nghiệm và vị thế trên bảng vàng server được tổng hợp chi tiết dưới thẻ hình ảnh."
    )
    embed.add_field(name="⭐ Cấp Độ (Level)", value=f"Level **{data['level']}**", inline=True)
    embed.add_field(name="🏆 Thứ Hạng Server", value=f"Rank **#{data['rank']}**", inline=True)
    embed.add_field(name="⚡ Tổng Kinh Nghiệm", value=f"**{data['xp']}** XP", inline=True)
    embed.add_field(name="🔥 Chuỗi Hoạt Động", value=f"**{data['streak']}** ngày liên tục", inline=True)
    embed.set_footer(text="Tiếp tục tích cực tham gia nối từ và tương tác để gia tăng điểm XP lên các cấp cao hơn!")
    
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
    
    embed = discord.Embed(
        title="🎁 TRUNG TÂM ĐIỂM DANH QUÀ TẶNG HẰNG NGÀY", 
        color=0x57F287 if claimed else 0xED4245
    )
    if claimed:
        embed.description = (
            f"🎉 Chúc mừng {ctx.author.mention} đã điểm danh thành công phiên làm việc hôm nay!\n"
            "Phần thưởng kinh nghiệm nóng hổi đã được chuyển trực tiếp vào tài khoản cá nhân."
        )
        embed.add_field(name="💰 Quà Tặng Nhận Được", value=f"+**{reward}** XP", inline=True)
        embed.add_field(name="📈 Chuỗi Điểm Danh", value=f"**{data['streak']}** ngày", inline=True)
    else:
        embed.description = (
            f"⚠️ Bình tĩnh nào {ctx.author.mention} ơi! Bạn đã nhận quà điểm danh trong vòng 24 giờ qua rồi.\n"
            "Hãy kiên nhẫn chờ đủ thời gian để quay lại nhận các phần quà giá trị tiếp theo nhé."
        )
        embed.add_field(name="⏱️ Trạng Thái", value="Đang trong thời gian hồi (Cooldown 24h)", inline=False)
    embed.set_footer(text="Duy trì điểm danh đều đặn mỗi ngày giúp hệ số nhân phần thưởng của bạn tăng vọt!")
    
    icon = TICK if claimed else CROSS
    await ctx.send(f"{icon} Yêu cầu từ {ctx.author.mention}", embed=embed, file=file)

@bot.command(name="noitu")
async def start_noitu(ctx, mode: str = "vi"):
    if ctx.channel.id in games: 
        return await ctx.send("kênh đang có ván chơi rồi")
    mode = mode.lower()
    
    if mode in ["en", "english", "eng", "noitueng"]:
        word = "apple"
        games[ctx.channel.id] = {"mode": "en_multi", "last_word": word, "used_words": {word}}
        embed = discord.Embed(title="🇬🇧 TRẬN ĐẤU NỐI TỪ TIẾNG ANH ĐÃ ĐƯỢC KHỞI TẠO", color=0xFF007F)
        embed.description = (
            "🔥 **SÀN ĐẤU NGÔN NGỮ QUỐC TẾ CHÍNH THỨC KHAI MẠC** 🔥\n\n"
            "Chế độ chơi chung kênh tiếng Anh đã kích hoạt thành công!\n"
            "Mọi người cùng nhau tập trung, huy động toàn bộ vốn từ vựng phong phú để tiếp nối chuỗi từ.\n\n"
            f"🎯 **TỪ KHÓA KHỞI ĐẦU TỪ HỆ THỐNG:**\n"
            f"👉 **`{word.upper()}`**\n\n"
            f"⚡ Quy tắc: Nhập từ tiếng Anh tiếp theo bắt đầu bằng ký tự **{word[-1].upper()}**"
        )
        embed.add_field(name="📌 Thể Thức", value="Multiplayer (Nhiều người chơi)", inline=True)
        embed.add_field(name="🎁 Điểm Thưởng", value="+25 XP mỗi từ đúng", inline=True)
        embed.add_field(name="🛡️ Bộ Lọc", value="Kiểm tra từ điển Alpha chuẩn xác", inline=True)
        embed.set_footer(text="Hãy chắc chắn từ của bạn có trong từ điển và chưa từng được sử dụng trước đó!")
        await ctx.send(embed=embed)
    else:
        word = "đá bóng"
        games[ctx.channel.id] = {"mode": "vi_multi", "last_word": word, "used_words": {word}}
        embed = discord.Embed(title="🇻🇳 TRẬN ĐẤU NỐI TỪ TIẾNG VIỆT ĐÃ ĐƯỢC KHỞI TẠO", color=0xFF007F)
        embed.description = (
            "🔥 **SÀN ĐẤU TIẾNG MẸ ĐẺ CHÍNH THỨC KHAI MẠC** 🔥\n\n"
            "Chế độ chơi chung kênh tiếng Việt đã kích hoạt thành công!\n"
            "Sẵn sàng tranh tài cao thấp, flex vốn từ phong phú cùng đồng đội trong server ngay lập tức.\n\n"
            f"🎯 **TỪ KHÓA KHỞI ĐẦU TỪ HỆ THỐNG:**\n"
            f"👉 **`{word.upper()}`**\n\n"
            f"⚡ Quy tắc: Nhập cụm từ 2 tiếng tiếp theo bắt đầu bằng âm tiết **{word.split()[-1].upper()}**"
        )
        embed.add_field(name="📌 Thể Thức", value="Multiplayer (Nhiều người chơi)", inline=True)
        embed.add_field(name="🎁 Điểm Thưởng", value="+25 XP mỗi từ đúng", inline=True)
        embed.add_field(name="🛡️ Bộ Lọc", value="Kho từ vựng tiếng Việt kiểm duyệt khắt khe", inline=True)
        embed.set_footer(text="Định dạng bắt buộc: Đúng 2 từ có nghĩa, không chơi từ lóng hoặc sai chính tả!")
        await ctx.send(embed=embed)

@bot.command(name="noituubot")
async def start_game_vi_bot(ctx):
    if ctx.channel.id in games: return await ctx.send("kênh đang có ván chơi rồi")
    word = "đá bóng"
    games[ctx.channel.id] = {"mode": "vi_bot", "last_word": word, "used_words": {word}}
    embed = discord.Embed(title="🤖 THÁCH ĐẤU AI: SOLO TIẾNG VIỆT KHÔ MÁU", color=0xFF007F)
    embed.description = (
        "⚔️ **CHẾ ĐỘ ĐƠN ĐẢ ĐỘC MÃ CHIẾN ĐẤU TRỰC TIẾP VỚI HỆ THỐNG AI** ⚔️\n\n"
        "Bạn đã tự tin bước vào lôi đài đối đầu 1v1 với con bot siêu trí tuệ tiếng Việt.\n"
        "Hãy tung chiêu thật nhanh và chính xác để không bị con bot bắt bẻ gục ngã.\n\n"
        f"🎯 **TỪ KHÓA MỞ MÀN TỪ TỔNG ĐÀI:**\n"
        f"👉 **`{word.upper()}`**\n\n"
        f"⚡ Âm tiết phản đòn tiếp theo bắt đầu bằng: **{word.split()[-1].upper()}**"
    )
    embed.add_field(name="🎯 Chế Độ", value="Solo vs Bot (Tiếng Việt)", inline=True)
    embed.add_field(name="⚡ Tốc Độ Phản Hồi", value="Tức thì ngay lập tức", inline=True)
    embed.set_footer(text="Bot sẽ tự động đáp trả ngay sau mỗi câu lệnh hợp lệ từ bạn. Cẩn thận hết từ nhé!")
    await ctx.send(embed=embed)

@bot.command(name="noitueng")
async def start_game_en(ctx):
    if ctx.channel.id in games: return await ctx.send("kênh đang có ván chơi rồi")
    word = "apple"
    games[ctx.channel.id] = {"mode": "en_multi", "last_word": word, "used_words": {word}}
    embed = discord.Embed(title="🇬🇧 TRẬN ĐẤU NỐI TỪ TIẾNG ANH ĐÃ ĐƯỢC KHỞI TẠO", color=0xFF007F)
    embed.description = (
        "🔥 **SÀN ĐẤU NGÔN NGỮ QUỐC TẾ CHÍNH THỨC KHAI MẠC** 🔥\n\n"
        "Chế độ chơi chung kênh tiếng Anh đã kích hoạt thành công!\n"
        "Mọi người cùng nhau tập trung, huy động toàn bộ vốn từ vựng phong phú để tiếp nối chuỗi từ.\n\n"
        f"🎯 **TỪ KHÓA KHỞI ĐẦU TỪ HỆ THỐNG:**\n"
        f"👉 **`{word.upper()}`**\n\n"
        f"⚡ Quy tắc: Nhập từ tiếng Anh tiếp theo bắt đầu bằng ký tự **{word[-1].upper()}**"
    )
    embed.add_field(name="📌 Thể Thức", value="Multiplayer (Nhiều người chơi)", inline=True)
    embed.add_field(name="🎁 Điểm Thưởng", value="+25 XP mỗi từ đúng", inline=True)
    embed.add_field(name="🛡️ Bộ Lọc", value="Kiểm tra từ điển Alpha chuẩn xác", inline=True)
    embed.set_footer(text="Hãy chắc chắn từ của bạn có trong từ điển và chưa từng được sử dụng trước đó!")
    await ctx.send(embed=embed)

@bot.command(name="noituuboteng")
async def start_game_en_bot(ctx):
    if ctx.channel.id in games: return await ctx.send("kênh đang có ván chơi rồi")
    word = "apple"
    games[ctx.channel.id] = {"mode": "en_bot", "last_word": word, "used_words": {word}}
    embed = discord.Embed(title="🤖 THÁCH ĐẤU AI: SOLO TIẾNG ANH KHÔ MÁU", color=0xFF007F)
    embed.description = (
        "⚔️ **CHẾ ĐỘ ĐƠN ĐẢ ĐỘC MÃ CHIẾN ĐẤU TRỰC TIẾP VỚI HỆ THỐNG AI** ⚔️\n\n"
        "Bạn đã tự tin bước vào lôi đài đối đầu 1v1 với con bot siêu trí tuệ quốc tế tiếng Anh.\n"
        "Hãy tung từ vựng ngoại ngữ thật chuẩn xác để áp đảo đối thủ máy móc này.\n\n"
        f"🎯 **TỪ KHÓA MỞ MÀN TỪ TỔNG ĐÀI:**\n"
        f"👉 **`{word.upper()}`**\n\n"
        f"⚡ Ký tự phản đòn tiếp theo bắt đầu bằng: **{word[-1].upper()}**"
    )
    embed.add_field(name="🎯 Chế Độ", value="Solo vs Bot (Tiếng Anh)", inline=True)
    embed.add_field(name="⚡ Tốc Độ Phản Hồi", value="Tức thì ngay lập tức", inline=True)
    embed.set_footer(text="Bot tiếng Anh sẵn sàng tiếp chiêu bất cứ lúc nào bạn ra từ!")
    await ctx.send(embed=embed)

@bot.command(name="huynoitu")
async def stop_game(ctx):
    if ctx.channel.id in games:
        del games[ctx.channel.id]
        embed = discord.Embed(title="⚙️ HỦY BỎ TRẬN ĐẤU THÀNH CÔNG", color=0xED4245)
        embed.description = (
            "🛑 **PHIÊN TRẬN ĐẤU ĐÃ ĐƯỢC KẾT THÚC CƯỠNG BỨC**\n\n"
            "Theo yêu cầu của ban quản trị/người chơi, ván đấu nối từ trong kênh này đã bị giải tán hoàn toàn.\n"
            "Toàn bộ bộ nhớ tạm về từ vựng đã được làm sạch sẽ."
        )
        embed.add_field(name="📌 Trạng Thái Kênh", value="Đã sẵn sàng khởi tạo ván mới bất cứ lúc nào", inline=False)
        embed.set_footer(text="Sử dụng lệnh ?noitu hoặc ?noitueng để mở bàn đấu mới khi cần.")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="⚠️ CẢNH BÁO: KHÔNG CÓ TRẬN ĐẤU NÀO", color=0xFEE75C)
        embed.description = (
            "🔍 Kênh chat này hiện tại làm gì có ván nối từ nào đang chạy mà bạn lại đòi hủy bỏ?\n"
            "Hãy chắc chắn rằng một trận đấu đang diễn ra trước khi gọi lệnh hủy nhé."
        )
        embed.set_footer(text="Mọi thắc mắc vui lòng kiểm tra lại tình trạng kênh hiện tại.")
        await ctx.send(embed=embed)

@bot.command(name="nghia")
async def nghia_cmd(ctx, word: str = None):
    if not word: 
        embed = discord.Embed(title="⚠️ THIẾU THÔNG TIN TỪ KHÓA TRA CỨU", color=0xFEE75C)
        embed.description = (
            "📌 Bạn muốn tra nghĩa từ nào thì phải gõ kèm từ đó theo cú pháp chuẩn chứ!\n\n"
            "👉 Ví dụ mẫu: `?nghia apple` hoặc `?nghia computer`"
        )
        embed.set_footer(text="Hệ thống từ điển thông minh hỗ trợ tra cứu trực tuyến.")
        return await ctx.send(embed=embed)
        
    w = word.strip().lower()
    if w in dictionary_en:
        embed = discord.Embed(title="📖 KẾT QUẢ TRA CỨU TỪ ĐIỂN: THÀNH CÔNG", color=0x57F287)
        embed.description = (
            f"🎉 Từ khóa **`{w}`** hoàn toàn hợp lệ và có mặt trong cơ sở dữ liệu từ điển tiếng Anh chuẩn!\n\n"
            "Bạn có thể hoàn toàn tự tin sử dụng từ này trong các ván đấu nối từ quốc tế."
        )
        embed.add_field(name="✅ Tình Trạng", value="Hợp lệ - Được hệ thống công nhận", inline=False)
        embed.set_footer(text="Tra cứu nhanh chóng, chính xác tuyệt đối 100%.")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="📖 KẾT QUẢ TRA CỨU TỪ ĐIỂN: THẤT BẠI", color=0xED4245)
        embed.description = (
            f"❌ Từ khóa **`{w}`** tuyệt đối KHÔNG tìm thấy trong hệ thống từ điển tiếng Anh!\n\n"
            "Có thể từ này không tồn tại, sai chính tả hoặc thuộc từ lóng không được hệ thống chuẩn hóa."
        )
        embed.add_field(name="⚠️ Tình Trạng", value="Không tồn tại trong từ điển chuẩn", inline=False)
        embed.set_footer(text="Hãy kiểm tra lại kỹ lưỡng từng ký tự trước khi đem ra thi đấu nhé.")
        await ctx.send(embed=embed)

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
            await message.add_reaction(CROSS)
            return
        game["used_words"].add(user_input)
        game["last_word"] = user_input
        await message.add_reaction(TICK)
        
        data = get_user_data(message.author.id)
        data["xp"] += 25
        if data["xp"] >= data["level"] * 300:
            data["xp"] -= data["level"] * 300
            data["level"] += 1
            await message.channel.send(f"🎉 {message.author.mention} vừa lên level {data['level']}")

        if mode == "vi_bot":
            last_syllable = user_input.split()[-1]
            possible_words = [w for w in dictionary_vi if w.startswith(last_syllable + " ") and w not in game["used_words"]]
            if possible_words:
                bot_word = random.choice(possible_words)
                game["used_words"].add(bot_word)
                game["last_word"] = bot_word
                await message.channel.send(f"🤖 Bot nối tiếp: **`{bot_word.upper()}`** {TICK}")
            else:
                await message.channel.send(f"🏆 {message.author.mention} đã win bot vì bot hết từ")
                del games[ctx.channel.id]

    elif mode in ["en_multi", "en_bot"]:
        w = user_input
        prev_char = game["last_word"][-1]
        if len(w.split()) != 1 or w[0] != prev_char or w in game["used_words"] or w not in dictionary_en:
            await message.add_reaction(CROSS)
            return
        game["used_words"].add(w)
        game["last_word"] = w
        await message.add_reaction(TICK)
        
        data = get_user_data(message.author.id)
        data["xp"] += 25
        if data["xp"] >= data["level"] * 300:
            data["xp"] -= data["level"] * 300
            data["level"] += 1
            await message.channel.send(f"🎉 {message.author.mention} vừa lên level {data['level']}")

        if mode == "en_bot":
            last_char = w[-1]
            possible_words = [word for word in dictionary_en if word.startswith(last_char) and word not in game["used_words"]]
            if possible_words:
                bot_word = random.choice(possible_words)
                game["used_words"].add(bot_word)
                game["last_word"] = bot_word
                await message.channel.send(f"🤖 Bot nối tiếp: **`{bot_word.upper()}`** {TICK}")
            else:
                await message.channel.send(f"🏆 {message.author.mention} đã win bot vì bot hết từ")
                del games[ctx.channel.id]

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
