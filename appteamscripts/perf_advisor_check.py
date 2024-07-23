#!/usr/bin/python
import operator
import platform
import sys

import requests

sys.path.append('../appteamscripts')
import os
import logging
import subprocess
import argparse
import json
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

from mdbaas.atlasutil import AtlasConnector

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


########################################################################################################################
# Base Methods
########################################################################################################################

def create_perf_report(report_data, max_slow_queries):
    """
    Create Perf Report

    :param report_data:
    :return:
    """
    perf_advisor_heading = f"<h1>Perf Advisor Report for Ops Mgr Project {report_data['projectName']} ({report_data['projectId']})</h1>"
    cluster_html = create_cluster_html_data(report_data, max_slow_queries)

    header = ("<!DOCTYPE html>"
              "<html>"
              "<head>"
              "<style>"
              "table, th, td {"
              " border: 1px solid black;"
              "})"
              "</style>"
              "</head>")

    html = (f"{header}"
            f"<body>"
                f"{perf_advisor_heading}"
                    f"{cluster_html}"
            f"</body>")

    html_file_name = "reports/perfAdvisorReport.html"
    with open(html_file_name, 'w') as f:
        f.write(html)

def create_metrics_plots_for_cluster(cluster_data):
    """
    Create Metrics Plots

    :param cluster_data:
    :return:
    """
    for measurement in cluster_data["metrics"]["measurements"]:

        # Plot the chart
        x = [d["timestamp"] for d in measurement["dataPoints"]]
        y = [d["value"] for d in measurement["dataPoints"]]
        y = np.array(y)
        p = plt.plot(x, y)

        # Y tickers
        plt.ylabel("{} ({})".format(measurement["name"], measurement["units"]))

        # X Tickers
        plt.xlabel("Date")
        ax = plt.gca()
        # num_xticks = 5
        new_x = [ x[i] if i%100 == 0 else "" for i in range(len(x))]
        ax.set_xticks(new_x)
        plt.xticks(rotation=30)

        plt.subplots_adjust(left=0.30)
        plt.subplots_adjust(bottom=0.30)
        plt.show()

        # plot_file_name = "{}.{}"
        # plt.savefig(plot_file_name)
    # return plots



