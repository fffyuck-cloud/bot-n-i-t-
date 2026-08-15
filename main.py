import discord
import os
import random
from keep_alive import keep_alive

# ==========================================
# CẤU HÌNH HỆ THỐNG & TỪ ĐIỂN
# ==========================================

def load_vocabulary(file_path):
    """Hàm tải từ vựng từ tệp văn bản an toàn và chuẩn hóa dữ liệu"""
    words = set()
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    cleaned = line.strip().lower()
                    if cleaned:
                        words.add(cleaned)
            print(f"Đã tải thành công {len(words)} từ từ {file_path}")
        else:
            print(f"Không tìm thấy tệp {file_path}, bỏ qua.")
    except Exception as e:
        print(f"Lỗi khi đọc tệp {file_path}: {e}")
    return words

# Nạp toàn bộ kho từ vựng tiếng Việt và từ bổ sung
vietnamese_dict = load_vocabulary('tu dien.txt')
vietnamese_dict.update(load_vocabulary('words.txt'))

english_dict = load_vocabulary('words_en.txt')

# ==========================================
# QUẢN LÝ TRẠNG THÁI TRÒ CHƠI & NGƯỜI DÙNG
# ==========================================

game_sessions = {} 
user_stats = {}    

def get_default_stats(user_id):
    if user_id not in user_stats:
        user_stats[user_id] = {
            "score": 0,
            "streak": 0,
            "last_daily": ""
        }
    return user_stats[user_id]

