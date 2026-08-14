import os
import discord
from discord.ext import commands
import random
import unicodedata
import re

# --- CẤU HÌNH ---
TOKEN = os.getenv("DISCORD_TOKEN")
COLOR = 0xFF1493
BANNER_URL = "https://cdn.discordapp.com/attachments/1398867543971946578/1405789128033099836/6ab3b622-3ac8-4d11-88e3-ede9d98f7f10.png"
EMOJI_TICK = "<:Screenshot20260812172055:1537043520790073424>"
EMOJI_CROSS = "<:Screenshot20260812173722:1537047895310602300>"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)

# Lưu trữ game: {channel_id: {data}}
games = {}

def norm(text):
    return unicodedata.normalize('NFC', text.lower().strip())

# --- GIAO DIỆN EMBED CHI TIẾT ---
def build_game_embed(game):
    embed = discord.Embed(title="🎮 HỆ THỐNG NỐI TỪ", color=COLOR)
    embed.set_image(url=BANNER_URL)
    
    hist = " ➔ ".join([w.upper() for w in game['history'][-5:]])
    
    # Đếm số và chi tiết ván
    embed.add_field(name="📊 THỐNG KÊ", value=f"**Tổng từ:** `{game['count']}`\n**Chế độ:** `{game['mode'].upper()}`", inline=True)
    embed.add_field(name="🔥 COMBO", value=f"**Level:** `{game['count']}`", inline=True)
    
    # Mục tiêu
    target = game['last_word'].split()[-1] if game['mode'] == 'vi' else game['last_word'][-1]
    embed.add_field(name="🎯 BẮT ĐẦU VỚI", value=f"```fix\n{target.upper()}\n```", inline=False)
    
    # Lịch sử
    embed.add_field(name="📜 5 TỪ GẦN NHẤT", value=f"`{hist}`", inline=False)
    
    embed.set_footer(text="Gõ từ của bạn vào khung chat | Dùng ?huynoitu để dừng")
    return embed

# --- LỆNH GAME ---
@bot.command(name="noitu")
async def start_vi(ctx):
    word = "đá bóng"
    games[ctx.channel.id] = {"mode": "vi", "last_word": word, "history": [word], "count": 1}
    await ctx.send(embed=build_game_embed(games[ctx.channel.id]))

@bot.command(name="noitueng")
async def start_en(ctx):
    word = "apple"
    games[ctx.channel.id] = {"mode": "en", "last_word": word, "history": [word], "count": 1}
    await ctx.send(embed=build_game_embed(games[ctx.channel.id]))

@bot.command(name="huynoitu")
async def stop_game(ctx):
    if ctx.channel.id in games:
        del games[ctx.channel.id]
        await ctx.send("🛑 **Đã hủy ván nối từ!**")
    else:
        await ctx.send("❌ Không có ván nào đang chạy.")

# --- XỬ LÝ NỐI TỪ ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    await bot.process_commands(message)
    
    cid = message.channel.id
    if cid not in games: return
    
    game = games[cid]
    user_word = norm(message.content)
    
    # Logic kiểm tra (đơn giản hóa cho ví dụ, bạn có thể nối vào dict từ điển thật)
    is_valid = True # Thay logic kiểm tra từ điển của bạn vào đây
    
    if is_valid:
        game['last_word'] = user_word
        game['history'].append(user_word)
        game['count'] += 1
        
        await message.add_reaction(EMOJI_TICK)
        await message.channel.send(embed=build_game_embed(game))
    else:
        await message.add_reaction(EMOJI_CROSS)

bot.run(TOKEN)
