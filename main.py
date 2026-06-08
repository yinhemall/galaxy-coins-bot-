import os
import discord
import asyncio
from discord.ext import commands
from aiohttp import web

# 初始化
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 簡易網頁伺服器（讓 Railway 認為你是個網站服務，不會殺掉你）
async def web_handler(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', web_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"✅ 網頁伺服器啟動於 port {port}")

# 當機器人準備好時
@bot.event
async def on_ready():
    print(f"✅ 機器人已成功登入: {bot.user}")
    # 注意：這裡不要呼叫 load_extension，我們在 main 裡呼叫
    try:
        await bot.load_extension('cogs.economy')
        print("✅ Economy Cog 載入成功")
    except Exception as e:
        print(f"❌ 載入失敗: {e}")

async def main():
    # 1. 先啟動網頁伺服器
    await start_web_server()
    # 2. 啟動機器人 (這行會掛起程式，讓它不會結束)
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ 錯誤: 請設定 DISCORD_TOKEN")
        return
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
