import discord
from discord.ext import commands
from discord import app_commands
import datetime

# 用來暫存錢包與冷卻時間
# 格式: {user_id: {"balance": 100, "last_daily": datetime}}
user_data = {}

class DailyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # 讓按鈕永久有效

    @discord.ui.button(label="領取每日銀河幣 🌑", style=discord.ButtonStyle.green, custom_id="daily_button")
    async def daily_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        now = datetime.datetime.now()
        
        # 初始化使用者資料
        if user_id not in user_data:
            user_data[user_id] = {"balance": 0, "last_daily": datetime.datetime(2000, 1, 1)}
        
        # 檢查 24 小時冷卻
        last_daily = user_data[user_id]["last_daily"]
        if now - last_daily < datetime.timedelta(hours=24):
            remaining = datetime.timedelta(hours=24) - (now - last_daily)
            await interaction.response.send_message(
                f"⏳ 你已經領取過了！請等待 {int(remaining.total_seconds() // 3600)} 小時 {int((remaining.total_seconds() % 3600) // 60)} 分鐘後再來。",
                ephemeral=True
            )
            return

        # 領取獎勵
        reward = 150 # 這裡可以寫隨機數字 random.randint(100, 300)
        user_data[user_id]["balance"] += reward
        user_data[user_id]["last_daily"] = now
        
        await interaction.response.send_message(
            f"✅ 簽到成功！獲得 {reward} 銀河幣。\n💰 目前餘額: **{user_data[user_id]['balance']}**",
            ephemeral=True
        )

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 這個指令用來發送那個「包含按鈕的訊息」
    @app_commands.command(name="setup_daily", description="發送簽到訊息 (管理員專用)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🌑 每日簽到",
            description="每天點擊下方按鈕領取 100~300 銀河幣 🌑\n\n"
                        "🎁 連續簽到滿 7 天 額外獲得 1,000 銀河幣週獎勵！\n"
                        "⏳ 24 小時冷卻，每人每天只能領一次\n"
                        "💼 輸入 /balance 查看你的錢包",
            color=discord.Color.blue()
        )
        await interaction.channel.send(embed=embed, view=DailyView())
        await interaction.response.send_message("簽到訊息已發送！", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Economy(bot))
