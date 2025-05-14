import discord
from discord.ext import commands
from discord import app_commands
from calendar import monthrange, month_name
from data.database import create_event
import re
import time


def get_month_choices():
    months = []
    for i in range(1, 13):
        months.append(discord.app_commands.Choice(name=list(month_name)[i], value=str(i)))
    return months

def validate_hex_color(hex_str):
    pattern = re.compile(r'^#?([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$')
    return None if not bool(pattern.match(hex_str)) else int(hex_str, 16) if not hex_str.startswith('#') else int(hex_str[1:], 16)


class Calendar(commands.GroupCog, description="🛠️"):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.tree.sync()
        print(f"{__name__} is ready.")

    class CreateEvent(discord.ui.View):
        def __init__(self, interaction, event):
            super().__init__(timeout=120)
            self.i = interaction
            self.e = event

        @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, emoji="<:BallOk:1333999538695831652>")
        async def event_confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            create_event(self.e)
            embed = discord.Embed(description="<:BallOk:1333999538695831652> **Event saved successfully**", color=discord.Color.green())
            await self.i.edit_original_response(embed=embed, content="", view=None)

        @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
        async def event_cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed = discord.Embed(description="<:spike:1325681519230193735> **Event discarded**", color=discord.Color.red())
            await self.i.edit_original_response(embed=embed, content="", view=None)


    @app_commands.command(name="create", description="Create an event")
    @app_commands.choices(month=get_month_choices())
    @app_commands.describe(day="Enter day of the month", month="Select a month of the year", name="Set your event name (ex. \"Lucia's Birthday\"). Saved for search, NOT displayed",
                           title="Set your event's embed title", message="Set your event's embed message",
                           color="Set your event's border color. Enter as a hex code (ex. #4e3c5c). Defaults to black",
                           mentions="Set user/role mentions", footer="Set footer embed text")
    async def create(self, interaction: discord.Interaction, day: app_commands.Range[int, 1, 31], month: discord.app_commands.Choice[str], name: str,
                     title: str = None, message: str = None, color: str = None, mentions: str = None, footer: str = None):
        days_in_month = monthrange(1, int(month.value))[1]

        if day > days_in_month:
            await interaction.response.send_message(f"**{month.name}** only has **{days_in_month}** days on the 365-day calendar. You entered `{day}` <:spike:1325681519230193735>\n-# Please try again.", ephemeral=True)
            return

        hex_code = validate_hex_color(color) if color else None
        embed = discord.Embed(title=title, description=message, color=discord.Color(hex_code) if color else None)
        embed.set_footer(text=footer) if footer else None

        content = f"> **Preview**\n> Confirm your event <t:{round(time.time()) + 120}:R> or it'll be automatically discarded. <:coffee:1249421545437270136>\n`---`\n\n{mentions}"
        event = {"userId": interaction.user.id, "month": int(month.value), "day": day, "name": name, "title": title, "message": message, "color": hex_code, "mentions": mentions, "footer": footer}
        await interaction.response.send_message(content=content, embed=embed, view=self.CreateEvent(interaction=interaction, event=event), ephemeral=True, delete_after=120)

    @app_commands.command(name="view", description="View your events")
    async def view(self, interaction: discord.Interaction):
        await interaction.response.send_message("in development")

async def setup(client):
    await client.add_cog(Calendar(client))