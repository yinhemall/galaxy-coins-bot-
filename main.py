import os
import discord
import asyncio
import random
from discord import ui
from discord.ext import commands
from aiohttp import web

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 賭場 UI 邏輯 ---
class BetModal(ui.Modal, title='🎰 決戰時刻 - 下注區'):
    amount = ui.TextInput(label='請輸入下注金額', style=discord.TextStyle.short, placeholder='例如: 1000')

    async def on_submit(self, interaction: discord.Interaction):
        try:
            bet_amount = int(self.amount.value)
            d1, d2 = random.randint(1, 6), random.randint(1, 6)
            total = d1 + d2
            win = total >= 7
            
            embed = discord.Embed(title="🎲 骰子轉動中...", description=f"點數為 **{d1}** + **{d2}** = **{total}**", color=0xFFD700 if win else 0xFF0000)
            if win:
                embed.add_field(name="結果", value=f"✅ 恭喜！你押中了「大」，贏得 {bet_amount} 代幣！", inline=False)
            else:
                embed.add_field(name="結果", value=f"❌ 可惜！你輸了 {bet_amount} 代幣。", inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except ValueError:
            await interaction.response.send_message("⚠️ 請輸入有效的數字！", ephemeral=True)

class CasinoView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🎲 猜大小 (骰子)", style=discord.ButtonStyle.blurple, emoji="🎲")
    async def roll_game(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(BetModal())

# --- 既有功能 ---
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
    
    # 發送賭場介面 (請將 123456789 替換為您的頻道 ID)
    channel = bot.get_channel(123456789) 
    if channel:
        embed = discord.Embed(title="✨ GALAXY COINS 豪華賭場 ✨", description=">>> 歡迎來到宇宙最強的交易中心！\n點擊下方按鈕即可開始你的財富傳奇。", color=0x00f2ff)
        await channel.send(embed=embed, view=CasinoView())

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
    await start_web_server()
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
