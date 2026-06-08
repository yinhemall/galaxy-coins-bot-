import os
import discord
import asyncio
from discord.ext import commands
from aiohttp import web

# 1. 設置 Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 2. 為了讓 Railway 不會關閉你的容器，必須啟動這個簡易網頁伺服器
async def web_server():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()

# 3. 機器人啟動邏輯
@bot.event
async def on_ready():
    await bot.load_extension('cogs.economy')
    print("✅ 機器人已上線")

# 4. 關鍵：使用 asyncio 讓兩個任務同時執行
async def main():
    await web_server() # 先啟動網頁伺服器
    await bot.start(os.getenv('DISCORD_TOKEN')) # 再啟動 Discord 機器人

if __name__ == "__main__":
    asyncio.run(main())
