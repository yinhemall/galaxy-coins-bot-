import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime
import random

DATA_FILE = "data.json"
CONFIG_FILE = "config.json"

# --- 基礎函數 ---
def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

# --- 簽到與賭博 UI ---
class DailyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="領取每日獎勵 🌑", style=discord.ButtonStyle.green, custom_id="daily_btn")
    async def daily_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        uid = str(interaction.user.id)
        now = datetime.datetime.now()
        
        if uid not in data: data[uid] = {"balance": 0, "last_daily": "2000-01-01 00:00:00", "streak": 0}
        last_daily = datetime.datetime.strptime(data[uid]["last_daily"], "%Y-%m-%d %H:%M:%S")
        diff = now - last_daily

        if diff > datetime.timedelta(hours=48):
            data[uid]["streak"] = 1
        elif diff >= datetime.timedelta(hours=24):
            data[uid]["streak"] += 1
        else:
            return await interaction.response.send_message("⏳ 冷卻中，請明天再來！", ephemeral=True)

        reward = random.randint(100, 300)
        bonus = 1000 if data[uid]["streak"] % 7 == 0 else 0
        data[uid]["balance"] += (reward + bonus)
        data[uid]["last_daily"] = now.strftime("%Y-%m-%d %H:%M:%S")
        save_data(data)
        
        msg = f"✅ 簽到成功！獲得 {reward} 幣。\n🔥 連續簽到: {data[uid]['streak']} 天"
        if bonus: msg += f"\n🎁 恭喜達成 7 天倍數！加贈 1000 幣！"
        await interaction.response.send_message(msg, ephemeral=True)

class GambleModal(discord.ui.Modal, title='賭博下注'):
    amount = discord.ui.TextInput(label='請輸入下注金額', placeholder='例如: 100', required=True)
    def __init__(self, game): super().__init__(); self.game = game
    async def on_submit(self, interaction: discord.Interaction):
        amt = int(self.amount.value)
        data = load_data()
        uid = str(interaction.user.id)
        if data.get(uid, {}).get("balance", 0) < amt: return await interaction.response.send_message("❌ 餘額不足！", ephemeral=True)
        
        win = random.choice([True, False])
        data[uid]["balance"] += (amt if win else -amt)
        save_data(data)
        await interaction.response.send_message(f"🎲 遊戲結束：{'贏了' if win else '輸了'}，餘額變動: {amt}", ephemeral=True)

class GameSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label="骰子比大小", emoji="🎲"), discord.SelectOption(label="拉霸機", emoji="🎰")]
        super().__init__(placeholder="請選擇遊戲...", options=options)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(GambleModal(self.values[0]))

class GameView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None); self.add_item(GameSelect())

# --- 管理員錢包 UI ---
class WalletView(discord.ui.View):
    def __init__(self, target):
        super().__init__(timeout=None)
        self.target = target
    @discord.ui.button(label="增加餘額", style=discord.ButtonStyle.green, custom_id="add_money_btn")
    async def add_btn(self, interaction: discord.Interaction, b: discord.ui.Button):
        await interaction.response.send_modal(AmountModal("add", self.target))
    @discord.ui.button(label="扣除餘額", style=discord.ButtonStyle.red, custom_id="sub_money_btn")
    async def sub_btn(self, interaction: discord.Interaction, b: discord.ui.Button):
        await interaction.response.send_modal(AmountModal("sub", self.target))

class AmountModal(discord.ui.Modal, title="調整餘額"):
    amount = discord.ui.TextInput(label="金額", style=discord.TextStyle.short)
    def __init__(self, action, target): super().__init__(); self.action = action; self.target = target
    async def on_submit(self, interaction: discord.Interaction):
        amt = int(self.amount.value)
        data = load_data()
        uid = str(self.target.id)
        if uid not in data: data[uid] = {"balance": 0, "streak": 0}
        data[uid]["balance"] += amt if self.action == "add" else -amt
        save_data(data)
        await interaction.response.send_message(f"✅ 已處理 {amt}。", ephemeral=True)

# --- Cog ---
class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="balance", description="查詢餘額")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        data = load_data()
        bal = data.get(str(target.id), {"balance": 0}).get("balance", 0)
        view = WalletView(target) if interaction.user.guild_permissions.administrator else None
        await interaction.response.send_message(f"💰 {target.display_name} 餘額: **{bal}**", view=view)

    @app_commands.command(name="setup_daily", description="發送簽到介面")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await channel.send("🌑 **每日簽到**", view=DailyView())
        await interaction.response.send_message(f"已發送至 {channel.mention}", ephemeral=True)

    @app_commands.command(name="setup_games", description="發送遊戲介面")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_games(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await channel.send("🎮 **銀河遊戲廳**", view=GameView())
        await interaction.response.send_message(f"已發送至 {channel.mention}", ephemeral=True)

async def setup(bot):
    bot.add_view(DailyView())
    bot.add_view(GameView())
    bot.add_view(WalletView(None))
    await bot.add_cog(Economy(bot))
