#!/usr/bin/python
import datetime
import platform
import sys
import requests
sys.path.append('.')
import os
import logging
import subprocess
import argparse
import json
import pymongo
import numpy
import uuid
import socket
import functools
from prettytable import PrettyTable
from datetime import datetime
from dateutil import tz

from mdbaas.opsmgrutil import OpsMgrConnector, OpsManagerGroupRole
from mdbaas.errors import HostNotFoundError

from operator import itemgetter

# Script metadata
version         = "1.0.0"
revdate         = "06-13-2024"
scriptName      = "healthcheck"
scriptNameFull  = scriptName + ".py"
completionStr   = "\n====================================================================\n                      Completed " + scriptName + "!!!!              \n ====================================================================\n"

BYTES_IN_GB = 1024*1024*1024
SECONDS_IN_HOUR = 60*60


MONGOD_TYPES =  [ "STANDALONE", "REPLICA_PRIMARY", "REPLICA_SECONDARY", "REPLICA_ARBITER", "RECOVERING", "SHARD_STANDALONE", "SHARD_PRIMARY", "SHARD_SECONDARY" ]
STANDALONE_TYPES = [ "STANDALONE" ]
RS_TYPES =  [ "STANDALONE", "REPLICA_PRIMARY", "REPLICA_SECONDARY", "REPLICA_ARBITER", "RECOVERING" ]
ARBITER_TYPES = [ "REPLICA_ARBITER" ]
SHARD_TYPES = [ "SHARD_STANDALONE", "SHARD_PRIMARY", "SHARD_SECONDARY" ]
MONGOS_TYPES =  [ "SHARD_MONGOS" ]
CONFIG_SERVER_TYPES = [ "SHARD_CONFIG" ]

MONGOD = "mongod"
RS_MEMBER = "replicaSetMember"
STANDALONE = "standalone"
ARBITER = "arbiter"
SHARDED_CLUSTER_MEMBER = "shardedClusterMember"
MONGOS = "mongos"
CONFIG_SERVER = "configServer"


def isHostOfType(hostInfo, type):
    """
    Is Host of Type

    :param hostInfo:
    :param type:
    :return:
    """
    if MONGOD == type:
        return hostInfo["typeName"] in MONGOD_TYPES
    if STANDALONE == type:
        return hostInfo["typeName"] in STANDALONE_TYPES
    if RS_MEMBER == type:
        return hostInfo["typeName"] in RS_TYPES
    if ARBITER == type:
        return hostInfo["typeName"] in ARBITER_TYPES
    if SHARDED_CLUSTER_MEMBER == type:
        return hostInfo["typeName"] in SHARD_TYPES
    if MONGOS == type:
        return hostInfo["typeName"] in MONGOS_TYPES
    if CONFIG_SERVER == type:
        return hostInfo["typeName"] in CONFIG_SERVER_TYPES
    return False

def findHostData(hostName, hostType=MONGOD):
    """
    Find Host

    Finds the name of the cluster and project that contains the host

    :param hostName:
    :return:
    """
    groupId = getGroupIdForHost(hostName)
    if groupId is None:
        raise ValueError("Could not find group for hostname {}".format(hostName))

    groupData = opsMgrConnector.getGroupById(groupId)
    groupName = groupData["name"]

    logging.info("Looking for group with id {} in ops manager...".format(groupId))
    matchingHost = None
    hostsInGroup = opsMgrConnector.getHosts(groupId)
    for host in hostsInGroup["results"]:
        logging.debug("Checking if hostname {} is in host".format(hostName, json.dumps(host, indent=4)))
        if isHostOfType(host, hostType) and host["hostname"] == hostName:
            matchingHost = host
    logging.debug("Found matching host {}".format(json.dumps(matchingHost, indent=4)))

    if matchingHost is None:
        raise HostNotFoundError(hostName)

    clusterName = None
    if "replicaSetName" in matchingHost:
        clusterName = matchingHost["replicaSetName"]
    elif "shardName" in matchingHost:
        clusterName = matchingHost["shardName"]

    replicaSetState = None
    if "replicaStateName" in matchingHost:
        replicaSetState = matchingHost["replicaStateName"]

    replcaSetMemberStateName = None
    if "typeName" in matchingHost:
        replcaSetMemberStateName = matchingHost["typeName"]

    resp = {
        "projectId" : groupId,
        "projectName" : groupName,
        "clusterName" : clusterName,
        "clusterId" : matchingHost.get("clusterId", None),
        "hostId" : matchingHost.get("id", None),
        "replicaSetState" : replicaSetState,
        "replicaSetMemberStateName" : replcaSetMemberStateName,
        "uptimeSecs" : matchingHost.get("uptimeMsec", None),
        "lastRestart" : matchingHost.get("lastRestart", None),
        "lastPing" : matchingHost.get("lastPing", None)
    }
    logging.debug("Returning response {}".format(resp))
    return resp