def create_cluster_html_data(report_data, max_slow_queries):
    """
    Create Cluster HTML Data
    :return:
    """
    MAX_NUM_LOG_ENTRIES_PER_SHAPE = 5
    html = ""
    query_shape_num = 0
    for cluster_data in report_data["clusters"]:

        # Create chart
        plots = create_metrics_plots_for_cluster(cluster_data)


        # Index Suggestions


        # Slow queries
        sample_log_entry = None
        slow_query_html = ""
        for slow_query_shape in cluster_data["slowQueries"]:
            log_entries_html = ""
            for log_entry in slow_query_shape["logs"][0:MAX_NUM_LOG_ENTRIES_PER_SHAPE]:
                log_entries_html += (f"<p>{str(log_entry)}</p>"
                                     f"<br></br>")
                sample_log_entry = log_entry

            log_entries_html += (f"<br></br>"
                                f"<span style='white-space: pre-line'></span>")

            query_shape_num += 1
            query_shape = sample_log_entry['logData']['attr']['command']['filter']
            slow_query_html += (f"<h4>Query Shape {query_shape_num}: {query_shape}</h4>"
                                f"<details>"
                                f"<table>"
                                f"<tr>"
                                    f"<th>Key</th>"
                                    f"<th>Value</th>"
                                f"</tr>"
                                f"<tr>"
                                    f"<td>MongoDB Namespace</td>"
                                    f"<td>{sample_log_entry['namespace']}</td>"
                                f"</tr>"
                                f"<tr>"
                                    f"<td>Query Hash</td>"
                                    f"<td>{slow_query_shape['query_hash']}</td>"
                                f"</tr>"
                                f"<tr>"
                                    f"<td>Query Predicate</td>"
                                    f"<td>{query_shape}</td>"
                                f"</tr>"
                                f"<tr>"
                                    f"<td>Number Slow Logs</td>"
                                    f"<td>{slow_query_shape['numLogs']}</td>"
                                f"</tr>"
                                f"<tr>"
                                    f"<td>Avg Duration Millis</td>"
                                    f"<td>{slow_query_shape['avgDurationMillis']}</td>"
                                f"</tr>"
                                f"</table>"
                                f"<h5>Logs:</h5>"
                                f"{log_entries_html}"
                                f"</details>")

        # Create header and general table
        html_for_cluster = (f"<h2>Report for {cluster_data['clusterName']}</h2>"
                f"<h3> General Data: </h3>"
                f"<table>"
                    f"<tr>"
                        f"<th>Key</th>"
                        f"<th>Value</th>"
                    f"</tr>"
                    f"<tr>"
                        f"<td>Report Date</td>"
                        f"<td>{datetime.utcnow()}</td>"
                    f"</tr>"
                    f"<tr>"
                        f"<td>MDB Version</td>"
                        f"<td>{cluster_data['mdbVersion']}</td>"
                    f"</tr>"
                f"</table>"
                f"<br></br>"
                f"<h3>Top {min(max_slow_queries, len(cluster_data['slowQueries']))} Slow Query Shapes: </h3>"
                    f"<details><summary>Slow Queries for {cluster_data['clusterName']}</summary>"
                        f"{slow_query_html}"
                    f"</details>"
                f"<br></br>"
                f"<h3>Suggested Indexes</h3>"
                    f"<details><summary>Suggested Indexes for {cluster_data['clusterName']}</summary>"
                        f"{slow_query_html}"
                    f"</details>")

        html += html_for_cluster

    return html

def write_logs_to_file(group_id, cluster_name, logs):
    """
    Write Logs to File

    :param group_id:
    :param cluster_name:
    :param logs:
    :return:
    """
    file_name = "reports/logs/slowQueries.{}.{}.log".format(
        group_id,
        cluster_name
    )
    logging.info("Writing logs to file {}".format(file_name))
    log_str = "\n".join(str(log_entry) for log_entry in logs)
    with open(file_name, "w") as f:
        f.write(log_str)

def collect_perf_advisor_data_for_project(groupId, max_num_queries=1000):
    """
    Collect Perf Advisor Data for Project

    :param project:
    :return:
    """
    project_info = atlasConnector.get_project(groupId)

    report_data = {
        "projectName" : project_info["name"],
        "projectId" : groupId,
        "clusters" : get_cluster_info_for_all_clusters(groupId)
    }

    processes_in_project = atlasConnector.get_processes_for_project(groupId)
    for process in processes_in_project["results"]:
        logging.debug("Getting performance advisor data for process: {}".format(json.dumps(process, indent=4)))
        for cluster in report_data["clusters"]:
            if process["userAlias"] in cluster["hosts"]:
                cluster["slowQueries"].extend(get_slow_queries(groupId, process, None))
                cluster["suggestedIndexes"].extend(get_suggested_indexes(groupId, process))
                write_logs_to_file(groupId, process["userAlias"], cluster["slowQueries"])
                if "REPLICA_PRIMARY" == process["typeName"]:
                    cluster["metrics"] = get_metrics_for_process(groupId, process)

    for cluster in report_data["clusters"]:
        cluster["slowQueries"] = aggregate_and_sort_queries(cluster["slowQueries"], max_num_queries)
        cluster["suggestedIndexes"] = aggregate_suggested_indexes(cluster["suggestedIndexes"])
        # sortedSlowQueries = sorted(cluster["slowQueries"], key=lambda x:x['logData']['attr']['durationMillis'], reverse=True)
        # cluster["slowQueries"] = sortedSlowQueries[0:max_num_queries]

    return report_data

