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

# --- 資料庫函數 (保持不變) ---
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

# --- View 類別 ---
class DailyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="領取每日獎勵 🌑", style=discord.ButtonStyle.green, custom_id="daily_button")
    async def daily_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # (這裡保留你原本簽到邏輯，為了簡潔我省略，貼上你原本的即可)
        await interaction.response.send_message("簽到功能運作中！", ephemeral=True)

class GameMenuView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    # (這裡保留你原本遊戲邏輯)

class MenuStarterView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    # (這裡保留你原本遊戲廳邏輯)

# --- 經濟系統 Cog ---
class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="balance", description="查詢餘額與管理")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        data = load_data()
        bal = data.get(str(target.id), {"balance": 0})["balance"]
        await interaction.response.send_message(f"💰 {target.display_name} 餘額: **{bal}**")

async def setup(bot):
    # 這是關鍵：在這裡註冊 View，main.py 就不會報錯了
    bot.add_view(DailyView())
    bot.add_view(MenuStarterView())
    bot.add_view(GameMenuView())
    await bot.add_cog(Economy(bot))
    print("✅ Economy Cog 與 Views 已成功註冊！")
