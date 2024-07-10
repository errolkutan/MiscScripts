#!/usr/bin/python
import operator
import platform
import sys

import requests

sys.path.append('.')
import os
import logging
import subprocess
import argparse
import json
from prettytable import PrettyTable

from mdbaas.opsmgrutil import OpsMgrConnector

# Script metadata
version         = "1.0.0"
revdate         = "07-10-2024"
scriptName      = "perf_advisor_check"
scriptNameFull  = scriptName + ".py"
completionStr   = "\n====================================================================\n                      Completed " + scriptName + "!!!!              \n ====================================================================\n"


BYTES_IN_GB = 1024*1024*1024
VALID_SCALES = {
    "b" : "bytes",
    "bytes" : "bytes",
    "k" : "kilobytes",
    "kb" : "kilobytes",
    "kilobytes" : "kilobytes",
    "m" : "megabytes",
    "mb" : "megabytes",
    "megabytes" : "megabytes",
    "g" : "gigabytes",
    "gb" : "gigabytes",
    "gigabytes" : "gigabytes"
}

VALID_SCALE_NAMES = {
    "b" : "B",
    "bytes" : "B",
    "k" : "KB",
    "kb" : "KB",
    "kilobytes" : "KB",
    "m" : "MB",
    "mb" : "MB",
    "megabytes" : "MB",
    "g" : "GB",
    "gb" : "GB",
    "gigabytes" : "GB"
}

SCALE_MAP = {
    "bytes" : 1,
    "kilobytes" : 1024,
    "megabytes" : 1024*1024,
    "gigabytes" : 1024*1024*1024,
}

# TODO -- remove
SECONDS_IN_HOUR = 60*60
APPLICATION_ENVS = [ "PROD", "UAT", "DEV"]

verifyCerts = True

########################################################################################################################
# Base Methods
########################################################################################################################

def collect_perf_advisor_data_for_project(groupId):
    """

    :param project:
    :return:
    """
    processes_in_project = get_processes_for_group(groupId)
    for process in processes_in_project:
        slow_queries = collect_slow_queries_for_project_and_process(groupId, process["id"])
        suggested_index = collect_suggested_indexes_for_project_and_process(groupId, process["id"])


def get_processes_for_group(groupId):
    """
    Get Processes for Group

    :param groupId:
    :return:
    """
    url = "https://cloud.mongodb.com/api/atlas/v1.0/groups/{}/processes".format(groupId)
    resp = requests.get(url)
    return resp.json()

def collect_slow_queries_for_project_and_process(groupId, processId):
    """

    :param groupId:
    :param processId:
    :return:
    """
    url = "https://cloud.mongodb.com/api/atlas/v1.0/groups/{}/processes/{}/performanceAdvisor/slowQueryLogs".format(
        groupId, processId
    )
    resp = requests.get(url)
    return resp.json()


def collect_suggested_indexes_for_project_and_process(groupId, processId):
    """
    Collect Suggested Indexes for Project and Process

    :param groupId:
    :param processId:
    :return:
    """
    url = "https://cloud.mongodb.com/api/atlas/v1.0/groups/{}/processes/{}/performanceAdvisor/suggestedIndexes".format(
        groupId, processId
    )
    resp = requests.get(url)
    return resp.json()


def shouldSkipOpsMgrProject(scriptConfig, groupData):
    """
    Should Skip Ops Manager Project

    :param scriptConfig:
    :param groupData:
    :return:
    """
    groupName = groupData["name"]
    groupNameParts = groupName.split("_")
    groupAppPneumonic = None
    groupEnv = None

    if len(groupNameParts) > 1:
        groupAppPneumonic = groupNameParts[0]
        groupEnv = groupNameParts[1]

    logging.debug("Checking if should skip with project id {}; project name {}, and configs {}".format(groupData["id"], groupName,
                                                                                                json.dumps(scriptConfig, indent=4)))
    if (scriptConfig["projectId"] is not None) and (groupData["id"] == scriptConfig["projectId"]):
        return False

    if (scriptConfig["projectName"] is not None) and (groupData["name"] == scriptConfig["projectName"]):
        return False

    if (scriptConfig["projectAppName"] is not None) and (groupAppPneumonic is not None) and (groupAppPneumonic == scriptConfig["projectAppName"]):
        return False

    if (scriptConfig["projectAppEnv"] is not None) and (groupEnv is not None) and (groupEnv == scriptConfig["projectAppEnv"]):
        return False

    # If no configs are set, never skip this data point
    if  (scriptConfig["projectId"] is None) and (scriptConfig["projectName"] is None) and \
        (scriptConfig["projectAppName"] is None) and (scriptConfig["projectAppEnv"] is None):
        return False
    return True


