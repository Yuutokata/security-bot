import discord
from discord.ext import commands

from utils.config import Config
from utils.logger import logger
from discord_slash import cog_ext
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_permission
from utils.mongodb import guild_settings
import aiohttp

config = Config()


async def decodeUsername(names: list):
    async with aiohttp.ClientSession() as session:
        async with session.post('https://entity.yuutokata.repl.co/encode',
                                json={"message": names}) as response:
            json = await response.json()
        return json


async def settingsEmbed(ctx, client):
    on = config.on
    off = config.off
    settings = await guild_settings.find_one({"_id": int(ctx.guild.id)})
    settings = settings["settings"]
    embed = discord.Embed(title=f"**{ctx.guild.name}** Settings",
                          description=f"Hier kannst du die Settings vom Server sehen um sie zu bearbeiten gebe jetzt `edit` ein.",
                          color=int(config.colorMain, 16))
    if settings["Links"] is True:
        embed.add_field(name=f"Pishing Links", value=f"**Status:** {on}", inline=False)
    if settings["Links"] is False:
        embed.add_field(name=f"Pishing Links", value=f"**Status:** {off}", inline=False)
    if settings["Invite"] is True:
        embed.add_field(name=f"Invite Links", value=f"**Status:** {on}", inline=False)
    if settings["Invite"] is False:
        embed.add_field(name=f"Invite Links", value=f"**Status:** {off}", inline=False)
    if settings["Auto-Ban"]["status"] is True:
        names = ""
        for name in settings["Auto-Ban"]["names"]:
            names += f"{name}\n"
        embed.add_field(name=f"Auto Ban", value=f"**Status:** {on}\n **Names:**\n `{names}`", inline=False)
    if settings["Auto-Ban"]["status"] is False:
        embed.add_field(name=f"Auto Ban", value=f"**Status:** {off}", inline=False)
    if settings["Min-Account-Age"]["Status"] is True:
        age = int(settings["Min-Account-Age"]["age"]) / 3600
        embed.add_field(name="Mindest Account Alter", value=f"**Status:** {on} \n **Alter:** {round(age)}",
                        inline=False)
    if settings["Min-Account-Age"]["Status"] is False:
        embed.add_field(name="Mindest Account Alter", value=f"**Status:** {off}", inline=False)
    if settings["quarantine"]["bots"] is True:
        embed.add_field(name="Auto Quarantine Bots", value=f"**Status:** {on}", inline=False)
    if settings["quarantine"]["bots"] is False:
        embed.add_field(name="Auto Quarantine Bots", value=f"**Status:** {off}", inline=False)

    if settings["Verification"]["Status"] is True:
        channel = client.get_channel(int(settings["Verification"]["channel"]))
        role = discord.utils.get(ctx.guild.roles, id=int(settings["Verification"]["role"]))
        embed.add_field(name="Verification",
                        value=f"**Status:** {on} **Channel:** {channel.mention} **Role:** {role.mention}", inline=False)
    if settings["Verification"]["Status"] is False:
        embed.add_field(name="Verification", value=f"**Status:** {off}", inline=False)
    if settings["Log"]["Status"] is True:
        channel = client.get_channel(int(settings["Log"]["channel"]))
        embed.add_field(name="Logging", value=f"**Status:** {on}\n **Channel:** {channel.mention}", inline=False)
    if settings["Log"]["Status"] is False:
        embed.add_field(name="Logging", value=f"**Status:** {off}", inline=False)

    return embed


