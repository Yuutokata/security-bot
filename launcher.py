from core.Bot import Bot
from discord_slash import SlashCommand

client = Bot()
slash = SlashCommand(client)

if __name__ == '__main__':
    client.run()