def aggregate_suggested_indexes(suggested_indexes):
    """
    Aggregate Suggested Indexes

    :param suggested_indexes:
    :return:
    """
    aggregated_indexes = {
    }
    for suggested_index in suggested_indexes:
        if suggested_index["namespace"] not in aggregated_indexes:
            aggregated_indexes[suggested_index["namespace"]] = {
            }
        if str(suggested_index["index"]) not in aggregated_indexes[str(suggested_index["namespace"])]:
            aggregated_indexes[suggested_index["namespace"]][str(suggested_index["index"])] = suggested_index

    indexes = []
    for namespace in aggregated_indexes:
        for index in aggregated_indexes[namespace]:
            indexes.append(aggregated_indexes[namespace][index])
    return indexes

def aggregate_and_sort_queries(slow_queries, max_num_queries=None):
    """
    Aggregate And Sort Queries

    :param slow_queries:
    :param max_num_queries:
    :return:
    """
    aggregated_queries = {
    }
    for slow_query in slow_queries:
        if "queryHash" not in slow_query["logData"]["attr"]:
            logging.debug("Skipping log entry as it does not have query hash")
            continue

        # Query Hash
        logging.debug("Found log entry with query hash")
        query_hash = slow_query["logData"]["attr"]["queryHash"]
        if query_hash not in aggregated_queries:
            aggregated_queries[query_hash] = {
                "query_hash" : query_hash,
                "logs" : [
                    slow_query
                ],
                "numLogs" : 1,
                "avgDurationMillis" : slow_query['logData']['attr']['durationMillis']
            }
        else:
            avgDurationMillis = aggregated_queries[query_hash]["avgDurationMillis"]
            numLogs = aggregated_queries[query_hash]["numLogs"]
            logs = aggregated_queries[query_hash]["logs"]
            logs.append(slow_query)
            aggregated_queries[query_hash]["logs"] = logs
            aggregated_queries[query_hash]["numLogs"] = numLogs+1
            aggregated_queries[query_hash]["avgDurationMillis"] = (avgDurationMillis * numLogs + slow_query['logData']['attr']['durationMillis'])/(numLogs+1)

    # Get slowest query shapes
    query_shapes = [ aggregated_queries[h] for h in aggregated_queries ]
    sorted_query_shapes = sorted(query_shapes, key=lambda x:x["avgDurationMillis"], reverse=True)
    if max_num_queries is not None:
        return sorted_query_shapes[0:max_num_queries]
    return sorted_query_shapes

def get_cluster_info_for_all_clusters(group_id):
    """
    Get Cluster Info For All Clusters

    :param group_id:
    :return:
    """
    clusterData = []
    clusters = atlasConnector.get_clusters_for_project(group_id)
    for cluster in clusters["results"]:
        logging.debug("Getting info for cluster {}".format(json.dumps(cluster, indent=4)))
        clusterInfo = {
            "clusterName": cluster["name"],
            "mdbVersion": cluster["mongoDBVersion"],
            "hosts": get_cluster_hosts(cluster),
            "slowQueries" : [],
            "suggestedIndexes" : [],
            "metrics" : []
        }
        clusterData.append(clusterInfo)
    return clusterData

def get_cluster_hosts(cluster):
    """
    Get Cluster Hosts

    :param cluster:
    :return:
    """
    cluster_conn_str_parts = cluster["connectionStrings"]["standard"].split("/")
    cluster_conn_str_parts = cluster_conn_str_parts[2].split(",")
    hosts = []
    for cluster_conn_str_part in cluster_conn_str_parts:
        cluster_proc_parts = cluster_conn_str_part.split(":")
        hosts.append(cluster_proc_parts[0])
    return hosts

