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
    statusLock = False
    statusDefault = None
    statusType = 0
    colorMain = "ffffff"
    colorError = "f44336"
    save = False


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

        self.prefix = config.get(section="Bot", option="Prefix", fallback=Fallbacks.Prefix)
        self.description = config.get(section="Bot", option="Description", fallback=Fallbacks.Description)
        self.developer = config.get(section="Bot", option="Developer", fallback=Fallbacks.Developer)
        self.admins = config.get(section="Bot", option="Admins", fallback=Fallbacks.Admins)

        self.statusLock = config.getboolean(section="Status", option="Lock", fallback=Fallbacks.statusLock)
        self.statusDefault = config.get(section="Status", option="Default", fallback=Fallbacks.statusDefault)
        self.statusType = config.getint(section="Status", option="Type", fallback=Fallbacks.statusType)

        self.colorMain = config.get(section="Color", option="Main", fallback=Fallbacks.colorMain)
        self.colorError = config.get(section="Color", option="Error", fallback=Fallbacks.colorError)

        self.loggingSave = config.getboolean(section="Logging", option="Save", fallback=Fallbacks.save)

        self.check()

    def check(self):

        if len(self.developer) != 0:
            try:
                ids = self.developer.split()
                self.dev_ids = []
                for id in ids:
                    self.developer.append(int(id))
            except:
                # logger.warning("The Developer IDs are Invalid!",
                #              error={"emoji": ":warning:"})
                self.developer = Fallbacks.Developer
            os._exit(1)

        if len(self.admins) != 0:
            try:
                ids = self.admins.split()
                self.dev_ids = []
                for id in ids:
                    self.admins.append(int(id))
            except:
                # logger.warning("The Admin IDs are Invalid!",
                #              error={"emoji": ":warning:"})
                self.admins = Fallbacks.Admins
            os._exit(1)
