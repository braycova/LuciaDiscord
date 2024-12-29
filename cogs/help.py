import discord
from discord.ext import commands
from discord import app_commands


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.tree.sync()
        print(f"{__name__} is ready.")

    class HelpSelect(discord.ui.Select):
        def __init__(self, client):
            options = [discord.SelectOption(label=cog.__cog_name__, emoji=cog.description) for cog in client.cogs.values()]
            super().__init__(placeholder="Select a category", options=options)

    class HelpMenu(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=120)
            self.add_item(Help.HelpSelect())

    @app_commands.command(name="help", description="View Lucia's commands")
    async def help(self, interaction: discord.Interaction):
        for cog in self.client.cogs.values():
            print(f"Group: {cog.__cog_name__} - {cog.description if cog.description else None}:")
            for command in cog.walk_app_commands():
                print(f"\t- {command.name} - {command.description}")
        await interaction.response.send_message("waffle")


async def setup(client):
    await client.add_cog(Help(client))