#!/usr/bin/python
import platform
import sys

sys.path.append('.')
import os
import logging
import subprocess
import argparse
from prettytable import PrettyTable

from mdbaas.opsmgrutil import OpsMgrConnector

# Script metadata
version = "1.0.0"
revdate = "05-13-2024"
scriptName = "setpassword"
scriptNameFull = scriptName + ".py"
completionStr = "\n====================================================================\n                      Completed " + scriptName + "!!!!              \n ====================================================================\n"

BYTES_IN_GB = 1024 * 1024 * 1024
SECONDS_IN_HOUR = 60 * 60
APPLICATION_ENVS = ["PROD", "UAT", "DEV"]


########################################################################################################################
# Password Rules
########################################################################################################################

def listProjectsForOrg(orgId):
    """
    List Projects for Org

    :return:
    """
    table = PrettyTable()
    table.field_names = [ "Project Name", "Project Id" ]

    groups = opsMgrConnector.getAllGroupsWithinOrg(orgId, verify=False)
    for project in groups["results"]:
        table.add_row([
            project["name"],
            project["id"]
        ])
    print(table.get_string())

########################################################################################################################
# Base Methods
########################################################################################################################

def checkOsCompatibility():
    """
    Check OS Compatibility

    Ensures that the script is being run on a linux machine
    """
    opSys = platform.system()
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
    parser.add_argument('--opsmgrUri', required=False, action="store", dest='opsMgrUri', default='http:127.0.0.1:8080/',
                        help='The uri of the ops manager instance under which this server will be managed.')
    parser.add_argument('--opsmgrapiuser', required=False, action="store", dest='opsMgrApiUser', default='',
                        help='The api user for the designated ops manager instance')
    parser.add_argument('--opsmgrapikey', required=False, action="store", dest='opsMgrApiKey', default='',
                        help='The api key for the designated ops manager instance')

    parser.add_argument('--orgId', required=False, action="store", dest='orgId', default=None,
                        help='The id of the project')

    parser.add_argument('--loglevel', required=False, action="store", dest='logLevel', default='info',
                        help='Log level. Possible values are [none, info, verbose]')

    # TODO Command line arg for update/refresh
    return parser.parse_args()


def _configureLogger(logLevel):
    format = '%(message)s'
    if logLevel != 'INFO':
        format = '%(levelname)s: %(message)s'
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
        out = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env).communicate()[0]
        return out

    commitDate = "N/A"
    gitVersion = "Unknown"
    try:
        # Get last commit version
        out = _getGitCommitSha(['git', 'rev-parse', 'HEAD'])
        gitVersion = out.strip().decode('ascii')

        # Get last commit date
        out = _getGitCommitSha(['git', 'show', '-s', '--format=%ci'])
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
    _configureLogger(args.logLevel.upper())
    versionInfo = gitVersion()
    logging.info(
        "Running {} v({}) last modified {}".format(scriptName, versionInfo['version'][:8], versionInfo['date']))
    # checkOsCompatibility()

    # Get Ops Manager connection
    global opsMgrConnector
    opsMgrConnector = OpsMgrConnector(args.opsMgrUri, args.opsMgrApiUser, args.opsMgrApiKey)
    listProjectsForOrg(args.orgId)


# -------------------------------
if __name__ == "__main__":
    main()