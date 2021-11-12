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
        filter = await self.filterFonts(name=name)
        if filter is not None:
            async with aiohttp.ClientSession() as session:
                async with session.post('https://entity.yuutokata.repl.co/encode',
                                        json={"message": f"{filter}"}) as response:
                    json = await response.json()
            return json["message"]
        else:
            return False

    async def filterFonts(self, name: str):
        chars = re.compile(r"([^-_a-zA-Z0-9!@#%&=,/'\";:~`\$\^\*\(\)\+\[\]\.\{\}\|\?\<\>\\]+|[^\s]+)")
        filtered = ""
        for char in name:
            if not re.search(chars, name):
                filtered += str(char)

        print(filtered)

        if filtered == "":
            return None
        return filtered

    @commands.Cog.listener()
    async def on_member_join(self, member):
        settings = await guild_settings.find_one({"_id": int(member.guild.id)})
        if settings["settings"]["Auto-Ban"]["status"] is True:
            for name in settings["settings"]["Auto-Ban"]["names"]:
                username = await self.decodeUsername(name=member.name.lower())
                if re.search(username, name):
                    await member.guild.ban(member, reason="Auto Banned\n Reason: Auto Ban Name")

        if settings["settings"]["Min-Account-Age"] > 0 or settings["settings"]["Min-Account-Age"] is not None:
            userAccountDate = member.created_at.timestamp()
            if settings["settings"]["Min-Account-Age"] > userAccountDate:
                readDate = userAccountDate / 3600
                readMin = settings["settings"]["Min-Account-Age"] / 3600
                embed = discord.Embed(title="Account Age", color=int(config.colorMain, 16))
                embed.add_field(name="Account Age", value=f"{readDate} Stunden", inline=True)
                embed.add_field(name="Mindest Account Age", value=f"{readMin} Stunden", inline=True)
                embed.add_field(name="Reason",
                                value=f"Dein/Der Account wurde gekickt da er zu Jung war und wir den Server vor Raid attacken schützen wollen!")

                try:
                    await member.send(embed=embed)
                except:
                    pass

                if settings["settings"]["log"] is not None:
                    channel = self.client.get_channel(int(settings["settings"]["log"]))
                    await channel.send(embed=embed)


def setup(client):
    client.add_cog(AutoBan(client))