class RowData():
    """
    Row Data
    """
    def setProjectName(self, name):
        self.name = name

    def setProjectId(self, id):
        self.projectId = id

    def setClusterName(self, clusterName):
        self.clusterName = clusterName

    def setClusterHost(self, clusterHost):
        self.clusterHost = clusterHost

    def setMDBVersion(self, version):
        self.version = version

    def setDB(self, dbName):
        self.dbName = dbName

    def setStatus(self, status):
        self.status = status

    def setOpenMode(self, openMode):
        self.openMode = openMode

    def getRowStr(self):
        return "{},{},{},{},{},{}".format(self.clusterHost, self.clusterName, self.version, self.dbName, self.status, self.openMode)


def getRowDataForGroup(group):
    """
    Get Row Data for Group

    :param group:
    :return:
    """
    clusters = opsMgrConnector.getClustersForGroup(group["id"], verifyBool=verifyCerts)
    automationConfigForGroup = opsMgrConnector.getAutomationConfig(group["id"], verifyBool=verifyCerts)
    rowData = []
    for cluster in clusters["results"]:
        rowData.extend(getRowDataForCluster(cluster, group, automationConfigForGroup))
    return rowData


def getRowDataForCluster(cluster, group, automationConfig=None):
    logging.debug("Getting data for cluster " + cluster["clusterName"])
    if automationConfig is None:
        automationConfig = opsMgrConnector.getAutomationConfig(cluster["groupId"], verifyBool=verifyCerts)
    processes = getProcessesForCluster(cluster, automationConfig)

    rowData = []
    for process in processes:
        rowData.extend(getRowDataForProcess(cluster, group, process, automationConfig))

    return rowData

def getRowDataForProcess(cluster, group, process, automationConfig):
    """
    Get Row Data for Process

    :param process:
    :param automationConfig:
    :return:
    """
    # Get host information
    logging.debug("Getting host information for process {}".format(json.dumps(process, indent=4)))
    hostname = process["hostname"]
    port = process["args2_6"]["net"]["port"]
    hostData = opsMgrConnector.getHostByHostnameAndPort(cluster["groupId"], hostname, port, verifyBool=verifyCerts)
    logging.debug("Received host data {}".format(json.dumps(hostData, indent=4)))

    hostType = hostData["typeName"]
    hostStatus = "RECOVERING" if hostType == "RECOVERING" else ( "DOWN/NO RECENT PING" if hostType == "NO_DATA" else "HEALTHY")

    # PRIMARY_TYPES = [ "REPLICA_PRIMARY", "SHARD_PRIMARY" ]
    processType = "SECONDARY" if hostType == "RECOVERING" else hostType

    # Get Databases for host
    dbsSeen = []
    pageNum = 0
    dbsOnHost = opsMgrConnector.getDatabasesForHost(cluster["groupId"], hostData["id"], pageNum, verifyBool=verifyCerts)
    while len(dbsSeen) < dbsOnHost["totalCount"]:
        logging.debug("Examining page {} of db results; there are a total of {} dbs".format(pageNum, dbsOnHost["totalCount"]))
        dbsSeen.extend([ db["databaseName"] for db in dbsOnHost["results"]])
        pageNum += 1
        dbsOnHost = opsMgrConnector.getDatabasesForHost(cluster["groupId"], hostData["id"], pageNum, verifyBool=verifyCerts)

    dbsSeen.add("admin")

    # TODO -- need to add for sharded cluster
    clusterName = cluster["replicaSetName"] if "replicaSetName" in cluster else cluster["clusterName"]

    # Create Row Data
    rows = []
    for db in dbsSeen:
        rowData = RowData()
        rowData.setProjectName(group["name"])
        rowData.setProjectId(cluster["groupId"])
        rowData.setClusterName(clusterName)
        rowData.setClusterHost(process["hostname"])
        rowData.setMDBVersion(process["version"])

        # Add db info
        rowData.setDB(db)

        # Add host info
        rowData.setStatus(hostStatus)
        rowData.setOpenMode(processType)

        data = rowData.getRowStr()
        rows.append(data)
    return rows


def getProcessesForCluster(cluster, automationConfig=None):
    """
    Get Processes for Cluster

    :param cluster:
    :param automationConfig:
    :return:
    """
    logging.debug("Getting processes for cluster with name " + cluster["clusterName"])
    processes = []


    replicaSetFound = False
    if "replicaSetName" in cluster:
        for replicaSet in automationConfig["replicaSets"]:
            if replicaSet["_id"] == cluster["replicaSetName"]:
                replicaSetFound = True
                members = [ member["host"] for member in replicaSet["members"] ]
                processes = [ process for process in automationConfig["processes"] if process["name"] in members]

    # TODO -- finish this for sharding
    # if not replicaSetFound:
    #     for shardedCluster in automationConfig["shardedClusters"]:
    #         if shardedCluster["_id"] == cluster["name"]:

    return processes


