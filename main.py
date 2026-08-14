@bot.command(name="help", aliases=["trogiup", "huongdan"])
async def custom_help(ctx):
    embed = discord.Embed(
        title="❖ ────── 📜 DANH SÁCH LỆNH BOT NỐI TỪ ────── ❖",
        description="Chào mừng bạn đến với **Word Chain Master**! Dưới đây là toàn bộ các lệnh bạn có thể sử dụng:",
        color=COLOR_PINK,
        timestamp=datetime.now()
    )
    if bot.user and bot.user.display_avatar:
        embed.set_thumbnail(url=bot.user.display_avatar.url)

    embed.add_field(
        name="🇻🇳 NỐI TỪ TIẾNG VIỆT",
        value="• `?noitu` ➔ Bắt đầu ván chơi nhóm (Server cùng chơi)\n• `?noitubot` ➔ Đấu 1v1 trực tiếp với Bot",
        inline=False
    )
    embed.add_field(
        name="🔤 ENGLISH WORD CHAIN",
        value="• `?noitueng` ➔ Bắt đầu ván Tiếng Anh nhóm\n• `?noituboteng` ➔ Đấu 1v1 Tiếng Anh với Bot",
        inline=False
    )
    embed.add_field(
        name="📊 TÍNH NĂNG & TIỆN ÍCH",
        value="• `?daily` ➔ Điểm danh hằng ngày (Nhận 3 lượt gợi ý)\n• `?profile` ➔ Xem hồ sơ & tỉ lệ thắng của bạn\n• `?profile @user` ➔ Xem hồ sơ người chơi khác\n• `?huynoitu` ➔ Hủy trận đấu ở kênh hiện tại",
        inline=False
    )
    embed.add_field(
        name="💡 LƯU Ý KHI CHƠI",
        value="* Khi trận đấu đã mở, bạn **không cần gõ `?`**, chỉ cần gõ trực tiếp từ nối vào kênh chat!\n* Nhấn nút **💡 Gợi Ý** trên Embed nếu bí từ.",
        inline=False
    )
    embed.set_footer(text="Gõ ?help hoặc ?trogiup bất kỳ lúc nào để xem lại bảng này!", icon_url="https://cdn-icons-png.flaticon.com/512/2069/2069581.png")
    
    await ctx.send(embed=embed)
