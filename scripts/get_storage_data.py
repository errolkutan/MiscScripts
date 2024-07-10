#!/usr/bin/python
import operator
import platform
import sys
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
revdate         = "07-08-2024"
scriptName      = "get_storage_data"
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

def collect_storage_data(destFileName, scale="BYTES"):
    """
    Collect Storage Data

    :return:
    """
    logging.debug("Using scale {}".format(scale))
    scale = scale.lower()
    if scale not in VALID_SCALES.keys():
        raise Exception("Scale {} is invalid. Must be one of {}".format(
            scale, VALID_SCALES.keys()
        ))

    metricScale = SCALE_MAP[VALID_SCALES.get(scale)]

    allGroups = opsMgrConnector.getAllGroups(verifyBool=verifyCerts)
    storageData = []
    for group in allGroups["results"]:
        storageDataForGroup = collect_storage_data_for_group(group)
        storageData.extend(storageDataForGroup)


    storageData = get_mock_data()

    logging.debug("Constructing report metadata table")
    table = PrettyTable()
    table.field_names = [ "Project Name", "Cluster Name", "Host Name",
                          "Storage Size ({})".format(VALID_SCALE_NAMES[scale]),
                          "Data Size ({})".format(VALID_SCALE_NAMES[scale]),
                          "Index Size ({})".format(VALID_SCALE_NAMES[scale]),
                          "Data + Index Size ({})".format(VALID_SCALE_NAMES[scale]),
                          "Disk Space Free on Data Partition ({})".format(VALID_SCALE_NAMES[scale]),
                          "Disk Space Used on Data Partition ({})".format(VALID_SCALE_NAMES[scale]),
                          "Disk Space Total on Data Partition ({})".format(VALID_SCALE_NAMES[scale]),
                          "Disk Space Free on Data Partition (%)",
                          "Disk Space Used on Data Partition (%)"
                          ]
    for record in storageData:
        table.add_row([
            record["groupName"], record["clusterName"], record["hostName"],
            "{0:.2f}".format(record["DB_STORAGE_TOTAL"] / metricScale),
            "{0:.2f}".format(record["DB_DATA_SIZE_TOTAL"]/metricScale),
            "{0:.2f}".format(record["DB_INDEX_SIZE_TOTAL"]/metricScale),
            "{0:.2f}".format((record["DB_INDEX_SIZE_TOTAL"] + record["DB_DATA_SIZE_TOTAL"])/metricScale),
            "{0:.2f}".format(record["DISK_PARTITION_SPACE_FREE"]/metricScale),
            "{0:.2f}".format(record["DISK_PARTITION_SPACE_USED"]/metricScale),
            "{0:.2f}".format((record["DISK_PARTITION_SPACE_FREE"] + record["DISK_PARTITION_SPACE_USED"])/metricScale),
            "{0:.2f}".format(record["DISK_PARTITION_SPACE_PERCENT_FREE"]),
            "{0:.2f}".format(record["DISK_PARTITION_SPACE_PERCENT_USED"])
        ])

    table_str = table.get_string(sort_key=operator.itemgetter(1,2), sortby="Project Name")
    if destFileName is not None:
        writeDataToFile(destFileName, table_str)
    else:
        print(table_str)
    print("Done!")

# def sort_by_columns_in_order(row1, row2=None):
#     """
#     Sort Order for Row Data
#
#     :param row1:
#     :param row2:
#     :return:
#     """
#     if row2 is None:
#         return 1
#     smallest_len = min(len(row1), len(row2))
#     for i in range(1, smallest_len):
#         # If Row 1 > Row 2 for Column i, then Row 1 should come after
#         if row1[i] > row2[i]:
#             return 1
#         # Otherwise it should come first
#         elif row1[i] < row2[i]:
#             return -1
#
#         # If they are equal, we should consider the next column for sorting
#     return -1

