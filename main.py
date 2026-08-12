import discord
from discord.ext import commands
from pyvi import ViTokenizer

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

games = {}

def is_valid_vietnamese_word(text):
    """Kiểm tra xem cụm 2 từ có phải là từ ghép có nghĩa trong tiếng Việt hay không."""
    tokenized = ViTokenizer.tokenize(text)
    # Nếu pyvi nối 2 từ bằng dấu gạch dưới (VD: "mèo_đen"), đó là từ có nghĩa
    return "_" in tokenized

@bot.event
async def on_ready():
    print(f"{bot.user} bố online rồi các con")

@bot.command(name="noitu")
async def start_game(ctx):
    channel_id = ctx.channel.id
    
    if channel_id in games:
        await ctx.send("⚠️ Kênh này đang có trận diễn ra rồi, phiền bố m mute!")
        return

    games[channel_id] = {
        "last_word": None,
        "count": 0,
        "used_words": set(),
        "last_player": None
    }
    
    await ctx.send(
        "🎮 **Đã bắt trò chơi nối từ béo béo béo!**\n"
        "• đéo được nối 2 lần liên tiếp , thay phiên nhau mà nối.\n"
        "• Đúng chính xác 2 từ có nghĩa tiếng Việt.\n"
        "• Gõ `?huynoitu` để end."
    )

@bot.command(name="huynoitu")
async def stop_game(ctx):
    channel_id = ctx.channel.id
    
    if channel_id in games:
        total_count = games[channel_id]["count"]
        del games[channel_id]
        await ctx.send(f"🛑 **Đã hủy con mẹ nó trận!** Tổng số từ nối thành công: **{total_count}** từ.")
    else:
        await ctx.send("❌ Kênh này hiện đéo có trận để huỷ đâu!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    channel_id = message.channel.id
    if channel_id not in games:
        return

    if message.content.startswith("?"):
        return

    text = message.content.strip().lower()
    words = text.split()

    if len(words) != 2:
        return

    game = games[channel_id]

    # 1. Kiểm tra luân phiên người chơi
    if game["last_player"] == message.author.id:
        await message.reply("Đợi đứa khác nối đi thằng l..., đừng tự sướng!")
        return

    # 2. Kiểm tra từ vô nghĩa (mới thêm)
    if not is_valid_vietnamese_word(text):
        await message.reply("Từ này đéo có trong từ điển tiếng Việt!")
        return

    # 3. Kiểm tra trùng lặp
    if text in game["used_words"]:
        return

    # 4. Kiểm tra quy tắc nối từ
    if game["last_word"] is not None:
        prev_last_single_word = game["last_word"].split()[-1]
        first_single_word = words[0]
        
        if first_single_word != prev_last_single_word:
            return

    # --- HỢP LỆ ---
    game["used_words"].add(text)
    game["last_word"] = text
    game["count"] += 1
    game["last_player"] = message.author.id

    await message.add_reaction("✅")
    await message.reply(f"🎯 **#{game['count']}**", mention_author=False)
import os

# ... (giữ nguyên toàn bộ code ở giữa) ...

bot.run(os.getenv("DISCORD_TOKEN"))