def getGroupIdForHost(hostName):
    """
    Get Group Id for Host

    :param hostName:
    :return:
    """
    hostNameParts = hostName.split(".")
    shortHostName = hostNameParts[0]
    hostnames = [
        hostName,
        shortHostName
    ]
    groupId = None
    if groupId is None:
        groupId = findGroupIdForHostDataInOpsManager(hostnames)
    return groupId


def findGroupIdForHostDataInOpsManager(hostNames):
    """
    Find Host Data in Ops Manager
    :param hostName:
    :return:
    """
    logging.debug("Finding group id for host with name {} in Ops Manager".format(str(hostNames)))

    groups = opsMgrConnector.getAllGroups()
    for group in groups["results"]:
        logging.debug("Found group {}".format(json.dumps(group, indent=4)))
        groupId = group["id"]

        logging.debug("Fetching hosts for group {}".format(groupId))
        hosts = opsMgrConnector.getHosts(groupId)
        for host in hosts["results"]:
            for hostName in hostNames:
                logging.debug("Inspecting host {} attempting to find host {}".format(json.dumps(host, indent=4), hostName))
                if host["hostname"] == hostName:
                    return groupId
    return None


def getMeasurementsForHost(groupId, hostId):
    """
    Get Measurements For Host

    :param groupId:
    :param hostId:
    :return:
    """

    diskForDataDir = None
    disksForHost = opsMgrConnector.getDiskPartitionName(groupId, hostId)
    for disk in disksForHost["results"]:
        diskForDataDir = disk

    diskMeasurementTypes = [
        # Disk data
        "DISK_PARTITION_SPACE_PERCENT_USED"
    ]
    granularity = "PT1M"  # 1 minute granularity
    period = "PT1H"  # 1 hour back
    diskMeasurementData = None

    if diskForDataDir is not None:
        diskMeasurementData = opsMgrConnector.getDiskPartitionMeasurementOverPeriodForHost(groupId, hostId, diskForDataDir["partitionName"],
                                                                                          granularity, period, diskMeasurementTypes)
        logging.debug("Got disk measurementsdata : {}".format(json.dumps(diskMeasurementData, indent=4)))
        diskMeasurementData = diskMeasurementData["measurements"]

    hostMeasurementTypes = [
        "CONNECTIONS",

        # CPU Data
        "PROCESS_CPU_USER",
        "SYSTEM_CPU_USER",
        "PROCESS_NORMALIZED_CPU_USER",

        # Memory data
        "SYSTEM_MEMORY_USED",
        "SYSTEM_MEMORY_FREE",
        "SYSTEM_MEMORY_AVAILABLE",
        "SWAP_USAGE_USED",
        "SWAP_USAGE_FREE",

        # Oplog data
        "OPLOG_RATE_GB_PER_HOUR",        # TODO -- find replication oplog window variable. Cannot find here https://www.mongodb.com/docs/ops-manager/current/reference/api/measures/measurement-types/
        "OPLOG_MASTER_TIME",

        # Query efficiency data
        "QUERY_TARGETING_SCANNED_PER_RETURNED",
        "QUERY_TARGETING_SCANNED_OBJECTS_PER_RETURNED"
    ]

    measurementsData = opsMgrConnector.getMeasurementsOverPeriodForHost(groupId, hostId, granularity, period, hostMeasurementTypes)
    logging.debug("Got measurements data : {}".format(json.dumps(measurementsData, indent=4)))
    measurementsData["measurements"].extend(diskMeasurementData)
    return measurementsData

