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

# --- 超高級 UI 簽到視窗 ---
class DailyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(
        label="領取每日補給 🚀", 
        style=discord.ButtonStyle.secondary, 
        custom_id="daily_btn_v4"
    )
    async def daily_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        uid = str(interaction.user.id)
        # 初始化使用者資料 (加入頭像 URL 欄位供未來擴充)
        if uid not in data: data[uid] = {"balance": 0, "last_daily": "2000-01-01", "streak": 0, "avatar_url": None}
        
        user = data[uid]
        now = datetime.now()
        last_daily = datetime.fromisoformat(user.get("last_daily", "2000-01-01"))
        
        # 1. 嚴格 24 小時冷卻
        if now - last_daily < timedelta(hours=24):
            remaining = (last_daily + timedelta(hours=24) - now)
            h = int(remaining.total_seconds() // 3600)
            m = int((remaining.total_seconds() % 3600) // 60)
            
            emb = discord.Embed(description=f"⏳ **時空傳送冷卻中...**\n請於 `{h} 小時 {m} 分鐘` 後再次嘗試訪問。", color=0x2b2d31)
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

        # 2. 嚴格斷簽邏輯：超過 48 小時沒簽，streak 歸零
        if now - last_daily > timedelta(hours=48):
            user["streak"] = 1
            streak_status = "❄️ 由於長時間未訪問，連續紀錄已重置。"
        else:
            user["streak"] += 1
            streak_status = f"🔥 已連續訪問銀河第 **{user['streak']}** 天！"
            
        # 3. 獎勵計算
        reward = random.randint(800, 1500) # 稍微提升基礎獎勵凸顯高級感
        bonus = 0
        if user["streak"] % 7 == 0:
            bonus = 10000 # 提升七日獎勵
            streak_status += "\n🏆 **達成週年慶典：額外獲贈 10,000！**"
            
        user["balance"] += (reward + bonus)
        user["last_daily"] = now.isoformat()
        save_data(data)
        
        # 4. 超高級成功 Embed (替換 thumbnail 為商城頭像)
        embed = discord.Embed(title="🌌 銀河補給成功載入", color=0xFFD700)
        # 這裡是你的銀河商城頭像 URL
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1111111111111111111/2222222222222222222/avatar.png") 
        embed.description = f"━━━━━━━━━━━━━━━━━━\n\n{streak_status}\n\n"
        embed.add_field(name="💰 獲得金額", value=f"`$ {reward + bonus:,}`", inline=True)
        embed.add_field(name="💳 目前餘額", value=f"`$ {user['balance']:,}`", inline=True)
        embed.set_footer(text=f"{interaction.user.display_name} • 感謝您的光臨")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# --- Economy Cog ---
class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="setup_daily", description="部署銀河商城頂級簽到面板")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        # 單一 Embed：標題橫幅 (替換 thumbnail 為商城頭像)
        main = discord.Embed(
            title="🪐 **GALAXY MALL 銀河商城**",
            description=(
                "━━━━━━━━━━━━━━━━━━━━\n"
                "**歡迎來到星際貿易的中心。**\n\n"
                "🔹 **每日補給：** `$ 800 - 1,500` 貨幣\n"
                "🔹 **週年慶典：** 連續七天簽到獲得額外 `$ 10,000`\n"
                "🔹 **嚴格規則：** 超過 48 小時未領取將重置連續紀錄\n\n"
                "請點擊下方按鈕，開啟今日的星際之旅。"
            ),
            color=0x5865F2
        )
        # 這裡是你的銀河商城頭像 URL
        main.set_thumbnail(url="https://media.discordapp.net/attachments/1111111111111111111/2222222222222222222/avatar.png") 
        main.set_footer(text="Galaxy Mall Persistence Engine • 穩定運行中")
        
        try:
            # 發送單一 Embed，利用頭像凸顯品牌
            await interaction.channel.send(embed=main, view=DailyView())
            await interaction.response.send_message("✅ 頂級簽到面板已部署。", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ 部署失敗: {e}", ephemeral=True)

async def setup(bot):
    bot.add_view(DailyView())
    await bot.add_cog(Economy(bot))
    print("✅ Premium Economy System Loaded")
