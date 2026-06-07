import sys
import os
import discord
from discord.ext import commands
from cogs.economy import CheckinView 

# 強制將當前目錄加入搜尋路徑，確保能找到 cogs
sys.path.append(os.getcwd())

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    # 確保 cogs 資料夾存在且讀取正確
    if os.path.exists('./cogs'):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    await load_extensions()
    
    # 註冊持久性視圖 (按鈕)
    bot.add_view(CheckinView()) 
    
    # 清除並同步指令
    bot.tree.clear_commands(guild=None) 
    await bot.tree.sync()
    
    print('機器人已啟動，指令同步完成，按鈕已註冊！')

bot.run(os.getenv('DISCORD_TOKEN'))
