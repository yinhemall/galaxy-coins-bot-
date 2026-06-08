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

# --- 超高級 UI 簽到視窗 ---
class DailyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(
        label="領取每日獎勵 🪐", 
        style=discord.ButtonStyle.secondary, 
        custom_id="daily_btn_v3"
    )
    async def daily_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        uid = str(interaction.user.id)
        if uid not in data: data[uid] = {"balance": 0, "last_daily": "2000-01-01", "streak": 0}
        
        user = data[uid]
        now = datetime.now()
        last_daily = datetime.fromisoformat(user.get("last_daily", "2000-01-01"))
        
        # 1. 嚴格 24 小時冷卻
        if now - last_daily < timedelta(hours=24):
            remaining = (last_daily + timedelta(hours=24) - now)
            h = int(remaining.total_seconds() // 3600)
            m = int((remaining.total_seconds() % 3600) // 60)
            
            emb = discord.Embed(description=f"⏳ **能量補充中...**\n請於 `{h} 小時 {m} 分鐘` 後再次訪問銀河。", color=0x2b2d31)
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

        # 2. 嚴格斷簽邏輯：超過 48 小時沒簽，streak 歸零
        if now - last_daily > timedelta(hours=48):
            user["streak"] = 1
            streak_status = "❄️ 連續紀錄已中斷，重新開始計算。"
        else:
            user["streak"] += 1
            streak_status = f"🔥 連續簽到第 **{user['streak']}** 天！"
            
        # 3. 獎勵計算
        reward = random.randint(600, 1200)
        bonus = 0
        if user["streak"] % 7 == 0:
            bonus = 5000
            streak_status += "\n💎 **達成七日里程碑：額外獲得 5,000！**"
            
        user["balance"] += (reward + bonus)
        user["last_daily"] = now.isoformat()
        save_data(data)
        
        # 4. 超高級成功 Embed
        embed = discord.Embed(title="🌌 銀河補給成功載入", color=0xFFD700)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.description = f"━━━━━━━━━━━━━━━━━━\n\n{streak_status}\n\n"
        embed.add_field(name="💰 獲得金額", value=f"`$ {reward + bonus:,}`", inline=True)
        embed.add_field(name="💳 目前餘額", value=f"`$ {user['balance']:,}`", inline=True)
        embed.set_footer(text="Galaxy Mall Persistence Engine • 穩定運行中")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# --- Economy Cog ---
class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="setup_daily", description="發送銀河商城高級簽到面板")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        # 第一個 Embed：標題橫幅
        banner = discord.Embed(color=0x5865F2)
        banner.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMDRkNjRjNjRkNjRkNjRkNjRkNjRkNjRkNjRkNjRkNjRkNjRkNjRkNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKVUn7iM8FMEU24/giphy.gif")
        
        # 第二個 Embed：主要說明
        main = discord.Embed(
            title="🪐 **GALAXY MALL 每日簽到系統**",
            description=(
                "━━━━━━━━━━━━━━━━━━━━\n"
                "**探索銀河的禮物，每日領取專屬補給。**\n\n"
                "🔹 **基礎獎勵：** `$ 600 - 1,200` 貨幣\n"
                "🔹 **七日加碼：** 連續七天簽到獲得額外 `$ 5,000`\n"
                "🔹 **嚴格規則：** 超過 48 小時未領取將重置連續紀錄\n\n"
                "請點擊下方按鈕開始領取程序。"
            ),
            color=0x5865F2
        )
        main.set_footer(text="Administrator Setup Required • 授權管理員已部署")
        
        try:
            # 發送多重 Embed 達到高級感
            await interaction.channel.send(embeds=[banner, main], view=DailyView())
            await interaction.response.send_message("✅ 頂級簽到面板已部署。", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ 部署失敗: {e}", ephemeral=True)

async def setup(bot):
    bot.add_view(DailyView())
    await bot.add_cog(Economy(bot))
    print("✅ Premium Economy System Loaded")

這份 code 的進步點：
1.  **多重 Embed (Embeds List)**：我們會先發送一張動態的星空圖，下方才是正式的面板，這能營造出極其專業的開場。
2.  **特殊的排版**：使用 `━━━━━━━━━━` 這種長線條區隔，讓訊息看起來像是一個真正的軟體介面。
3.  **格式化數字**：使用 `:,`（例如 `10,000`）讓金額顯示更有質感。
4.  **按鈕表情**：使用了 `secondary`（灰黑色）按鈕搭配 `🪐` 表情，走的是低調奢華風格。

部署完後，請執行 `!sync`，然後輸入 `/setup_daily` 看看成果！這種高級感正是目前 Discord 頂尖商城機器人的標配。
