


class DeploymentTopologyName():
    """
    DeploymentTopologyName class

    Effectively a static class used in lieu of an enum (only supported by python
     3.4+), representing possible deployment topologies that customer APDS supports
    """
    THREE_NODE  = "THREE-NODE"
    FIVE_NODE   = "FIVE-NODE"
    SINGLE_NODE = "SINGLE-NODE"
    STANDALONE  = "STANDALONE"
    VALUES = [THREE_NODE, FIVE_NODE, SINGLE_NODE, STANDALONE]

    @staticmethod
    def isValid(deploymentTopologyStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid deployment topology
        """
        return (deploymentTopologyStr.upper() in DeploymentTopologyName.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        ctr = 0
        for value in DeploymentTopologyName.VALUES:
            ctr += 1
            if ctr != len(DeploymentTopologyName.VALUES):
                str += value + ","
        str += "]"
        return str




class DeploymentTopologyNode():
    def __init__(self, dataCenter, priority, votes, slaveDelay, hidden, arbiterOnly=False):
        self.priority   = priority
        self.votes      = votes
        self.slaveDelay = slaveDelay
        self.hidden     = hidden
        self.arbiterOnly= arbiterOnly

class DeploymentTopology():
    def __init__(self, name):
        self.name = name
        self.nodes = []

    def getReplicaSetDocument(self, targetHosts, replicaSetName):
        replicaSetDocument = {}
        replicaSetDocument["_id"] = replicaSetName
        replicaSetDocument["members"] = []
        replicaSetMemberNum = 0
        for targetHost in targetHosts:
            replicaSetMemberDoc = getReplicaSetMemberDocument(replicaSetName, replicaSetMemberNum)
            replicaSetDocument["members"].append(replicaSetMemberDoc)
            replicaSetMemberNum += 1
        replicaSetDocument["settings"] = {}
        return replicaSetDocument

    def getReplicaDocumentArr(self):
        return []

class SingleNodeTopology(DeploymentTopology):
    def __init__(self):
        DeploymentTopology.__init__("SINGLE-NODE")
        priority    = 1
        votes       = 1
        slaveDelay  = 0
        hidden      = False
        arbiterOnly = False
        self.nodes = [ DeploymentTopologyNode("", priority, votes, slaveDelay, hidden, arbiterOnly)]

class ThreeNodeTopology(DeploymentTopology):
    def __init__(self):
        DeploymentTopology.__init__("THREE-NODE")
        priority    = 1
        votes       = 1
        slaveDelay  = 0
        hidden      = False
        arbiterOnly = False
        node1       = DeploymentTopologyNode("", priority, votes, slaveDelay, hidden, arbiterOnly)
        node2       = DeploymentTopologyNode("", priority, votes, slaveDelay, hidden, arbiterOnly)
        node3       = DeploymentTopologyNode("", priority, votes, slaveDelay, hidden, arbiterOnly)
        self.nodes = [ node1, node2, node3 ]

class FiveNodeTopology(DeploymentTopology):
    def __init__(self):
        DeploymentTopology.__init__("FIVE-NODE")
        priority    = 1
        votes       = 1
        slaveDelay  = 0
        hidden      = False
        arbiterOnly = False
        node1       = DeploymentTopologyNode("", priority, votes, slaveDelay, hidden, arbiterOnly)
        node2       = DeploymentTopologyNode("", priority, votes, slaveDelay, hidden, arbiterOnly)
        node3       = DeploymentTopologyNode("", priority, votes, slaveDelay, hidden, arbiterOnly)
        node4       = DeploymentTopologyNode("", priority, votes, slaveDelay, hidden, arbiterOnly)
        node5       = DeploymentTopologyNode("", priority, votes, slaveDelay, hidden, arbiterOnly)
        self.nodes = [ node1, node2, node3, node4, node5 ]

class DeploymentTopologyFactor():

    def getDeployment(self, deploymentTopologyName):
        """
        Get Deployment

        Factory method that gets the appropriate DeploymentTopology based on the type requested

        :param  deploymentTopologyName:     A DeploymentTopologyName string
        :return:                            A DeploymentTopology object
        """
        if DeploymentTopologyName.FIVE_NODE == deploymentTopologyName:
            return FiveNodeTopology()
        elif DeploymentTopologyName.THREE_NODE == deploymentTopologyName:
            return ThreeNodeTopology()
        elif DeploymentTopologyName.SINGLE_NODE == deploymentTopologyName:
            return SingleNodeTopology()
        elif DeploymentTopologyName.STANDALONE == deploymentTopologyName:
            return ""

class AuthCreds():

    def __init__(self, userName, userPass):
        """

        :param userName:
        :param userPss:
        """
        self.userName = userName
        self.userPass = userPass