def isSystemNamespace(mongoDBNamespace):
    """
    Is System Namespace

    :param mongoDBNamespace:
    :return:
    """
    return mongoDBNamespace.startswith("local") or mongoDBNamespace.startswith("admin") or mongoDBNamespace.startswith("config")

def getSlowQueryLogForTime(groupId, hostId, timePeriod):
    """
    Get Slow Query Log for Time

    :param groupId:
    :param hostId:
    :param timePeriod:
    :return:
    """
    resp = opsMgrConnector.getSlowQueryLogsForGroupAndHost(groupId, hostId, timePeriod, None, None, None)
    logging.debug("Got slow query logs resp {}".format(json.dumps(resp, indent=4)))

    if "errorCode" in resp and resp["errorCode"] == "USER_UNAUTHORIZED":
        logging.debug("Creating a temporary project-level API key...")
        apiKeyResp = createGroupAPIKey(groupId)
        try:
            orgId = None
            for role in apiKeyResp["roles"]:
                if "orgId" in role:
                    orgId = role["orgId"]
            addCurrentIPToAPIKeyWhitelist(orgId, apiKeyResp["id"])

            logging.debug("Creating new connector...")
            tempConnector = OpsMgrConnector(opsMgrConnector.opsMgrUri, apiKeyResp["publicKey"], apiKeyResp["privateKey"])
            resp = tempConnector.getSlowQueryLogsForGroupAndHost(groupId, hostId, timePeriod, None, None, None)
        except Exception as e:
            logging.error("Encountered exception: {}".format(e))
            deleteGroupAPIKey(orgId, apiKeyResp["id"])
        finally:
            deleteGroupAPIKey(orgId, apiKeyResp["id"])
        return resp
    else:
        return resp


def createGroupAPIKey(groupId):
    """
    Create Group API Key

    :param groupId:
    :param desc:
    :return:
    """
    opsMgrGroupUserRole = OpsManagerGroupRole.GROUP_DATA_ACCESS_READ_ONLY
    opsMgrGroupUserDesc = "healthcheck.{}.temp.key".format(str(uuid.uuid4()))
    resp = opsMgrConnector.createAndAssignAnOrgAPIKeyToProject(groupId, opsMgrGroupUserDesc, [ opsMgrGroupUserRole ])
    return resp

def addCurrentIPToAPIKeyWhitelist(orgId, apiKeyId):
    """
    Add Current IP to API Key Whitelist

    :param orgId:
    :param apiKeyId:
    :return:
    """
    hostname = socket.gethostname()
    internalIPAddr = socket.gethostbyname(hostname)

    # externalIPAddr = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    # externalIPAddr = requests.get('https://api.ipify.org').content.decode('utf8')
    externalIPAddr = requests.get('https://ifconfig.me').content.decode('utf8')
    accessList = [
        { "ipAddress" : internalIPAddr },
        { "ipAddress" : externalIPAddr }
    ]
    return opsMgrConnector.createAccessListEntriesForAnOrganizationAPIKey(orgId, apiKeyId, accessList)


def deleteGroupAPIKey(orgId, apiKeyId):
    """
    Delete Group API Key

    :param groupId:
    :param desc:
    :return:
    """
    logging.debug("Deleting api key with id {}".format(apiKeyId))
    return opsMgrConnector.deleteOrganizationAPIKey(orgId, apiKeyId)


def getSlowQueryLogsForLastHour(groupId, hostId):
    """
    Get Slow Query Logs

    :param groupId:
    :param hostId:
    :return:
    """
    lastHourInMillis = 60*60*1000
    slowQueryLogs = getSlowQueryLogForTime(groupId, hostId, lastHourInMillis)

    # Remove system collections
    slowQueryLogsCleaned = []
    for log in slowQueryLogs["slowQueries"]:
        if isSystemNamespace(log["namespace"]):
            continue
        jsonLog = {
            "namespace": log["namespace"],
            "line": json.loads(log["line"])
        }
        slowQueryLogsCleaned.append(jsonLog)

    return slowQueryLogsCleaned


