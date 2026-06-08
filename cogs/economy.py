import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime
import random

# 設定檔案路徑
DATA_FILE = "data.json"
CONFIG_FILE = "config.json"

# --- 資料庫函數 ---
def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

# --- 設定貨幣名稱 ---
def get_currency_name():
    if not os.path.exists(CONFIG_FILE): return "銀河幣"
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f).get("currency_name", "銀河幣")
    except: return "銀河幣"

def set_currency_name(name):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump({"currency_name": name}, f, ensure_ascii=False)

# --- 簽到與遊戲選單 View ---
class DailyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="領取每日獎勵 🌑", style=discord.ButtonStyle.green, custom_id="daily_button")
    async def daily_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        curr = get_currency_name()
        data = load_data()
        user_id = str(interaction.user.id)
        now = datetime.datetime.now()
        
        if user_id not in data: data[user_id] = {"balance": 0, "last_daily": "2000-01-01 00:00:00"}
        
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
        await interaction.response.send_message(f"✅ 簽到成功！獲得 {reward} {curr}。\n💰 目前餘額: **{data[user_id]['balance']}** {curr}", ephemeral=True)

# --- 遊戲表單與選單 ---
class GambleModal(discord.ui.Modal, title='賭博下注'):
    amount = discord.ui.TextInput(label='請輸入下注金額', style=discord.TextStyle.short, placeholder='例如: 100', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        curr = get_currency_name()
        try:
            amt = int(self.amount.value)
            data = load_data()
            uid = str(interaction.user.id)
            if amt <= 0 or data.get(uid, {"balance": 0})["balance"] < amt:
                return await interaction.response.send_message(f"❌ 餘額不足或金額無效！", ephemeral=True)

            user_dice, bot_dice = random.randint(1, 6), random.randint(1, 6)
            if user_dice > bot_dice:
                data[uid]["balance"] += amt
                msg = f"🎉 **你贏了！** 點數: {user_dice} vs {bot_dice}，獲得 {amt} {curr}！"
            else:
                data[uid]["balance"] -= amt
                msg = f"💀 **你輸了！** 點數: {user_dice} vs {bot_dice}，失去 {amt} {curr}。"
            save_data(data)
            await interaction.response.send_message(msg, ephemeral=True)
        except ValueError: await interaction.response.send_message("❌ 請輸入有效的數字。", ephemeral=True)

class GameSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label="賭博 (比大小)", description="下注貨幣，比拚運氣！", emoji="🎲")]
        super().__init__(placeholder="請選擇遊戲...", min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "賭博 (比大小)": await interaction.response.send_modal(GambleModal())

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
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="set_currency_name", description="[管理員] 修改貨幣名稱")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_currency(self, interaction: discord.Interaction, name: str):
        set_currency_name(name)
        await interaction.response.send_message(f"✅ 貨幣名稱已修改為: **{name}**")

    @app_commands.command(name="balance", description="查詢餘額")
    async def balance(self, interaction: discord.Interaction):
        curr = get_currency_name()
        data = load_data()
        bal = data.get(str(interaction.user.id), {"balance": 0})["balance"]
        await interaction.response.send_message(f"💰 你目前的餘額是: **{bal}** {curr}。")

    @app_commands.command(name="transfer", description="轉帳給其他用戶")
    async def transfer(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        curr = get_currency_name()
        data = load_data()
        sender_id, receiver_id = str(interaction.user.id), str(member.id)
        if amount <= 0 or data.get(sender_id, {"balance": 0})["balance"] < amount:
            return await interaction.response.send_message("❌ 餘額不足或金額無效！", ephemeral=True)
        
        data[sender_id]["balance"] -= amount
        if receiver_id not in data: data[receiver_id] = {"balance": 0, "last_daily": "2000-01-01 00:00:00"}
        data[receiver_id]["balance"] += amount
        save_data(data)
        await interaction.response.send_message(f"✅ 已成功轉帳 {amount} {curr} 給 {member.mention}！")

    @app_commands.command(name="setup_daily", description="[管理員] 發送簽到訊息")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        embed = discord.Embed(title="每日簽到", description="點擊下方按鈕領取獎勵", color=discord.Color.blue())
        await interaction.channel.send(embed=embed, view=DailyView())
        await interaction.response.send_message("簽到訊息已發送！", ephemeral=True)

    @app_commands.command(name="setup_games", description="[管理員] 發送遊戲廳入口")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_games(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🎮 遊戲廳", description="點擊下方按鈕查看所有遊戲！", color=discord.Color.green())
        await interaction.channel.send(embed=embed, view=MenuStarterView())
        await interaction.response.send_message("遊戲廳入口已發送！", ephemeral=True)

async def setup(bot): await bot.add_cog(Economy(bot))
