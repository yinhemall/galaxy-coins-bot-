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

# --- UI 介面類別 ---
class DailyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="領取每日獎勵 🌑", style=discord.ButtonStyle.green, custom_id="daily_btn_v2")
    async def daily_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 這是簽到核心邏輯
        data = load_data()
        uid = str(interaction.user.id)
        if uid not in data: data[uid] = {"balance": 0, "last_daily": "2000-01-01", "streak": 0}
        
        user = data[uid]
        now = datetime.now()
        last_daily = datetime.fromisoformat(user.get("last_daily", "2000-01-01"))
        
        # 簡單冷卻判斷
        if now - last_daily < timedelta(hours=24):
            await interaction.response.send_message("⏳ 正在冷卻中，請稍後再來！", ephemeral=True)
            return
            
        user["balance"] += 500
        user["last_daily"] = now.isoformat()
        save_data(data)
        await interaction.response.send_message(f"✅ 簽到成功！獲得 500 貨幣。目前餘額: {user['balance']}", ephemeral=True)

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
        embed = discord.Embed(
            title="📆 銀河商城每日簽到", 
            description="歡迎領取每日補給！點擊下方按鈕領取獎勵。", 
            color=discord.Color.blue()
        )
        
        try:
            # 這是發送到頻道的動作
            await interaction.channel.send(embed=embed, view=DailyView())
            # 這是給發送者的私人回饋
            await interaction.response.send_message("✅ 簽到面板已部署！", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ 錯誤：我沒有在該頻道發送訊息或 Embed 的權限！", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ 錯誤: {e}", ephemeral=True)

async def setup(bot):
    bot.add_view(DailyView())
    bot.add_view(GameView())
    bot.add_view(WalletView())
    await bot.add_cog(Economy(bot))
    print("✅ Economy Cog 與 UI 視窗已成功載入")