def collect_storage_data_for_group(group):
    """
    Collect Storage Data For Group

    :param groupId:
    :return:
    """
    groupId = group["id"]
    logging.info("Found group with id {}".format(groupId))
    logging.debug("Found group: {}".format(json.dumps(group, indent=4)))

    storageDataForGroup = []

    # Get each cluster in this project
    clusterForProject = opsMgrConnector.getClustersForGroup(group["id"], verifyBool=verifyCerts)
    for cluster in clusterForProject["results"]:
        storageDataForCluster = collect_storage_data_for_cluster(group, cluster)
        storageDataForGroup.extend(storageDataForCluster)

    return storageDataForGroup

def collect_storage_data_for_cluster(group, cluster):
    """
    Collect Storage Data for Cluster

    :param cluster:
    :return:
    """
    clusterId = cluster["id"]
    logging.info("Found cluster with id {}".format(clusterId))
    logging.debug("Found cluster: {}".format(json.dumps(cluster, indent=4)))

    storageDataForCluster = []

    # Get each host in this cluster
    hostsForProject = opsMgrConnector.getHosts(cluster["groupId"], verifyBool=verifyCerts)
    for host in hostsForProject["results"]:
        if host["clusterId"] == clusterId:
            storageDataForHost = collect_storage_data_for_host(group, cluster, host)
            storageDataForCluster.append(storageDataForHost)

    return storageDataForCluster


def collect_storage_data_for_host(group, cluster, host):
    """
    Collect Storage Data For Host

    :param host:
    :return:
    """
    diskMeasurementNames = [
        "DISK_PARTITION_SPACE_FREE",
        "DISK_PARTITION_SPACE_PERCENT_FREE",
        "DISK_PARTITION_SPACE_USED",
        "DISK_PARTITION_SPACE_PERCENT_USED"
    ]
    disks = opsMgrConnector.getDiskPartitionName(host["groupId"], host["id"], verifyBool=verifyCerts)

    disk_measurement_data = None
    for disk in disks["results"]:
        diskMeaurementsForPartition = opsMgrConnector.getDiskPartitionMeasurementOverPeriodForHost(
            host["groupId"], host["id"], disk["partitionName"], "PT1H", "P30D", diskMeasurementNames, verifyBool=verifyCerts
        )
        disk_measurement_data = diskMeaurementsForPartition

    validDiskMeasurements = get_valid_nonnull_measurement(disk_measurement_data, diskMeasurementNames)

    storageMeasurements = [
        "DB_DATA_SIZE_TOTAL",
        "DB_STORAGE_TOTAL",
        "DB_INDEX_SIZE_TOTAL"
    ]

    host_measurement_data = opsMgrConnector.getMeasurementsOverPeriodForHost(
        host["groupId"], host["id"], "PT1H", "P30D", storageMeasurements, verifyBool=verifyCerts
    )

    validMeasurement = get_valid_nonnull_measurement(host_measurement_data, storageMeasurements)

    cluster_name = cluster["clusterName"]
    if cluster["typeName"] == "REPLICA_SET":
         cluster_name = cluster["replicaSetName"]
    elif cluster["typeName"] == "SHARDED":
        cluster_name = cluster["shardName"]

    data = {
        "groupId" : host["groupId"],
        "groupName" : group["name"],
        "clusterId" : host["clusterId"],
        "clusterName" : cluster_name,
        "hostId" : host["id"],
        "hostName" : host["hostname"],
        "DB_DATA_SIZE_TOTAL" : validMeasurement["DB_DATA_SIZE_TOTAL"],
        "DB_STORAGE_TOTAL" : validMeasurement["DB_STORAGE_TOTAL"],
        "DB_INDEX_SIZE_TOTAL" : validMeasurement["DB_INDEX_SIZE_TOTAL"],
        "DISK_PARTITION_SPACE_FREE" : validDiskMeasurements["DISK_PARTITION_SPACE_FREE"],
        "DISK_PARTITION_SPACE_PERCENT_FREE" : validDiskMeasurements["DISK_PARTITION_SPACE_PERCENT_FREE"],
        "DISK_PARTITION_SPACE_USED" : validDiskMeasurements["DISK_PARTITION_SPACE_USED"],
        "DISK_PARTITION_SPACE_PERCENT_USED" : validDiskMeasurements["DISK_PARTITION_SPACE_PERCENT_USED"]
    }
    return data

