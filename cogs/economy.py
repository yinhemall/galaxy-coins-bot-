
import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
from datetime import datetime, timedelta

DATA_FILE = "data.json"

# --- 基礎資料處理 ---
def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: 
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- UI 介面類別 (必須在 setup 之前定義) ---
class DailyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="領取每日獎勵 🌑", style=discord.ButtonStyle.green, custom_id="daily_btn_v2")
    async def daily_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ... (你的簽到邏輯保持不變)
        await interaction.response.send_message("簽到功能運作中！", ephemeral=True)

class GameView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="進入遊戲廳", style=discord.ButtonStyle.blurple, custom_id="game_persistent_btn")
    async def game_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("遊戲開發中...", ephemeral=True)

class WalletView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="管理餘額", style=discord.ButtonStyle.gray, custom_id="wallet_persistent_btn")
    async def manage_btn(self, interaction: discord.Interaction, b: discord.ui.Button):
        await interaction.response.send_message("管理員指令調整。", ephemeral=True)

# --- Economy Cog ---
class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="setup_daily", description="發送專業簽到面板")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        # ... (你的發送面板邏輯)
        await interaction.response.send_message("已發送！", ephemeral=True)

# --- setup 函數 (一定要放在檔案的最底部) ---
async def setup(bot):
    bot.add_view(DailyView())
    bot.add_view(GameView())
    bot.add_view(WalletView())
    await bot.add_cog(Economy(bot))
    print("✅ Economy Cog 與 UI 視窗已成功載入")
