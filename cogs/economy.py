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
        now = datetime.now()

        # 1. 首次簽到處理
        if uid not in data:
            data[uid] = {"balance": 1000, "last_daily": now.isoformat(), "streak": 1}
            save_data(data)
            await self.send_success_embed(interaction, 1, 1000, 1000, "🎉 歡迎加入！首次簽到已啟用。")
            return

        user = data[uid]
        last_daily = datetime.fromisoformat(user.get("last_daily", "2000-01-01"))
        
        # 2. 冷卻判斷 (24小時)
        if now - last_daily < timedelta(hours=24):
            remaining = (last_daily + timedelta(hours=24) - now)
            h, m = int(remaining.total_seconds() // 3600), int((remaining.total_seconds() % 3600) // 60)
            await interaction.response.send_message(
                embed=discord.Embed(description=f"⏳ **簽到冷卻中...**\n請於 `{h} 小時 {m} 分鐘` 後再次嘗試。", color=0x2b2d31), 
                ephemeral=True
            )
            return

        # 3. 嚴格斷簽 (超過 24 小時則重置)
        if now - last_daily > timedelta(hours=24):
            user["streak"] = 1
            status_msg = "❄️ 超過 24 小時未簽到，連簽紀錄已重置為 1。"
        else:
            user["streak"] += 1
            status_msg = f"🔥 完美連簽第 **{user['streak']}** 天！"
            
        # 4. 獎勵與結算
        reward = random.randint(800, 1500)
        bonus = 5000 if user["streak"] % 7 == 0 else 0
        user["balance"] += (reward + bonus)
        user["last_daily"] = now.isoformat()
        save_data(data)
        
        await self.send_success_embed(interaction, user["streak"], reward, user["balance"], status_msg, bonus)

    async def send_success_embed(self, interaction, streak, reward, balance, status, bonus=0):
        embed = discord.Embed(title="🌌 簽到系統成功載入", color=0xFFD700)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/你的頭像連結.png") 
        embed.description = f"━━━━━━━━━━━━━━━━━━\n\n{status}\n\n"
        embed.add_field(name="📅 連續簽到", value=f"`{streak} 天`", inline=True)
        embed.add_field(name="💰 本次獲得", value=f"`$ {reward + bonus:,}`", inline=True)
        embed.add_field(name="💳 目前餘額", value=f"`$ {balance:,}`", inline=True)
        embed.set_footer(text="Galaxy Store Persistence Engine • 嚴格模式運行中")
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
                "🔹 **嚴格規則：** 超過 24 小時未領取，連簽紀錄立即歸零！\n\n"
                "請點擊下方按鈕，領取今日的獎勵。"
            ),
            color=0x5865F2
        )
        main.set_thumbnail(url="https://media.discordapp.net/attachments/你的頭像連結.png")
        await interaction.channel.send(embed=main, view=DailyView())
        await interaction.response.send_message("✅ 頂級簽到面板已部署。", ephemeral=True)

async def setup(bot):
    bot.add_view(DailyView())
    await bot.add_cog(Economy(bot))
