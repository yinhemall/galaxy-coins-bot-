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
    await load_extensions()
    
    # 【關鍵步驟】先清空舊指令
    bot.tree.clear_commands(guild=None) 
    
    # 【關鍵步驟】推送到全域
    await bot.tree.sync()
    
    print('已清除舊指令並完成全域同步')

# ----------------------

bot.run(os.getenv('DISCORD_TOKEN'))
