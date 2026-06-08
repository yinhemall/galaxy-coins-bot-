import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime
import random

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

# --- 簽到與遊戲選單 View ---
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

# --- 遊戲選單系統 ---
class GameSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="賭博 (比大小)", description="下注銀河幣，比拚運氣！", emoji="🎲"),
        ]
        super().__init__(placeholder="請選擇你要玩的遊戲...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "賭博 (比大小)":
            await interaction.response.send_message("請使用 `/gamble <金額>` 指令來下注！", ephemeral=True)

class GameMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GameSelect())

class MenuStarterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="開啟遊戲廳 🎮", style=discord.ButtonStyle.blurple, custom_id="game_menu_btn")
    async def open_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("請選擇一個遊戲：", view=GameMenuView(), ephemeral=True)

# --- 經濟系統 Cog ---
class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- 既有指令 ---
    @app_commands.command(name="balance", description="查詢你的銀河幣餘額")
    async def balance(self, interaction: discord.Interaction):
        data = load_data()
        bal = data.get(str(interaction.user.id), {"balance": 0})["balance"]
        await interaction.response.send_message(f"💰 你目前的餘額是: **{bal}** 銀河幣。")

    @app_commands.command(name="transfer", description="轉帳銀河幣給其他用戶")
    async def transfer(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount <= 0: return await interaction.response.send_message("❌ 金額必須大於 0！", ephemeral=True)
        data = load_data()
        sender_id, receiver_id = str(interaction.user.id), str(member.id)
        if data.get(sender_id, {"balance": 0})["balance"] < amount:
            return await interaction.response.send_message("❌ 餘額不足！", ephemeral=True)
        
        data[sender_id]["balance"] -= amount
        if receiver_id not in data: data[receiver_id] = {"balance": 0, "last_daily": "2000-01-01 00:00:00"}
        data[receiver_id]["balance"] += amount
        save_data(data)
        await interaction.response.send_message(f"✅ 已成功轉帳 {amount} 銀河幣給 {member.mention}！")

    @app_commands.command(name="gamble", description="使用銀河幣進行賭博")
    async def gamble(self, interaction: discord.Interaction, amount: int):
        data = load_data()
        uid = str(interaction.user.id)
        if amount <= 0 or data.get(uid, {"balance": 0})["balance"] < amount:
            return await interaction.response.send_message("❌ 餘額不足或金額無效！", ephemeral=True)

        user_dice, bot_dice = random.randint(1, 6), random.randint(1, 6)
        if user_dice > bot_dice:
            data[uid]["balance"] += amount
            msg = f"🎉 **你贏了！** 點數: {user_dice} vs {bot_dice}，獲得 {amount} 銀河幣！"
        else:
            data[uid]["balance"] -= amount
            msg = f"💀 **你輸了！** 點數: {user_dice} vs {bot_dice}，失去 {amount} 銀河幣。"
        save_data(data)
        await interaction.response.send_message(msg)

    @app_commands.command(name="setup_daily", description="[管理員] 發送簽到訊息")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🌑 每日簽到", description="點擊下方按鈕領取銀河幣 🌑", color=discord.Color.blue())
        await interaction.channel.send(embed=embed, view=DailyView())
        await interaction.response.send_message("簽到訊息已發送！", ephemeral=True)

    @app_commands.command(name="setup_games", description="[管理員] 發送遊戲廳入口")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_games(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🎮 銀河遊戲廳", description="點擊下方按鈕查看所有遊戲！", color=discord.Color.green())
        await interaction.channel.send(embed=embed, view=MenuStarterView())
        await interaction.response.send_message("遊戲廳入口已發送！", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Economy(bot))
