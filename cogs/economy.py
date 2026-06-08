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
    
    @discord.ui.button(label="領取每日獎勵 🪐", style=discord.ButtonStyle.secondary, custom_id="daily_btn_v3")
    async def daily_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        uid = str(interaction.user.id)
        if uid not in data: data[uid] = {"balance": 0, "last_daily": "2000-01-01", "streak": 0}
        
        user = data[uid]
        now = datetime.now()
        last_daily = datetime.fromisoformat(user.get("last_daily", "2000-01-01"))
        
        if now - last_daily < timedelta(hours=24):
            remaining = (last_daily + timedelta(hours=24) - now)
            h, m = int(remaining.total_seconds() // 3600), int((remaining.total_seconds() % 3600) // 60)
            await interaction.response.send_message(embed=discord.Embed(description=f"⏳ **能量補充中...**\n請於 `{h} 小時 {m} 分鐘` 後再次訪問。", color=0x2b2d31), ephemeral=True)
            return

        user["streak"] = user["streak"] + 1 if now - last_daily < timedelta(hours=48) else 1
        reward = random.randint(600, 1200)
        bonus = 5000 if user["streak"] % 7 == 0 else 0
        user["balance"] += (reward + bonus)
        user["last_daily"] = now.isoformat()
        save_data(data)
        
        embed = discord.Embed(title="🌌 銀河補給成功載入", color=0xFFD700)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.description = f"🔥 連續簽到第 **{user['streak']}** 天！" + ("\n💎 **七日里程碑獎勵！**" if bonus else "")
        embed.add_field(name="💰 獲得", value=f"`$ {reward + bonus:,}`", inline=True)
        embed.add_field(name="💳 餘額", value=f"`$ {user['balance']:,}`", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="setup_daily", description="發送銀河商城高級簽到面板")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        banner = discord.Embed(color=0x5865F2)
        banner.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMDRkNjRjNjRkNjRkNjRkNjRkNjRkNjRkNjRkNjRkNjRkNjRkNjRkNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKVUn7iM8FMEU24/giphy.gif")
        main = discord.Embed(title="🪐 GALAXY MALL 每日簽到", description="探索銀河的禮物，每日領取專屬補給。", color=0x5865F2)
        main.set_footer(text="Administrator Setup Required")
        await interaction.channel.send(embeds=[banner, main], view=DailyView())
        await interaction.response.send_message("✅ 頂級簽到面板已部署。", ephemeral=True)

async def setup(bot):
    bot.add_view(DailyView())
    await bot.add_cog(Economy(bot))
    print("✅ Premium Economy System Loaded")
