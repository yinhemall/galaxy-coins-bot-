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

class DailyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="領取每日獎勵 🚀", style=discord.ButtonStyle.secondary, custom_id="daily_btn_v4")
    async def daily_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        uid = str(interaction.user.id)
        if uid not in data: data[uid] = {"balance": 0, "last_daily": "2000-01-01", "streak": 0}
        
        user = data[uid]
        now = datetime.now()
        last_daily = datetime.fromisoformat(user.get("last_daily", "2000-01-01"))
        
        # 1. 檢查是否在 24 小時冷卻內 (小於 24 小時)
        if now - last_daily < timedelta(hours=24):
            remaining = (last_daily + timedelta(hours=24) - now)
            h = int(remaining.total_seconds() // 3600)
            m = int((remaining.total_seconds() % 3600) // 60)
            await interaction.response.send_message(
                embed=discord.Embed(description=f"⏳ **能量傳輸中...**\n請於 `{h} 小時 {m} 分鐘` 後再次訪問。", color=0x2b2d31), 
                ephemeral=True
            )
            return

        # 2. 嚴格斷簽：只要超過 24 小時沒簽，立刻重置為 1
        if now - last_daily > timedelta(hours=24):
            user["streak"] = 1
            streak_status = "❄️ 由於超過 24 小時未簽到，連續紀錄已重置。"
        else:
            user["streak"] += 1
            streak_status = f"🔥 完美連簽第 **{user['streak']}** 天！"
            
        # 3. 獎勵計算
        reward = random.randint(800, 1500)
        bonus = 10000 if user["streak"] % 7 == 0 else 0
        
        user["balance"] += (reward + bonus)
        user["last_daily"] = now.isoformat()
        save_data(data)
        
        # 4. 成功 Embed
        embed = discord.Embed(title="🌌 每日簽到成功載入", color=0xFFD700)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/你的頭像連結.png") 
        embed.description = f"━━━━━━━━━━━━━━━━━━\n\n{streak_status}\n\n"
        embed.add_field(name="💰 獲得金額", value=f"`$ {reward + bonus:,}`", inline=True)
        embed.add_field(name="💳 目前餘額", value=f"`$ {user['balance']:,}`", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="setup_daily", description="部署銀河商城頂級簽到面板")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        main = discord.Embed(
            title="🪐 **銀河商城**",
            description=(
                "━━━━━━━━━━━━━━━━━━━━\n"
                "**歡迎來到銀河商城的每日簽到系統。**\n\n"
                "🔹 **每日補給：** `$ 500 - 1,000` 貨幣\n"
                "🔹 **七日加碼：** 連續七天簽到獲得額外 `$ 5,000`\n"
                "🔹 **嚴格規則：** 超過 24 小時未領取，連續紀錄立即歸零！\n\n"
                "請點擊下方按鈕，領取今日的獎勵。"
            ),
            color=0x5865F2
        )
        main.set_thumbnail(url="https://media.discordapp.net/attachments/你的頭像連結.png")
        main.set_footer(text="Galaxy Store Persistence Engine • 嚴格模式運行中")
        
        try:
            await interaction.channel.send(embed=main, view=DailyView())
            await interaction.response.send_message("✅ 頂級簽到面板已部署。", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ 部署失敗: {e}", ephemeral=True)

async def setup(bot):
    bot.add_view(DailyView())
    await bot.add_cog(Economy(bot))
    print("✅ Premium Economy System Loaded")
