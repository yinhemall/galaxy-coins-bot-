import discord
from discord.ext import commands
import sqlite3

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 初始化資料庫
conn = sqlite3.connect('galaxy.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER)')
conn.commit()

# 簽到系統
@bot.command()
async def 簽到(ctx):
    # 這裡加入你的按鈕邏輯
    await ctx.send("點擊下方按鈕領取銀河幣！")

# 轉帳系統
@bot.command()
async def 轉帳(ctx, target: discord.Member, amount: int):
    # 這裡加入扣除自己、增加對方餘額的邏輯
    await ctx.send(f"已轉帳 {amount} 銀河幣給 {target.name}")

@bot.event
async def on_ready():
    print(f'銀河幣機器人已啟動！')

# 記得填入 Token (建議用環境變數管理)
import os
bot.run(os.getenv('DISCORD_TOKEN'))