# ==========================================
# KHỞI TẠO DISCORD BOT CLIENT
# ==========================================

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot đã đăng nhập thành công dưới tên: {client.user}')
    print(f'Tổng số từ vựng hiện có trong bộ nhớ: {len(vietnamese_dict)}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    channel_id = message.channel.id
    msg = message.content.lower().strip()
    
    if channel_id not in game_sessions:
        game_sessions[channel_id] = {
            "active": False,
            "mode": None, 
            "last_word": "",
            "used_words": set()
        }
    
    session = game_sessions[channel_id]

    # ==========================================
    # CÁC LỆNH ĐIỀU KHIỂN HỆ THỐNG & GAME
    # ==========================================
    
    if msg == "?noitu":
        session["active"] = True
        session["mode"] = "pvp_vi"
        session["last_word"] = ""
        session["used_words"].clear()
        await message.channel.send("🎮 **Đã bật chế độ Nối từ Tiếng Việt (Người vs Người)!** Hãy nhập từ đầu tiên.")
        return

    elif msg == "?noituubot":
        session["active"] = True
        session["mode"] = "bot_vi"
        session["last_word"] = ""
        session["used_words"].clear()
        await message.channel.send("🤖 **Đã bật chế độ Đấu với Bot (Tiếng Việt)!** Hãy nhập từ đầu tiên.")
        return

    elif msg == "?noitueng":
        session["active"] = True
        session["mode"] = "pvp_eng"
        session["last_word"] = ""
        session["used_words"].clear()
        await message.channel.send("🇬🇧 **Đã bật chế độ Nối từ Tiếng Anh (Người vs Người)!** Hãy nhập từ đầu tiên.")
        return

    elif msg == "?noituuboteng":
        session["active"] = True
        session["mode"] = "bot_eng"
        session["last_word"] = ""
        session["used_words"].clear()
        await message.channel.send("🤖🇬🇧 **Đã bật chế độ Đấu với Bot (Tiếng Anh)!** Hãy nhập từ đầu tiên.")
        return

    elif msg == "?huynoitu":
        session["active"] = False
        session["mode"] = None
        session["last_word"] = ""
        session["used_words"].clear()
        await message.channel.send("🚫 **Đã hủy ván nối từ hiện tại trong kênh này.**")
        return

    elif msg.startswith("?nghia"):
        parts = message.content.split()
        if len(parts) > 1:
            word_to_check = parts[1].lower()
            if word_to_check in vietnamese_dict:
                await message.channel.send(f"✅ Từ **'{parts[1]}'** có tồn tại trong cơ sở dữ liệu từ điển.")
            else:
                await message.channel.send(f"❌ Không tìm thấy từ **'{parts[1]}'** trong từ điển.")
        else:
            await message.channel.send("⚠️ Vui lòng chỉ định từ cần tra cứu, ví dụ: `?nghia <từ>`")
        return

    elif msg == "?rank":
        stats = get_default_stats(message.author.id)
        await message.channel.send(f"🏆 **Thành tích của {message.author.name}:**\n- Điểm số: `{stats['score']}`\n- Chuỗi thắng hiện tại: `{stats['streak']}`")
        return

    elif msg == "?daily":
        stats = get_default_stats(message.author.id)
        stats["score"] += 50
        await message.channel.send(f"🎁 **Điểm danh thành công!** Bạn đã nhận được `50 điểm` thưởng vào tài khoản.")
        return

    elif msg == "?help":
        help_text = (
            "📖 **HỆ THỐNG LỆNH BOT NỐI TỪ:**\n"
            "• `?noitu` - Chơi nối từ tiếng Việt (PvP)\n"
            "• `?noituubot` - Đấu nối từ tiếng Việt với Bot\n"
            "• `?noitueng` - Chơi nối từ tiếng Anh (PvP)\n"
            "• `?noituuboteng` - Đấu nối từ tiếng Anh với Bot\n"
            "• `?huynoitu` - Dừng trận đấu hiện tại\n"
            "• `?nghia <từ>` - Tra cứu từ điển\n"
            "• `?rank` - Xem bảng điểm cá nhân\n"
            "• `?daily` - Nhận thưởng điểm danh hằng ngày"
        )
        await message.channel.send(help_text)
        return

    # ==========================================
    # LOGIC XỬ LÝ TRÒ CHƠI NỐI TỪ
    # ==========================================
    
    if session["active"]:
        is_english = "eng" in session["mode"]
        current_dict = english_dict if is_english else vietnamese_dict

        if msg not in current_dict:
            await message.channel.send("❌ **Từ này không có trong từ điển của hệ thống!**")
            return

        if msg in session["used_words"]:
            await message.channel.send("⚠️ **Từ này đã được sử dụng rồi!** Hãy chọn từ khác.")
            return

        if session["last_word"] != "":
            last_part = session["last_word"].split()[-1]
            if not msg.startswith(last_part):
                await message.channel.send(f"⚠️ **Sai quy tắc!** Từ phải bắt đầu bằng chữ: **'{last_part}'**")
                return

        session["last_word"] = msg
        session["used_words"].add(msg)
        
        stats = get_default_stats(message.author.id)
        stats["score"] += 10
        stats["streak"] += 1

        next_required = msg.split()[-1]
        reply_msg = f"✅ **Hợp lệ!** (+10 điểm). Từ tiếp theo phải bắt đầu bằng: **'{next_required}'**"

        if "bot" in session["mode"]:
            possible_words = [w for w in current_dict if w.startswith(next_required) and w not in session["used_words"]]
            if possible_words:
                bot_choice = random.choice(possible_words)
                session["last_word"] = bot_choice
                session["used_words"].add(bot_choice)
                bot_next = bot_choice.split()[-1]
                reply_msg += f"\n🤖 **Bot đáp trả:** `{bot_choice}` ➔ Tiếp theo bắt đầu bằng: **'{bot_next}'**"
            else:
                reply_msg += f"\n🎉 **Chúc mừng!** Bot không tìm được từ nối tiếp, bạn đã chiến thắng!"
                session["active"] = False

        await message.channel.send(reply_msg)

# ==========================================
# KHỞI CHẠY ỨNG DỤNG
# ==========================================
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('DISCORD_TOKEN')
    if token:
        client.run(token)
    else:
        print("Lỗi trọng yếu: Không tìm thấy biến môi trường DISCORD_TOKEN.")
