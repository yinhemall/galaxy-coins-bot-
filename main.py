import sys
import os
import discord
import asyncio
from discord.ext import commands
from aiohttp import web

# 匯入所有的 View，確保重啟後按鈕都能運作
from cogs.economy import DailyView, MenuStarterView, GameMenuView

sys.path.append(os.getcwd())

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 網頁伺服器 ---
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

# --- 載入 Cogs ---
async def load_extensions():
    if os.path.exists('./cogs'):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"已載入: {filename}")

@bot.event
async def on_ready():
    # 載入所有功能模組
    await load_extensions()
    
    # 【關鍵】重啟後必須重新註冊所有 View，否則按鈕會顯示 "互動失敗"
    bot.add_view(DailyView())
    bot.add_view(MenuStarterView())
    bot.add_view(GameMenuView())
    
    print(f'✅ 機器人已上線: {bot.user}')
    print(f'✅ 所有按鈕監聽器已註冊完畢')

@bot.command()
@commands.is_owner()
async def sync(ctx):
    # 自動同步斜線指令
    synced = await bot.tree.sync()
    await ctx.send(f"✅ 指令已同步！共 {len(synced)} 個。")

async def main():
    await start_web_server()
    # 記得確保 Railway 的變數 DISCORD_TOKEN 有設定好
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())