def conductHealthCheck(hostName, showCollScans, sortCollScans, logPath=None):
    """
    Conduct Health Check

    :param hostName:
    :return:
    """
    logging.info("Conducting health check on host {}".format(hostName))
    # healthCheckData = getHealthCheckData(hostName)
    healthCheckData, collScans = getHealthCheckData(hostName)
    # collScans = getLogsStub()

    logging.info("Results:")
    constructAndPrintMetaDataTable(hostName, healthCheckData)
    constructAndPrintResultsTable(hostName, healthCheckData)

    if showCollScans:
        print("\nShowing collection scans:")
        if len(collScans) == 0:
            print("     Could not find any COLLSCANS in last 24 hours")
        if sortCollScans:
            logging.debug("Sorting collection scans")
            collScans = sorted(collScans, key=lambda log: ( log['line']['attr']['durationMillis'] ), reverse=True )


        path = "healthcheck/logs" if logPath is None else logPath
        pathExists = os.path.exists(path)
        if not pathExists:
            logging.debug("Making logs directory")
            os.mkdir(path)

        # Affix date to slow query logs
        writeLogsToFile(collScans, "{}/{}.slowQueryLogs.json".format(path, hostName))
        summarizeLogs(collScans)

def writeLogsToFile(logs, fileName):
    """
    Write Logs to File

    :param logs:
    :param fileName:
    :return:
    """
    logging.debug("Writing data to file " + fileName)
    logStr = ""
    for collScanLog in logs:
        logStr += json.dumps(collScanLog, indent=4) + ",\n"
    logging.debug("Writing data to file")
    with open(fileName, "w") as logsFile:
        logsFile.writelines(logStr)


def summarizeLogs(slowQueryLogs):
    """
    Summarize Logs

    :param logs:
    :return:
    """
    logging.debug("Summarizing logs")
    logsPerNamespace = {}
    for slowQueryLog in slowQueryLogs:
        logging.debug("Got log {}".format(json.dumps(slowQueryLog, indent=4)))
        logsForNS = logsPerNamespace.get(slowQueryLog["namespace"], [])
        logsForNS.append(slowQueryLog)
        logsPerNamespace[slowQueryLog["namespace"]] = logsForNS

    totalsForNamespace = {}
    for namespace in logsPerNamespace:
        logging.debug("Computing totals for namespace " + namespace)
        logsForNS = logsPerNamespace[namespace]
        numLogs = len(logsForNS)
        defaultTimeReading = { "timeReadingMicros" : 0 }

        totalDuration = 0
        totalTimeReadingMicros = 0
        totalTimeWritingMicros = 0
        try:
            if numLogs == 1:
                firstLog = logsForNS[0]
                totalDuration = getTotalDurationFromLogEntry(firstLog)
                totalTimeReadingMicros = getStorageTimeReadingMicrosFromLogEntry(firstLog)
                totalTimeWritingMicros = getStorageTimeWritingMicrosFromLogEntry(firstLog)

            elif numLogs > 1:
                durations = [ getTotalDurationFromLogEntry(logEntry) for logEntry in logsForNS ]
                timeReadingMicros = [ getStorageTimeReadingMicrosFromLogEntry(logEntry) for logEntry in logsForNS ]
                timeWritingMicros = [ getStorageTimeWritingMicrosFromLogEntry(logEntry) for logEntry in logsForNS ]

                totalDuration = functools.reduce((lambda a, b: a+b), durations)
                totalTimeReadingMicros = functools.reduce((lambda a, b: a+b), timeReadingMicros)
                totalTimeWritingMicros = functools.reduce((lambda a, b: a+b), timeWritingMicros)
        except Exception as e:
            logging.error("Encountered exception {}".format(e))
            logging.error("Logs are: \n{}".format(logsForNS))

        totalsForNamespace[namespace] = {
            "numQueries" : len(logsForNS),
            "totalDurationMillis" : totalDuration,
            "avgDurationMillis" : totalDuration/len(logsForNS),
            "totalTimeReadingMicros": totalTimeReadingMicros,
            "avgTimeReadingMicros" : totalTimeReadingMicros/len(logsForNS),
            "totalTimeWritingMicros": totalTimeWritingMicros,
            "avgTimeWritingMicros": totalTimeWritingMicros / len(logsForNS)
        }
        logging.debug("Computed total for namespace {}: {}".format(namespace, json.dumps(totalsForNamespace, indent=4)))
    printLogSummaryTable(totalsForNamespace)

