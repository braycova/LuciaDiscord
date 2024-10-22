import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import os
from dotenv import load_dotenv

client = commands.Bot(command_prefix=".", help_command=None, intents=discord.Intents.all())


async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")


@client.event
async def on_ready():
    await load()
    await client.tree.sync()
    print(f"\n{client.user.name} has connected to Discord.")


@client.event
async def on_command_error(error):  # Safeguards from mistaking all periods as prefixes
    if isinstance(error, CommandNotFound):
        return

load_dotenv()
client.run(os.getenv("TOKEN"))
