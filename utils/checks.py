import discord
from discord.ext import commands

from utils.config import Config

config = Config()


def isTeam(self):
    async def pred(ctx):
        for roleId in config.team:
            guild = self.client.get_guild(888873222521626674)
            role = discord.utils.get(guild.roles, id=int(roleId))
            if ctx.author in role.members:
                return True
            else:
                return False

    return commands.check(pred)


def isAdmin(self):
    async def pred(ctx):
        for roleId in config.admins:
            guild = self.client.get_guild(888873222521626674)
            role = discord.utils.get(guild.roles, id=int(roleId))
            if ctx.author in role.members:
                return True
            else:
                return False

    return commands.check(pred)


def isDev(self):
    async def pred(ctx):
        for roleId in config.dev_ids:
            guild = self.client.get_guild(888873222521626674)
            role = discord.utils.get(guild.roles, id=int(roleId))
            if ctx.author in role.members:
                return True
            else:
                return False

    return commands.check(pred)
