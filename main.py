import os
import discord
import asyncio
from discord.ext import commands
from aiohttp import web

# 初始化機器人
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 簡易網頁伺服器（用於保活）
async def web_handler(request):
    return web.Response(text="Bot is running!", status=200)

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', web_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"✅ 網頁伺服器已啟動於 port {port}")

# 載入 Cog 的邏輯
async def load_extensions():
    # 確保 cogs 資料夾存在且裡面有 economy.py
    try:
        await bot.load_extension('cogs.economy')
        print("✅ 已載入: cogs.economy")
    except Exception as e:
        print(f"❌ 無法載入 economy.py: {e}")

@bot.event
async def on_ready():
    await load_extensions()
    # 同步指令到 Discord
    try:
        synced = await bot.tree.sync()
        print(f"✅ 已同步 {len(synced)} 個指令到 Discord")
    except Exception as e:
        print(f"❌ 指令同步失敗: {e}")
    print(f'✅ 機器人已上線: {bot.user}')

async def main():
    await start_web_server()
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ 錯誤: 未找到 DISCORD_TOKEN 環境變數")
        return
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())

