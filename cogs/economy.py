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

# --- 介面類別 (UI) ---
class DailyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="領取每日獎勵 🌑", style=discord.ButtonStyle.green, custom_id="daily_btn_v2")
    async def daily_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        uid = str(interaction.user.id)
        if uid not in data: data[uid] = {"balance": 0, "last_daily": "2000-01-01", "streak": 0}
        
        user = data[uid]
        now = datetime.now()
        last_daily = datetime.fromisoformat(user.get("last_daily", "2000-01-01"))
        
        if now - last_daily < timedelta(hours=24):
            remaining = (last_daily + timedelta(hours=24) - now)
            hours, minutes = int(remaining.total_seconds() // 3600), int((remaining.total_seconds() % 3600) // 60)
            await interaction.response.send_message(embed=discord.Embed(title="⏳ 簽到冷卻中", description=f"請在 **{hours} 小時 {minutes} 分鐘** 後再來。", color=discord.Color.red()), ephemeral=True)
            return

        user["streak"] = user["streak"] + 1 if now - last_daily < timedelta(hours=48) else 1
        reward, extra = random.randint(500, 1000), 0
        bonus_msg = ""
        
        if user["streak"] >= 7:
            extra, user["streak"] = 2000, 0 
            bonus_msg = "\n✨ **達成連簽七天：額外獲得 2,000 獎勵！**"
            
        user["balance"] += (reward + extra)
        user["last_daily"] = now.isoformat()
        save_data(data)
        
        embed = discord.Embed(title="✅ 簽到成功！", color=discord.Color.gold())
        embed.add_field(name="💰 本次獎勵", value=f"{reward} 貨幣", inline=True)
        embed.add_field(name="🔥 連續簽到", value=f"{user['streak']} 天", inline=True)
        if bonus_msg: embed.add_field(name="🎁 特別獎勵", value=bonus_msg, inline=False)
        embed.set_footer(text=f"目前餘額: {user['balance']} | 下次重置: {(now + timedelta(hours=24)).strftime('%H:%M')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class GameView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="進入遊戲廳", style=discord.ButtonStyle.blurple, custom_id="game_persistent_btn")
    async def game_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("遊戲開發中...", ephemeral=True)

class WalletView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="管理餘額", style=discord.ButtonStyle.gray, custom_id="wallet_persistent_btn")
    async def manage_btn(self, interaction: discord.Interaction, b: discord.ui.Button):
        await interaction.response.send_message("請使用管理員指令。", ephemeral=True)

# --- Economy Cog ---
class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="setup_daily", description="發送專業簽到面板")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📆 銀河商城每日簽到",
            description="歡迎領取每日補給，連簽7天額外獲得 2,000 貨幣！\n*點擊下方按鈕領取獎勵*",
            color=discord.Color.blue()
        )
        if interaction.guild.icon: embed.set_thumbnail(url=interaction.guild.icon.url)
        await interaction.channel.send(embed=embed, view=DailyView())
        await interaction.response.send_message("已部署！", ephemeral=True)

# --- 重要：setup 務必在最下方 ---
async def setup(bot):
    bot.add_view(DailyView())
    bot.add_view(GameView())
    bot.add_view(WalletView())
    await bot.add_cog(Economy(bot))
    print("✅ Economy Cog 與 UI 視窗已成功載入")