class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx):
        rsettings = await guild_settings.find_one({"_id": int(ctx.guild.id)})
        settings = rsettings["settings"]
        embed = await settingsEmbed(ctx, self.client)
        await ctx.send(embed=embed)

        def check(m):
            if m.author == ctx.author and m.channel == ctx.channel:
                return m.content
            else:
                pass

        msg = await self.client.wait_for('message', check=check)
        if msg.content.lower() == "edit":
            await ctx.send(
                "Was möchtest du bearbeiten?\n **Pishing Links \n Invite Links \n Auto Ban \n Min Acc Alter \n Quarantine Bots \n Verification \nLogging**")
            msg = await self.client.wait_for('message', check=check)
            if msg.content.lower() == "pishing links":
                if settings["Links"] is True:
                    new = settings["Links"] = False
                    await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                    await ctx.send("Pishing Links ist jetzt deaktiviert")

                if settings["Links"] is False:
                    new = settings["Links"] = True
                    await ctx.send("Pishing Links ist jetzt aktiviert")
                    await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
            if msg.content.lower() == "invite links":
                if settings["Invite"] is True:
                    new = settings["Invite"] = False
                    await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                    await ctx.send("Invite Links ist jetzt deaktiviert")

                if settings["Invite"] is False:
                    new = settings["Invite"] = True
                    await ctx.send("Invite Links ist jetzt aktiviert")
                    await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
            if msg.content.lower() == "auto ban":
                await ctx.send("Was möchtest du bearbeiten? \n **Status \n Names**")
                msg = await self.client.wait_for('message', check=check)
                if msg.content.lower() == "status":
                    if settings["Auto-Ban"]["status"] is True:
                        new = settings["Auto-Ban"]["status"] = False
                        await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                        await ctx.send("Auto Ban ist jetzt deaktiviert")

                    if settings["Auto-Ban"]["status"] is False:
                        new = settings["Auto-Ban"]["status"] = True
                        await ctx.send("Auto Ban ist jetzt aktiviert")
                        await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})

                if msg.content.lower() == "names":
                    await ctx.send(
                        "Bitte schicke jetzt alle namen in den chat mit jeweils einem Leerzeichen zwischen den Namen z.B:\n ξ𝙓 du ha niklas [ƉɆ⩔Ӿ]ᶠᵘᶜᵏ")
                    msg = await self.client.wait_for('message', check=check)
                    usernames = await decodeUsername(names=msg.content.lower().split())
                    #new = rsettings["names"] = usernames["message"]
                    print(usernames["message"])
                    await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": {"names": usernames["message"]}})

                    await ctx.send(f"Die neuen Namen sind jetzt:\n {msg.content}")

            if msg.content.lower() == "min acc alter":
                await ctx.send("Was möchtest du bearbeiten? \n **Status \n Alter**")
                msg = await self.client.wait_for('message', check=check)
                if msg.content.lower() == "status":
                    if settings["Min-Account-Age"]["Status"] is True:
                        new = settings["Min-Account-Age"]["Status"] = False
                        await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                        await ctx.send("Mindest Account Alter ist jetzt deaktiviert")

                    if settings["Min-Account-Age"]["Status"] is False:
                        new = settings["Min-Account-Age"]["Status"] = True
                        await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                        await ctx.send("Mindest Account Alter ist jetzt aktiviert")

                if msg.content.lower() == "age":
                    await ctx.send("Bitte gebe eine neue Zeit in Stunden an z.B. 5")
                    msg = await self.client.wait_for('message', check=check)
                    if msg.content == int:
                        new = settings["Min-Account-Age"]["age"] = int(msg.content * 3600)
                        await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                        await ctx.send(f"Das neue Mindest Account Alter ist jetzt {msg.content}")

            if msg.content.lower() == "quarantine bots":
                await ctx.send("Was möchtest du bearbeiten? \n **Status \n Rolle**")
                msg = await self.client.wait_for('message', check=check)
                if msg.content.lower() == "status":
                    if settings["quarantine"]["bots"] is True:
                        new = settings["quarantine"]["bots"] = False
                        await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                        await ctx.send("Auto Quarantine Bots ist jetzt deaktiviert")
                    if settings["quarantine"]["bots"] is False:
                        new = settings["quarantine"]["bots"] = True
                        await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                        await ctx.send("Auto Quarantine Bots ist jetzt aktiviert")

                if msg.content.lower() == "rolle":
                    await ctx.send("Bitte schicke von der neuen Quarantine Rolle die ID in den Chat")
                    msg = await self.client.wait_for('message', check=check)
                    try:
                        role = discord.utils.get(ctx.guild.roles, id=int(msg.content))
                        new = settings["quarantine"]["role"] = int(msg.content)
                        await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                        await ctx.send(f"Die neue Quarantine Rolle ist jetzt {role.mention}")
                    except:
                        await ctx.send("Ich konnte diese Rolle nicht finden")

            if msg.content.lower() == "verification":
                await ctx.send("Was möchtest du bearbeiten? \n **Status \n Channel** \n **Rolle**")
                msg = await self.client.wait_for('message', check=check)
                if msg.content.lower() == "status":
                    if settings["Verification"]["Status"] is True:
                        new = settings["Verification"]["Status"] = False
                        await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                        await ctx.send("Verification ist jetzt deaktiviert")
                    if settings["Verification"]["Status"] is False:
                        new = settings["Verification"]["Status"] = True
                        await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                        await ctx.send("Verification ist jetzt aktiviert")
                if msg.content.lower() == "channel":
                    await ctx.send("Bitte schicke von dem neuen Verification Channel die ID in den Chat")
                    msg = await self.client.wait_for('message', check=check)
                    try:
                        channel = self.client.get_channel(int(msg.content))
                        new = settings["Verification"]["channel"] = int(msg.content)
                        await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                        await ctx.send(f"Der neue Verification Channel ist jetzt {channel.mention}")
                    except:
                        await ctx.send("Ich konnte diesen Channel nicht finden")
                if msg.content.lower() == "rolle":
                    await ctx.send("Bitte schicke von der neuen Verification Rolle die ID in den Chat")
                    msg = await self.client.wait_for('message', check=check)
                    try:
                        role = discord.utils.get(ctx.guild.roles, id=int(msg.content))
                        new = settings["Verification"]["role"] = int(msg.content)
                        await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                        await ctx.send(f"Die neue Verification Rolle ist jetzt {role.mention}")
                    except:
                        await ctx.send("Ich konnte diese Rolle nicht finden")

            if msg.content.lower() == "logging":
                await ctx.send("Was möchtest du bearbeiten? \n **Status \n Channel**")
                msg = await self.client.wait_for('message', check=check)
                if msg.content.lower() == "status":
                    if settings["Log"]["Status"] is True:
                        new = settings["Log"]["Status"] = False
                        await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                        await ctx.send("Logging ist jetzt deaktiviert")
                    if settings["Log"]["Status"] is False:
                        new = settings["Log"]["Status"] = True
                        await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                        await ctx.send("Logging ist jetzt aktiviert")

                if msg.content.lower() == "channel":
                    await ctx.send("Bitte schicke von dem neuen Logging Channel die ID in den Chat")
                    msg = await self.client.wait_for('message', check=check)
                    try:
                        channel = self.client.get_channel(int(msg.content))
                        new = settings["Log"]["channel"] = int(msg.content)
                        await guild_settings.update_one({"_id": int(ctx.guild.id)}, {"$set": new})
                        await ctx.send(f"Der neue Logging Channel ist jetzt {channel.mention}")
                    except:
                        await ctx.send("Ich konnte diesen Channel nicht finden")


def setup(client):
    client.add_cog(Settings(client))
