import discord
from discord.ext import commands
from discord import app_commands, ui
import random
import os
from datetime import datetime, timedelta
from pymongo import MongoClient

# --- MongoDB 與原有的函數維持不變 ---
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["GalaxyBot"]
users_col = db["users"]
settings_col = db["settings"]

def load_data():
    all_users = list(users_col.find({}))
    users_dict = {str(u["_id"]): {k: v for k, v in u.items() if k != "_id"} for u in all_users}
    all_settings = list(settings_col.find({}))
    guild_dict = {str(s["_id"]): {k: v for k, v in s.items() if k != "_id"} for s in all_settings}
    return {"guild_settings": guild_dict, "users": users_dict}

def save_data(data):
    for uid, udata in data["users"].items():
        users_col.update_one({"_id": uid}, {"$set": udata}, upsert=True)
    for gid, gdata in data["guild_settings"].items():
        settings_col.update_one({"_id": gid}, {"$set": gdata}, upsert=True)

def get_token_name(guild_id):
    setting = settings_col.find_one({"_id": str(guild_id)})
    return setting.get("token_name", "貨幣") if setting else "貨幣"

# --- 新增：華麗賭場 UI ---
class BetModal(ui.Modal, title='🎰 決戰時刻 - 下注區'):
    amount = ui.TextInput(label='請輸入下注金額', style=discord.TextStyle.short, placeholder='例如: 1000')

    async def on_submit(self, interaction: discord.Interaction):
        try:
            bet_amount = int(self.amount.value)
            data = load_data()
            uid = str(interaction.user.id)
            token_name = get_token_name(interaction.guild_id)
            
            # 檢查餘額
            user_balance = data["users"].get(uid, {}).get("balance", 0)
            if user_balance < bet_amount:
                return await interaction.response.send_message("❌ 你的餘額不足以進行這場豪賭！", ephemeral=True)

            d1, d2 = random.randint(1, 6), random.randint(1, 6)
            total = d1 + d2
            win = total >= 7
            
            if win:
                data["users"][uid]["balance"] += bet_amount
                status_text = f"✅ 恭喜！骰子點數 {total}，你贏得 {bet_amount} {token_name}！"
                color = 0xFFD700
            else:
                data["users"][uid]["balance"] -= bet_amount
                status_text = f"❌ 可惜！骰子點數 {total}，你輸了 {bet_amount} {token_name}。"
                color = 0xFF0000
            
            save_data(data)
            embed = discord.Embed(title="🎲 骰子轉動結果", description=status_text, color=color)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except ValueError:
            await interaction.response.send_message("⚠️ 請輸入有效的數字！", ephemeral=True)

class CasinoView(ui.View):
    def __init__(self): super().__init__(timeout=None)

    @ui.button(label="🎲 猜大小 (骰子)", style=discord.ButtonStyle.blurple, custom_id="casino_roll_btn", emoji="🎲")
    async def roll_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BetModal())

# --- 原有的 DailyView 與 Economy Cog ---
class DailyView(discord.ui.View):
    # ... (您的原有 DailyView 程式碼保持不變，略過以節省篇幅) ...
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="領取每日獎勵 🚀", style=discord.ButtonStyle.secondary, custom_id="daily_btn_v4")
    async def daily_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        # (保持原邏輯)
        pass 

class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    # ... (您的 set_token_name, balance, transfer, leaderboard, setup_daily 保持不變) ...

    @app_commands.command(name="setup_casino", description="部署華麗賭場面板")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_casino(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✨ GALAXY COINS 豪華賭場 ✨",
            description=">>> 歡迎來到宇宙最強的交易中心！\n點擊下方按鈕即可開始你的財富傳奇。",
            color=0x00f2ff
        )
        embed.set_thumbnail(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZzV3bHh3eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/l41lTjJp90ZlP2gCs/giphy.gif")
        await interaction.channel.send(embed=embed, view=CasinoView())
        await interaction.response.send_message("✅ 賭場面板已部署。", ephemeral=True)

async def setup(bot):
    bot.add_view(DailyView())
    bot.add_view(CasinoView()) # 註冊賭場按鈕
    await bot.add_cog(Economy(bot))
