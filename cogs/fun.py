import discord
from discord.ext import commands
from discord import app_commands
from data.database import get_random_response
import requests
import random
import asyncio
import datetime
import regex
import os
import alexflipnote
from dotenv import load_dotenv


async def handle_api_exceptions(interaction, api_name, command_name, exception):
    print(f"(X) An error occurred while accessing {api_name} API in /{command_name} - {exception}")
    embed = discord.Embed(
        description="<:dnd:821458583773904937> Something went wrong while accessing the API. Please try again later.",
        colour=discord.Colour.red())
    embed.set_footer(text="⚠️ Noted has been notified.")
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=8)


class Fun(commands.Cog, description="<a:chicken:1252681208916217949>"):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.tree.sync()
        print(f"{__name__} is ready.")

    @app_commands.command(name="8ball", description="Receive wisdom from Lucia's magic 8ball")
    async def _8ball(self, interaction: discord.Interaction, question: str):
        embed = discord.Embed(title=f"🎱 {get_random_response("8ball")[0]}", description=f"> \"{question}\"", colour=interaction.user.colour)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="say", description="Make Lucia say anything")
    async def say(self, interaction: discord.Interaction, message: str = None, image: discord.Attachment = None):
        await interaction.channel.send(content=message) if message else None
        await interaction.channel.send(image) if image else None
        embed = discord.Embed(description="<a:catdance:1209558708908986421> **Sent!**", colour=discord.Colour(0x33c438)) if message or image else discord.Embed(description="I can't say anything out of thin air..", colour=discord.Colour(0xb51b00))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=8)

    @app_commands.command(name="momentos", description="View the showcase of discord moment shenanigans")
    @app_commands.describe(source="Select a channel source (optional)")
    @app_commands.choices(source=[discord.app_commands.Choice(name="#discord-momentos (new day, new pain)", value="817926054172688405"), discord.app_commands.Choice(name="#ball-of-fame (Ballodise)", value="1101507144496451635")])
    async def momentos(self, interaction: discord.Interaction, source: discord.app_commands.Choice[str] = None):
        async def fetch_momento(channel):
            images = []

            async for message in channel.history():
                if message.attachments:
                    for attachment in message.attachments:
                        images.append(attachment.url)

            momento = random.choice(images)
            embed = discord.Embed(colour=discord.Colour.random())
            embed.set_image(url=momento)
            return embed

        async def fetch_fame_post(channel):
            posts = []

            async for message in channel.history():
                if message.webhook_id:
                    for embed in message.embeds:
                        posts.append(embed)

            while True:
                post = random.choice(posts)
                try:
                    link = regex.search(r"\(([^)]+)\)", post.fields[0].value).group(1)  # Grabs the message link
                    break
                except Exception:
                    pass

            channel_link = self.client.get_channel(int(link.split("/")[-2]))  # Locates user for their current profile image
            message_link = await channel_link.fetch_message(int(link.split("/")[-1]))

            try:
                user_link = await self.client.fetch_user(message_link.author.id)
            except discord.errors.NotFound:
                user_link = await self.client.fetch_user(1089292852963590224)

            embed = discord.Embed(description=post.description, color=discord.Colour.random())
            embed.set_author(name=post.author.name, icon_url=user_link.avatar)
            embed.add_field(name='\u200b', value=f"**[View Message]({link})**")
            if post.image.url is not None:
                embed.set_image(url=post.image.url)
            return embed

        source_id = source.value if source else random.choice(["817926054172688405", "1101507144496451635"])
        loading_message = "### <a:kirbyspin:799127471868870667> *Fetching momentos..*\n-# From Atlas Space, Earth Clan, and beyond" if source_id == "817926054172688405" else "### <a:loadingbeats:817973961182674965> *Fetching balls of fame..*\n-# Starred posts considered to be very baller"
        await interaction.response.send_message(loading_message)
        source = self.client.get_channel(int(source_id))
        embed = await fetch_momento(source) if source_id == "817926054172688405" else await fetch_fame_post(source)
        await interaction.edit_original_response(embed=embed, content="")

    @app_commands.command(name="achievement", description="Achievement Get!")
    async def achievement(self, interaction: discord.Interaction, text: str):
        try:
            api = alexflipnote.Client()
            image_url = await api.achievement(text)
            await interaction.response.send_message(content=f"-# <a:minecraft:1323388841981247549> Source: [alexflipnote]({image_url})")
            await api.close()
        except Exception as e:
            await handle_api_exceptions(interaction, "alexflipnote", "achievement", e)

    @app_commands.command(name="cat", description="Get a random cat :3")
    async def cat(self, interaction: discord.Interaction):
        try:
            data = requests.get("https://api.thecatapi.com/v1/images/search").json()
            image_url = data[0]["url"]
            await interaction.response.send_message(content=f"-# <:Lucia:1253852411542372535> Source: [thecatapi]({image_url})")
        except Exception as e:
            await handle_api_exceptions(interaction, "thecatapi", "cat", e)

    @app_commands.command(name="coffee", description="Get a random dosage of virtual caffeine")
    async def coffee(self, interaction: discord.Interaction):
        try:
            api = alexflipnote.Client()
            image_url = await api.coffee()
            await interaction.response.send_message(content=f"-# <:coffee:1249421545437270136> Source: [alexflipnote]({image_url})")
            await api.close()
        except Exception as e:
            await handle_api_exceptions(interaction, "alexflipnote", "coffee", e)

    @app_commands.command(name="color", description="Generate a random color")
    async def color(self, interaction: discord.Interaction):
        try:
            data = requests.get("https://www.thecolorapi.com/random?format=json").json()
            rgb = data['rgb']
            embed = discord.Embed(colour=discord.Colour.from_rgb(rgb['r'], rgb['g'], rgb['b']))
            embed.add_field(name="Hex", value=data['hex']['value'])
            embed.add_field(name='RGB', value=f"{rgb['r']}, {rgb['g']}, {rgb['b']}")
            embed.set_footer(text="🎨 thecolorapi")
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await handle_api_exceptions(interaction, "thecolorAPI", "color", e)

    @app_commands.command(name="dadjoke", description="Want hear a dad joke?")
    @app_commands.guild_only()
    async def dad_joke(self, interaction: discord.Interaction):
        try:
            data = requests.get(url="https://icanhazdadjoke.com", headers={"Accept": "application/json"}).json()
            await interaction.response.send_message(data['joke'])
        except Exception as e:
            await handle_api_exceptions(interaction, "icanhazdadjoke", "dadjoke", e)

    @app_commands.command(name="decide", description="Let Lucia decide for you")
    @app_commands.describe(options="List out your choices, seperated by commas (,)")
    async def decide(self, interaction: discord.Interaction, options: str):
        thinking_icon = random.choice(["<a:toothless:1190413513143894127>", "<a:cathappy:1209569404300427295>",
                                       "<a:silvercoin:845776048586358805>", "<:saxorat:799284586634805248>"])
        thinking_message = random.choice(["Making a decision for you", "Spinning an online wheel",
                                          "Betting your life savings in the casino- I mean, deciding for you",
                                          "Flipping a variety of coins", "Getting ready to shoot blind (America only)"])
        await interaction.response.send_message(content=f"{thinking_icon} {thinking_message}")

        option_list = options.split(',')
        selected_option = random.choice(option_list)
        await asyncio.sleep(3)  # For suspense reasons
        await interaction.edit_original_response(content=f"<:Lucia:1253852411542372535> **{selected_option}**")

    @app_commands.command(name="movie", description="Search up movie information")
    @app_commands.describe(title="Movie title", year="Release year (optional)")
    async def movie(self, interaction: discord.Interaction, title: str, year: app_commands.Range[int, 1900, None] = None):
        year = year if year else ""

        try:
            load_dotenv()
            movie_data = requests.get(f"http://www.omdbapi.com/?apikey={os.getenv("OMDB_API")}&t={title}&y={str(year)}&type=movie").json()
        except Exception as e:
            await handle_api_exceptions(interaction, "omdbAPI", "movie", e)
            return

        if movie_data['Response'] == 'False':
            fail_embed = discord.Embed(description=f"<:BallHmm:851605297863852102> Can't find movie, \"**{title}**\". Make sure title/year are correct :)", color=discord.Color.yellow())
            fail_embed.set_footer(text="✉️ If this seems incorrect, contact Noots")
            await interaction.response.send_message(embed=fail_embed, ephemeral=True)
            return

        embed = discord.Embed(title=f"{movie_data['Title']}", description=f"**[{movie_data['Rated']}]** • {movie_data['Released']} • {movie_data['Genre']} • {movie_data['Runtime']}",
                              color=discord.Colour(0x20205f))
        embed.add_field(name="Plot", value=movie_data['Plot'], inline=False)
        embed.add_field(name="Awards 🏆", value=movie_data['Awards'], inline=True)
        embed.add_field(name="Box Office 💵", value=movie_data['BoxOffice'], inline=True)
        embed.set_thumbnail(url=movie_data['Poster'])
        embed.set_footer(text=f"Requested by {interaction.user.name} • Powered by The Open Movie Database", icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roll", description="Roll a dice")
    @app_commands.describe(sides="Number of sides per dice (defaults to 6)", rolls="Number of rolls (defaults to 1)")
    async def roll(self, interaction: discord.Interaction, sides: app_commands.Range[int, 1, None] = None, rolls: app_commands.Range[int, 1, 16] = None):
        sides = sides if sides else 6
        rolls = rolls if rolls else 1
        accumulator = 0
        roll_numbers = "-# 🎲 "

        if rolls == 1:
            roll_result = random.randint(1, sides)
            await interaction.response.send_message(f"## 🎲 {('{:,}'.format(roll_result))}")
            return

        await interaction.response.send_message("## <a:rolling:1205962287710478346>")

        for r in range(rolls):
            roll_result = random.randint(1, sides)
            accumulator += roll_result
            formatted_result = f"**{('{:,}'.format(roll_result))}**"
            roll_numbers += f"{formatted_result} • "
            await interaction.edit_original_response(content=f"## <a:rolling:1205962287710478346> {formatted_result}\n{roll_numbers}")
            await asyncio.sleep(0.6)

        await interaction.edit_original_response(content=f"## <:Lucia:1253852411542372535> {('{:,}'.format(accumulator))}\n{roll_numbers[:-2]}")

    @app_commands.command(name="topic", description="Start a conversation with a random topic")
    async def topic(self, interaction: discord.Interaction):
        response = get_random_response("topics")
        await interaction.response.send_message(f"> {response[0]}\n-# #{response[1]+1}")

    @app_commands.command(name="weather", description="Check the weather of any city")
    @app_commands.describe(city="Enter a city name")
    async def weather(self, interaction: discord.Interaction, city: str):
        try:
            load_dotenv()
            data = requests.get(f"http://api.openweathermap.org/data/2.5/weather?appid={os.getenv("OPENWEATHER_API")}&q={city}").json()
        except Exception as e:
            await handle_api_exceptions(interaction, "openweathermap", "weather", e)
            return


        if data['cod'] != 200:
            fail_embed = discord.Embed(description=f"<a:EarthOrb:719683332547412021> **City doesn't exist.**\n Searched far and wide, but no city found in sight. Check for typos or try another location.", color=discord.Color.yellow())
            await interaction.response.send_message(embed=fail_embed, ephemeral=True, delete_after=12)
            return

        await interaction.response.defer(thinking=True)

        current_temp = data['main']['temp']
        current_feel = data['main']['feels_like']
        celsius = int(round(current_temp - 273.15))
        fahrenheit = int(round(celsius * 9 / 5 + 32))
        celsius_feel = int(round(current_feel - 273.15))
        fahrenheit_feel = int(round(celsius_feel * 9 / 5 + 32))
        humidity = data['main']['humidity']
        cloud_cover = data['clouds']['all']

        weather = data['weather'][0]['main']
        icon_url = f"http://openweathermap.org/img/w/{data['weather'][0]['icon']}.png"

        offset_time = datetime.timedelta(seconds=data['timezone'])
        time = (datetime.datetime.now(datetime.timezone.utc) + offset_time).strftime('%I:%M %p')

        embed = discord.Embed(title=f"{city.title()}'s Weather Report", colour=discord.Colour(0x21abcf))
        embed.add_field(name="Description", value=f"{weather.title()}")
        embed.add_field(name="Temp", value=f"{celsius}°C | {fahrenheit}°F")
        embed.add_field(name="Feels Like", value=f"{celsius_feel}°C | {fahrenheit_feel}°F")
        embed.add_field(name="Humidity", value=f"{humidity}%")
        embed.add_field(name="Cloud Cover", value=f"{cloud_cover}%")
        embed.add_field(name="Local Time", value=time)
        embed.set_thumbnail(url=icon_url)
        embed.set_footer(text=f"Lookup by {interaction.user.name} | Powered by OpenWeatherAPI", icon_url=interaction.user.avatar)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="xkcd", description="Get an xkcd comic")
    @app_commands.describe(comic="Specify a comic number", latest="View the latest xkcd comic")
    async def xkcd(self, interaction: discord.Interaction, comic: int = None, latest: bool = False):
        async def random_comic():
            try:
                data = requests.get("https://xkcd.com/info.0.json").json()
                return random.randint(1, data['num'])
            except Exception as e:
                await handle_api_exceptions(interaction, "xkcd", "xkcd", e)

        comic = await random_comic() if not comic and not latest else comic
        link = "https://xkcd.com/info.0.json" if latest else f"https://xkcd.com/{comic}/info.0.json"

        try:
            data = requests.get(link).json()
        except Exception as e:
            await handle_api_exceptions(interaction, "xkcd", "xkcd", e)
            return

        embed = discord.Embed(title=f"#{data['num']}: {data['title']}", description=f"{data['alt']}", colour=discord.Colour(0x6e7b91), url=link)
        embed.set_image(url=data['img'])
        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=embed)


async def setup(client):
    await client.add_cog(Fun(client))