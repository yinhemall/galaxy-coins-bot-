import discord
from discord import app_commands
from discord.ext import commands

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 簡單的資料庫：儲存 {user_id: balance}
        self.balances = {}

    @app_commands.command(name="簽到", description="每日領取獎勵")
    async def daily(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        reward = 100 # 假設每天簽到給 100 元
        
        # 增加餘額
        if user_id not in self.balances:
            self.balances[user_id] = 0
        self.balances[user_id] += reward
        
        # 告知使用者領取後的餘額
        current_balance = self.balances[user_id]
        await interaction.response.send_message(
            f"✅ 簽到成功！你獲得了 {reward} 元。\n"
            f"💰 你目前的總餘額為: **{current_balance}** 元。"
        )

    @app_commands.command(name="餘額", description="查詢錢包")
    async def balance(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        balance = self.balances.get(user_id, 0)
        await interaction.response.send_message(f"💰 你目前的餘額是: **{balance}** 元。")

async def setup(bot):
    await bot.add_cog(Economy(bot))
