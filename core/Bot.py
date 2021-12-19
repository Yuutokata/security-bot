import asyncio
import os
import random

import discord
from discord.ext import commands, tasks

from utils.config import Config
from utils.logger import logger, session_id
from utils.mongodb import blacklist, guild_settings


class Bot(commands.Bot):
    def __init__(self):
        allowed_mentions = discord.AllowedMentions(everyone=False, users=True, roles=True)
        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=True,
            voice_states=True,
            messages=True,
            reactions=True)
        super().__init__(command_prefix=Config().prefix,
                         intents=intents,
                         allowed_mentions=allowed_mentions,
                         description=Config().description,
                         heartbeat_timeout=150.0,
                         chunk_guilds_at_startup=False)

        self.config = Config()
        self.logger = logger
        self.blacklist = blacklist
        self.settings = guild_settings
        self.session_id = session_id

    async def on_ready(self):
        self.logger.debug(f"Bot Started with Session ID: {self.session_id} ...", extra={"emoji": ":rocket:"})
        self.logger.debug(f"Name: {self.user.name}", extra={"emoji": ":rocket:"})
        self.logger.debug(f"Id: {self.user.id}", extra={"emoji": ":rocket:"})

    async def on_guild_join(self, guild):
        self.logger.info(f"Joined new Server {guild.name}")
        try:
            await self.settings.insert_one({"_id": int(guild.id),
                                            "settings": {"Links": False, "Log": {"Status": False, "channel": None},
                                                         "Invite": False,
                                                         "Auto-Ban": {"status": False},
                                                         "Min-Account-Age": {"Status": False, "age": None},
                                                         "quarantine": {"bots": False, "role": None},
                                                         "Verification": {"Status": False, "channel": None,
                                                                          "role": None}},
                                            "names": []})
        except:
            pass

    async def on_guild_remove(self, guild):
        self.logger.error(f"Left Server {guild.name}")
        try:
            await self.settings.remove_one({"_id": int(guild.id)})
        except:
            pass

    @tasks.loop(minutes=15)
    async def activity(self):
        await self.wait_until_ready()
        presences = ["user", "guilds"]
        presence = random.choice(presences)
        status = self.status()
        if presence == "user":
            users = len(self.users) - self.get_guild(839207316808007761).member_count
            await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name=f"{users} Users"),
                status=status)
        if presence == "guilds":
            guild = len(self.guilds) - 1
            await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name=f"{guild} Guilds"),
                status=status)

    def presence(self):
        status = self.status()
        if self.config.statusLock is True:
            asyncio.run(self.change_presence(
                activity=discord.Game(name=self.config.statusDefault),
                status=status))

        if self.config.statusLock is False:
            self.activity.start()

    def status(self):
        if self.config.statusType == 0:
            return discord.Status.online
        if self.config.statusType == 1:
            return discord.Status.idle
        if self.config.statusType == 2:
            return discord.Status.offline

    def cogs(self):
        if not os.path.isdir("cogs"):
            return
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    self.load_extension(f'cogs.{filename[:-3]}')
                except Exception as e:
                    logger.error(f"Cant Load {filename[:-3]} Reason: {e} ", extra={"emoji": ":stop_sign:"})

    async def close(self):
        await super().close()

    def run(self):
        self.logger.debug(f"Starting ...", extra={"emoji": ":bomb:"})
        try:
            try:
                self.cogs()
                self.presence()
            finally:
                super().run(self.config.token, reconnect=True, bot=True)

        except Exception as e:
            self.logger.critical(f"The Bot can't start, Reason: {e}", extra={"emoji": ":warning:"})
