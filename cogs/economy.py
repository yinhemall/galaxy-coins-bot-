# --- 在檔案最上方加入必要的 import (確保都有) ---
import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
from datetime import datetime, timedelta

# (load_data / save_data 函數保持不變，照舊即可)

# --- 更新後的 DailyView ---
class DailyView(discord.ui.View):
    def __init__(self): 
        super().__init__(timeout=None)
    
    @discord.ui.button(label="領取每日獎勵 🌑", style=discord.ButtonStyle.green, custom_id="daily_btn_v2")
    async def daily_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        uid = str(interaction.user.id)
        
        if uid not in data: data[uid] = {"balance": 0, "last_daily": "2000-01-01", "streak": 0}
        
        user = data[uid]
        now = datetime.now()
        last_daily = datetime.fromisoformat(user.get("last_daily", "2000-01-01"))
        
        # 檢查冷卻
        if now - last_daily < timedelta(hours=24):
            remaining = (last_daily + timedelta(hours=24) - now)
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            
            embed = discord.Embed(title="⏳ 簽到冷卻中", description=f"您太勤勞了！請在 **{hours} 小時 {minutes} 分鐘** 後再來領取。", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # 計算連續簽到 (48小時內沒簽到則重置)
        if now - last_daily < timedelta(hours=48):
            user["streak"] += 1
        else:
            user["streak"] = 1
            
        # 發獎
        reward = random.randint(500, 1000)
        extra = 0
        bonus_msg = ""
        
        if user["streak"] >= 7:
            extra = 2000
            user["streak"] = 0 
            bonus_msg = "✨ **達成連簽七天：獲得額外 2,000 獎勵！**"
            
        user["balance"] += (reward + extra)
        user["last_daily"] = now.isoformat()
        save_data(data)
        
        # 顯示結果
        embed = discord.Embed(title="✅ 簽到成功！", color=discord.Color.gold())
        embed.add_field(name="💰 本次獎勵", value=f"{reward} 貨幣", inline=True)
        embed.add_field(name="🔥 連續簽到", value=f"{user['streak']} 天", inline=True)
        if bonus_msg: embed.add_field(name="🎁 特別獎勵", value=bonus_msg, inline=False)
        embed.set_footer(text=f"目前餘額: {user['balance']} | 下次重置時間: {(now + timedelta(hours=24)).strftime('%H:%M')}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# --- Economy Cog ---
class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    # 專業面板指令
    @app_commands.command(name="setup_daily", description="發送專業簽到面板")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📆 銀河商城每日簽到",
            description=(
                "歡迎領取每日補給，提升您的貨幣餘額。\n\n"
                "**✅ 每日基礎補給**\n"
                "• 領取 500 ～ 1000 隨機貨幣。\n\n"
                "**💸 忠誠獎勵計畫**\n"
                "• 每連續簽到 7 天，額外加碼 **2,000 貨幣**。\n\n"
                "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                "*點擊下方按鈕，開始您今天的銀河冒險。*"
            ),
            color=discord.Color.blue()
        )
        if interaction.guild.icon: embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(text="Galaxy Coins System | 每日重置")
        
        await interaction.channel.send(embed=embed, view=DailyView())
        await interaction.response.send_message("✅ 專業版簽到面板已部署！", ephemeral=True)

# 確保這是在 Cog 載入後正確執行
async def setup(bot):
    bot.add_view(DailyView())
    bot.add_view(GameView())
    bot.add_view(WalletView())
    await bot.add_cog(Economy(bot))
    print("✅ Economy Cog 與 UI 視窗已成功載入")
