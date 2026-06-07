import sys
import os
import discord
import asyncio
from discord.ext import commands
from aiohttp import web

# 強制路徑
sys.path.append(os.getcwd())

# 1. 初始化 Intents 與 Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 網頁伺服器 (解決 Railway 強制重啟問題) ---
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
    print(f"網頁伺服器已啟動於 port {port}")

# --- 動態載入 Cogs ---
async def load_extensions():
    if os.path.exists('./cogs'):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"已載入: {filename}")

@bot.event
async def on_ready():
    await load_extensions()
    print(f'機器人已上線: {bot.user}')

# --- 指令 ---
@bot.command()
@commands.is_owner()
async def sync(ctx):
    synced = await bot.tree.sync()
    await ctx.send(f"✅ 指令已同步！共 {len(synced)} 個。")

# --- 整合啟動 ---
async def main():
    # 同時啟動網頁伺服器與 Bot
    await start_web_server()
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())
