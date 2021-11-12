import motor.motor_asyncio

from utils.config import Config

config = Config()

cluster = motor.motor_asyncio.AsyncIOMotorClient(config.mongoURI)

db = cluster["Discord"]

guild_settings = db["settings"]

blacklist = db["blacklist"]
