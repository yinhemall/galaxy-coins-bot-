import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime
import random

DATA_FILE = "data.json"
CONFIG_FILE = "config.json"

# --- 基礎函數 ---
def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

# --- 簽到 UI ---
class DailyView(discord.ui.View):
    def __init__(self): 
        super().__init__(timeout=None) # 必須設定 None
    
    @discord.ui.button(label="領取每日獎勵 🌑", style=discord.ButtonStyle.green, custom_id="daily_persistent_btn")
    async def daily_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ... (這裡保留你原本的邏輯)
        await interaction.response.send_message("簽到功能運作中！", ephemeral=True)

# --- 遊戲 UI ---
class GambleModal(discord.ui.Modal, title='賭博下注'):
    amount = discord.ui.TextInput(label='請輸入下注金額', style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"下注 {self.amount.value} 幣中...", ephemeral=True)

class GameSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label="骰子比大小", value="dice", emoji="🎲"), 
                   discord.SelectOption(label="拉霸機", value="slots", emoji="🎰")]
        super().__init__(placeholder="請選擇遊戲...", options=options, custom_id="game_persistent_select")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(GambleModal())

class GameView(discord.ui.View):
    def __init__(self): 
        super().__init__(timeout=None)
        self.add_item(GameSelect())

# --- 管理員錢包 UI ---
class WalletView(discord.ui.View):
    def __init__(self, target=None):
        super().__init__(timeout=None)
        self.target = target
    @discord.ui.button(label="增加餘額", style=discord.ButtonStyle.green, custom_id="add_btn_id")
    async def add_btn(self, interaction: discord.Interaction, b: discord.ui.Button):
        await interaction.response.send_message("增加餘額操作...", ephemeral=True)

# --- Cog 系統 ---
class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="balance", description="查詢餘額")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        await interaction.response.send_message(f"{target.display_name} 的錢包")

async def setup(bot):
    # 註冊這些 Persistent Views
    bot.add_view(DailyView())
    bot.add_view(GameView())
    bot.add_view(WalletView())
    await bot.add_cog(Economy(bot))
    print("✅ 所有 UI 已成功註冊")
