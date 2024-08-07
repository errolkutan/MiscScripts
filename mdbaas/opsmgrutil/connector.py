import sys
sys.path.append('')
import requests
import logging
import json
import math
from requests.auth import HTTPDigestAuth
from mdbaas.opsmgrutil.constants import ServerPoolServerStatusName
from mdbaas.opsmgrutil.omusers import OpsManagerOrgRole, OpsManagerGroupRole

# Other constants
GROUPS_PER_PAGE = 100

# TODO -- ADD
MAX_GROUPS_PER_PAGE = 500

EXTERNAL_OPS_MANAGER_URL = "https://opsmanager.mongodb.com"

class OpsMgrConnector:
    """
    OpsMgrConnector class

    A wrapper class that sends requests to the specified ops manager
    """
    def __init__(self, opsMgrUri, apiUser, apiKey):
        """
        Constructor to create an OpsMgrConnector object.

        :param opsMgrUri:   The uri to the target ops manager
        :param apiUser:     The api user with which we will authenticate to the target ops manager
        :param apiKey:      The api key for the api user with which we will authenticate to the target ops manager
        """
        self.opsMgrUri = opsMgrUri
        self.staticDataUrl = "{}/static/".format(opsMgrUri)
        self.apiURL = "{}/api/public/v1.0".format(opsMgrUri)
        self.auth   = HTTPDigestAuth(apiUser, apiKey)

    def prettyPrint(self, payload):
        return json.dumps(payload, indent=4, sort_keys=True)

    ############################################################################
    # Base HTTP Request Methods
    ############################################################################

    def post(self, url, payload, verifyBool=True):
        """
        Post

        Sends an HTTP post request to the target url with the desired payload

        :param url:         A String representing the url to which the request shall go
        :param payload:     A JSON document containing the payload to be posted

        :return:            The response from the request
        """
        logging.debug("Sending a POST request to {} with payload:\n {}".format(url, self.prettyPrint(payload)))
        result = requests.post(url, json=payload, auth=self.auth, verify=verifyBool).json()
        if "error" in result:
            logging.debug("Encountered an error: {} ".format(self.prettyPrint(result)))  #TODO more sophisticated error handling
        else:
            logging.debug("Received response: {}".format(self.prettyPrint(result)))
        return result

    def put(self, url, payload, verifyBool=True):
        """
        Put

        Sends an HTTP put request to the target url with the desired payload

        :param url:         A String representing the url to which the request shall go
        :param payload:     A JSON document containing the payload to be put

        :return:            The response from the request
        """
        logging.debug("Sending a PUT request to {} with payload:\n {}".format(url, self.prettyPrint(payload)))
        result = requests.put(url, json=payload, auth=self.auth, verify=verifyBool)
        result = result.json()
        if "error" in result:
            logging.debug("Encountered an error {}: ".format(self.prettyPrint(result)))  #TODO more sophisticated error handling
        else:
            logging.debug("Received response: {}".format(self.prettyPrint(result)))
        return result

    def patch(self, url, payload, verifyBool=True):
        """
        Patch

        Sends an HTTP patch request to the target url with the desired payload

        :param url:         A String representing the url to which the request shall go
        :param payload:     A JSON document containing the payload to be patched

        :return:            The response from the request
        """
        logging.debug("Sending a PATCH request to {} with payload:\n {}".format(url, self.prettyPrint(payload)))
        result = requests.patch(url, json=payload, auth=self.auth, verify=verifyBool).json()
        if "error" in result:
            logging.debug("Encountered an error: {}".format(self.prettyPrint(result)))  #TODO more sophisticated error handling
        else:
            logging.debug("Received response: {}".format(json.dumps(result)))
        return result

    def get(self, url, verifyBool=True):
        """
        Get

        Sends an HTTP get request to the target url

        :param url:         A String representing the url to which the request shall go

        :return:            The response from the request
        """
        logging.debug("Sending a GET request to {}".format(url))
        result = requests.get(url, auth=self.auth, verify=verifyBool).json()
        if "error" in result:
            logging.debug("Encountered an error: {}".format(self.prettyPrint(result)))  #TODO more sophisticated error handling
        else:
            logging.debug("Received response: {}".format(self.prettyPrint(result)))
        return result

    def delete(self, url, verifyBool=True):
        """
        Delete

        Sends an HTTP delete request to the target url

        :param url:         A String representing the url to which the request shall go

        :return:            The response from the request
        """
        logging.debug("Sending a DELETE request to {}".format(url))
        result = requests.delete(url, auth=self.auth, verify=verifyBool)
        if result.status_code == 204:
            return result
        result = result.json()
        if "error" in result:
            logging.debug("Encountered an error: {} ".format(self.prettyPrint(result)))  #TODO more sophisticated error handling
        else:
            logging.debug("Received response: {} ".format(self.prettyPrint(result)))
        return result

    ###########################################################################
    # Misc Non API Methods
    ###########################################################################

    def getVersionManifestSuperset(self, majorVersion, verifyBool=True):
        """
        Get Version Manifest Superset

        Gets the version manifest that contains all minor versions up to the specified major version. Does
        so by sending a get request to the local ops manager endpoint /static/version_manifest/(version).json

        :param  majorVersion:   A String representing the major version--eg '4.0', '3.6', '3.4'

        :return:                A json document representing the version manifest
        """
        return self.get("{}/version_manifest/{}.json".format(self.staticDataUrl, majorVersion), verifyBool=verifyBool)

    def getExternalVersionManifestSuperset(self, majorVersion, verifyBool=True):
        """
        Get External Version Manifest Superset

        Gets the version manifest that contains all minor versions up to the specified major version. Does
        so by sending a get request to the external ops manager endpoint https://www.opsmanager.com/static/version_manifest/(version).json

        :param  majorVersion:   A String representing the major version--eg '4.0', '3.6', '3.4'

        :return:                A json document representing the version manifest
        """
        return self.get("{}/static/version_manifest/{}.json".format(EXTERNAL_OPS_MANAGER_URL, majorVersion), verifyBool=verifyBool)

    ############################################################################
    # Agent Methods
    ############################################################################

    def getAgentForGroup(self, groupId, agentType, verifyBool=True):
        """
        Get Agent For Group

        Gets the agent of a desired type from a specific group by checking the following API endpoint:

        GET /groups/{GROUP-ID}/agents/{TYPE}

        :param groupId:     The id of the group whose agents we are inquiring
        :param agentType:   The agent type we are inquiring
        :return:            The response from the request
        """
        return self.get("{}/groups/{}/agents/{}".format(self.apiURL, groupId, agentType), verifyBool=verifyBool)

    ############################################################################
    # Automation Config Methods
    ############################################################################

    def getAutomationConfig(self, groupId, verifyBool=True):
        """
        Get Automation Config

        Retrieves the automation configuration for a particular ops manager group
        via the folowing API endpoint:

        GET /groups/GROUP-ID/automationConfig

        :param groupId:    The id of the group whose automation configuration we are retrieving

        :return:           The response from the request
        """
        return self.get("{}/groups/{}/automationConfig".format(self.apiURL, groupId), verifyBool)

    def putAutomationConfig(self, groupId, newAutomationConfig, verifyBool=True):
        """
        Put Automation Configuration

        Pushes a new automation configuration for a particular ops manager group via the following API endpoint:

        PUT /groups/GROUP-ID/automationConfig

        :param  groupId:                The id of the group whose automation configuration we are updating
        :param  newAutomationConfig:    A document representing the new automation configuration

        :return:                        The response from the request
        """
        return self.put("{}/groups/{}/automationConfig".format(self.apiURL, groupId), newAutomationConfig, verifyBool)

    def getAutomationStatus(self, groupId, verifyBool=True):
        """
        Get Automation Status

        Retrieves the automation status for the specified group via the following API endpoint:

        GET /groups/GROUP-ID/automationStatus

        :param groupId:                 The id of the group whose automation status we are checking

        :return:                        The response from the request
        """
        return self.get("{}/groups/{}/automationStatus".format(self.apiURL, groupId), verifyBool)

    ############################################################################
    # Organization Methods
    ############################################################################

    def getOrganizations(self, verifyBool=True):
        """
        Get Organization

        Retrieves the organizations for the target ops manager instance via the
        following API endpoint:

        GET	/orgs

        :return:    The response from the request
        """
        return self.get("{}/orgs".format(self.apiURL), verifyBool=verifyBool)

    def getOrganizationById(self, orgId, verifyBool=True):
        """
        Get Organization By Id

        Retrieves an organization by its id via the following API endopoint:

        GET	/orgs/{ORG-ID}

        :param  orgId:      The organization Id whose data we are retrieving
        :return:            The response from the request
        """
        return self.get("{}/orgs/{}".format(self.apiURL, orgId), verifyBool=verifyBool)



    def getGroupsWithinOrganization(self, orgId, pageNum=None, itemsPerPage=None, verify=False):
        """
        Get Groups Within an Organization

        Retrieves all groups within a target organization via the following API
        endpoint:

        GET	/orgs/{ORG-ID}/groups

        :param  orgId:      The organization Id whose data we are retrieving

        :return:            The response from the request
        """
        queryStr = "{}/orgs/{}/groups".format(self.apiURL, orgId)
        if pageNum is not None:
            queryStr += "?pageNum={}".format(pageNum)
        if itemsPerPage is not None:
            if pageNum is not None:
                queryStr += "&itemsPerPage={}".format(itemsPerPage)
            else:
                queryStr += "?itemsPerPage={}".format(itemsPerPage)
        return self.get(queryStr, verifyBool=verify)

    def getAllGroupsWithinOrg(self, orgId, verify=False):
        """
        Get All Groups Within Org

        :param orgId:
        :param verify:
        :return:
        """
        data = self.getGroupsWithinOrganization(orgId, verify=verify)
        totalCount = data["totalCount"]
        numPages = int(math.ceil(float(totalCount) / float(GROUPS_PER_PAGE)))

        doc = {}
        doc["results"] = []
        for i in range(1, numPages + 1):
            groupDoc = self.getGroupsWithinOrganization(orgId, pageNum=i, itemsPerPage=GROUPS_PER_PAGE, verify=verify)
            doc["results"].extend(groupDoc["results"])

        return doc

    def getUsersWithinOrganization(self, orgId, verifyBool=True):
        """
        Get Users Within an Organization

        Retrieves all users within a target organization via the following API
        endpoint:

        GET	/orgs/{ORG-ID}/users

        :param  orgId:      The organization Id whose data we are retrieving

        :return:            The response from the request
        """
        return self.get("{}/orgs/{}/users".format(self.apiURL, orgId), verifyBool=verifyBool)

    def createOrganization(self, orgName, verifyBool=True):
        """
        Create Organization

        Creates an organization with the desired name via the following API endpoint:

        POST	/orgs

        :return:            The response from the request
        """
        payload = {
                    "name" : orgName
                  }
        return self.post("{}/orgs".format(self.apiURL), payload, verifyBool=verifyBool)

    def deleteOrganization(self, orgId, verifyBool=True):
        """
        Delete Organization

        Deletes an organization with the specified Id via the following API endpoint:

        DELETE	/orgs/{ORG-ID}

        :param orgId:   The id of the organization we wish to delete

        :return:        The response from the request
        """
        return self.delete("{}/orgs/{}".format(self.apiURL, orgId), verifyBool=verifyBool)

    ############################################################################
    # Hosts Methods
    ############################################################################

    def getHosts(self, groupId, verifyBool=True):
        """
        Get Hosts

        Gets all hosts within a particular group via the following API endpoint:

        GET	/groups/{GROUP-ID}/hosts

        :param groupId:     The id of the group whose hosts we wish to fetch

        :return:            The response from the request
        """
        return self.get("{}/groups/{}/hosts".format(self.apiURL, groupId), verifyBool=verifyBool)

    def getHostById(self, groupId, hostId, verifyBool=True):
        """
        Get Hosts by Id

        Gets an individual host within a particular group by its id via the following
        API endpoint:

        GET	/groups/{GROUP-ID}/hosts/{HOST-ID}

        :param  groupId:        The id of the group whose hosts we wish to fetch
        :param  hostId:         The id of the host we wish to fetch

        :return:                The response from the request
        """
        return self.get("{}/groups/{}/hosts/{}".format(self.apiURL, groupId, hostId), verifyBool=verifyBool)

    def getHostByHostnameAndPort(self, groupId, hostname, port, verifyBool=True):
        """
        Get Hosts by Hostname and Port

        Gets an individual host within a particular group by its hostname and port
        using the following API endpoint:

        GET	/groups/{GROUP-ID}/hosts/byName/{HOSTNAME:PORT}

        :param  groupId:        The id of the group whose hosts we wish to fetch
        :param  hostname:       The hostname of the server
        :param  port:           The port on which the mongod process is running

        :return:                The response from the request
        """
        return self.get("{}/groups/{}/hosts/byName/{}:{}".format(self.apiURL, groupId, hostname, port), verifyBool=verifyBool)

    def getlastSnapshot(self, groupId, clusterId, verifyBool=True):

        """
        Get last backup snapshot information

        Gets an individual host within a particular group by its hostname and port
        using the following API endpoint:

        GET	/groups/{GROUP-ID}/clusters/clusterId/snapshots

        :param  groupId:        The id of the group whose hosts we wish to fetch
        :param  clusterId       The cluster Id

            :return:                The response from the request
        """

        return self.get("{}/groups/{}/clusters/{}/snapshots".format(self.apiURL, groupId, clusterId), verifyBool=verifyBool)


    def startMonitoringHost(self, groupId, verifyBool=True):
        """
        Start Monitoring Host

        Deploys a monitoring agent to the specified host via the API endpoint:

        POST	/groups/{GROUP-ID}/hosts

        :param  groupId:    The id of the group for which we are setting up monitoring

        :return:            The response from the request
        """
        # TODO finish this
        return ""

    def updateMonitoringConfig(self, groupId, hostId, verifyBool=True):
        """
        Update Monitoring Configuration

        Update the monitoring configuration on a particular host via the following
        API endpoint:

        PATCH	/groups/{GROUP-ID}/hosts/{HOST-ID}

        :param  groupId:    The id of the group for which we are editing monitoring
        :param  hostId:     The id of the host for which we are editing monitoring

        :return:            The response from the request
        """
        #TODO finish this

    def stopMonitoringOnHost(self, groupId, hostId, verifyBool=True):
        """
        Stop Monitoring on Host

        Stops monitoring agent on the specified host for the specified group via the
        following API endpoint:

        DELETE	/groups/{GROUP-ID}/hosts/{HOST-ID}

        :param  groupId:    The id of the group for which we are stopping monitoring
        :param  hostId:     The id of the host for which we are stopping monitoring

        :return:            The response from the request
        """
        return self.delete("{}/groups/{}/hosts/{}".format(self.apiURL, groupId, hostId), verifyBool=verifyBool)

    def getLastPingForHost(self, groupId, hostId, verifyBool=True):
        """
        Get Last Ping For Host

        Gets the ping information on all agents for hosts within the designated group

        :param groupId:     The id of the group whose agents we will fetch ping data for
        :param hostId:      The id of the hosts whose agents we will fetch ping data for
        :return:            A document representing the ping data
        """
        return self.get("{}/groups/{}/hosts/{}/lastPing".format(self.apiURL, groupId, hostId), verifyBool=verifyBool)

    def getDiskPartitionMeasurementOverPeriodForHost(self, groupId, hostId, diskPartitionName, granularity, period, verifyBool=True):
        """
        Get Disk Partition Measurement Over Period For Host

        Gets the disk partition measurement information over a specified period per the following API endpoint:

        GET /groups/{GROUP-ID}/hosts/{HOST-ID}/disks/{PARTITION-NAME}/measurements

        :param groupId:
        :param hostId:
        :param diskPartitionName:
        :return:
        """
        # TODO fill this out--remember to include URI query params
        return self.get("{}/groups/{}/hosts/{}/disks/{}/measurements?granularity={}&period={}".format(self.apiURL, groupId,
                                                                                             hostId, diskPartitionName, granularity,
                                                                                             period), verifyBool=verifyBool)

    def getDiskPartitionMeasurementOverPeriodForHost(self, groupId, hostId, diskPartitionName, granularity, period,
                                                     measurementTypes=None, verifyBool=True):
        """
        Get Disk Partition Measurement Over Period For Host

        Gets the disk partition measurement information over a specified period per the following API endpoint:

        GET /groups/{GROUP-ID}/hosts/{HOST-ID}/disks/{PARTITION-NAME}/measurements

        :param groupId:
        :param hostId:
        :param diskPartitionName:
        :return:
        """
        if measurementTypes is None:
            return self.get(
                "{}/groups/{}/hosts/{}/disks/{}/measurements?granularity={}&period={}".format(self.apiURL, groupId,
                                                                                              hostId,
                                                                                              diskPartitionName,
                                                                                              granularity,
                                                                                              period), verifyBool=verifyBool)
        measurementTypeStr = ""
        for measurementType in measurementTypes:
            measurementTypeStr += "m={}&".format(measurementType)
        return self.get(
            "{}/groups/{}/hosts/{}/disks/{}/measurements?{}granularity={}&period={}".format(self.apiURL, groupId,
                                                                                            hostId, diskPartitionName,
                                                                                            measurementTypeStr,
                                                                                            granularity,
                                                                                            period), verifyBool=verifyBool)

    def getDiskPartitionName(self, groupId, hostId, verifyBool=True):
        """
        Get Disk Partition Measurement Over Period For Host

        Gets the disk partition measurement information over a specified period per the following API endpoint:

        GET /groups/{GROUP-ID}/hosts/{HOST-ID}/disks/{PARTITION-NAME}/measurements

        :param groupId:
        :param hostId:
        :param diskPartitionName:
        :return:
        """
        # TODO fill this out--remember to include URI query params
        return self.get("{}/groups/{}/hosts/{}/disks/".format(self.apiURL, groupId, hostId), verifyBool=verifyBool)


    def getDiskPartitionMeasurementOverIntervalForHost(self, groupId, hostId, diskPartitionName, granularity, intervalStart, intervalEnd, verifyBool=True):
        """
        Get Disk Partition Measurement For Host

        Gets the disk partition measurement information over a specified time interval per the following API endpoint:

        GET /groups/{GROUP-ID}/hosts/{HOST-ID}/disks/{PARTITION-NAME}/measurements

        :param groupId:
        :param hostId:
        :param diskPartitionName:
        :param granularity:
        :param intervalStart:
        :param intervalEnd:
        :return:
        """
        # TODO fill this out--remember to include URI query params
        return {}

    def getCputMeasurementOverPeriodForHost(self, groupId, hostId,granularity, period, verifyBool=True):
        """
        Get Disk Partition Measurement Over Period For Host

        Gets the disk partition measurement information over a specified period per the following API endpoint:

        GET /groups/{GROUP-ID}/hosts/{HOST-ID}/measurements

        :param groupId:
        :param hostId:
        :param diskPartitionName:
        :return:
        """
        # TODO fill this out--remember to include URI query params
        measurementTypes = [ "" ]
        return self.get("{}/groups/{}/hosts/{}/measurements?granularity={}&period={}".format(self.apiURL, groupId,
                                                                                                  hostId,granularity,
                                                                                                  period), verifyBool=verifyBool)

    def getMeasurementsOverPeriodForHost(self, groupId, hostId,granularity, period, measurementTypes, verifyBool=True):
        """
        Get Measurements over period for host

        :param groupId:             A string representing the group id whose host to retrieve measurements for
        :param hostId:              A string representing the host id whose measurements to retrieve
        :param granularity:
        :param period:
        :param measurementTypes:    An array of measurement types
        :return:
        """
        measurementTypeStr = ""
        for measurementType in measurementTypes:
            measurementTypeStr += "m={}&".format(measurementType)
        url = "{}/groups/{}/hosts/{}/measurements?{}granularity={}&period={}".format(self.apiURL, groupId,
                                                                                             hostId, measurementTypeStr,
                                                                                             granularity, period)
        return self.get(url, verifyBool=verifyBool)

    ############################################################################
    # Performance Advisor Methods
    ############################################################################

    def getSlowQueryLogsForGroupAndHost(self, groupId, hostId, since, duration, nLogs, namespaces, verifyBool=True):
        """
        Get Slow Query Logs for Group and Host

        :param groupId:             A string representing the group id whose host to retrieve measurements for
        :param hostId:              A string representing the host id whose measurements to retrieve
        :param since:
        :param duration:
        :param nLogs:
        :param namespaces:          An array of strings representing namespaces to capture
        :return:
        """
        queryParamStr = ""
        if nLogs is not None:
            queryParamStr += "&nLogs={}".format(nLogs)
        if since is not None:
            queryParamStr += "&since={}".format(since)
        if duration is not None:
            queryParamStr += "&duration={}".format(duration)
        if namespaces is not None:
            for namespace in namespaces:
                queryParamStr += "&namespace={}".format(namespace)
        if queryParamStr != "":
            queryParamStr = "?" + queryParamStr[1:]
        url = "{}/groups/{}/hosts/{}/performanceAdvisor/slowQueryLogs{}".format(self.apiURL, groupId, hostId, queryParamStr)
        return self.get(url, verifyBool=verifyBool)


    ############################################################################
    # Cluster Methods
    ############################################################################

    def getClustersForGroup(self, groupId, verifyBool=True):
        """
        Get Clusters for Group

        Gets all clusters within a particular group via the following API endpoint:

        GET /groups/{GROUP-ID}/clusters

        :param  groupId:    The id of the group whose clusters we want to fetch

        :return:            The response from the request
        """
        return self.get("{}/groups/{}/clusters".format(self.apiURL, groupId), verifyBool=verifyBool)

    def getClusterById(self, groupId, clusterId, verifyBool=True):
        """
        Get Cluster by ID

        Gets a specified cluster by its id via the following API endpoint:

        GET /groups/{GROUP-ID}/clusters/{CLUSTER-ID}

        :param  groupId:    The id of the group whose clusters we want to fetch
        :param  clusterId:  The id of the cluster we want to fetch

        :return:            The response from the request
        """
        return self.get("{}/groups/{}/clusters/{}".format(self.apiURL, groupId, clusterId), verifyBool=verifyBool)

    def changeClusterName(self, groupId, clusterId, clusterName, verifyBool=True):
        """
        Change Cluster Name

        Changes the cluster name via the following API endpoint:

        PATCH /groups/{GROUP-ID}/clusters/{CLUSTER-ID}

        :param  groupId:        The id of the group whose cluster we want to change
        :param  clusterId:      The id of the cluster we wish to change
        :param  clusterName:    The new name for the cluster

        :return:                The response from the request
        """
        payload = {
                    "clusterName" : clusterName
                  }
        return self.patch("{}/groups/{groupId}/clusters/{clusterId}".format(self.apiURL, groupId, clusterId), payload, verifyBool=verifyBool)

    ############################################################################
    # Groups Methods
    #############################Å###############################################

    def getAllGroups(self, verifyBool=True):
        """
        Get All Groups

        Gets all groups for the target ops manager instance via the following
        API endopoint:

        GET	/groups
        """
        data        = self.getGroups(verifyBool=verifyBool)
        totalCount  = data["totalCount"]
        numPages    = int(math.ceil(float(totalCount)/float(GROUPS_PER_PAGE)))

        doc             = {}
        doc["results"]  = []
        for i in range(1, numPages+1):
            groupDoc = self.getGroups(pageNum=i, verifyBool=verifyBool)
            doc["results"].extend(groupDoc["results"])
        return doc

    def getGroups(self, pageNum=None, itemsPerPage=None, verifyBool=True):
        """

        :param pageNum:
        :param itemsPerPage:
        :return:
        """
        queryStr    = "{}/groups".format(self.apiURL)
        if pageNum is not None:
            queryStr += "?pageNum={}".format(pageNum)
        if itemsPerPage is not None:
            if pageNum is not None:
                queryStr += "&itemsPerPage={}".format(itemsPerPage)
            else:
                queryStr += "?itemsPerPage={}".format(itemsPerPage)
        return self.get(queryStr, verifyBool=verifyBool)

    def getGroupById(self, groupId, verifyBool=True):
        """
        Get Groups By ID

        Gets an ops manager group by its group id via the following API endpoints:

        GET	/groups/byName/{GROUP-NAME}

        :param  groupId:    The id of the group that we wish to fetch

        :return:            The response from the request
        """
        return self.get("{}/groups/{}".format(self.apiURL, groupId), verifyBool=verifyBool)

    def getGroupByName(self, groupName, verifyBool=True):
        """
        Get Group By Name

        Gets an ops manager group by its name via the following API endpoint:

        GET	/groups/byName/{GROUP-NAME}

        :param  groupName:  The name of the group which we want to fetch

        :return:            The response from the request
        """
        return self.get("{}/groups/byName/{}".format(self.apiURL, groupName), verifyBool=verifyBool)

    def getGroupByAgentApiKey(self, agentApiKey, verifyBool=True):
        """
        Get Group by Agent Api Key

        Gets an ops manager group by its automation agent api key via the following
        API endpoint:

        GET	/groups/byAgentApiKey/{AGENT-API-KEY}

        :param  agentApiKey:    The automation agent api key of the agent maintaining the group

        :return:                The response from the request
        """
        return self.get("{}/groups/byAgentApiKey/{}".format(self.apiURL, agentApiKey), verifyBool=verifyBool)

    def getUsersInGroup(self, groupId, verifyBool=True):
        """
        Get Users in Group

        Gets all users in a target ops manager group via the following API endpoint:

        GET	/groups/{GROUP-ID}/users

        :param  groupId:        The id of the group whose users we want to fetch

        :return:                The response from the request
        """
        return self.get("{}/groups/{}/users".format(self.apiURL, groupId), verifyBool=verifyBool)

    def getTeamsInGroup(self, groupId, verifyBool=True):
        """
        Get Teanms in Group

        Gets all teams in a target ops manager group via the following API endpoint:

        GET	/groups/{GROUP-ID}/teams

        :param  groupId:        The id of the group whose teams we want to fetch

        :return:                The response from the request
        """
        return self.get("{}/groups/{}/teams".format(self.apiURL, groupId), verifyBool=verifyBool)


    def addGroup(self, newGroupName, organizationId, verifyBool=True):
        """
        Add Group

        Add a new group with the specified name under the specified organization
        via the following API endpoint:

        POST	/groups

        :param  newGroupName:       The name of the new ops manager group
        :param  organizationId:     The id of the organization under which the new group will be added

        :return:                    The response from the request
        """
        payload = {
                    "name"  : newGroupName,
                    "orgId" : organizationId
                  }
        return self.post("{}/groups".format(self.apiURL), payload, verifyBool=verifyBool)

    def addUsersToGroup(self, groupId, userId, rolesArr, groupRoleId, roleName, verifyBool=True):
        """
        Add Users to Group

        Adds users who exist in ops manager to another group via the following API
        endpoint:

        POST /groups/{GROUP-ID}/users

        :param  groupId:    The id of the group to which the new user will be moved
        :param  userId:     The id of the user which will be moved
        :param  rolesArr:   The new roles to which the user will be assigned
        :param  groupRoleId:The identifier for the group role
        :param  roleName:   The display name for the user role

        :return:            The response from the request
        """
        # TODO need to play around with this; still not clear exactly how it works
        payload = {
                    "id"            : userId,
                    "roles"         : rolesArr,
                   }
        return self.post("{}/groups/{}/users".format(self.apiURL, groupId), payload, verifyBool=verifyBool)

    def addTeamsToGroup(self, groupId, verifyBool=True):
        """
        Add Teams To Group

        :param  groupId

        :return:            The response from the request
        """
        # TODO populate this
        return ""

    def changeGroupName(self, groupId, newName, verifyBool=True):
        """
        Change Group Name

        Changes the group name to a desired name via the following API endpoint:

        PATCH /groups/{GROUP-ID}

        :param  groupId:    The id of the group whose name we wish to change
        :param  newName:    A string to which we want to change the group's

        :return:            The response from the request
        """
        payload = {
                    "id"    : groupId,
                    "name"  : newName
                  }
        return self.patch("{}/groups/{}".format(self.apiURL, groupId), payload, verifyBool=verifyBool)

    def removeUserFromGroup(self, groupId, userId, verifyBool=True):
        """
        Remove User From Group

        Removes a user from a specified group via the following API endpoint:

        DELETE /groups/{GROUP-ID}/users/{USER-ID}

        :param  groupId:        The group from which we want to remove the user
        :param  userId:         The user we wish to remove

        :return:                The response from the request
        """
        return self.delete("{}/groups/{}/users/{}".format(self.apiURL, groupId, userId), verifyBool=verifyBool)

    def removeGroup(self, groupId, verifyBool=True):
        """
        Remove Group

        Deletes the specified Ops Manager group via the API endpoint:

        DELETE	/groups/{GROUP-ID}

        :param  groupId:        The id of the group that we wish to delete

        :return:                The response from the request
        """
        return self.delete("{}/groups/{}".format(self.apiURL, groupId), verifyBool=verifyBool)

    ############################################################################
    # API Keys
    ############################################################################

    def createProgrammaticAPIKeyForOrg(self, organizationId, description, roles, verifyBool=True):
        """
        Create Programmatic API Key via the API endpoint:

        POST /orgs/{ORG-ID}/apiKeys

        :param organizationId:      The id of the organization to add a programmatic API key to
        :param description:         A string description of the API key
        :param roles:               An array of roles for the API key

        :return:
        """
        for role in roles:
            if not OpsManagerOrgRole.isValid(role):
                raise Exception("Org role {} is not valid! ".format(role))
        payload = {
            "desc" : description,
            "roles" : roles
        }
        return self.post("{}/orgs/{}/apiKeys".format(self.apiURL, organizationId), payload, verifyBool=verifyBool)


    def deleteOrganizationAPIKey(self, organizationId, apiKeyId, verifyBool=True):
        """
        Delete Organization API Key

        Deletes an organization API key via the endpoint

        DELETE /orgs/{ORG-ID}/apiKeys/{API-KEY-ID}


        :param organizationId:
        :param apiKeyId:
        :return:
        """
        return self.delete("{}/orgs/{}/apiKeys/{}".format(self.apiURL, organizationId, apiKeyId), verifyBool=verifyBool)


    def createAccessListEntriesForAnOrganizationAPIKey(self, organizationId, apiKeyId, accessList, verifyBool=True):
        """
        Create Access List Entries for an Organization API Key

        Adds access list entries to an API key via the endpoint:

        POST /orgs/{ORG-ID}/apiKeys/{API-KEY-ID}/accessList

        :param organizationId:
        :param apiKeyId:
        :param accessList:
        :return:
        """
        return self.post("{}/orgs/{}/apiKeys/{}/accessList".format(self.apiURL, organizationId, apiKeyId), accessList, verifyBool=verifyBool)


    def createAndAssignAnOrgAPIKeyToProject(self, projectId, description, roles, verifyBool=True):
        """
        Create and Assign one Organization API Key to a Project via the endpoint

        POST /groups/{PROJECT-ID}/apiKeys

        :param projectId:
        :param description:
        :param roles:
        :return:
        """
        for role in roles:
            if not OpsManagerGroupRole.isValid(role):
                raise Exception("Group role {} is not valid! ".format(role))
        payload = {
            "desc": description,
            "roles": roles
        }
        return self.post("{}/groups/{}/apiKeys".format(self.apiURL, projectId), payload, verifyBool=verifyBool)

    ############################################################################
    # Server Pools Methods
    ############################################################################

    def getServerPoolsEnabled(self, verifyBool=True):
        """
        Get Server Pools Enabled

        Determines whether the server pool is enabled on the target ops manager
        instance via the following API endpoint:

        GET /serverPool

        :return:    The response from the request
        """
        return self.get("{}/serverPool".format(self.apiURL), verifyBool=True)

    def getServerPoolServers(self, status=None, verifyBool=True):
        """
        Get Server Pool Servers

        Gets the server pool servers on the target ops manager instance via the
        following API endpoint:

        GET /serverPool/servers

        Here you have the ability to filter the result by server pool status

        status:     The server pool status you wish to filter the results by
        """
        if ServerPoolServerStatusName.AVAILABLE == status or ServerPoolServerStatusName.TRASH == status:
            return self.get("{}/serverPool/servers?status={}".format(self.apiURL, status))
        elif status is not None:
            logging.error("Encountered an error")
        return self.get("{}/serverPool/servers".format(self.apiURL))

    def getServerPoolServerById(self, poolServerId, verifyBool=True):
        """
        Get Server Pool Server By Id

        Gets information on a particular server from the server pool by its id via
        the following API endpoint:

        GET /serverPool/servers/SERVER-ID

        :param  poolServerId:   The id of the server pool server we wish to fetch

        :return:                The response from the request
        """
        return self.get("{}/serverPool/servers/{}".format(self.apiURL, poolServerId), verifyBool=verifyBool)

    def getServerPoolServersByHostname(self, hostname, groupId, verifyBool=True):
        """
        Get Server Pool Servers By Hostname

        Gets infomation on a particular server from the server pool by its hostname
        via the following API endpoint:

        GET /serverPool/servers/byName/HOSTNAME

        :param  hostname:       The name of the host on which the server pool server resides

        :return:                The response from the request
        """
        return self.get("{}/serverPool/servers/byName/{}".format(self.apiURL, hostname), verifyBool=verifyBool)

    def removeServerFromPool(self, poolServerId, verifyBool=True):
        """
        Remove Server from Server Pool

        Removes a server from the server pool via its id via the following API endpoint:

        DELETE /serverPool/servers/SERVER-ID

        :param  poolServerId:   The id of the server pool server we wish to remove

        :return:                The response from the request
        """
        return self.delete("{}/serverPool/servers/{}".format(self.apiURL, poolServerId), verifyBool=verifyBool)

    def getServerPoolRequests(self, requestStatus=None, requestId=None, verifyBool=True):
        """
        Get Server Pool Requests

        Gets outstanding server pool requests and offers the ability to filter by
        id or status. Does so via the following API endpoint:

        GET /serverPool/requests

        :param  requestStatus:      The status to filter requests on. Can be one of
                                        EXECUTING
                                        CANCELLING
                                        CANCELLED
                                        FAILED
                                        COMPLETED
        :param  requestId:          The id of the request we wish to acquire

        :return:                    The response from the request
        """
        if requestId is not None:
            return self.get("{}/serverPool/requests/{}".format(self.apiURL, requestId), verifyBool=verifyBool)
        if requestStatus is not None:
            return self.get("{}/serverPool/requests?status={}".format(self.apiURL, requestStatus), verifyBool=verifyBool)
        return self.get("{}/serverPool/requests".format(self.apiURL), verifyBool=verifyBool)

    def cancelServerPoolRequest(self, requestId, verifyBool=True):
        """
        Cancel Server Pool Request

        Cancels the server pool request represented by the requestId specified via
        the following API endpoint:

        DELETE /serverPool/requests/REQUEST-ID

        :param  requestId:      The id of the request to cancel

        :return:                The response from the request
        """
        return self.delete("{}/serverPool/requests/{}".format(self.apiURL, requestId), verifyBool=verifyBool)

    def getServerPoolProperties(self, verifyBool=True):
        """
        Get Server Pool Properties

        Gets the server pool properties available within the server pool via the
        following API endpoint:

        GET /serverPool/properties

        :return:                The response from the request
        """
        return self.get("{}/serverPool/properties".format(self.apiURL), verifyBool=verifyBool)

    # TODO fix this
    def updatePropertySettings(self, propertyId, newPropertyDescription, multiSelect=False, newStatusName=None, verifyBool=True):
        """
        Update Property Settings

        Updates a server pool property via the following API endpoint:

        PATCH /serverPool/properties/PROPERTY-ID

        :param  newPropertyDescription:     A String representing the new name of the property
        :param  multiSelect:                True or False, indicating whether or not this
                                            property can be selected more than once for
                                            different servers
        :param  newStatusName:              A String representing the new status of the server

        :return:                            The response from the request
        """
        payload = {
                    "description"   : newPropertyDescription,
                    "multiSelect"   : multiSelect,
                    "statusName"    : newStatusName
                }
        return self.patch("{}/serverPool/properties/{}".format(self.apiURL, propertyId), payload, verifyBool=verifyBool)

    # TODO fix this
    def updatePropertyValue(self, propertyId, newValue, verifyBool=True):
        """
        Update Property Value

        Updates the value of the property indicated by its Id via the following API endpoint

        PATCH /serverPool/properties/PROPERTY-ID/values/PROPERTY-VALUE

        :param  propertyId:     The id of the property we wish to change
        :parm   newValue:       The value to which you want to change the property

        :return:                The response from the request
        """
        return self.patch("{}/serverPool/properties/{}/values/{}".format(self.apiURL, propertyId, newValue), {}, verifyBool=verifyBool)

    def deleteProperty(self, propertyId, verifyBool=True):
        """
        Delete Property

        Delete a property via its Id using the following API endpoint:

        DELETE /serverPool/properties/PROPERTY-ID

        :param  propertyId:     The id of the property we wish to change

        :return:                The response from the request
        """
        return self.delete("{}/serverPool/properties/{}".format(self.apiURL, propertyId), verifyBool=verifyBool)

    def deletePropertyValue(self, propertyId, propertyValue, verifyBool=True):
        """
        Delete Property Value

        Delete a property value via the property id and the value you wish to delete. Does
        this via the following API endpoint:

        DELETE /serverPool/properties/PROPERTY-ID/values/PROPERTY-VALUE

        :param  propertyId:     The id of the property whose value we wish to change
        :param  propertyValue:  The value of the property that we wish to delete

        :return:                The response from the request
        """
        return self.delete("{}/serverPool/properties/{}/values/{}".format(self.apiURL, propertyId, propertyValue), verifyBool=verifyBool)

    def getServerPoolServersForGroup(self, groupId, verifyBool=True):
        """
        Get Server Pool Servers For Group

        Gets sever pool servers bound to a particular group via the following API endpoint:

        GET /groups/{GROUP-ID}/serverPool

        :param  groupId:        The id of the group whose servers we wish to change

        :return:                The response from the request
        """
        return self.get("{}/groups/{}/serverPool/servers".format(self.apiURL, groupId), verifyBool=verifyBool)

    def sendServerPoolRequestForGroup(self, groupId, numServersRequested, serverPoolProperties, verifyBool=True):
        """
        Send Server Pool Request For Group

        Sends as server pool request for a particular number of servers with the desired properties.
        Does so via the following API endpoint:

        POST /groups/GROUP-ID/serverPool/requests

        Note that this only provisions servers that all have the exact same properties.

        :param  groupId:                    The id of the group to which we will assign the servers
        :param  numServersRequested:        An integer representing the number of servers requested
        :param  serverPoolProperties:       A ServerPoolProperties object containing the desired properties

        :return:                            The response from the request
        """
        arr = []
        i = 0
        while i < numServersRequested:
            arr.append(serverPoolProperties.getDocument())
            i += 1
        payload = { "properties" : arr }
        return self.post("{}/groups/{}/serverPool/requests".format(self.apiURL, groupId), payload, verifyBool=verifyBool)

    ############################################################################
    # Alerts Methods
    ############################################################################

    def sendAlertConfigurationForGroup(self, groupId, alertConfigurationDocument, verifyBool=True):
        """
        Send Alert Configuration For Group

        Sets up an alert for a group via the following API endpoint:

        POST /groups/{GROUP-ID}/alertConfigs

        :param  groupId:                        The id of the group for which we want to create a group
        :param  alertConfigurationDocument:     A JSON document with the alert configurations you want to create

        :return:                                The response from the request
        """
        # payload = json.dumps(alertConfigurationDocument)
        return self.post("{}/groups/{}/alertConfigs".format(self.apiURL, groupId), alertConfigurationDocument, verifyBool=verifyBool)

    ############################################################################
    # Backup Admin Methods
    ############################################################################

    def getProjectBackupJobConfigs(self, groupId=None, verifyBool=True):
        """
        Get All Project Backup Job Configs

        :return:
        """
        if groupId is None:
            return self.get("{}/admin/backup/groups".format(self.apiURL))
        return self.get("{}/admin/backup/groups/{}".format(self.apiURL, groupId), verifyBool=verifyBool)

    def getBlockstoreConfigs(self, blockStoreId=None, verifyBool=True):
        """
        Get BlockStore Configs for a Blockstore

        :param blockStoreId:
        :return:
        """
        if blockStoreId is None:
            return self.get("{}/admin/backup/snapshot/mongoConfigs".format(self.apiURL), verifyBool=verifyBool)
        return self.get("{}/admin/backup/snapshot/mongoConfigs/{}".format(self.apiURL, blockStoreId), verifyBool=verifyBool)

    def getOplogstoreConfig(self, oplogStoreId=None, verifyBool=True):
        """
        Get Oplog Store

        :param oplogStoreId:
        :return:
        """
        if oplogStoreId is None:
            return self.get("{}/admin/backup/oplog/mongoConfigs".format(self.apiURL), verifyBool=verifyBool)
        return self.get("{}/admin/backup/oplog/mongoConfigs/{}".format(self.apiURL, oplogStoreId), verifyBool=verifyBool)

    ############################################################################
    # Backup Config Methods
    ############################################################################

    def getBackupConfigsForGroup(self, groupId, verifyBool=True):
        """
        Get Backup Configs For Group

        Gets the backup configurations for a particular group via the following API
        endpoint:

        GET	/groups/{GROUP-ID}/backupConfigs

        :param  groupId:        The id of the group whose backup configurations we are fetching

        :return:                The response from the request
        """
        return self.get("{}/groups/{}/backupConfigs".format(self.apiURL, groupId), verifyBool=verifyBool)

    # TODO change the naming from Deployment to Cluster
    def getBackupConfigsForDeployment(self, groupId, clusterId, verifyBool=True):
        """
        Get Backup Configs for Cluster

        Gets the backup configurations for a particular cluster and group via the
        following API endpoint:

        GET	/groups/{GROUP-ID}/backupConfigs/{CLUSTER-ID}

        :param  groupId:        The id of the group whose backup configurations we are fetching
        :param  clusterId:      The id of the cluster whose backup configs we are fetching

        :return:                The response from the request
        """
        return self.get("{}/groups/{}/backupConfigs/{}".format(self.apiURL, groupId, clusterId), verifyBool=verifyBool)

    def updateBackupConfigurationForDeployment(self, groupId, clusterId, statusName, syncSource, verifyBool=True):
        """
        Update Backup Configs for Cluster

        Updates the backup configurations for a particular cluster and group via the
        following API endpoint:

        PATCH	/groups/{GROUP-ID}/backupConfigs/{CLUSTER-ID}

        :param  groupId:        The id of the group whose backup configurations we are fetching
        :param  clusterId:      The id of the cluster whose backup configs we are fetching

        :return:                The response from the request
        """
        payload = { "authMechanismName" : "NONE",
                    "storageEngineName" : "WIRED_TIGER",
                    "clusterId"         : clusterId,
                    "encryptionEnabled" : False,
                    "excludedNamespaces": [],
                    "groupId"           : groupId,
                    "sslEnabled"        : False,
                    "syncSource"        : syncSource,
                    "statusName"        : statusName
                  }
        return self.patch("{}/groups/{}/backupConfigs/{}".format(self.apiURL, groupId, clusterId), payload, verifyBool=verifyBool)

    ############################################################################
    # Snapshot Schedule Methods
    ############################################################################

    def getSnapshotScheduleForCluster(self, groupId, clusterId, verifyBool=True):
        """
        Get Snapshot Schedule For Cluster

        Gets the snapshot schedule for a particular group and cluster via the following
        API endpoint:

        GET	/groups/{GROUP-ID}/backupConfigs/{CLUSTER-ID}/snapshotSchedule

        :param  groupId:    The id of the group whose snapshot schedule we are retrieving
        :param  clusterId:  The id of the cluster whose snapshot schedule we are retrieving

        :return:            The response from the request
        """
        return self.get("{}/groups/{}/backupConfigs/{}/snapshotSchedule".format(self.apiURL, groupId, clusterId), verifyBool=verifyBool)

    def setupSnapshotScheduleForCluster(self, groupId, clusterId, snapshotSchedule, verifyBool=True):
        """
        Set Snapshot Schedule For Cluster

        Sets the snapshot schedule for a particular group and cluster via the
        following API endpoint:

        PATCH	/groups/{GROUP-ID}/backupConfigs/{CLUSTER-ID}/snapshotSchedule

        :param  groupId:    The id of the group whose snapshot schedule we are retrieving
        :param  clusterId:  The id of the cluster whose snapshot schedule we are retrieving

        :return:            The response from the request
        """
        return self.patch("{}/groups/{}/backupConfigs/{}/snapshotSchedule".format(self.apiURL, groupId, clusterId),
                          snapshotSchedule, verifyBool=verifyBool)

    def updateSnapshotScheduleForCluster(self, groupId, clusterId, verifyBool=True):
        """
        Update Snapshot Schedule for Cluster

        Updates the snapshot schedule for a particular group and cluster via the
        following API endpoint:

        PATCH	/groups/{GROUP-ID}/backupConfigs/{CLUSTER-ID}/snapshotSchedule

        :param  groupId:    The id of the group whose snapshot schedule we are retrieving
        :param  clusterId:  The id of the cluster whose snapshot schedule we are retrieving

        :return:            The response from the request
        """
        # TODO edit the payload
        payload = {
                    "groupId"                       : "",
                    "clusterId"                     : "",
                    "snapshotIntervalHours"         : "",
                    "snapshotRetentionDays"         : "",
                    "clusterCheckpointIntervalMin"  : "",
                    "dailySnapshotRetentionDays"    : "",
                    "weeklySnapshotRetentionWeeks"  : "",
                    "monthlySnapshotRetentionMonths": "",
                    "pointInTimeWindowHours"        : "",
                    "referenceHourOfDay"            : "",
                    "referenceMinuteOfHour"         : "",
                    "referenceTimeZoneOffset"       : ""
                }
        return self.patch("{}/groups/{}/backupConfigs/{}/snapshotSchedule".format(self.apiURL, groupId, clusterId), payload, verifyBool=verifyBool)

    ############################################################################
    # Snapshot Methods
    ############################################################################

    def getSnapshotForCluster(self, groupId, clusterId, verifyBool=True):
        """
        Get Snapshot For Cluster

        Gets the Snapshot for a particular cluster and group via the following API
        endpoint

        GET /groups/{groupId}/clusters/{clusterId}/snapshots

        :param  groupId:    The id of the group whose snapshots we will be retrieving
        :param  clusterId:  The id of the cluster whose snapshots we will be retrieving

        :return:            The response from the request
        """
        return self.get("{}/groups/{}/clusters/{}/snapshots".format(self.apiURL, groupId, clusterId), verifyBool=verifyBool)

    def getSnapshotById(self, groupId, clusterId, snapshotId, verifyBool=True):
        """
        Get Snapshot By Id

        Gets the Snapshot by id for a particular cluster and group via the following
        API endpoint:

        GET /groups/{groupId}/clusters/{clusterId}/snapshots/{snapshotId}

        :param  groupId:    The id of the group whose snapshots we will be retrieving
        :param  clusterId:  The id of the cluster whose snapshots we will be retrieving
        :param  snapshotId: The id of the snapshot we are retrieving

        :return:            The response from the request
        """
        return self.get("{}/groups/{}/clusters/{}/snapshot/{}".format(self.apiURL, groupId, clusterId, snapshotId), verifyBool=verifyBool)

    def changeExpirationDateForSnapshot(self, groupId, clusterId, snapshotId, newExpirationDate, verifyBool=True):
        """
        Change Expiration Date for Snapshot

        Updates the snapshot expiration date for a particular snapshot in a particular
        group and cluster via the following API endpoint:

        PATCH return self.get("{}/groups/{}/clusters/{}/snapshot".format(self.apiURL, groupId, clusterId))

        :param  groupId:            The id of the group whose snapshots we will be changing
        :param  clusterId:          The id of the cluster whose snapshots we will be changing
        :param  snapshotId:         The id of the snapshot we are changing
        :param  newExpirationDate:  The new expiration date of the snapshot

        :return:                    The response from the request
        """
        payload = { "doNotDelete" : False,
                    "expires" : newExpirationDate
                  }
        return self.patch("{}/groups/{}/clusters/{}/snapshot/{}".format(self.apiURL, groupId, clusterId, snapshotId),
                          payload, verifyBool=verifyBool)

    def getSnapshotsForConfigServer(self, groupId, hostId, verifyBool=True):
        """
        Get Snapshots for Config Server

        Gets all snapshots for a particular host given the following API endpoint:

        GET	/groups/{groupId}/hosts/{hostId}/snapshots

        :param  groupId:        The id of the group whose snapshots we will be retrieving
        :param  hostId:         The id of the host whose snapshots we will be retrieving

        :return:                The response from the request
        """
        return self.get("{}/groups/{}/hosts/{}/snapshots".format(self.apiURL, groupId, hostId), verifyBool=verifyBool)

    def getSnapshotByIdForConfigServer(self, groupId, hostId, snapshotId, verifyBool=True):
        """
        Get Snapshots by ID for Config Server

        Gets a particular snapshots for a particular host given the following API endpoint:

        GET	/groups/{groupId}/hosts/{hostId}/snapshots/{snapshotId}

        :param  groupId:        The id of the group whose snapshots we will be retrieving
        :param  hostId:         The id of the host whose snapshots we will be retrieving
        :param  snapshotId:     The id of the individual snapshot we will be retrieving

        :return:                The response from the request
        """
        return self.get("{}/groups/{}/hosts/{}/snapshots/{}".format(self.apiURL, groupId, hostId,snapshotId), verifyBool=verifyBool)

    # TODO ##########################################################
    # TODO ADD EVERYTHING  below this line
    # TODO ##########################################################

    def getDatabasesForHost(self, groupId, hostId, pageNum, verifyBool=True):
        """
        Get Databases For Host

        :param groupId:
        :param hostId:
        :return:
        """
        return self.get("{}/groups/{}/hosts/{}/databases?page={}".format(self.apiURL, groupId, hostId, pageNum), verifyBool=verifyBool)

    # def getCollectionsInDB(self, groupId, clusterId, pageNum):

