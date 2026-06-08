import os
import discord
import asyncio
from discord.ext import commands
from aiohttp import web

# 1. 機器人初始化
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 2. 加入同步指令 (!sync)
@bot.command(name="sync")
@commands.has_permissions(administrator=True)
async def sync(ctx):
    """手動同步指令到 Discord"""
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"✅ 已成功同步 {len(synced)} 個指令到 Discord！")
    except Exception as e:
        await ctx.send(f"❌ 同步失敗: {e}")

# 3. 網頁伺服器 (保活)
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
    print(f"✅ 網頁伺服器啟動於 port {port}")

# 4. 機器人啟動邏輯
@bot.event
async def on_ready():
    print(f"✅ 機器人已成功登入: {bot.user}")
    try:
        await bot.load_extension('cogs.economy')
        print("✅ Economy Cog 載入成功")
    except Exception as e:
        print(f"❌ 載入失敗: {e}")

async def start_bot():
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        print("❌ 錯誤: 未設定 DISCORD_TOKEN 環境變數")
        return
    await bot.start(token)

async def main():
    await asyncio.gather(start_web_server(), start_bot())

if __name__ == "__main__":
    asyncio.run(main())
