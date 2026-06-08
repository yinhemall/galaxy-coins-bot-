import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime

# 設定檔案路徑
DATA_FILE = "data.json"

# --- 資料庫函數 ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- 簽到按鈕系統 ---
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
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            await interaction.response.send_message(f"⏳ 冷卻中，還需等待 {hours} 小時 {minutes} 分鐘。", ephemeral=True)
            return

        reward = 150
        data[user_id]["balance"] += reward
        data[user_id]["last_daily"] = now.strftime("%Y-%m-%d %H:%M:%S")
        save_data(data)
        
        await interaction.response.send_message(f"✅ 簽到成功！獲得 {reward} 銀河幣。\n💰 目前餘額: **{data[user_id]['balance']}**", ephemeral=True)

# --- 經濟系統 Cog ---
class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="balance", description="查詢你的銀河幣餘額")
    async def balance(self, interaction: discord.Interaction):
        data = load_data()
        bal = data.get(str(interaction.user.id), {"balance": 0})["balance"]
        await interaction.response.send_message(f"💰 你目前的餘額是: **{bal}** 銀河幣。")

    @app_commands.command(name="transfer", description="轉帳銀河幣給其他用戶")
    @app_commands.describe(member="要轉帳的對象", amount="轉帳金額")
    async def transfer(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ 金額必須大於 0！", ephemeral=True)
            return
        if member.id == interaction.user.id:
            await interaction.response.send_message("❌ 你不能轉帳給自己！", ephemeral=True)
            return

        data = load_data()
        sender_id = str(interaction.user.id)
        receiver_id = str(member.id)
        
        sender_bal = data.get(sender_id, {"balance": 0})["balance"]
        if sender_bal < amount:
            await interaction.response.send_message("❌ 餘額不足！", ephemeral=True)
            return
        
        # 執行轉帳
        data[sender_id]["balance"] -= amount
        if receiver_id not in data:
            data[receiver_id] = {"balance": 0, "last_daily": "2000-01-01 00:00:00"}
        data[receiver_id]["balance"] += amount
        
        save_data(data)
        await interaction.response.send_message(f"✅ 已成功轉帳 {amount} 銀河幣給 {member.mention}！")

    @app_commands.command(name="admin_give", description="[管理員] 調整用戶餘額")
    @app_commands.checks.has_permissions(administrator=True)
    async def admin_give(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        data = load_data()
        uid = str(member.id)
        if uid not in data:
            data[uid] = {"balance": 0, "last_daily": "2000-01-01 00:00:00"}
        
        data[uid]["balance"] += amount
        save_data(data)
        await interaction.response.send_message(f"🛠️ 已調整 {member.name} 的餘額，變更值: {amount}。目前餘額: {data[uid]['balance']}")

    @app_commands.command(name="leaderboard", description="查看財富排行榜")
    async def leaderboard(self, interaction: discord.Interaction):
        data = load_data()
        if not data:
            await interaction.response.send_message("目前還沒有任何資料！")
            return
        sorted_users = sorted(data.items(), key=lambda x: x[1]["balance"], reverse=True)[:10]
        embed = discord.Embed(title="🏆 銀河幣富豪榜", color=discord.Color.gold())
        for i, (uid, info) in enumerate(sorted_users, 1):
            try:
                user = await self.bot.fetch_user(int(uid))
                name = user.name
            except:
                name = "未知用戶"
            embed.add_field(name=f"{i}. {name}", value=f"💰 {info['balance']} 銀河幣", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setup_daily", description="發送簽到訊息 (管理員)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🌑 每日簽到", description="點擊下方按鈕領取銀河幣 🌑", color=discord.Color.blue())
        await interaction.channel.send(embed=embed, view=DailyView())
        await interaction.response.send_message("簽到訊息已發送！", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Economy(bot))