def checkOsCompatibility():
    """
    Check OS Compatibility

    Ensures that the script is being run on a linux machine
    """
    opSys  = platform.system()
    if opSys != 'Linux':
        logging.exception(
            "{}: Unsupported Operating System\n"
            "{}: Supported Operating Systems are: Linux".format(scriptName, opSys, scriptName)
        )
        sys.exit()

########################################################################################################################
# Base Methods
########################################################################################################################

def setupArgs():
    """
    Setup args
    Parses all command line arguments to the script
    """
    parser = argparse.ArgumentParser(description='Conducts a health check on the specified host')
    parser.add_argument('--opsmgrUri',      required=False, action="store", dest='opsMgrUri',       default='http:127.0.0.1:8080/', help='The uri of the ops manager instance under which this server will be managed.')
    parser.add_argument('--opsmgrapiuser',  required=False, action="store", dest='opsMgrApiUser',   default='',                     help='The api user for the designated ops manager instance')
    parser.add_argument('--opsmgrapikey',   required=False, action="store", dest='opsMgrApiKey',    default='',                     help='The api key for the designated ops manager instance')
    parser.add_argument('--scale',          required=False, action="store", dest='scale',           default='bytes',                help='Scale in which to view metrics. One of {}'.format(VALID_SCALES.keys()))

    # parser.add_argument('--projectName',              required=False, action="store", dest='projectName',       default=None,                help='The full name of the project.')
    # parser.add_argument('--projectId',                  required=False, action="store", dest='projectId',       default=None,                help='The id of the project in ops manager.')
    # parser.add_argument('--projectAppName',           required=False, action="store", dest='projectAppName',    default=None,                help='The Application pneumonic.')
    # parser.add_argument('--projectAppEnv',            required=False, action="store", dest='projectAppEnv',     default=None,                help='The application environment. One of ' + APPLICATION_ENVS.__str__() )

    parser.add_argument('--fileName',     required=False, action="store", dest='fileName',          default=None,                 help='Path of the file to write to; if not used, will write to standard out')
    parser.add_argument('--verifycerts',  required=False, action="store", dest='verifycerts',       default=True,                 help='Whether or not to verify TLS certs on HTTPS requests')
    parser.add_argument('--loglevel',     required=False, action="store", dest='logLevel',          default='info',                 help='Log level. Possible values are [none, info, verbose]')

    # TODO Command line arg for update/refresh
    return parser.parse_args()

def _configureLogger(logLevel):
    format = '%(message)s'
    if logLevel != 'INFO':
        format = '%(levelname)s: %(message)s'
    # logLevelMapping = logging.getLevelNamesMapping()
    # logging.basicConfig(format=format, level=logLevelMapping.get(logLevel.upper()), filename="debug.log")
    logging.basicConfig(format=format, level=logLevel.upper(), filename="debug.log")

def gitVersion():
    """
    Git Version

    Gets the git revision (the sha denoting the revision) of the current versionselfself.
    If the local version of the code does not have .git metadata files returns the
    version of the script as indicated by version and revDate variables above.
    """
    def _getGitCommitSha(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(cmd, stdout = subprocess.PIPE, env = env).communicate()[0]
        return out

    commitDate = "N/A"
    gitVersion = "Unknown"
    try:
        # Get last commit version
        out        = _getGitCommitSha(['git', 'rev-parse', 'HEAD'])
        gitVersion = out.strip().decode('ascii')

        # Get last commit date
        out        = _getGitCommitSha(['git', 'show', '-s', '--format=%ci'])
        commitDate = out.strip().decode('ascii')
    except OSError:
        gitVersion = version
        commitDate = revdate
        logging.exception("Unable to get the version")

    return {
        'version': gitVersion,
        'date': commitDate
    }

def writeDataToFile(fileName, data):
    """
    Write Data To File

    :return:
    """
    logging.info("Writing data to file with name " + fileName)
    with open(fileName, "w") as file:
        file.write(data)
        file.close()

def main():

    args = setupArgs()
    _configureLogger(args.logLevel.upper())
    versionInfo = gitVersion()
    logging.info("Running {} v({}) last modified {}".format(scriptName, versionInfo['version'][:8], versionInfo['date']))
    # checkOsCompatibility()

    # Get Ops Manager connection
    global opsMgrConnector
    opsMgrConnector = OpsMgrConnector(args.opsMgrUri, args.opsMgrApiUser, args.opsMgrApiKey)

    global verifyCerts
    verifyCerts = (args.verifycerts.lower() == 'true')
    collect_storage_data(args.fileName, args.scale)


#-------------------------------
if __name__ == "__main__":
    main()