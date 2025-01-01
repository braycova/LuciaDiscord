import discord
from discord.ext import commands
from discord import app_commands


class Economy(commands.Cog, description="<a:LuciaOrb:1251215260031914048>"):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.tree.sync()
        print(f"{__name__} is ready.")


async def setup(client):
    await client.add_cog(Economy(client))