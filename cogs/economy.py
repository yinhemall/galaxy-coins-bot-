import discord
from discord.ext import commands
from discord import app_commands
import datetime

# 假設這是你的全域資料，如果以後要持久化，這裡要換成讀寫 JSON 檔案
user_data = {} 

class DailyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="領取每日銀河幣 🌑", style=discord.ButtonStyle.green, custom_id="daily_button")
    async def daily_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        now = datetime.datetime.now()
        
        if user_id not in user_data:
            user_data[user_id] = {"balance": 0, "last_daily": datetime.datetime(2000, 1, 1)}
        
        last_daily = user_data[user_id]["last_daily"]
        if now - last_daily < datetime.timedelta(hours=24):
            remaining = datetime.timedelta(hours=24) - (now - last_daily)
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            await interaction.response.send_message(
                f"⏳ 你已經領取過了！請等待 {hours} 小時 {minutes} 分鐘後再來。",
                ephemeral=True
            )
            return

        reward = 150 
        user_data[user_id]["balance"] += reward
        user_data[user_id]["last_daily"] = now
        
        await interaction.response.send_message(
            f"✅ 簽到成功！獲得 {reward} 銀河幣。\n💰 目前餘額: **{user_data[user_id]['balance']}**",
            ephemeral=True
        )

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- 查看錢包系統 ---
    @app_commands.command(name="balance", description="查詢你的銀河幣餘額")
    async def balance(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = user_data.get(user_id, {"balance": 0, "last_daily": datetime.datetime(2000, 1, 1)})
        
        balance = data["balance"]
        last_daily = data["last_daily"]
        
        # 計算是否可以簽到
        can_sign = datetime.datetime.now() - last_daily >= datetime.timedelta(hours=24)
        status = "✅ 可簽到" if can_sign else "⏳ 冷卻中"
        
        embed = discord.Embed(title=f"{interaction.user.name} 的錢包", color=discord.Color.gold())
        embed.add_field(name="💰 銀河幣餘額", value=f"**{balance}**", inline=False)
        embed.add_field(name="📅 簽到狀態", value=status, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setup_daily", description="發送簽到訊息 (管理員)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🌑 每日簽到",
            description="點擊下方按鈕領取銀河幣 🌑",
            color=discord.Color.blue()
        )
        await interaction.channel.send(embed=embed, view=DailyView())
        await interaction.response.send_message("已發送！", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Economy(bot))
