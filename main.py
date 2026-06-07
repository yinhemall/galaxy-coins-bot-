import sys
import os
import discord
from discord.ext import commands

# 強制將當前工作目錄加入系統路徑，確保能找到 cogs
sys.path.append(os.getcwd())

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=self.intents)

async def load_extensions():
    # 動態載入 cogs 資料夾下的所有檔案
    if os.path.exists('./cogs'):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    await load_extensions()
    
    # 啟動時自動同步所有斜線指令
    try:
        await bot.tree.sync()
        print('機器人已啟動，並自動完成了指令同步！')
    except Exception as e:
        print(f"自動同步失敗: {e}")

# 手動強制同步指令 (僅限機器人擁有者使用)
@bot.command()
@commands.is_owner()
async def sync(ctx):
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"✅ 指令已強制同步！本次共同步了 {len(synced)} 個指令。")
    except Exception as e:
        await ctx.send(f"❌ 同步失敗: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
