import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import os
from dotenv import load_dotenv
from data.database import get_config_info

client = commands.Bot(command_prefix=".", help_command=None, intents=discord.Intents.all())


async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")


@client.event
async def on_ready():
    await load()
    await client.tree.sync()
    await client.change_presence(status=eval(get_config_info("presence")["status"]), activity=discord.Game(name=get_config_info("presence")["activity"]))
    print(f"\n{client.user.name} has connected to Discord.")


@client.event
async def on_command_error(error):  # Safeguards from mistaking all periods as prefixes
    if isinstance(error, CommandNotFound):
        return

load_dotenv()
client.run(os.getenv("TOKEN"))