def getTotalDurationFromLogEntry(logEntry):
    """

    :param logEntry:
    :return:
    """
    default = {
        "line": {
            "attr": {
                "durationMillis": 0
            }
        }
    }
    try:
        return logEntry.get("line", default["line"])\
                        .get("attr", default["line"]["attr"])\
                        .get("durationMillis", 0)
    except Exception as e:
        return 0

def getStorageTimeReadingMicrosFromLogEntry(logEntry):
    """

    :param logEntry:
    :return:
    """
    default = {
        "line" : {
            "attr" : {
                "storage" : {
                    "data" : {
                        "timeReadingMicros" : 0
                    }
                }
            }
        }
    }
    try:
        return logEntry.get("line", default["line"])\
            .get("attr", default["line"]["attr"])\
            .get("storage", default["line"]["attr"]["storage"])\
            .get("data", default["line"]["attr"]["storage"]["data"])\
            .get("timeReadingMicros",0)
    except Exception as e:
        return 0

def getStorageTimeWritingMicrosFromLogEntry(logEntry):
    """

    :param logEntry:
    :return:
    """
    default = {
        "line" : {
            "attr" : {
                "storage" : {
                    "data" : {
                        "timeWritingMicros" : 0
                    }
                }
            }
        }
    }
    try:
        return logEntry.get("line", default["line"])\
            .get("attr", default["line"]["attr"])\
            .get("storage", default["line"]["attr"]["storage"])\
            .get("data", default["line"]["attr"]["storage"]["data"])\
            .get("timeWritingMicros",0)
    except Exception as e:
        return 0

def printLogSummaryTable(logSummaryNamespaceMap):
    """
    Print Log Summary Table

    :param logSummaryNamespaceMap:
    :return:
    """
    collScanSummaryTable = PrettyTable()
    collScanSummaryTable.field_names = [ "Namespace", "numQueries", "totalDurationMillis", "avgDurationMillis",
                                        "totalTimeReadingMicros", "avgTimeReadingMicros",
                                        "totalTimeWritingMicros", "avgTimeWritingMicros" ]
    for namespace in logSummaryNamespaceMap:
        row = [
            namespace,
            logSummaryNamespaceMap[namespace].get("numQueries", 0),
            logSummaryNamespaceMap[namespace].get("totalDurationMillis", 0),
            logSummaryNamespaceMap[namespace].get("avgDurationMillis", 0),
            logSummaryNamespaceMap[namespace].get("totalTimeReadingMicros", 0),
            logSummaryNamespaceMap[namespace].get("avgTimeReadingMicros", 0),
            logSummaryNamespaceMap[namespace].get("totalTimeWritingMicros", 0),
            logSummaryNamespaceMap[namespace].get("avgTimeWritingMicros", 0)
        ]
        collScanSummaryTable.add_row(row)
    print("Slow Query Summary Over Last 24 Hours)")
    print(collScanSummaryTable.get_string(sortby="Namespace"))


