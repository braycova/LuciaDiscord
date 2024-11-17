import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.tree.sync()
        print(f"{__name__} is ready.")

    async def send_direct_message(self, interaction, message, user_id):
        user = await self.client.fetch_user(user_id)
        channel = await user.create_dm()
        await channel.send(content=f"{message}\n-# \\- {interaction.user.name}")

    @app_commands.command(name="about", description="Learn what Lucia is")
    async def about(self, interaction: discord.Interaction):
        desc = ("**Lucia** is a self-hosted discord bot with a variety of functions, yet prioritized in notefoolery ;)\nHer commands are viewable through the `/help` menu.\n\n"
                "As this is an ongoing project, expect frequent *and* infrequent changes, many bugs. Feedback is greatly appreciated. 🍪")
        credits = ("- Developed by <@401134972360065028> <:cat_by_ball:931020898016837672>\n"
                   "- Emotes by <@316225006323499008> <a:LuciaOrbFlash:1251215257968312391>\n"
                   "- Powered by <@371564926097031169>'s coffee <:coffee:1249421545437270136>\n"
                   "- Avatar from [Kotoro's](https://www.instagram.com/nikoandkota.toro/) Instagram <:Lucia:1253852411542372535>")
        embed = discord.Embed(title="About Lucia", description=desc, colour=discord.Colour(0xb39eb5))
        embed.add_field(name="Credits", value=credits)
        embed.set_footer(text="Created March 25, 2023", icon_url=self.client.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="featured", description="View featured Discord servers")
    async def featured(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "### Welcome to Lucia Express Train ✦\n"
            "Select a destination to teleport to :3\n"
            "- <:cat_by_ball:931020898016837672> - [**new day, new pain**](<https://discord.gg/gSErrGDUyR>), residence of Noted and Lucia\n" 
            "- <a:Ballistimite:637405677458948127> - [**Ballistimite Paradise**](<https://discord.gg/fjdnr4M6XA>), the land of ballers\n"
            "- <:AtlasCorp:816132912365436959> - [**Atlas Space Station**](<https://discord.gg/KaDX4F5rBC>)*****, a spacecraft piloted by cock council\n" 
            "- <a:earthorb:719683332547412021> - [**The Earth Clan**](<https://discord.gg/ph6KcAs>)*****, the abandoned land, precedes Atlas Station\n"
            "-# *These are inactive, kept for history preservation")

    @app_commands.guild_only()
    @app_commands.command(name="pingball", description="Send a message to your favourite Ballodrite")
    async def ping_ball(self, interaction: discord.Interaction, message: str):
        await Misc.send_direct_message(self, interaction, message, 316225006323499008)
        await interaction.response.send_message("Sent to Ballos via British Express 📨")

    @app_commands.guild_only()
    @app_commands.command(name="trolljoe", description="Send a message to our cuppa' Joe")
    async def troll_joe(self, interaction: discord.Interaction, message: str):
        await Misc.send_direct_message(self, interaction, message, 371564926097031169)
        await interaction.response.send_message("Sent to Joe via quick coffee delivery ☕")

    @app_commands.guild_only()
    @app_commands.command(name="annoynoted", description="Annoy Noted by sending him a message")
    async def annoy_noted(self, interaction: discord.Interaction, message: str):
        async def wait_then_send(message):
            await asyncio.sleep(4)
            await interaction.edit_original_response(content=message)

        async def generate_progress(progress):
            bar_length = 20
            filled_length = int(bar_length * progress / 100)
            bar = ("▮" * filled_length) + ("▯" * (bar_length - filled_length))
            return f"📨 |{bar}| **{progress}%**"

        async def update_progress():
            points = [5, 15, 40, 50, 70, 75, 85, 90, 95, 96, 97, 98, 99]
            for progress in points:
                progress_bar = await generate_progress(progress)
                await wait_then_send(progress_bar)

        await interaction.response.send_message("You are using, **Lucia Mailing Systems**, I'll have your message processed shortly.. ✉️")
        await wait_then_send("*Locating Noted's Direct Message Mailbox..* <a:earthorb:719683332547412021>")
        await wait_then_send("**Located!** *Sending now..* 📨")
        await update_progress()

        verdict = random.choice([True, False])
        if verdict:
            await wait_then_send(f"📬 |{"▮" * 20}| **100%**")
            await Misc.send_direct_message(self, interaction, message, 401134972360065028)
            await wait_then_send("**Success!** Your message has been successfully delivered! ✅")
            return

        await wait_then_send(f"<:blobcat:1207179390199267338> |{"▯" * 20}| **--%**")
        await wait_then_send("**oh no.** Your message was dropped before it could reach its recipient. ❌")


async def setup(client):
    await client.add_cog(Misc(client))