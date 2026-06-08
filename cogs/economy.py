import discord
from discord.ext import commands
from discord import app_commands
import json
import os

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

# --- 互動視窗 ---
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
            await interaction.response.send_message(f"✅ 已完成！{self.target_member.display_name} 餘額已更新。", ephemeral=True)
        except: await interaction.response.send_message("❌ 請輸入有效的數字。", ephemeral=True)

class WalletView(discord.ui.View):
    def __init__(self, target_member):
        super().__init__(timeout=None)
        self.target_member = target_member

    @discord.ui.button(label="增加餘額", style=discord.ButtonStyle.green, custom_id="add_money_btn")
    async def add_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator: return await interaction.response.send_message("❌ 無權限", ephemeral=True)
        await interaction.response.send_modal(AmountModal("add", self.target_member))

    @discord.ui.button(label="扣除餘額", style=discord.ButtonStyle.red, custom_id="sub_money_btn")
    async def sub_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator: return await interaction.response.send_message("❌ 無權限", ephemeral=True)
        await interaction.response.send_modal(AmountModal("sub", self.target_member))

# --- 經濟系統 Cog ---
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
        
        # 僅當操作者是管理員時才顯示按鈕
        if interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=embed, view=WalletView(target))
        else:
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    # 註冊永久性視窗
    bot.add_view(WalletView(None))
    await bot.add_cog(Economy(bot))
    print("✅ Economy Cog 已註冊，管理員錢包功能已啟用！")
