import sys
import os
import discord
from discord.ext import commands

# 確保路徑正確
sys.path.append(os.getcwd())

# 1. 初始化 Intents
intents = discord.Intents.default()
intents.message_content = True

# 2. 初始化 Bot (這裡修正為 intents，不是 self.intents)
bot = commands.Bot(command_prefix="!", intents=intents)

# 3. 簡單的同步指令 (只在有需要時打 !sync)
@bot.command()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("指令已同步！")

@bot.event
async def on_ready():
    # 這裡放你要載入的 cogs
    print(f'機器人已上線: {bot.user}')

# 4. 這裡直接啟動，這是最穩定的方式
bot.run(os.getenv('DISCORD_TOKEN'))
