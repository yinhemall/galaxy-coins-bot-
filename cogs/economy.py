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

def get_currency_name():
    if not os.path.exists(CONFIG_FILE): return "銀河幣"
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f).get("currency_name", "銀河幣")
    except: return "銀河幣"

def set_currency_name(name):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump({"currency_name": name}, f, ensure_ascii=False)

# --- 簽到系統 ---
class DailyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="領取每日獎勵 🌑", style=discord.ButtonStyle.green, custom_id="daily_button")
    async def daily_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        curr = get_currency_name()
        data = load_data()
        uid = str(interaction.user.id)
        now = datetime.datetime.now()
        
        if uid not in data: 
            data[uid] = {"balance": 0, "last_daily": "2000-01-01 00:00:00", "streak": 0}
        
        last_daily = datetime.datetime.strptime(data[uid]["last_daily"], "%Y-%m-%d %H:%M:%S")
        diff = now - last_daily
        
        # 嚴格 24 小時重置邏輯
        if diff >= datetime.timedelta(hours=24):
            if diff < datetime.timedelta(hours=48):
                data[uid]["streak"] += 1
            else:
                data[uid]["streak"] = 1
        else:
            remaining = datetime.timedelta(hours=24) - diff
            await interaction.response.send_message(f"⏳ 請冷卻後再試 (剩餘 {int(remaining.total_seconds()//3600)} 時 {int(remaining.total_seconds()%3600//60)} 分)", ephemeral=True)
            return
            
        reward = random.randint(100, 300)
        bonus = 0
        if data[uid]["streak"] % 7 == 0:
            bonus = 1000
            reward += bonus
            
        data[uid]["balance"] += reward
        data[uid]["last_daily"] = now.strftime("%Y-%m-%d %H:%M:%S")
        save_data(data)
        
        msg = f"✅ 簽到成功！獲得 {reward} {curr}。\n🔥 已連續簽到 **{data[uid]['streak']}** 天！"
        if bonus > 0: msg += f"\n🎁 恭喜達成滿 7 天，額外領取 1,000 {curr}！"
        await interaction.response.send_message(msg, ephemeral=True)

# --- 遊戲系統 ---
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

    @app_commands.command(name="leaderboard_streak", description="查看連續簽到排行榜")
    async def leaderboard_streak(self, interaction: discord.Interaction):
        data = load_data()
        sorted_users = sorted([(uid, info.get("streak", 0)) for uid, info in data.items()], key=lambda x: x[1], reverse=True)[:10]
        msg = "🏆 **連續簽到排行榜 (Top 10)**\n\n"
        for i, (uid, streak) in enumerate(sorted_users, 1):
            user = self.bot.get_user(int(uid))
            name = user.name if user else "未知用戶"
            msg += f"{i}. {name}: **{streak}** 天\n"
        await interaction.response.send_message(msg)

    @app_commands.command(name="setup_daily", description="[管理員] 發送簽到訊息")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        curr = get_currency_name()
        embed = discord.Embed(title="🌑 每日簽到", description=f"每天領取 100-300 {curr}\n🔥 連續滿 7 天加贈 1,000 {curr}！", color=discord.Color.blue())
        await interaction.channel.send(embed=embed, view=DailyView())
        await interaction.response.send_message("簽到訊息已發送！", ephemeral=True)

    @app_commands.command(name="setup_games", description="[管理員] 發送遊戲廳入口")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_games(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🎮 銀河遊戲廳", description="點擊下方按鈕查看所有遊戲！", color=discord.Color.green())
        await interaction.channel.send(embed=embed, view=MenuStarterView())
        await interaction.response.send_message("遊戲廳入口已發送！", ephemeral=True)

async def setup(bot): await bot.add_cog(Economy(bot))
