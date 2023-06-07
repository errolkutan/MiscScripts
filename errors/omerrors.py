import sys
sys.path.append('.')
# TODO do I need to import ServerPoolProperties

class InvalidEnvironmentTypeError(ValueError):
    def __init__(self, environment):
        self.environment = environment
    def __str__(self):
        return "InvalidEnvironmentTypeError: Environment type " + self.environment + " is not valid!"

class InvalidDeploymentTopologyError(ValueError):
    def __init__(self, deploymentTopology):
        self.deploymentTopology = deploymentTopology
    def __str__(self):
        return "InvalidDeploymentTopologyError: Deployment topology " + self.deploymentTopology + " is not valid!"

class InvalidTshirtSizeError(ValueError):
    def __init__(self, tShirtSize):
        self.tShirtSize = tShirtSize
    def __str__(self):
        return "InvalidTshirtSizeError: tShirtSize " + self.tShirtSize + " is not valid!"

class InvalidChipsetError(ValueError):
    def __init__(self, chipset):
        self.chipset = chipset
    def __str__(self):
        return "InvalidChipsetError: chipset " + self.chipset + " is not valid!"

class InvalidLocationError(ValueError):
    def __init__(self, location):
        self.location = location
    def __str__(self):
        return "InvalidLocationError: location " + self.location + " is not valid!"

class ServerPoolsDisabledError(ValueError):
    def __str__(self):
        return "ServerPoolsDisabledError: unable to make server pool requests to target ops manager instance!"

class InsufficientServerPoolResourcesError(ValueError):
    def __init__(self, numServersRequested, serverPoolProperties):
        self.numServersRequested = numServersRequested
        self.serverPoolProperties = serverPoolProperties
    def __str__(self):
        return "InsufficientServerPoolResourcesError: Unable to find " + str(self.numServersRequested) + " servers within" + " server pool with requested properties: " + str(self.serverPoolProperties)

class NoHostsToDeployToError(ValueError):
    def __str__(self):
        return "NoHostsToDeployToError: Unable to locate any hosts to deploy mongod node(s) to!"

class NoHostsMatchingDeploymentTopologyError(ValueError):
    def __init__(self, deploymentTopology):
        self.deploymentTopology = deploymentTopology
    def __str__(self):
        return "NoHostsMatchingDeploymentTopology: Unable to find hosts matching the specified deployment topology " + self.deploymentTopology

class NoMongoDbVersionSpecifiedError(ValueError):
    def __str__(self):
        return "NoMongoDbVersionSpecified: No MongoDB version specified for deployment!"


class HostNotFoundError(ValueError):
    def __init__(self, hostNameOrId):
        self.hostNameOrId  = hostNameOrId
    def __str__(self):
        return "HostNotFoundError: Unable to find host " + self.hostNameOrId


class ClusterNotFoundError(ValueError):
    def __init__(self, groupId, clusterId):
        self.groupId    = groupId
        self.clusterId  = clusterId
    def __str__(self):
        return "ClusterNotFoundError: Unable to find cluster " + self.clusterId + " within group " + self.groupId

class GroupNotFoundError(ValueError):
    def __init__(self, groupId):
        self.groupId    = groupId
    def __str__(self):
        return "GroupNotFoundError: Unable to find group " + self.groupId

class NodeLaunchFailure(ValueError):
    def __init__(self, clusterName):
        self.clusterName = clusterName
    def __str__(self):
        return "NodeLaunchFailure: Unable to launch desired cluster with name " + self.clusterName

class InvalidRoleError(ValueError):
    def __init__(self, role):
        self.role = role
    def __str__(self):
        return "InvalidRoleError: Role {} not a valid role!".format(self.role)

class ErrorCodes():
    """

    """
    GROUP_ALREADY_EXISTS = "GROUP_ALREADY_EXISTS"

    VALUES = [GROUP_ALREADY_EXISTS]

    @staticmethod
    def isValid(errorCode):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid event type for which ops manager can produce an alert
        """
        return (errorCode.upper() in ErrorCodes.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        for value in ErrorCodes.VALUES:
            str += value + ","
        str += "]"
        return str
