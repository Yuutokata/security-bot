import datetime
import re
import discord
from discord.ext import commands
import aiohttp
from utils.config import Config
from utils.mongodb import guild_settings

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
        if settings["settings"]["Auto-Ban"]["status"] is True:
            for names in settings["settings"]["Auto-Ban"]["names"]:
                username = await self.decodeUsername(name=member.name.lower())
                name = re.compile(names)
                if re.search(name, username["message"]):
                    await member.guild.ban(member, reason="Auto Banned\n Grund: Raider Group Tag")
                    if settings["settings"]["log"] is not None:
                        channel = self.client.get_channel(int(settings["settings"]["log"]))
                        embed = discord.Embed(title="Auto Banned")
                        embed.add_field(name=f"Name", value=f"{member.name}", inline=True)
                        embed.add_field(name="Time", value=f"<t:{datetime.datetime.now().timestamp()}:T", inline=True)
                        embed.add_field(name="Reason", value="Raider Group Tag", inline=False)
                        embed.set_thumbnail(url=member.avatar_url)
                        await channel.send(embed=embed)

        if int(settings["settings"]["Min-Account-Age"]) > 0 or settings["settings"]["Min-Account-Age"] is not None:
            userAccountDate = member.created_at.timestamp()
            if settings["settings"]["Min-Account-Age"] > userAccountDate:
                readDate = userAccountDate / 3600
                readMin = settings["settings"]["Min-Account-Age"] / 3600
                embed = discord.Embed(title="Account Age", color=int(config.colorMain, 16))
                embed.add_field(name="Account Age", value=f"{readDate} Stunden", inline=True)
                embed.add_field(name="Mindest Account Age", value=f"{readMin} Stunden", inline=True)
                embed.add_field(name="Reason",
                                value=f"Dein Account wurde gekickt da er zu Jung war und wir den Server vor Raid attacken schützen wollen!")

                try:
                    await member.send(embed=embed)
                except:
                    pass

                if settings["settings"]["log"] is not None:
                    channel = self.client.get_channel(int(settings["settings"]["log"]))
                    await channel.send(embed=embed)
        if settings["settings"]["quarantine"]["bots"] is True:
            if member.bot:
                role = discord.utils.get(member.guild.roles, id=int(settings["settings"]["roles"]["quarantine"]))
                await member.add_roles(role)
                if settings["settings"]["log"] is not None:
                    channel = self.client.get_channel(int(settings["settings"]["log"]))
                    embed = discord.Embed(title="Bot Quarantine",
                                          description=f"Der Bot {member.name} wurde in die Quarantine versetzt. Um einen Nuke/Raid zu verhindern falls du gerade nicht da bist.")
                    await channel.send(embed=embed)


def setup(client):
    client.add_cog(AutoBan(client))
