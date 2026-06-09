Import discord
from discord.ext import commands
from discord import app_commands
import random
import os
from datetime import datetime, timedelta
from pymongo import MongoClient

# --- MongoDB 連線設定 ---
# 確保你在 Railway 的 Variables 中設定了 MONGO_URI
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["GalaxyBot"]  # 資料庫名稱
users_col = db["users"]   # 用戶資料集合
settings_col = db["settings"] # 設定集合

# --- 修正後的基礎資料處理 ---
def load_data():
    """模擬舊版結構，從 MongoDB 抓取所有資料"""
    all_users = list(users_col.find({}))
    users_dict = {str(u["_id"]): {k: v for k, v in u.items() if k != "_id"} for u in all_users}
    
    all_settings = list(settings_col.find({}))
    guild_dict = {str(s["_id"]): {k: v for k, v in s.items() if k != "_id"} for s in all_settings}
    
    return {"guild_settings": guild_dict, "users": users_dict}

def save_data(data):
    """將資料更新回 MongoDB"""
    # 更新使用者資料
    for uid, udata in data["users"].items():
        users_col.update_one({"_id": uid}, {"$set": udata}, upsert=True)
    
    # 更新設定資料
    for gid, gdata in data["guild_settings"].items():
        settings_col.update_one({"_id": gid}, {"$set": gdata}, upsert=True)

def get_token_name(guild_id):
    setting = settings_col.find_one({"_id": str(guild_id)})
    return setting.get("token_name", "貨幣") if setting else "貨幣"

# --- 原有的簽到邏輯 ---
class DailyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="領取每日獎勵 🚀", style=discord.ButtonStyle.secondary, custom_id="daily_btn_v4")
    async def daily_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        uid = str(interaction.user.id)
        gid = str(interaction.guild_id)
        token_name = get_token_name(gid)
        now = datetime.now()

        # 1. 首次簽到處理
        if uid not in data["users"]:
            reward = random.randint(500, 1000)
            data["users"][uid] = {"balance": reward, "last_daily": now.isoformat(), "streak": 1}
            save_data(data)
            await self.send_success_embed(interaction, 1, reward, reward, token_name, "🎉 歡迎加入！首次簽到已啟用。")
            return

        user = data["users"][uid]
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
        reward = random.randint(500, 1000)
        bonus = 5000 if user["streak"] % 7 == 0 else 0
        user["balance"] += (reward + bonus)
        user["last_daily"] = now.isoformat()
        save_data(data)
        
        await self.send_success_embed(interaction, user["streak"], reward + bonus, user["balance"], token_name, status_msg)

    async def send_success_embed(self, interaction, streak, total_reward, balance, token_name, status):
        embed = discord.Embed(
            title="🪐 銀河商城", 
            color=0x5865F2 
        )
        embed.description = (
            f"------------------------------\n"
            f"{status}\n\n"
            f"📅 **連續簽到**：`{streak} 天`\n"
            f"💰 **本次獲得**：`{total_reward:,} {token_name}`\n"
            f"💳 **目前餘額**：`{balance:,} {token_name}`"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# --- 經濟指令集 ---
class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="set_token_name", description="設置此伺服器的代幣名稱")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_token_name(self, interaction: discord.Interaction, name: str):
        data = load_data()
        gid = str(interaction.guild_id)
        if "guild_settings" not in data: data["guild_settings"] = {}
        data["guild_settings"][gid] = {"token_name": name}
        save_data(data)
        await interaction.response.send_message(f"✅ 代幣名稱已更新為: **{name}**", ephemeral=True)

    @app_commands.command(name="balance", description="查看自己的餘額")
    async def balance(self, interaction: discord.Interaction):
        data = load_data()
        uid, gid = str(interaction.user.id), str(interaction.guild_id)
        token_name = get_token_name(gid)
        balance = data["users"].get(uid, {}).get("balance", 0)
        await interaction.response.send_message(f"💳 目前餘額: `{balance:,} {token_name}`", ephemeral=True)

    @app_commands.command(name="transfer", description="轉帳給其他成員")
    async def transfer(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount <= 0: return await interaction.response.send_message("❌ 金額需大於 0。", ephemeral=True)
        data = load_data()
        sender, receiver = str(interaction.user.id), str(member.id)
        gid = str(interaction.guild_id)
        token_name = get_token_name(gid)
        
        if data["users"].get(sender, {}).get("balance", 0) < amount:
            return await interaction.response.send_message("❌ 餘額不足。", ephemeral=True)
        
        data["users"][sender]["balance"] -= amount
        if receiver not in data["users"]: data["users"][receiver] = {"balance": 0, "last_daily": "2000-01-01", "streak": 0}
        data["users"][receiver]["balance"] += amount
        save_data(data)
        await interaction.response.send_message(f"✅ 成功轉帳 `{amount:,} {token_name}` 給 {member.mention}！")

    @app_commands.command(name="leaderboard", description="顯示伺服器財富排行榜")
    async def leaderboard(self, interaction: discord.Interaction):
        data = load_data()
        gid = str(interaction.guild_id)
        token_name = get_token_name(gid)
        sorted_users = sorted(data["users"].items(), key=lambda x: x[1].get("balance", 0), reverse=True)[:10]
        
        embed = discord.Embed(
            title="🌌 **貨幣排行榜** 🪐", 
            description="這裡是伺服器最有錢的人：\n━━━━━━━━━━━━━━━━━━━━", 
            color=0x00F0FF
        )
        
        desc = ""
        for i, (uid, info) in enumerate(sorted_users, start=1):
            user_display = f"<@{uid}>"
            balance = info.get('balance', 0)
            rank_icon = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"`#{i}` ")
            desc += f"{rank_icon} {user_display}\n💰 擁有餘額：`{balance:,} {token_name}`\n\n"
        
        embed.description += f"\n{desc}" if desc else "\n目前還沒有人擁有財富！"
        embed.set_footer(text="Galaxy Store Persistence Engine • 數據每秒同步中", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setup_daily", description="部署銀河商城頂級簽到面板")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        token_name = get_token_name(interaction.guild_id)
        main = discord.Embed(
            title="🪐 **銀河商城**",
            description=(
                f"歡迎來到銀河商城的每日簽到系統。\n\n"
                f"🔹 **每日補給**：$ 500 - 1,000 貨幣\n"
                f"🔹 **七日加碼**：連續七天簽到獲得額外 $ 5,000\n"
                f"🔹 **嚴格規則**：超過一天未領取，連簽紀錄立即歸零！\n\n"
                f"請點擊下方按鈕，領取今日的獎勵。"
            ),
            color=0x5865F2
        )
        await interaction.channel.send(embed=main, view=DailyView())
        await interaction.response.send_message("✅ 頂級簽到面板已部署。", ephemeral=True)

async def setup(bot):
    bot.add_view(DailyView())
    await bot.add_cog(Economy(bot))

幫我
