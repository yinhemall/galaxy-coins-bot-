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

def set_currency_name(name):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump({"currency_name": name}, f, ensure_ascii=False)

# --- 簽到系統 ---
class DailyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="領取每日獎勵 🌑", style=discord.ButtonStyle.green, custom_id="daily_button")
    async def daily_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        curr = get_currency_name()
        data = load_data()
        uid = str(interaction.user.id)
        now = datetime.datetime.now()
        if uid not in data: data[uid] = {"balance": 0, "last_daily": "2000-01-01 00:00:00", "streak": 0}
        
        last_daily = datetime.datetime.strptime(data[uid]["last_daily"], "%Y-%m-%d %H:%M:%S")
        diff = now - last_daily
        if diff >= datetime.timedelta(hours=24):
            data[uid]["streak"] = (data[uid]["streak"] + 1) if diff < datetime.timedelta(hours=48) else 1
        else:
            remaining = datetime.timedelta(hours=24) - diff
            await interaction.response.send_message(f"⏳ 冷卻中 (剩餘 {int(remaining.total_seconds()//3600)} 小時)", ephemeral=True)
            return
            
        reward = random.randint(100, 300)
        bonus = 1000 if data[uid]["streak"] % 7 == 0 else 0
        data[uid]["balance"] += (reward + bonus)
        data[uid]["last_daily"] = now.strftime("%Y-%m-%d %H:%M:%S")
        save_data(data)
        await interaction.response.send_message(f"✅ 簽到成功！獲得 {reward} {curr}。\n🔥 已連續簽到 **{data[uid]['streak']}** 天！" + (f"\n🎁 恭喜達成 7 天！加贈 1,000 {curr}！" if bonus else ""), ephemeral=True)

# --- 遊戲系統 ---
class GambleModal(discord.ui.Modal, title='賭博下注'):
    amount = discord.ui.TextInput(label='請輸入下注金額', style=discord.TextStyle.short, placeholder='例如: 100', required=True)
    def __init__(self, game_type): super().__init__(); self.game_type = game_type

    async def on_submit(self, interaction: discord.Interaction):
        curr = get_currency_name()
        try:
            amt = int(self.amount.value)
            data = load_data()
            uid = str(interaction.user.id)
            if amt <= 0 or data.get(uid, {"balance": 0})["balance"] < amt: return await interaction.response.send_message(f"❌ 餘額不足或金額無效！", ephemeral=True)

            if self.game_type == "dice":
                u, b = random.randint(1, 6), random.randint(1, 6)
                win = u > b
                data[uid]["balance"] += (amt if win else -amt)
                msg = f"{'🎉 你贏了！' if win else '💀 你輸了！'} 點數: {u} vs {b}"
            else: # 拉霸機
                symbols = ['🍒', '🍋', '🔔', '💎', '7️⃣']
                weights = [40, 30, 20, 9, 1]
                res = random.choices(symbols, weights=weights, k=3)
                win_mult = { '🍒':2, '🍋':3, '🔔':5, '💎':8, '7️⃣':15 }
                if res[0] == res[1] == res[2]:
                    data[uid]["balance"] += amt * win_mult[res[0]]
                    msg = f"🎰 {''.join(res)}\n🌟 **大獎！** 獲得 {amt * win_mult[res[0]]} {curr}！"
                else:
                    data[uid]["balance"] -= amt
                    msg = f"🎰 {''.join(res)}\n💔 可惜沒中，失去 {amt} {curr}。"
            
            save_data(data)
            await interaction.response.send_message(msg, ephemeral=True)
        except: await interaction.response.send_message("❌ 錯誤。", ephemeral=True)

class GameSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="賭博 (比大小)", description="骰子比拚運氣！", emoji="🎲"),
            discord.SelectOption(label="拉霸機 (Slots)", description="拉下搖桿，拚 3 個 7 拿大獎！", emoji="🎰")
        ]
        super().__init__(placeholder="請選擇遊戲...", options=options)
    async def callback(self, interaction: discord.Interaction):
        game = "dice" if "比大小" in self.values[0] else "slots"
        await interaction.response.send_modal(GambleModal(game))

class GameMenuView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None); self.add_item(GameSelect())

class MenuStarterView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="開啟遊戲廳 🎮", style=discord.ButtonStyle.blurple, custom_id="game_menu_btn")
    async def open_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("請選擇遊戲：", view=GameMenuView(), ephemeral=True)

# --- 經濟系統 Cog ---
class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot
    
    @app_commands.command(name="set_currency_name", description="[管理員] 修改貨幣名稱")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_currency(self, interaction: discord.Interaction, name: str):
        set_currency_name(name); await interaction.response.send_message(f"✅ 貨幣名稱已修改為: **{name}**")

    @app_commands.command(name="balance", description="查詢餘額")
    async def balance(self, interaction: discord.Interaction):
        curr = get_currency_name(); data = load_data()
        bal = data.get(str(interaction.user.id), {"balance": 0})["balance"]
        await interaction.response.send_message(f"💰 目前餘額: **{bal}** {curr}。")

    @app_commands.command(name="leaderboard_streak", description="查看連續簽到排行榜")
    async def leaderboard_streak(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        # 篩選掉數據異常的用戶，並進行排序
        sorted_users = sorted(
            [(uid, info.get("streak", 0)) for uid, info in data.items() if info.get("streak", 0) > 0], 
            key=lambda x: x[1], reverse=True
        )[:10]
        
        if not sorted_users:
            return await interaction.followup.send("目前還沒有人簽到過喔！")

        msg = "🏆 **連續簽到排行榜 (Top 10)**\n\n"
        for i, (uid, streak) in enumerate(sorted_users, 1):
            # 使用 <@uid> 格式產生標記
            msg += f"{i}. <@{uid}>: **{streak}** 天\n"
        await interaction.followup.send(msg)

    @app_commands.command(name="setup_daily", description="[管理員] 發送簽到訊息")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_daily(self, interaction: discord.Interaction):
        curr = get_currency_name()
        embed = discord.Embed(title="🌑 每日簽到", description=f"每天領取 100-300 {curr}\n🔥 連續滿 7 天加贈 1,000 {curr}！", color=discord.Color.blue())
        await interaction.channel.send(embed=embed, view=DailyView()); await interaction.response.send_message("已發送", ephemeral=True)

    @app_commands.command(name="setup_games", description="[管理員] 發送遊戲廳入口")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_games(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🎮 銀河遊戲廳", description="點擊下方按鈕進行遊戲！", color=discord.Color.green())
        await interaction.channel.send(embed=embed, view=MenuStarterView()); await interaction.response.send_message("已發送", ephemeral=True)

async def setup(bot): await bot.add_cog(Economy(bot))