def constructAndPrintResultsTable(hostName, healthCheckData):
    """
    Construct And Print Results Table

    :param hostName:            A String representing the name of the host for which the results are describing
    :param healthCheckData:     A python dictionary containing the health check data
    """
    logging.debug("Creating results table")
    healthCheckTable = PrettyTable()
    healthCheckTable.field_names = ["Metric", "Current Value", "Avg Value", "Stdev", "Percent Growth", "% Above 80"]
    metricsLabelsMap = {
        "OPLOG_MASTER_TIME" : "Replication Window"
    }
    for measurement in healthCheckData["measurements"]:
        logging.debug("Adding row for measurement " + measurement)

        divisor = 1
        measurementSuffix = ""
        if measurement in ["SYSTEM_MEMORY_USED", "SYSTEM_MEMORY_AVAILABLE", "SYSTEM_MEMORY_FREE", "SWAP_USAGE_USED",
                           "SWAP_USAGE_FREE"]:
            divisor = BYTES_IN_GB
            measurementSuffix = " (GB)"
        elif measurement in ["OPLOG_MASTER_TIME"]:
            divisor = SECONDS_IN_HOUR
            measurementSuffix = " (Hours)"

        measurementLabel = measurement
        if measurement in metricsLabelsMap:
            measurementLabel = metricsLabelsMap[measurement]

        row = [
            measurementLabel + measurementSuffix,
            formatData(healthCheckData["measurements"][measurement]["current"], divisor),
            formatData(healthCheckData["measurements"][measurement]["avg"], divisor),
            formatData(healthCheckData["measurements"][measurement]["stdev"], divisor),
            formatData(healthCheckData["measurements"][measurement]["pctGrowth"], 1),
            formatData(healthCheckData["measurements"][measurement]["pctAbove80"], 1)
        ]
        healthCheckTable.add_row(row)

    startTimeLocalTZ = convertToLocalTimezone(healthCheckData["meta"]["start"])
    endTimeLocalTZ = convertToLocalTimezone(healthCheckData["meta"]["end"])

    print("Measurements for {} over last hour ({} - {})".format(hostName, startTimeLocalTZ, endTimeLocalTZ))
    print(healthCheckTable.get_string(sortby="Metric"))

def convertToLocalTimezone(dateTimeStr):
    """

    :param time:
    :return:
    """
    fromZone = tz.gettz("UTC")
    toZone = tz.tzlocal()
    dateTime = datetime.strptime(dateTimeStr, '%Y-%m-%dT%H:%M:%SZ')
    dateTime = dateTime.replace(tzinfo=fromZone)
    dateTimeLocal = dateTime.astimezone(toZone)
    return dateTimeLocal

def constructAndPrintMetaDataTable(hostName, healthCheckData):
    """
    Construct and Print Meta Data Table

    :param hostName:            A String representing the name of the host for which the results are describing
    :param healthCheckData:     A python dictionary containing the health check data
    """
    logging.debug("Constructing report metadata table")
    metaDataTable = PrettyTable()
    metaDataTable.field_names = ["Key", "Value"]
    metaDataTable.add_row(["Hostname", hostName])
    metaDataTable.add_row(["Host ID", healthCheckData["meta"]["hostId"]])
    metaDataTable.add_row(["RS State", healthCheckData["meta"]["replicaSetMemberStateName"]])
    metaDataTable.add_row(["Host State", healthCheckData["meta"]["state"]])
    metaDataTable.add_row(["Cluster Name", healthCheckData["meta"]["clusterName"]])
    metaDataTable.add_row(["Cluster ID", healthCheckData["meta"]["clusterId"]])
    metaDataTable.add_row(["Project Name", healthCheckData["meta"]["projectName"]])
    metaDataTable.add_row(["Project ID", healthCheckData["meta"]["projectId"]])
    metaDataTable.add_row(["Last ping", healthCheckData["meta"]["lastPing"]])
    metaDataTable.add_row(["Last restart", healthCheckData["meta"]["lastRestart"]])
    metaDataTable.add_row(["Server Uptime (secs)", healthCheckData["meta"]["uptimeSecs"] ])
    metaDataTable.add_row(["Time Run", datetime.now()])
    print("Report Info:")
    print(metaDataTable.get_string(sortby="Key") + "\n")


def formatData(data, divisor):
    """
    Format data

    :param data:
    :return:
    """
    if not isinstance(data, str):
        return round(data/divisor, 4)
    return data