def get_slow_queries(group_id, process, max_num_queries=1000):
    """
    Get Slow Queries

    :param process:
    :param groupId:
    :return:
    """
    slow_queries = atlasConnector.get_slow_queries(group_id, process["id"])
    for slow_query in slow_queries["slowQueries"]:
        process_id_parts = process["id"].split(":")
        port = process_id_parts[1]
        slow_query["processName"] = "{}:{}".format(process["userAlias"], port)
        slow_query["logData"] = json.loads(slow_query["line"])

    sorted_queries = sorted(slow_queries["slowQueries"], key=lambda x:x['logData']['attr']['durationMillis'], reverse=True)
    if max_num_queries is None:
        return sorted_queries
    return sorted_queries[0:max_num_queries]

def get_suggested_indexes(group_id, process):
    """
    Get Suggested Indexes

    :param group_id:
    :param process_id:
    :return:
    """
    suggested_indexes = atlasConnector.get_suggested_indexes(group_id, process["id"])
    for suggested_index in suggested_indexes["suggestedIndexes"]:
        process_id_parts = process["id"].split(":")
        port = process_id_parts[1]
        suggested_index["processName"] = "{}:{}".format(process["userAlias"], port)
        print("{}".format(suggested_index))
    return suggested_indexes["suggestedIndexes"]


def get_metrics_for_process(group_id, process):
    """
    Get Metrics for Process

    :param group_id:
    :param process:
    :return:
    """
    metrics = atlasConnector.get_measurements_for_process_for_period(group_id, process["id"], granularity="PT1M", period="P2D")
    return metrics

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
    parser.add_argument('--atlasGroupId',       required=False, action="store", dest='atlasGroupId',    default=None, help='The id of the Atlas project/group in which the cluster is contained ')
    parser.add_argument('--atlasApiUser',       required=False, action="store", dest='atlasApiUser',   default='',   help='The API public key with which to access the Atlas API for the project/group')
    parser.add_argument('--atlasApiKey',        required=False, action="store", dest='atlasApiKey',    default='',   help='The API private key with which to access the Atlas API for the project/group')
    parser.add_argument('--scale',              required=False, action="store", dest='scale',           default='bytes',                help='Scale in which to view metrics. One of {}'.format(VALID_SCALES.keys()))

    # parser.add_argument('--projectName',              required=False, action="store", dest='projectName',       default=None,                help='The full name of the project.')
    # parser.add_argument('--projectId',                  required=False, action="store", dest='projectId',       default=None,                help='The id of the project in ops manager.')
    # parser.add_argument('--projectAppName',           required=False, action="store", dest='projectAppName',    default=None,                help='The Application pneumonic.')
    # parser.add_argument('--projectAppEnv',            required=False, action="store", dest='projectAppEnv',     default=None,                help='The application environment. One of ' + APPLICATION_ENVS.__str__() )

    parser.add_argument('--fileName',     required=False, action="store", dest='fileName',          default=None,                 help='Path of the file to write to; if not used, will write to standard out')
    parser.add_argument('--verifycerts',  required=False, action="store", dest='verifycerts',       default=True,                 help='Whether or not to verify TLS certs on HTTPS requests')
    parser.add_argument('--loglevel',     required=False, action="store", dest='logLevel',          default='info',                 help='Log level. Possible values are [none, info, verbose]')

    # TODO Command line arg for update/refresh
    return parser.parse_args()

def _configureLogger(logLevel, fileName=None):
    format = '%(message)s'
    if logLevel != 'INFO':
        format = '%(levelname)s: %(message)s'
    if fileName is not None:
        logging.basicConfig(format=format, level=logLevel.upper(), filename="../scripts/debug.log")
    logging.basicConfig(format=format, level=logLevel.upper())

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
    global atlasConnector
    atlasConnector = AtlasConnector(args.atlasApiUser, args.atlasApiKey)
    report_data = collect_perf_advisor_data_for_project(args.atlasGroupId, 100)
    create_perf_report(report_data, 100)

#-------------------------------
if __name__ == "__main__":
    main()