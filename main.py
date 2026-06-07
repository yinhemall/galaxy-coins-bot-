import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

# --- 這裡就是關鍵位置 ---
@bot.event
async def on_ready():
    # 1. 載入外掛
    await load_extensions()
    
    # 2. 【清除舊指令】這一行會把 Discord 上所有以前殘留的指令全部刪掉
    bot.tree.clear_commands(guild=None) 
    
    # 3. 【同步新指令】這一行會重新上傳你現在寫好的指令
    await bot.tree.sync()
    
    print(f'機器人已啟動，舊指令已清除，新指令同步完成！')
# ----------------------

bot.run(os.getenv('DISCORD_TOKEN'))