def get_mock_data():
    """

    :return:
    """
    data = [
        {
            "groupId": "groupId2",
            "groupName": "group2",
            "clusterId": "clusterId3",
            "clusterName": "clusterName1",
            "hostId": "2",
            "hostName": "hostname1",
            "DB_DATA_SIZE_TOTAL": 22,
            "DB_STORAGE_TOTAL": 22,
            "DB_INDEX_SIZE_TOTAL": 33,
            "DISK_PARTITION_SPACE_FREE": 344,
            "DISK_PARTITION_SPACE_PERCENT_FREE": 33,
            "DISK_PARTITION_SPACE_USED": 24,
            "DISK_PARTITION_SPACE_PERCENT_USED": 55
        },
        {
            "groupId": "groupId1",
            "groupName": "group1",
            "clusterId": "clusterId3",
            "clusterName": "clusterName3",
            "hostId": "2",
            "hostName": "hostname1",
            "DB_DATA_SIZE_TOTAL": 22,
            "DB_STORAGE_TOTAL": 22,
            "DB_INDEX_SIZE_TOTAL": 33,
            "DISK_PARTITION_SPACE_FREE": 344,
            "DISK_PARTITION_SPACE_PERCENT_FREE": 33,
            "DISK_PARTITION_SPACE_USED": 24,
            "DISK_PARTITION_SPACE_PERCENT_USED": 55
        },
        {
            "groupId": "groupId1",
            "groupName": "group1",
            "clusterId": "clusterId1",
            "clusterName": "clusterName1",
            "hostId": "2",
            "hostName": "hostname1",
            "DB_DATA_SIZE_TOTAL": 22,
            "DB_STORAGE_TOTAL": 22,
            "DB_INDEX_SIZE_TOTAL": 33,
            "DISK_PARTITION_SPACE_FREE": 344,
            "DISK_PARTITION_SPACE_PERCENT_FREE": 33,
            "DISK_PARTITION_SPACE_USED": 24,
            "DISK_PARTITION_SPACE_PERCENT_USED": 55
        },
        {
            "groupId": "groupId1",
            "groupName": "group1",
            "clusterId": "clusterId2",
            "clusterName": "clusterName2",
            "hostId": "2",
            "hostName": "hostname1",
            "DB_DATA_SIZE_TOTAL": 22,
            "DB_STORAGE_TOTAL": 22,
            "DB_INDEX_SIZE_TOTAL": 33,
            "DISK_PARTITION_SPACE_FREE": 344,
            "DISK_PARTITION_SPACE_PERCENT_FREE": 33,
            "DISK_PARTITION_SPACE_USED": 24,
            "DISK_PARTITION_SPACE_PERCENT_USED": 55
        }
    ]
    return data


def get_valid_nonnull_measurement(measurements_data, measurement_names):
    """
    Get Valid Non-null Measurements

    :param measurements_data:
    :param measurement_names:
    :return:
    """
    # Get minimum length of data points among all of the measurements in question
    endIndex = 10000000
    for measurement in measurements_data["measurements"]:
        if measurement["name"] in measurement_names:
            endIndex = min(endIndex, len(measurement["dataPoints"]))

    # Construct Default Measurement
    valid_measurement = { }
    for name in measurement_names:
        valid_measurement[name] = None

    # Find valid measurement
    for i in sorted(range(0, endIndex), reverse=True):

        # Construct measurement at index i
        measurementAtIndex = { }
        for name in measurement_names:
            for measurement in measurements_data["measurements"]:
                if measurement["name"] == name:
                    measurementAtIndex[name] = measurement["dataPoints"][i]["value"]

        # Check if valid
        isValid = True
        for name in measurement_names:
            isValid = isValid and measurementAtIndex[name] is not None

        if isValid:
            return measurementAtIndex

    return valid_measurement


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