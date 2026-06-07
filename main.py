import discord
from discord.ext import commands
import os
# 從 cogs 資料夾底下的 economy 檔案匯入 CheckinView
from cogs.economy import CheckinView 

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    await load_extensions()
    
    # 【關鍵】註冊按鈕，讓它在重啟後依然有效
    bot.add_view(CheckinView()) 
    
    # 清除舊指令並同步新指令
    bot.tree.clear_commands(guild=None) 
    await bot.tree.sync()
    
    print('機器人已啟動，指令同步完成，按鈕已註冊！')

bot.run(os.getenv('DISCORD_TOKEN'))
