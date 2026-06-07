import sys
import os
import discord
import asyncio
from discord.ext import commands
from aiohttp import web

# 強制將當前工作目錄加入系統路徑
sys.path.append(os.getcwd())

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 1. 簡易網頁伺服器 (用來騙過 Railway 的健康檢查) ---
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
    print(f"網頁伺服器已啟動於 port {port}")

# --- 2. 擴充功能載入 ---
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

@bot.command()
@commands.is_owner()
async def sync(ctx):
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"✅ 指令已強制同步！本次共同步了 {len(synced)} 個指令。")
    except Exception as e:
        await ctx.send(f"❌ 同步失敗: {e}")

# --- 3. 整合啟動 ---
async def main():
    await start_web_server()
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())
