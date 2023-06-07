# TODO there is currently lots of unnecessary redundant code here. This is due to some
# lack of understanding on python inheritance, and the lack of enums in pre 3.4
# thereby forcing me to implement my own enums as static classes. Need to research
# and fix this for simplication

class MongoDTypeName():
    """
    MongoDTypeName class

    Effectively a static class used in lieu of an enum (only supported by python
    3.4+), representing possible mongod types reported by the API call
    GET /groups/{GROUP-ID}/hosts
    """
    STANDALONE = "STANDALONE"
    REPLICA_PRIMARY = "REPLICA_PRIMARY"
    REPLICA_SECONDARY = "REPLICA_SECONDARY"
    REPLICA_ARBITER = "REPLICA_ARBITER"
    RECOVERING = "RECOVERING"
    MASTER = "MASTER"
    SLAVE = "SLAVE"
    SHARD_MONGOS = "SHARD_MONGOS"
    SHARD_CONFIG = "SHARD_CONFIG"
    SHARD_PRIMARY = "SHARD_PRIMARY"
    SHARD_SECONDARY = "SHARD_SECONDARY"
    NO_DATA = "NO_DATA"
    VALUES = [STANDALONE, REPLICA_PRIMARY, REPLICA_SECONDARY, REPLICA_ARBITER, RECOVERING,
                MASTER, SLAVE, SHARD_MONGOS, SHARD_CONFIG, SHARD_PRIMARY, SHARD_SECONDARY,
                NO_DATA]

    @staticmethod
    def isValid(mongoDTypeNameStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid deployment topology
        """
        return (mongoDTypeNameStr.upper() in MongoDTypeName.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        ctr = 0
        for value in MongoDTypeName.VALUES:
            ctr += 1
            if ctr != len(MongoDTypeName.VALUES):
                str += value + ","
        str += "]"
        return str

class ServerPoolServerStatusName():
    """
    ServerPoolServerStatusName

    Represents the state of servers within the server pool
    """
    AVAILABLE = "AVAILABLE"         # The server is available to host new MongoDB instances.
                                    # It is not bound to a project.

    RESERVED = "RESERVED"           # The server has been selected as part of a multi-server
                                    # request that is still executing.

    BOUND = "BOUND"                 # The server is hosting one or more MongoDB processes.
                                    # The server is visible only to the project that is running
                                    # the processes.

    NEEDS_CLEAN = "NEEDS_CLEAN"     # The server is no longer hosting MongoDB processes and
                                    # no longer bound to a project, but the server still contains
                                    # the MongoDB data and logs. The server has not yet been returned to
                                    # the server pool and is not visible to Ops Manager users.

    TRASH = "TRASH"                 # The server is no longer hosting MongoDB processes and
                                    # no longer bound to a project. The server no longer contains
                                    # the MongoDB data and logs. The server has not yet been returned to
                                    # the server pool and is not visible to Ops Manager users.

    DELETED = "DELETED"             # The server has been removed from Ops Manager.
    VALUES = [AVAILABLE, RESERVED, BOUND, NEEDS_CLEAN, TRASH]

    @staticmethod
    def isValid(serverPoolStatusNameStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid deployment topology
        """
        return (serverPoolStatusNameStr.upper() in ServerPoolServerStatusName.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        ctr = 0
        for value in ServerPoolServerStatusName.VALUES:
            ctr += 1
            if ctr != len(ServerPoolServerStatusName.VALUES):
                str += value + ","
        str += "]"
        return str

class ServerPoolRequestStatusName():
    """
    ServerPoolRequestStatusName class

    Represents possible server pool request states
    """
    EXECUTING   = "EXECUTING"
    CANCELLING  = "CANCELLING"
    CANCELLED   = "CANCELLED"
    FAILED      = "FAILED"
    COMPLETED   = "COMPLETED"
    VALUES = [EXECUTING, CANCELLING, CANCELLED, FAILED, COMPLETED]

    @staticmethod
    def isValid(serverPoolRequestStatusNameStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid deployment topology
        """
        return (serverPoolRequestStatusNameStr.upper() in ServerPoolRequestStatusName.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        ctr = 0
        for value in ServerPoolRequestStatusName.VALUES:
            ctr += 1
            if ctr != len(ServerPoolRequestStatusName.VALUES):
                str += value + ","
        str += "]"
        return str

class AgentTypeName():
    """
    AgentTypeName class

    Represents possible agent types
    """
    MONITORING  = "MONITORING"
    BACKUP      = "BACKUP"
    AUTOMATION  = "AUTOMATION"
    VALUES = [MONITORING, BACKUP, AUTOMATION]

    @staticmethod
    def isValid(agentTypeNameStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid agent type
        """
        return (agentTypeNameStr.upper() in AgentTypeName.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        ctr = 0
        for value in AgentTypeName.VALUES:
            ctr += 1
            if ctr != len(AgentTypeName.VALUES):
                str += value + ","
        str += "]"
        return str

class AgentStatusName():
    """
    AgentStatusName class

    Represents possible running states of a mongodb ops manager status
    """
    ACTIVE          = "ACTIVE"
    STANDBY         = "STANDBY"
    NO_PROCESSES    = "NO_PROCESSES"
    VALUES = [ACTIVE, STANDBY, NO_PROCESSES]

    @staticmethod
    def isValid(agentStatusNameStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid agent state
        """
        return (agentStatusNameStr.upper() in AgentStatusName.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        ctr = 0
        for value in AgentStatusName.VALUES:
            ctr += 1
            if ctr != len(AgentStatusName.VALUES):
                str += value + ","
        str += "]"
        return str
