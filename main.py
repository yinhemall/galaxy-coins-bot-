import os
import discord
import asyncio
from discord.ext import commands

# 設定 Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ 機器人已登入: {bot.user}")
    
    # 1. 載入 Cog
    try:
        await bot.load_extension('cogs.economy')
        print("✅ Economy Cog 載入成功")
    except Exception as e:
        print(f"❌ 載入失敗: {e}")

    # 2. 自動同步指令
    try:
        synced = await bot.tree.sync()
        print(f"✅ 指令同步成功: {len(synced)} 個指令已註冊")
    except Exception as e:
        print(f"❌ 同步失敗: {e}")

async def main():
    # 直接啟動 Bot，無需再執行網頁伺服器
    token = os.environ.get('DISCORD_TOKEN')
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
