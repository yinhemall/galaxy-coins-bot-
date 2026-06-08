import os
import discord
import asyncio
from discord.ext import commands
from aiohttp import web

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 網頁伺服器 (保活專用)
async def handle(request): return web.Response(text="Bot is running")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"✅ Web server running on port {port}")

@bot.event
async def on_ready():
    print(f"✅ 機器人已登入: {bot.user}")
    
    # 1. 載入 Cog
    try:
        await bot.load_extension('cogs.economy')
        print("✅ Economy Cog 載入成功")
    except Exception as e:
        print(f"❌ 載入失敗: {e}")

    # 2. 自動同步指令 (核心修改：解決 0 個指令問題)
    try:
        synced = await bot.tree.sync()
        print(f"✅ 指令同步成功: {len(synced)} 個指令已註冊")
    except Exception as e:
        print(f"❌ 同步失敗: {e}")

async def start_bot():
    token = os.environ.get('DISCORD_TOKEN')
    await bot.start(token)

async def main():
    await asyncio.gather(start_web_server(), start_bot())

if __name__ == "__main__":
    asyncio.run(main())
