import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime
import random

# --- (前面基礎函數 load_data, save_data 請保留) ---
# ... (請保留你原本的 load_data, save_data, get_currency_name 函數)

# --- UI 類別 ---
class DailyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="領取每日獎勵 🌑", style=discord.ButtonStyle.green, custom_id="daily_persistent_btn")
    async def daily_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("簽到功能運作中！", ephemeral=True)

class GameView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    # (請保留你的遊戲選擇邏輯)

class WalletView(discord.ui.View):
    def __init__(self, target=None):
        super().__init__(timeout=None)
        self.target = target
    @discord.ui.button(label="增加餘額", style=discord.ButtonStyle.green, custom_id="add_btn_id")
    async def add_btn(self, interaction: discord.Interaction, b: discord.ui.Button):
        await interaction.response.send_message("請使用 Modal 進行調整", ephemeral=True)

# --- Economy Cog ---
class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    # 強制同步指令 (放在這裡最保險)
    @commands.command(name="sync")
    @commands.is_owner()
    async def sync(self, ctx):
        synced = await self.bot.tree.sync()
        await ctx.send(f"✅ 已同步 {len(synced)} 個指令到全域！")

    @app_commands.command(name="balance", description="查詢餘額")
    async def balance(self, interaction: discord.Interaction):
        await interaction.response.send_message("餘額查詢功能")

async def setup(bot):
    bot.add_view(DailyView())
    bot.add_view(GameView())
    bot.add_view(WalletView())
    await bot.add_cog(Economy(bot))
    print("✅ Cog 與指令同步系統已載入")