def getHealthCheckData(hostName):
    """
    Get Health Check Data

    :param hostName:
    :return:
    """
    logging.info("Getting health check data")
    hostInfo = findHostData(hostName)
    logging.debug("Found info for host {}".format(json.dumps(hostInfo, indent=4)))
    measurementsData = getMeasurementsForHost(hostInfo["projectId"], hostInfo["hostId"])


    # Rearrange health check data
    startTime = measurementsData["start"] if "start" in measurementsData else None
    endTime = measurementsData["end"] if "end" in measurementsData else None
    measurementsMap = {
        "meta" : {
            "start" : startTime,
            "end" : endTime,
            "projectId" : hostInfo["projectId"],
            "projectName" : hostInfo["projectName"],
            "hostId" : hostInfo["hostId"],
            "clusterName" : hostInfo["clusterName"],
            "clusterId" : hostInfo["clusterId"],
            "state" : hostInfo["replicaSetState"],
            "replicaSetMemberStateName" : hostInfo["replicaSetMemberStateName"],
            "uptimeSecs": hostInfo["uptimeSecs"],
            "lastRestart": hostInfo["lastRestart"],
            "lastPing": hostInfo["lastPing"]
        },
        "measurements" : { }
    }
    for measurement in measurementsData["measurements"]:
        rawData = []
        for dataValue in measurement["dataPoints"]:
            if dataValue["value"] is not None:
                rawData.append(dataValue["value"])          # TODO -- do we need to handle Null values?
        measurementsMap["measurements"][measurement["name"]] = {
            "data" : measurement["dataPoints"],
            "rawData" : rawData
        }

    NOT_AVAILABLE = "N/A"
    measurementThresholdsOfConcern = {
        "CONNECTIONS" : NOT_AVAILABLE,

        # CPU Data
        "PROCESS_CPU_USER" : 0.80,
        "SYSTEM_CPU_USER" : 0.80,
        "PROCESS_NORMALIZED_CPU_USER" : 0.8,

        # Memory data
        "SYSTEM_MEMORY_USED" : NOT_AVAILABLE,
        "SYSTEM_MEMORY_FREE" : NOT_AVAILABLE,
        "SYSTEM_MEMORY_AVAILABLE" : NOT_AVAILABLE,
        "SWAP_USAGE_USED" : NOT_AVAILABLE,
        "SWAP_USAGE_FREE" : NOT_AVAILABLE,

        # Oplog data
        "OPLOG_RATE_GB_PER_HOUR" : NOT_AVAILABLE,
        "OPLOG_MASTER_TIME" : NOT_AVAILABLE,

        # Disk data
        "DISK_PARTITION_SPACE_PERCENT_USED" : 80,

         # Query efficiency data
         "QUERY_TARGETING_SCANNED_PER_RETURNED" : NOT_AVAILABLE,
        "QUERY_TARGETING_SCANNED_OBJECTS_PER_RETURNED" : NOT_AVAILABLE
    }

    # Construct statistics
    for measurement in measurementsMap["measurements"]:

        logging.debug("Creating measurement map for measurement {}".format(measurement))
        data = measurementsMap["measurements"][measurement]["data"]
        rawData = measurementsMap["measurements"][measurement]["rawData"]

        measurementsMap["measurements"][measurement]["current"] = rawData[len(rawData) - 1]
        measurementsMap["measurements"][measurement]["avg"] = numpy.mean(rawData)       # TODO -- consider exponential moving avg
        measurementsMap["measurements"][measurement]["stdev"] = numpy.std(rawData)

        measurementThreshold = measurementThresholdsOfConcern[measurement]
        if NOT_AVAILABLE == measurementThreshold:
            measurementsMap["measurements"][measurement]["pctAbove80"] = NOT_AVAILABLE
        else:
            measurementsMap["measurements"][measurement]["pctAbove80"] = getPercentOfDataAboveThreshold(rawData, measurementThreshold)
        measurementsMap["measurements"][measurement]["pctGrowth"] = getDataGrowth(rawData)  # TODO -- consider checking growth (max / over start, like candlestick chart)

    slowQueryLogs = getSlowQueryLogsForLastHour(hostInfo["projectId"], hostInfo["hostId"])
    collscans = [ logEntry for logEntry in slowQueryLogs if isCollScan(logEntry) ]
    measurementsMap["measurements"]["COLLSCANS"] = {
        "current" : len( collscans ),
        "avg" : NOT_AVAILABLE,
        "stdev" : NOT_AVAILABLE,
        "pctAbove80" : NOT_AVAILABLE,
        "pctGrowth" : NOT_AVAILABLE,
    }
    return measurementsMap, collscans
    # return measurementsMap

