import configparser
import os


class Fallbacks:
    Token = None
    MongoURI = None
    MongoDB = None
    GoogleApiKey = None
    Prefix = None
    Description = None
    Developer = []
    Admins = []
    Team = []
    statusLock = False
    statusDefault = None
    statusType = 0
    colorMain = "ffffff"
    colorError = "f44336"
    save = False
    emojiWarning = None
    DatabaseAPI = None
    Version = None

class Config:
    def __init__(self):
        self.path = "config/config.ini"

        if not os.path.isfile(self.path):
            raise KeyError("There is no config.ini file in config/config.ini")

        config = configparser.ConfigParser(interpolation=None)

        config.read(self.path, encoding="utf-8")

        sections = {"Credentials", "Bot", "Status", "Color", "Logging"}.difference(
            config.sections())

        if sections:
            raise KeyError("The sections in config/config.ini is not correct")

        self.token = config.get(section="Credentials", option="Token", fallback=Fallbacks.Token)
        self.mongoURI = config.get(section="Credentials", option="MongoURI", fallback=Fallbacks.MongoURI)
        self.mongoDB = config.get(section="Credentials", option="Database Name", fallback=Fallbacks.MongoDB)
        self.googleKey = config.get(section="Credentials", option="Google Api Key", fallback=Fallbacks.GoogleApiKey)
        self.databaseAPI = config.get("Credentials", option="Database API", fallback=Fallbacks.DatabaseAPI)

        self.prefix = config.get(section="Bot", option="Prefix", fallback=Fallbacks.Prefix)
        self.description = config.get(section="Bot", option="Description", fallback=Fallbacks.Description)
        self.developer = config.get(section="Bot", option="Developer", fallback=Fallbacks.Developer)
        self.admins = config.get(section="Bot", option="Admins", fallback=Fallbacks.Admins)
        self.team = config.get(section="Bot", option="Team Roles", fallback=Fallbacks.Team)

        self.statusLock = config.getboolean(section="Status", option="Lock", fallback=Fallbacks.statusLock)
        self.statusDefault = config.get(section="Status", option="Default", fallback=Fallbacks.statusDefault)
        self.statusType = config.getint(section="Status", option="Type", fallback=Fallbacks.statusType)

        self.colorMain = config.get(section="Color", option="Main", fallback=Fallbacks.colorMain)
        self.colorError = config.get(section="Color", option="Error", fallback=Fallbacks.colorError)
        
        self.emojiWarning = config.get(section="Emoji", option="warning", fallback=Fallbacks.emojiWarning)
        
        self.version = config.get(section="Info", option="Version", fallback=Fallbacks.Version)
        self.loggingSave = config.getboolean(section="Logging", option="Save", fallback=Fallbacks.save)

        self.check()

    def check(self):

        if self.mongoURI is None:
            raise RuntimeError("No MongoURI was set")

        if len(self.developer) != 0:
            try:
                ids = self.developer.split()
                self.dev_ids = []
                for id in ids:
                    self.developer.append(int(id))
            except:

                self.developer = Fallbacks.Developer

        if len(self.admins) != 0:
            try:
                ids = self.admins.split()
                self.dev_ids = []
                for id in ids:
                    self.admins.append(int(id))
            except:

                self.admins = Fallbacks.Admins

        if len(self.team) != 0:
            try:
                ids = self.team.split()
                self.dev_ids = []
                for id in ids:

                    self.team.append(int(id))
            except:

                self.team = Fallbacks.Team
