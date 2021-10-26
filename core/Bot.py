import asyncio
import os
import random

import discord
from discord.ext import commands, tasks

from utils.config import Config
from utils.logger import logger
from utils.mongodb import blacklist


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

    async def on_ready(self):
        self.logger.debug(f"Bot Started ...", extra={"emoji": ":rocket:"})

    async def process_commands(self, message):
        ctx = await self.get_context(message)
        if ctx.command is None:
            return

        if self.blacklist.find_one({"_id": int(ctx.author.id)}):
            print("Test")
            return

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    @tasks.loop(minutes=15)
    async def activity(self):
        await self.wait_until_ready()
        presences = ["user", "guilds"]
        presence = random.choice(presences)
        status = self.status()
        if presence == "user":
            await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.users)} Users"),
                status=status)
        if presence == "guilds":
            await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.guilds)} Guilds"),
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
