import discord
from discord.ext import commands

import utils.checks
from utils.config import Config

config = Config()


class Team(commands.Cog):
    def __init__(self, client):
        self.client = client



def setup(client):
    client.add_cog(Team(client))
