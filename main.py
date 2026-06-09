Import os
import discord
import asyncio
from discord.ext import commands
from aiohttp import web

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 為了防止 Render 休眠，保留 Web Server
async def handle(request):
    return web.Response(text="Bot is running")

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
    try:
        await bot.load_extension('cogs.economy')
        print("✅ Economy Cog 載入成功")
    except Exception as e:
        print(f"❌ 載入失敗: {e}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ 指令同步成功: {len(synced)} 個指令")
    except Exception as e:
        print(f"❌ 同步失敗: {e}")

async def main():
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        print("❌ 錯誤: 未設定 DISCORD_TOKEN")
        return

    # 同時啟動網頁伺服器與機器人
    await start_web_server()
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
直接幫
