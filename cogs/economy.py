import discord
from discord.ext import commands
from discord import app_commands
import json
import os

DATA_FILE = "data.json"

# --- 基礎資料處理函數 ---
def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: 
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- UI 介面類別 ---
class DailyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="領取每日獎勵 🌑", style=discord.ButtonStyle.green, custom_id="daily_persistent_btn")
    async def daily_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("簽到功能運作中！", ephemeral=True)

class GameView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="進入遊戲廳", style=discord.ButtonStyle.blurple, custom_id="game_persistent_btn")
    async def game_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("遊戲功能開發中！", ephemeral=True)

class WalletView(discord.ui.View):
    def __init__(self, target=None):
        super().__init__(timeout=None)
        self.target = target
    @discord.ui.button(label="管理餘額", style=discord.ButtonStyle.gray, custom_id="wallet_persistent_btn")
    async def manage_btn(self, interaction: discord.Interaction, b: discord.ui.Button):
        await interaction.response.send_message("請使用管理員指令調整。", ephemeral=True)

# --- Economy Cog ---
class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.command(name="sync")
    @commands.has_permissions(administrator=True) # 改成管理員即可同步
    async def sync(self, ctx):
        synced = await self.bot.tree.sync()
        await ctx.send(f"✅ 已同步 {len(synced)} 個指令到 Discord！")

    @app_commands.command(name="balance", description="查詢餘額")
    async def balance(self, interaction: discord.Interaction):
        data = load_data()
        bal = data.get(str(interaction.user.id), {}).get("balance", 0)
        await interaction.response.send_message(f"💰 你的餘額: **{bal}**")

async def setup(bot):
    # 註冊所有 Persistent Views
    bot.add_view(DailyView())
    bot.add_view(GameView())
    bot.add_view(WalletView())
    await bot.add_cog(Economy(bot))
    print("✅ Economy Cog 與 UI 視窗已成功載入")
