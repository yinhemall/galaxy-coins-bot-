import sys
import os
import discord
import asyncio
from discord.ext import commands
from aiohttp import web

sys.path.append(os.getcwd())

# 正確的 Intents 設定
intents = discord.Intents.default()
intents.message_content = True

# 關鍵：這裡必須是 intents，絕對不能寫 self.intents
bot = commands.Bot(command_prefix="!", intents=intents)

async def start_web_server():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    # 嘗試從環境變數獲取 PORT，預設為 8080
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"網頁伺服器已啟動於 port {port}")

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

async def main():
    await start_web_server()
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())
