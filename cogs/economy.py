import discord
from discord.ext import commands
from discord import app_commands
import data.database as db
from data.database import update_balance_value, get_economy_profile, get_random_response
import random
import time


async def send_exit_message(message, interaction):
    embed = discord.Embed(description=f"<:coffee:1249421545437270136> {message}", color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

def get_net_worth(bal):
    return bal['wallet'] + bal['bank']


class Economy(commands.Cog, description="<a:LuciaOrb:1251215260031914048>"):
    def __init__(self, client):
        self.client = client
        self.currency_icon = "<a:LuciaOrb:1251215260031914048>"
        self.net_worth_icon = "<a:LuciaOrbGold:1251216810817359993>"
        self.bank_note_icon = "<:LuciaBankNote:1252676126699028685>"
        self.coffee = "<:coffee:1249421545437270136>"

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.tree.sync()
        print(f"{__name__} is ready.")

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            remaining_time = int(time.time()) + round(error.retry_after)
            embed = discord.Embed(description=f"{self.coffee} **Slow down**. You can try again <t:{remaining_time}:R>.", color=discord.Color.dark_gray())
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        else:
            embed = (discord.Embed(description="**whoops**. Lucia tripped over a wire. Please try again later.", color=discord.Color.dark_red())
                     .set_footer(text="⚠️ If this persists, notify Noted"))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            print(f"(X) Error while using Economy command by {interaction.user.name} - {error}")    # todo: fix this


    @app_commands.guild_only()
    @app_commands.command(name="balance", description="View your balance")
    @app_commands.describe(member="View someone else's balance")
    async def balance(self, interaction: discord.Interaction, member: discord.User = None):
        member = member if member else interaction.user

        if member.bot:
            await send_exit_message("Can't read a bot's balance if they don't have one.", interaction)
            return

        bal = db.get_economy_profile(member.id)['balance']
        embed = discord.Embed(color=discord.Color.blurple())
        embed.set_author(name=member.name, icon_url=member.avatar)
        embed.add_field(name="Wallet", value=f"{self.currency_icon} {bal['wallet']:,}")
        embed.add_field(name="Bank", value=f"{self.currency_icon} {bal['bank']:,}/{bal['storage']:,}")
        embed.add_field(name="Net Worth", value=f"{self.net_worth_icon} {get_net_worth(bal):,}")

        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @app_commands.command(name="inventory", description="View your inventory")
    @app_commands.describe(member="View someone else's inventory")
    async def inventory(self, interaction: discord.Interaction, member: discord.User = None):
        member = member if member else interaction.user

        if member.bot:
            await send_exit_message("Can't let you view a bot's inventory, it's all binary.", interaction)
            return

        inv = db.get_economy_profile(member.id)['inventory']

        inventory_list = ""
        for name, qty in inv.items():
            for shop_item in db.get_all_shop_items():
                if shop_item['name'] == name:
                    inventory_list += f"{shop_item['emoji']} **{name}** ─ {qty:,}\n"

        embed = discord.Embed(description=inventory_list, colour=discord.Color.blurple())
        embed.set_author(name=member.name, icon_url=member.avatar)
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @app_commands.command(name="bank", description="View Lucia's bank assets")
    async def bank(self, interaction: discord.Interaction):
        bank = get_economy_profile("bank")['balance']
        lucia = self.client.get_user(1089292852963590224)

        embed = discord.Embed(color=discord.Color.blurple())
        embed.set_author(name=f"{lucia.name}'s Bank Vault", icon_url=lucia.avatar)
        embed.add_field(name="Register", value=f"{self.currency_icon} {bank['register']:,}")
        embed.add_field(name="Vault", value=f"{self.currency_icon} {bank['vault']:,}")
        embed.add_field(name="Total", value=f"{self.net_worth_icon} {(bank['register'] + bank['vault']):,}")
        embed.set_footer(text="💰 Bank robberies are under development.")
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 600)
    @app_commands.command(name="work", description="Earn orbs by working")
    async def work(self, interaction: discord.Interaction):
        user = get_economy_profile(interaction.user.id)     # Used to initialize member if no account exists

        work_amount = random.randint(20, 375)
        response, index = get_random_response("work")
        formatted_response = response.format(amt=f"{self.currency_icon} **{work_amount}**")

        embed = discord.Embed(description=formatted_response, color=discord.Color.green())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.set_footer(text=f"Reply #{index+1}")

        update_balance_value(interaction.user.id, "wallet", work_amount)
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 600)
    @app_commands.command(name="crime", description="Steal orbs to earn orbs")
    async def crime(self, interaction: discord.Interaction):
        user = get_economy_profile(interaction.user.id)

        success = True if random.random() < .45 else False

        if success:
            response, index = get_random_response("crime-success")
            crime_amount = random.randint(275, 975)
            update_balance_value(interaction.user.id, "wallet", crime_amount)
            resp = response.format(amt=f"{self.currency_icon} **{crime_amount}**")
            embed = discord.Embed(description=resp, color=discord.Color.dark_green())
        else:
            response, index = get_random_response("fail-crime")
            crime_amount = random.randint(250, 850)
            update_balance_value(interaction.user.id, "wallet", -crime_amount)
            update_balance_value("bank", "register", round(crime_amount * .1))
            update_balance_value("bank", "vault", round(crime_amount * .9))

            resp = response.format(amt=f"{self.currency_icon} **{crime_amount}**")
            embed = discord.Embed(description=resp, color=discord.Color.red())

        embed.set_footer(text=f"Reply #{index + 1}")
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        await interaction.followup.send(embed=embed)

    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 1200, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(member="Select who you want to rob")
    @app_commands.command(name="rob", description="Rob an unsuspecting member")
    async def rob(self, interaction: discord.Interaction, member: discord.Member):
        if member.bot:
            await send_exit_message("Try robbing a bot and they'll smite you. I'm not getting in the crossfire.", interaction)
            return

        if member.id == interaction.user.id:
            await send_exit_message("You can't rob yourself.", interaction)
            return

        robber = get_economy_profile(interaction.user.id)
        victim = get_economy_profile(member.id)['balance']

        if victim['wallet'] < 1:
            await send_exit_message(f"{member.mention} has no orbs in their wallet to rob.", interaction)
            return

        success = True if random.random() < .6 else False

        if success:
            winnings_percentage = max(0.2, min(random.random(), 0.8))
            winnings = round(winnings_percentage * victim['wallet'])
            update_balance_value(interaction.user.id, "wallet", winnings)
            update_balance_value(member.id, "wallet", -winnings)
            embed = discord.Embed(description=f"Successfully robbed {member.mention} for {self.currency_icon} **{winnings:,}**.", color=discord.Color.dark_green())
        else:
            fine = random.randint(350, 1000)
            update_balance_value(interaction.user.id, "wallet", -fine)
            update_balance_value("bank", "vault", fine)
            embed = discord.Embed(description=f"Failed to rob {member.mention}, you've been fined {self.currency_icon} **{fine:,}**.", color=discord.Color.red())

        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @app_commands.command(name="give", description="Give some orbs to someone else")
    @app_commands.describe(member="Select who you want to give orbs to", orbs="Number of orbs to give (defaults to ALL if left blank)")
    async def give(self, interaction: discord.Interaction, member: discord.User, orbs: int = None):
        if member.bot:
            await send_exit_message("You can't give orb currency to a bot.", interaction)
            return

        if member.id == interaction.user.id:
            await send_exit_message("No, you can't use this as an infinite orb generator.", interaction)
            return

        sender = db.get_economy_profile(interaction.user.id)['balance']['wallet']
        receiver = db.get_economy_profile(member.id)   # Used to initialize receiver if user hasn't used Lucia

        if sender < 1:
            await send_exit_message("You MUST have at least **1** orb in your wallet to give orbs.", interaction)
            return

        orbs = orbs if orbs else sender
        orbs = sender if orbs > sender else orbs

        if orbs < 1:
            await send_exit_message("You can't give someone zero orbs.", interaction)
            return

        update_balance_value(interaction.user.id, "wallet", -orbs)
        update_balance_value(member.id, "wallet", orbs)

        embed = discord.Embed(description=f"Gave {self.currency_icon} **{orbs:,}** to {member.mention}", colour=discord.Color.green())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @app_commands.command(name="deposit", description="Deposit your orbs to your safe vault")
    async def deposit(self, interaction: discord.Interaction, orbs: int = None):
        bal = get_economy_profile(interaction.user.id)['balance']

        orbs = orbs if orbs else bal['wallet']
        orbs = bal['wallet'] if orbs > bal['wallet'] else orbs

        if orbs < 1:
            await send_exit_message("I can only deposit orbs to your bank, not air.", interaction)
            return

        if orbs + bal['bank'] > bal['storage']:
            orbs = bal['storage'] - bal['bank']

        if orbs < 1:
            await send_exit_message(f"**Your bank is full**. Use bank notes to expand your bank vault. {self.bank_note_icon}", interaction)
            return

        update_balance_value(interaction.user.id, "wallet", -orbs)
        update_balance_value(interaction.user.id, "bank", orbs)

        embed = discord.Embed(description=f"Deposited {self.currency_icon} **{orbs:,}** to your bank.", color=discord.Color.green())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @app_commands.command(name="withdraw", description="Withdraw orbs to your wallet")
    async def withdraw(self, interaction: discord.Interaction, orbs: int = None):
        bal = get_economy_profile(interaction.user.id)['balance']

        orbs = orbs if orbs else bal['bank']
        orbs = bal['bank'] if orbs > bal['bank'] else orbs

        if orbs < 1:
            await send_exit_message("**Your bank is empty**. There are no orbs to withdraw", interaction)
            return

        update_balance_value(interaction.user.id, "wallet", orbs)
        update_balance_value(interaction.user.id, "bank", -orbs)

        embed = discord.Embed(description=f"Withdrew {self.currency_icon} **{orbs:,}** from your bank.", color=discord.Color.green())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @app_commands.command(name="leaderboard", description="View the economic leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        def get_rank_ordinal(num):
            return f"{num}th" if 11 <= (num % 100) <= 13 else f"{num}{['th', 'st', 'nd', 'rd', 'th'][min(num % 10, 4)]}"

        users = db.get_all_economy_profiles()
        sorted_users = sorted(users, key=lambda user: get_net_worth(user['balance']), reverse=True)[:10]

        leaderboard_list = ""
        user_rank = "You don't have a ranking. Use /work to get started :3"
        for i, user in enumerate(sorted_users):
            if interaction.user.id == int(user['userId']):
                user_rank = f"You're in {get_rank_ordinal(i+1)} place"
            leaderboard_list += f"**{i+1}**. {self.client.get_user(int(user['userId'])).mention} • {self.currency_icon} {get_net_worth(user['balance']):,}\n"

        embed = discord.Embed(description=leaderboard_list, colour=discord.Color.blurple())
        embed.set_author(name="Leaderboard", icon_url=interaction.guild.icon)
        embed.set_footer(text=user_rank, icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=embed)

    # TODO: Add /shop commands + modals


async def setup(client):
    await client.add_cog(Economy(client))