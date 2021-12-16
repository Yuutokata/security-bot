import datetime
import re
import discord
from discord.ext import commands
import aiohttp
from utils.config import Config
from utils.mongodb import guild_settings
from utils.logger import logger

config = Config()


class AutoBan(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def decodeUsername(self, name: str):
        async with aiohttp.ClientSession() as session:
            async with session.post('https://entity.yuutokata.repl.co/encode',
                                    json={"message": f"{name}"}) as response:
                json = await response.json()
            return json

    @commands.Cog.listener()
    async def on_member_join(self, member):
        settings = await guild_settings.find_one({"_id": int(member.guild.id)})
        settings = settings["settings"]
        if settings["Auto-Ban"]["status"] is True:
            username = await self.decodeUsername(name=member.name.lower())
            for names in settings["Auto-Ban"]["names"]:
                name = re.compile(names)
                if re.search(name, username["message"]):
                    await member.guild.ban(member, reason="Auto Banned\n Grund: Raider Group Tag")
                    if settings["Log"]["Status"]:
                        logger.info(f"{member.name} got banned potential Raider")
                        try:
                            channel = self.client.get_channel(int(settings["Log"]["channel"]))
                            embed = discord.Embed(title="Auto Banned")
                            embed.add_field(name=f"Name", value=f"{member.name}", inline=True)
                            embed.add_field(name="Time", value=f"<t:{round(datetime.datetime.now().timestamp())}:f:",
                                            inline=True)
                            embed.add_field(name="Reason", value="Raider Group Tag", inline=False)
                            embed.set_thumbnail(url=member.avatar_url)
                            await channel.send(embed=embed)
                        except:
                            pass
        if settings["Min-Account-Age"]["Status"]:
            if settings["Min-Account-Age"]["age"] is not None:
                userAccountDate = member.created_at.timestamp()
                if int(settings["Min-Account-Age"]["age"]) > userAccountDate:
                    readMin = round(settings["Min-Account-Age"]["age"]) / 3600
                    embed = discord.Embed(title="Account Alter", color=int(config.colorMain, 16))
                    embed.add_field(name="Account Alter", value=f"<t:{round(userAccountDate)}:f>", inline=True)
                    embed.add_field(name="Mindest Alter", value=f"{round(readMin)} Stunden", inline=True)
                    embed.add_field(name="Grund",
                                    value=f"Dein Account wurde gekickt da er zu Jung war und wir den Server vor Raid attacken schützen wollen!")

                    try:
                        await member.send(embed=embed)
                    except:
                        pass

                    if settings["Log"]["Status"]:
                        logger.info(f"{member.name}'s got Kicked because its too young", extra={"emoji": ":warning:"})
                        try:
                            channel = self.client.get_channel(int(settings["Log"]["channel"]))
                            await channel.send(embed=embed)
                        except:
                            pass

                    await member.kick(reason=f"The Account was too young")

        if settings["quarantine"]["bots"] is True:
            if member.bot:
                role = discord.utils.get(member.guild.roles, id=int(settings["role"]["quarantine"]))
                await member.add_roles(role)
                if settings["Log"]["Status"]:
                    channel = self.client.get_channel(int(settings["Log"]["channel"]))
                    embed = discord.Embed(title="Bot Quarantine",
                                          description=f"Der Bot {member.name} wurde in die Quarantine versetzt. Um einen Nuke/Raid zu verhindern falls du gerade nicht da bist.")
                    await channel.send(embed=embed)


def setup(client):
    client.add_cog(AutoBan(client))
