import discord
from PIL import Image, ImageDraw, ImageOps
import io
import urllib.request

# Định nghĩa mấy cái emoji cho dễ gọi
TICK = "<:Screenshot20260812172055:1537043520790073424>"
CROSS = "<:Screenshot20260812173722:1537047895310602300>"

def get_background():
    try:
        # Load đúng cái file mày gửi
        bg = Image.open("d89db057-b415-48f7-8603-47052617b39e.png").convert("RGBA")
        bg = ImageOps.fit(bg, (600, 200), Image.Resampling.LANCZOS)
        return bg
    except Exception as e:
        print(f"Lỗi load ảnh: {e}")
        return Image.new("RGBA", (600, 200), "#0b0b0e")

async def create_rank_card(member, data):
    image = get_background()
    draw = ImageDraw.Draw(image)
    
    # Overlay đen cho chữ nổi
    overlay = Image.new("RGBA", (600, 200), (0, 0, 0, 120))
    image.alpha_composite(overlay)
    
    # Vẽ viền
    draw.rectangle([5, 5, 595, 195], outline="#ff007f", width=3)
    
    # Avatar
    try:
        avatar_url = member.display_avatar.with_size(128).url
        with urllib.request.urlopen(avatar_url) as resp:
            avatar_img = Image.open(io.BytesIO(resp.read())).convert("RGBA")
            avatar_img = avatar_img.resize((110, 110))
            mask = Image.new("L", (110, 110), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 110, 110), fill=255)
            image.paste(avatar_img, (40, 45), mask)
    except: pass
        
    draw.ellipse((38, 43, 152, 157), outline="#ff007f", width=4)
    
    # Text
    draw.text((170, 50), f"{member.display_name}", fill="#ffffff", font_size=20)
    draw.text((450, 50), f"LVL {data['level']}", fill="#ff007f", font_size=20)
    
    # Progress Bar
    progress = min(data["xp"] / (data["level"] * 300), 1.0)
    draw.rounded_rectangle([170, 120, 560, 142], radius=11, fill="#1a1a24")
    draw.rounded_rectangle([170, 120, 170 + int(390 * progress), 142], radius=11, fill="#ff007f")
    
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return discord.File(buffer, filename="rank.png")

async def create_daily_card(member, reward, success):
    image = get_background()
    draw = ImageDraw.Draw(image)
    overlay = Image.new("RGBA", (600, 200), (0, 0, 0, 150))
    image.alpha_composite(overlay)
    
    draw.rectangle([5, 5, 595, 195], outline="#ff007f", width=3)
    
    # Text trạng thái
    status_text = "ĐIỂM DANH THÀNH CÔNG" if success else "ĐÃ ĐIỂM DANH RỒI"
    color = "#57F287" if success else "#ED4245"
    
    draw.text((50, 80), status_text, fill=color, font_size=30)
    draw.text((50, 120), f"Phần thưởng: {reward} XP" if success else "Mai quay lại nhé!", fill="#ffffff", font_size=20)
    
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return discord.File(buffer, filename="daily.png")
