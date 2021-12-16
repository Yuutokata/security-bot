import datetime
import re

import discord
import requests
from discord.ext import commands

from utils.config import Config
from utils.mongodb import guild_settings
from utils.logger import logger

config = Config()


class Links(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def checkPish(self, link):
        r = requests.get("https://api.yuutokata.repl.co/domains", headers={"Token": config.databaseAPI})
        for url in r.json():
            if link == url:
                return True
            else:
                pass

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self, message):
        settings = await guild_settings.find_one({"_id": int(message.guild.id)})
        settings = settings["settings"]
        if settings["Links"] is True:
            regex = re.compile(
                r"(?:https?:\\.)?(www\.)?[-a-zA-Z0-9@:%.+~#=]{2,256}\.[a-z]{2,6}\b[-a-zA-Z0-9@:%+.~#?&=]*")
            search = re.search(regex, message.content.lower())
            if search:
                if await self.checkPish(link=search.group(0)):
                    embed = discord.Embed(title=f"{config.emojiWarning} Pishing Link {config.emojiWarning}",
                                          color=int(config.colorMain, 16), description=f"""\n\rDiese Website könnte dich dazu verleiten, etwas Gefährliches zu tun,
                        wie z. B. Software zu installieren oder deine persönlichen Daten (z. B. Kennwörter, Telefonnummern oder Kreditkarten) preiszugeben.
                        Weitere Informationen über Phishing/Social Engineering (Phishing) finden Sie unter [Phishing(Phishing und betrügerische Websites)](https://support.google.com/webmasters/answer/6350487)
                        oder unter [www.antiphishing.org](https://www.antiphishing.org).""")
                    embed.add_field(name="Domain", value=f"||{search.group(0)} ||")
                    embed.set_footer(text="Powered by Phish.surf")
                    await message.channel.send(embed=embed)
                    await message.delete()
                    try:
                        await message.guild.kick(message.author, reason=f"Pishing Link:\n{search.group(0)}")
                    except:
                        pass
                    if settings["Log"]["Status"]:
                        logger.info(f"{message.author.name} send a Pishing Domain/Link in {message.channel.name}",
                                    extra={"emoji": ":warning:"})
                        if settings["Log"]["channel"] is not None:
                            try:
                                channel = self.client.get_channel(int(settings["Log"]["channel"]))
                                embed = discord.Embed(title=f"{config.emojiWarning} Invite {config.emojiWarning}",
                                                      color=int(config.colorMain, 16),
                                                      description=f"\n\r {message.author.name} \n hat einen Link in {message.channel.mention} geschickt.")
                                embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)

                                await channel.send(embed=embed)
                            except:
                                pass

        if settings["Invite"] is True:
            regex = re.compile(r'discord(?:\.com|app\.com|\.gg)/(?:invite/)?([a-zA-Z0-9\-]{2,32})')
            search = re.search(regex, message.content.lower())
            if search:
                if not message.author.guild_permissions.administrator:
                    await message.delete()
                    embed = discord.Embed(title=f"{config.emojiWarning} Invite {config.emojiWarning}",
                                          color=int(config.colorMain, 16),
                                          description=f"\n\r {message.author.mention} \nBitte sende keine Server Invites in einen Channel von diesem Server,"
                                                      "dies ist gegen unsere Regeln. Sollte sich dies wiederholen wirst du bestraft.")
                    await message.channel.send(embed=embed)

                    if settings["Log"]["Status"]:
                        logger.info(f"{message.author.name} send a Server Invite in {message.channel.name}",
                                    extra={"emoji": ":warning:"})
                        if settings["Log"]["channel"] is not None:
                            try:
                                channel = self.client.get_channel(int(settings["Log"]["channel"]))
                                embed = discord.Embed(title=f"{config.emojiWarning} Invite {config.emojiWarning}",
                                                      color=int(config.colorMain, 16),
                                                      description=f"\n\r {message.author.name} \n hat einen Link in {message.channel.mention} geschickt.")
                                embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)

                                await channel.send(embed=embed)
                            except:
                                pass


def setup(client):
    client.add_cog(Links(client))
