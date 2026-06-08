import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
from datetime import datetime, timedelta

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: 
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- UI 介面 ---
class DailyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="領取每日獎勵 🌑", style=discord.ButtonStyle.green, custom_id="daily_persistent_btn")
    async def daily_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        uid = str(interaction.user.id)
        
        if uid not in data: data[uid] = {"balance": 0, "last_daily": "2000-01-01", "streak": 0}
        
        user = data[uid]
        now = datetime.now()
        last_daily = datetime.fromisoformat(user.get("last_daily", "2000-01-01"))
        
        # 檢查是否已過 24 小時
        if now - last_daily < timedelta(hours=24):
            remaining = (last_daily + timedelta(hours=24) - now)
            await interaction.response.send_message(f"⏳ 請在 {int(remaining.total_seconds() // 3600)} 小時後再領取。", ephemeral=True)
            return

        # 計算連續簽到
        if now - last_daily < timedelta(hours=48):
            user["streak"] += 1
        else:
            user["streak"] = 1
            
        # 發獎
        reward = random.randint(500, 1000)
        extra = 0
        if user["streak"] >= 7:
            extra = 2000
            user["streak"] = 0 # 歸零重新計算
            msg = f"🎉 連續簽到 7 天！獲得隨機獎勵 {reward} + 額外獎勵 {extra}！"
        else:
            msg = f"✅ 簽到成功！獲得 {reward}，已連續簽到 {user['streak']} 天。"

        user["balance"] += (reward + extra)
        user["last_daily"] = now.isoformat()
        save_data(data)
        
        await interaction.response.send_message(msg, ephemeral=True)

# (GameView 和 WalletView 保持原樣即可)
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
    @commands.has_permissions(administrator=True)
    async def sync(self, ctx):
        synced = await self.bot.tree.sync()
        await ctx.send(f"✅ 已同步 {len(synced)} 個指令到 Discord！")

    @app_commands.command(name="balance", description="查詢餘額")
    async def balance(self, interaction: discord.Interaction):
        data = load_data()
        bal = data.get(str(interaction.user.id), {}).get("balance", 0)
        await interaction.response.send_message(f"💰 你的餘額: **{bal}**")

    @app_commands.command(name="setup_daily", description="發送簽到面板 (管理員)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        await interaction.channel.send("點擊下方按鈕進行每日簽到：", view=DailyView())
        await interaction.response.send_message("簽到面板已發送！", ephemeral=True)

    @app_commands.command(name="setup_games", description="發送遊戲面板 (管理員)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_games(self, interaction: discord.Interaction):
        await interaction.channel.send("選擇你想玩的遊戲：", view=GameView())
        await interaction.response.send_message("遊戲面板已發送！", ephemeral=True)

async def setup(bot):
    bot.add_view(DailyView())
    bot.add_view(GameView())
    bot.add_view(WalletView())
    await bot.add_cog(Economy(bot))
    print("✅ Economy Cog 與 UI 視窗已成功載入")
