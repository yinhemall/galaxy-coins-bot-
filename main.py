# ... 上面的 web server 程式碼保持不變 ...

# 機器人初始化
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ 機器人已成功登入: {bot.user}")
    # 這裡載入你的 Cog
    try:
        await bot.load_extension('cogs.economy')
        print("✅ Economy Cog 載入成功")
    except Exception as e:
        print(f"❌ 載入失敗: {e}")

async def start_bot():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ 錯誤: 未設定 DISCORD_TOKEN")
        return
    # 這是最關鍵的一行，之前你那邊是空的
    await bot.start(token)

async def main():
    await asyncio.gather(start_web_server(), start_bot())

if __name__ == "__main__":
    asyncio.run(main())
