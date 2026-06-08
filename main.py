import sys
import os
import discord
import asyncio
from discord.ext import commands
from aiohttp import web

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
    await load_extensions()
    print(f'✅ 機器人已上線: {bot.user}')

@bot.command()
@commands.is_owner()
async def sync(ctx):
    bot.tree.copy_global_to(guild=ctx.guild)
    synced = await bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"✅ 已強制同步指令至本伺服器！同步了 {len(synced)} 個指令。")

async def main():
    await start_web_server()
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())
