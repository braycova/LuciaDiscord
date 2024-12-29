import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import time
import pytz


class Utility(commands.Cog, description="<:hola:799126033383030794>"):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.tree.sync()
        print(f"{__name__} is ready.")

    @app_commands.command(name="ping", description="View Lucia's latency")
    async def ping(self, interaction: discord.Interaction):
        start_time = time.time()
        await self.client.fetch_channel(interaction.channel_id)
        end_time = time.time()
        api_lat = round((end_time - start_time) * 1000)
        bot_lat = round(self.client.latency * 1000)

        embed = (discord.Embed(color=discord.Color(0x8b497a))
                 .add_field(name="Latency", value=f"**API** - {api_lat} ms\n**Websocket** - {bot_lat} ms"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Get a user's avatar")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member if member else interaction.user
        embed = (discord.Embed(title=f"{member.name}'s Avatar", color=member.color)
                 .set_image(url=member.avatar))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="user", description="View member information")
    async def user_info(self, interaction: discord.Interaction, member: discord.Member = None):
        member = interaction.guild.get_member(member.id) if member else interaction.guild.get_member(interaction.user.id)

        name = member.name if member.discriminator == "0" else f"{member.name}#{member.discriminator}"
        activity = "None" if member.activity is None else member.activity.name
        bot_check = "Yes" if member.bot else "No"

        embed = (discord.Embed(color=member.color)
                 .set_thumbnail(url=member.avatar).add_field(name="Name", value=name)
                 .add_field(name="Nickname", value=member.display_name)
                 .add_field(name="Status", value=str(member.status).capitalize())
                 .add_field(name="Activity", value=activity)
                 .add_field(name="Top Role", value=f"<@&{member.top_role.id}>")
                 .add_field(name="Bot?", value=bot_check)
                 .add_field(name="Registered", value=f"<t:{int(member.created_at.timestamp())}>")
                 .add_field(name="Joined", value=f"<t:{int(member.joined_at.timestamp())}>")
                 .set_author(name=f"{member.name}", icon_url=member.avatar)
                 .set_footer(text=f"User ID: {member.id}"))
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only
    @app_commands.command(name="server", description="View server information")
    async def server_info(self, interaction: discord.Interaction):
        s = interaction.guild
        embed = (discord.Embed(color=discord.Colour.random())
                 .set_thumbnail(url=s.icon)
                 .add_field(name="Owner", value=s.owner.mention)
                 .add_field(name="Members", value=s.member_count)
                 .add_field(name="Roles", value=len(s.roles))
                 .add_field(name="Text Channels", value=len(s.text_channels))
                 .add_field(name="Voice Channels", value=len(s.voice_channels))
                 .add_field(name="Emojis", value=len(s.emojis))
                 .add_field(name="Created On", value=f"<t:{int(s.created_at.timestamp())}>")
                 .set_author(name=f"{s.name}", icon_url=s.icon)
                 .set_footer(text=f"Server ID: {s.id}"))
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only
    @app_commands.command(name="react", description="React to a message using message ID")
    @app_commands.describe(reaction="Emoji you want to react with (if multiple, separate by space)", message_id="Message ID of target message")
    async def react(self, interaction: discord.Interaction, reaction: str, message_id: str):
        try:
            target_msg = await interaction.channel.fetch_message(int(message_id))
            for react in reaction.split():
                await target_msg.add_reaction(react)
            embed = discord.Embed(description="<a:catdance:1209558708908986421> **Reacted** ✓", colour=discord.Colour(0x33c438))
        except discord.errors.NotFound:
            embed = discord.Embed(description="<a:catwhat:1207179377025097758> **Invalid Message ID**. Make sure your message ID is valid and are within Lucia's view.", colour=discord.Colour(0xfec411))
        except discord.errors.HTTPException:
            embed = discord.Embed(description="<:blobcat:1207179390199267338> **Invalid emoji**. Make sure the emoji you use comes from a server Lucia's in.", colour=discord.Colour(0xFF0000))

        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

    @app_commands.command(name="time", description="Fetch current time from US, UK, and UTC time zones")
    async def time(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        timezones = {"America/Chicago": (":flag_us:", "Central US"), "America/New_York": (":flag_us:", "East US"),
                     "UTC": ("🌐", "UTC"), "Europe/London": (":flag_gb:", "UK")}
        tzs_formatted = ""
        for zone, label in timezones.items():
            tzs_formatted += f"{label[0]} **{label[1]}** - {datetime.now(pytz.timezone(zone)).strftime('%I:%M %p').lstrip('0')}\n"

        embed = (discord.Embed(title="🕑 - time go wee")
                 .add_field(name="Your Time", value=f"🗺️ **Local** - <t:{int(time.time())}:t>", inline=False)
                 .add_field(name="Other Time Zones", value=tzs_formatted, inline=False)
                 .set_footer(text="cloc"))  # TODO: Replace with random response key
        await interaction.followup.send(embed=embed)


async def setup(client):
    await client.add_cog(Utility(client))