def isCollScan(jsonLogLine):
    """
    Is Collection Scan

    :param jsonLogLine:
    :return:
    """
    try:
        return jsonLogLine["line"]["attr"]["planSummary"] == "COLLSCAN"
    except Exception as e:
        return False


def getDataGrowth(data):
    """
    Get Data Growth

    :param data:
    :return:
    """
    if data is None:
        return None
    if len(data) == 0:
        return None
    if data[0] == 0 and data[len(data)-1] == 0:
        return 0
    elif data[0] == 0:
        data[0] = 1
    growthPercent = 100*(float(data[len(data)-1]) / float(data[0]) - 1.0)
    return growthPercent

def getPercentOfDataAboveThreshold(data, threshold):
    """
    Get Percent of Data Above Threshold

    :param data:
    :param threshold:
    :return:
    """
    logging.info("Getting percentage of data above threshold {}".format(threshold))
    numDataPtsAboveThreshold = 0
    for dataPt in data:
        if dataPt > threshold:
            numDataPtsAboveThreshold+=1
    return 100*float(numDataPtsAboveThreshold)/float(len(data))


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

def setupArgs():
    """
    Setup args
    Parses all command line arguments to the script
    """
    parser = argparse.ArgumentParser(description='Conducts a health check on the specified host')
    parser.add_argument('--opsmgrUri',                  required=False, action="store", dest='opsMgrUri',               default='http:127.0.0.1:8080/', help='The uri of the ops manager instance under which this server will be managed.')
    parser.add_argument('--opsmgrapiuser',              required=False, action="store", dest='opsMgrApiUser',           default='',                     help='The api user for the designated ops manager instance')
    parser.add_argument('--opsmgrapikey',               required=False, action="store", dest='opsMgrApiKey',            default='',                     help='The api key for the designated ops manager instance')

    parser.add_argument('--hostName',                   required=False, action="store", dest='hostName',                default=None,                help='FQDN of the host being checked.')
    parser.add_argument('--showCollScans',              required=False, action="store_true", dest='showCollScans',      default=False,                help='Include flag to print collection scans.')
    parser.add_argument('--sortCollScansByDuration',    required=False, action="store_true", dest='sortCollScansByDuration', default=False,           help='Include flag to sort collection scans by duration.')
    parser.add_argument('--logFilePath',                required=False, action="store", dest='logFilePath',             default=False,           help='Path to slow query log file')
    parser.add_argument('--loglevel',                   required=False, action="store", dest='logLevel',                default='info',                 help='Log level. Possible values are [none, info, debug]')

    # TODO Command line arg for update/refresh
    return parser.parse_args()

def _configureLogger(logLevel):
    format = '%(message)s'
    if logLevel != 'INFO':
        format = '%(levelname)s: %(message)s'
    logLevel = logging.ERROR if (logLevel is None or logLevel.upper() == "NONE") else logLevel.upper()
    logging.basicConfig(format=format, level=logLevel)

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

def main():

    args = setupArgs()
    _configureLogger(args.logLevel)
    versionInfo = gitVersion()
    logging.info("Running {} v({}) last modified {}".format(scriptName, versionInfo['version'][:8], versionInfo['date']))
    # checkOsCompatibility()

    # Get Ops Manager connection
    global opsMgrConnector
    opsMgrConnector = OpsMgrConnector(args.opsMgrUri, args.opsMgrApiUser, args.opsMgrApiKey)

    # TODO -- add temporary project API key with project owner access; add current server's IP addr to whitelist
    conductHealthCheck(args.hostName, args.showCollScans, args.sortCollScansByDuration, args.logFilePath)
    # TODO -- remove temporary API key

#-------------------------------
if __name__ == "__main__":
    main()