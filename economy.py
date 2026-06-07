import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime

DATA_FILE = "data.json"

# 載入資料
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# 儲存資料
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

class DailyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="領取每日銀河幣 🌑", style=discord.ButtonStyle.green, custom_id="daily_button")
    async def daily_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        user_id = str(interaction.user.id)
        now = datetime.datetime.now()
        
        if user_id not in data:
            data[user_id] = {"balance": 0, "last_daily": "2000-01-01 00:00:00"}
        
        last_daily = datetime.datetime.strptime(data[user_id]["last_daily"], "%Y-%m-%d %H:%M:%S")
        if now - last_daily < datetime.timedelta(hours=24):
            remaining = datetime.timedelta(hours=24) - (now - last_daily)
            await interaction.response.send_message(f"⏳ 冷卻中，還需等待 {int(remaining.total_seconds()//3600)} 小時。", ephemeral=True)
            return

        reward = 150
        data[user_id]["balance"] += reward
        data[user_id]["last_daily"] = now.strftime("%Y-%m-%d %H:%M:%S")
        save_data(data)
        
        await interaction.response.send_message(f"✅ 簽到成功！餘額: {data[user_id]['balance']}", ephemeral=True)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="balance", description="查詢餘額")
    async def balance(self, interaction: discord.Interaction):
        data = load_data()
        bal = data.get(str(interaction.user.id), {"balance": 0})["balance"]
        await interaction.response.send_message(f"💰 你目前的餘額是: **{bal}** 元。")

    @app_commands.command(name="leaderboard", description="查看財富排行榜")
    async def leaderboard(self, interaction: discord.Interaction):
        data = load_data()
        # 將資料排序 (從大到小)
        sorted_users = sorted(data.items(), key=lambda x: x[1]["balance"], reverse=True)[:10]
        
        embed = discord.Embed(title="🏆 銀河幣富豪榜", color=discord.Color.gold())
        for i, (uid, info) in enumerate(sorted_users, 1):
            user = self.bot.get_user(int(uid))
            name = user.name if user else "未知用戶"
            embed.add_field(name=f"{i}. {name}", value=f"{info['balance']} 元", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
