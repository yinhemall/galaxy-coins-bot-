import os
import discord
import asyncio
from discord.ext import commands
from aiohttp import web

# 建立一個簡單的 web server 來滿足 Railway 的需求
async def handle(request):
    return web.Response(text="Bot is running")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()
    print("✅ 網頁伺服器啟動於 port 8080")

# 你的機器人啟動邏輯
async def start_bot():
    # 這裡放你初始化 bot 的程式碼
    # ...
    # 最後記得用 await bot.start(token)
    pass

async def main():
    await asyncio.gather(start_web_server(), start_bot())

if __name__ == "__main__":
    asyncio.run(main())
