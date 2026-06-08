import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime
import random

# 設定檔案路徑
DATA_FILE = "data.json"
CONFIG_FILE = "config.json"

# --- 資料庫函數 ---
def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

def get_currency_name():
    if not os.path.exists(CONFIG_FILE): return "銀河幣"
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f).get("currency_name", "銀河幣")
    except: return "銀河幣"

# --- 按鈕與互動系統 ---

class AmountModal(discord.ui.Modal):
    def __init__(self, action, target_member):
        super().__init__(title=f"{'增加' if action == 'add' else '扣除'}餘額")
        self.action = action
        self.target_member = target_member
    
    amount = discord.ui.TextInput(label='請輸入金額', style=discord.TextStyle.short, placeholder='例如: 100', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amt = int(self.amount.value)
            if amt <= 0: raise ValueError
            data = load_data()
            uid = str(self.target_member.id)
            if uid not in data: data[uid] = {"balance": 0, "last_daily": "2000-01-01 00:00:00", "streak": 0}
            
            if self.action == "add":
                data[uid]["balance"] += amt
            else:
                data[uid]["balance"] = max(0, data[uid]["balance"] - amt)
            
            save_data(data)
            await interaction.response.send_message(f"✅ 已完成操作：{self.target_member.display_name} 的餘額已變更。", ephemeral=True)
        except: await interaction.response.send_message("❌ 請輸入有效的數字。", ephemeral=True)

class WalletView(discord.ui.View):
    def __init__(self, target_member):
        super().__init__(timeout=60)
        self.target_member = target_member

    @discord.ui.button(label="增加餘額", style=discord.ButtonStyle.green)
    async def add_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator: return await interaction.response.send_message("❌ 無權限", ephemeral=True)
        await interaction.response.send_modal(AmountModal("add", self.target_member))

    @discord.ui.button(label="扣除餘額", style=discord.ButtonStyle.red)
    async def sub_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator: return await interaction.response.send_message("❌ 無權限", ephemeral=True)
        await interaction.response.send_modal(AmountModal("sub", self.target_member))

# --- 其他系統 (DailyView, GameView 保持不變) ---
# (為了縮短篇幅，請保留你原本的 DailyView, GambleModal, GameSelect 等邏輯)
# ... [請繼續使用你原本的簽到與遊戲邏輯] ...

class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="balance", description="查詢餘額與管理錢包")
    @app_commands.guild_only()
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        curr = get_currency_name()
        data = load_data()
        bal = data.get(str(target.id), {"balance": 0})["balance"]
        
        embed = discord.Embed(title=f"💰 {target.display_name} 的錢包", description=f"目前餘額: **{bal}** {curr}", color=discord.Color.gold())
        view = WalletView(target) if interaction.user.guild_permissions.administrator else None
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="leaderboard_streak", description="查看連續簽到排行榜")
    async def leaderboard_streak(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        sorted_users = sorted([(uid, info.get("streak", 0)) for uid, info in data.items()], key=lambda x: x[1], reverse=True)[:10]
        if not sorted_users: return await interaction.followup.send("目前無資料。")
        msg = "🏆 **連續簽到排行榜 (Top 10)**\n\n"
        for i, (uid, streak) in enumerate(sorted_users, 1):
            msg += f"{i}. <@{uid}>: **{streak}** 天\n"
        await interaction.followup.send(msg)

    # 這裡保留你原本的 setup_daily, setup_games 指令即可
    @app_commands.command(name="setup_daily", description="[管理員] 發送簽到")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        # ... 原本邏輯 ...
        pass

async def setup(bot): await bot.add_cog(Economy(bot))
