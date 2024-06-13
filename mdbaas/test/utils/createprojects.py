#!/usr/bin/python
import platform
import sys

sys.path.append('.')
import os
import logging
import subprocess
import argparse

from mdbaas.opsmgrutil import OpsMgrConnector

# Script metadata
version = "1.0.0"
revdate = "06-03-2024"
scriptName = "createprojects"
scriptNameFull = scriptName + ".py"
completionStr = "\n====================================================================\n                      Completed " + scriptName + "!!!!              \n ====================================================================\n"

BYTES_IN_GB = 1024 * 1024 * 1024
SECONDS_IN_HOUR = 60 * 60
APPLICATION_ENVS = ["PROD", "UAT", "DEV"]


########################################################################################################################
# Main Substantive Methods
########################################################################################################################
def requestManualConfirmationFromUser(prompt, requiredResp):
    """
    Request Manual Confirmation from User

    :param prompt:
    :param requiredResp:
    :return:
    """
    resp = input(prompt)
    respInvalid = (resp != requiredResp)
    while respInvalid:
        print("Response is not valid. Please type {{}} to proceed or CTRL + C to exit".format(requiredResp))
        resp = input(prompt)
        respInvalid = (resp != requiredResp)


def deleteProjectsInOrg(orgId, numProjects, startProjNum=0):
    """
    Delete Projects in Org

    :param orgId:
    :param numProjects:
    :param startProjNum:
    :return:
    """
    global opsMgrConnector
    projectsToDelete = []
    endProjNum = startProjNum + numProjects
    for i in range(startProjNum, endProjNum):
        projName = "project{}".format(i)
        projectsToDelete.append(projName)

    requiredResp = "Y"
    requestManualConfirmationFromUser(
        "Confirm you would like to delete projects project{} - project{}: Press {} to proceed...".format(startProjNum, endProjNum, requiredResp),
        requiredResp
    )

    groupsInOrg = opsMgrConnector.getGroupsWithinOrganization(orgId)
    for group in groupsInOrg["results"]:
        if group["name"] in projectsToDelete:
            resp = opsMgrConnector.removeGroup(group["id"])
            logging.info("Deleting group with name {} and id {}".format(group["name"], group["id"]))

    logging.info("Done")

def createProjectsInOrg(orgId, numProjects, startProjNum=0):
    """
    Create Projects in Org

    :param orgId:
    :param numProjects:
    :return:
    """
    global opsMgrConnector
    for i in range(startProjNum, startProjNum + numProjects):
        projName = "project{}".format(i)
        logging.info("Creating project {} in org with id {}".format(projName, orgId))
        opsMgrConnector.addGroup(projName, orgId)
    logging.info("Done")


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
                        help='The id of the organization in ops manager.')

    parser.add_argument('--numProjects', required=False, action="store", dest='numProjects', default=20,
                        help='The number of projects to create.')

    parser.add_argument('--startProjNum', required=False, action="store", dest='startProjNum', default=0,
                        help='The numerical id of first project to create. This is used so that you can create projects starting with the last project created in the most recent run of this app')

    parser.add_argument('--cleanup', required=False, action="store_true", dest='cleanup', default=False,
                        help='Include this flag to delete the projects in the specified range')

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
    if args.cleanup is not None and bool(args.cleanup):
        deleteProjectsInOrg(args.orgId, int(args.numProjects), int(args.startProjNum))
    else:
        createProjectsInOrg(args.orgId, int(args.numProjects), int(args.startProjNum))

# -------------------------------
if __name__ == "__main__":
    main()