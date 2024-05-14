# TODO there is currently lots of unnecessary redundant code here. This is due to some
# lack of understanding on python inheritance, and the lack of enums in pre 3.4
# thereby forcing me to implement my own enums as static classes. Need to research
# and fix this for simplication

class TShirtSizes():
    """
    TShirtSizes class

    Effectively a static class used in lieu of an enum (only supported by python
     3.4+), representing possible tshirt sizes of servers within our server pool
    """
    SMALL   = "SMALL"          # A machine with 2 cores and 4 GB of RAM
    MEDIUM  = "MEDIUM"         # A machine with 4 cores and 16 GB of RAM
    LARGE   = "LARGE"          # A machine with 8 cores and 32 GB of RAM
    VALUES  = [SMALL, MEDIUM, LARGE]

    @staticmethod
    def isValid(sizeStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid tshirt size
        """
        return (sizeStr.upper() in TShirtSizes.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        ctr = 0
        for value in TShirtSizes.VALUES:
            ctr += 1
            if ctr != len(tShirtSize.VALUES):
                str += value + ","
        str += "]"
        return str

class Chipset():
    """
    Chipset class

    Represents the possible CPU manufacturers/types among servers within the
    server pool
    """
    POWER = "POWER"
    INTEL = "INTEL"
    VALUES = [POWER, INTEL]

    @staticmethod
    def isValid(chipsetStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid cpu set
        """
        return (chipsetStr.upper() in Chipset.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        ctr = 0
        for value in Chipset.VALUES:
            ctr += 1
            if ctr != len(Chipset.VALUES):
                str += value + ","
        str += "]"
        return str

class EnvironmentType():
    """
    EnvironmentType class

    Represents the possible environment types among servers within the server pool
    """
    DEV     = "DEV"
    PROD    = "PROD"
    SIT     = "SIT"
    PERF    = "PERF"
    UAT     = "UAT"

    ORG_TO_ENV_MAP = {
                        "Development Environment"   : DEV,
                        "Production Environment"    : PROD,
                        "Staging Environment"       : SIT,
                        "Performance Environment"   : PERF,
                        "UAT Environment"           : UAT
    }
    VALUES = [DEV, PROD, SIT, PERF, UAT]

    @staticmethod
    def isValid(environmentTypeStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid environment type
        """
        return (environmentTypeStr.upper() in EnvironmentType.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        ctr = 0
        for value in EnvironmentType.VALUES:
            ctr += 1
            if ctr != len(EnvironmentType.VALUES):
                str += value + ","
        str += "]"
        return str

class Location():
    """
    Location class
    Represents the possible locations among servers within the server pool
    """
    HB = "HB"           # Harrisonburg, VA
    VA = "VA"           # Richmond, VA
    MO = "MO"           # Missouri
    VALUES = [HB, VA, MO]

    @staticmethod
    def isValid(locationStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid location type
        """
        return (locationStr.upper() in Location.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        ctr = 0
        for value in Location.VALUES:
            ctr += 1
            if ctr != len(Location.VALUES):
                str += value + ","
        str += "]"
        return str

class Tag():
    """
    Tag

    Represents possible tags that a server can assume
    """
    NONE = "NONE"

class ServerPoolProperties():
    """
    ServerPoolProperties class

    A class that collects all the aforementioned server pool/farm server properties
    """
    def __init__(self, tShirtSize, chipset, environmentType, location, tag=Tag.NONE):
        self.tShirtSize      = tShirtSize
        self.chipset         = chipset
        self.environmentType = environmentType
        self.location        = location
        self.tag             = tag

    def getDocument(self):
        """

        :return:
        """
        doc = {
            "tshirtsize"    : self.tShirtSize,
            "chipset"       : self.chipset,
            "env"           : self.environmentType,
            "location"      : self.location,
            "tag"           : self.tag
        }
        return doc

    def __str__(self):
        """
        To String

        Returns a string representation of the object. Does this by returning the
        values on all instance fields.
        """
        # return "{ tshirtsize : {}, chipset : {}, env : {}, location : {}, tag : {} }".format(self.tShirtSize, self.chipset, self.environmentType, self.location, self.tag)
        return "{ tshirtsize : " + self.tShirtSize + ", chipset : " + self.chipset + " , env : " + self.environmentType + ", location : " + self.location + " , tag : " + self.tag + " }"
