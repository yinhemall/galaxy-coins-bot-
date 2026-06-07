import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    await load_extensions()
    # 自動同步斜線指令到 Discord (這一行非常重要！)
    await bot.tree.sync() 
    print(f'已載入所有功能，斜線指令同步完成！')

bot.run(os.getenv('DISCORD_TOKEN'))
