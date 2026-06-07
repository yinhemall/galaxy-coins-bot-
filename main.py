import sys
import os
import discord
from discord.ext import commands

# 強制路徑
sys.path.append(os.getcwd())

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    # 這裡我們會動態載入
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    await load_extensions()
    
    # 【避開報錯的關鍵】在這裡手動把該類別找出來註冊
    # 因為我們已經 load_extensions() 了，所以 cogs 已經被載入
    try:
        cog = bot.get_cog('Economy')
        # 假設你的 economy.py 裡面定義的 class 是 Economy
        # 我們直接從裡面找 View，或者乾脆在 economy.py 的 setup 裡面做 add_view
        print("指令與擴充功能已載入")
    except Exception as e:
        print(f"載入失敗: {e}")
    
    bot.tree.clear_commands(guild=None) 
    await bot.tree.sync()
    print('機器人已啟動！')

bot.run(os.getenv('DISCORD_TOKEN'))
