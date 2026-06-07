import sys
import os
import discord
import asyncio
from discord.ext import commands
from aiohttp import web

# 強制路徑
sys.path.append(os.getcwd())

# 1. 建立 intents 與 bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 2. 網頁伺服器 (用來騙過 Railway 檢測)
async def start_web_server():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"網頁伺服器已啟動於 port {port}")

# 3. 載入擴充功能
async def load_extensions():
    if os.path.exists('./cogs'):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    await load_extensions()
    try:
        await bot.tree.sync()
        print('機器人已啟動，並自動完成了指令同步！')
    except Exception as e:
        print(f"自動同步失敗: {e}")

# 4. 整合啟動
async def main():
    # 這裡同時啟動 Web Server 和 Bot
    await start_web_server()
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())
