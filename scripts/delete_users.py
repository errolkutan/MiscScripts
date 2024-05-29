#!/usr/bin/python
import platform
import sys

sys.path.append('.')
import os
import logging
import subprocess
import argparse
import json
import string
from getpass import getpass

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

class PasswordRule():

    def __init__(self):
        self.name = "PasswordRule"
        self.desc = "Generic abstract password rule"

    def validate(self, password):
        return {"passed": False}


class LongPasswordRule():

    def __init__(self, numChars):
        super().__init__()
        self.name = "LongPasswordRule"
        self.numChars = numChars
        self.desc = "Password must be at least {} chars long".format(self.numChars)
        self.validationErrMsg = "{} rule failed: Password must be at least {} chars long".format(self.name,
                                                                                                 self.numChars)

    def validate(self, password):
        logging.debug(f'Attempting to validate password according to rule {self.name}')
        resp = {
            "passed": len(password) >= self.numChars
        }
        return resp


class UppercaseCharPasswordRule():

    def __init__(self, numCharsMustSatisfyRule):
        super().__init__()
        self.name = "UppercaseCharPasswordRule"
        self.numCharsMustSatisfyRule = numCharsMustSatisfyRule
        self.desc = "Password should have at least {} chars that are uppercase".format(self.numCharsMustSatisfyRule)
        self.validationErrMsg = "{} rule failed: Password should have at least {} chars that are uppercase".format(
            self.name,
            self.numCharsMustSatisfyRule)

    def validate(self, password):
        logging.debug(f'Attempting to validate password according to sub-rule {self.name}')
        uppercaseChars = ''.join(c for c in password if c.isupper())
        resp = {
            "passed": len(uppercaseChars) >= self.numCharsMustSatisfyRule
        }
        return resp


class LowercaseCharPasswordRule():

    def __init__(self, numCharsMustSatisfyRule):
        super().__init__()
        self.name = "LowercaseCharPasswordRule"
        self.numCharsMustSatisfyRule = numCharsMustSatisfyRule
        self.desc = "Password should have at least {} chars that are lowercase".format(self.numCharsMustSatisfyRule)
        self.validationErrMsg = "{} rule failed: Password should have at least {} chars that are lowercase".format(
            self.name,
            self.numCharsMustSatisfyRule)

    def validate(self, password):
        logging.debug(f'Attempting to validate password according to sub-rule {self.name}')
        lowercaseChars = ''.join(c for c in password if c.islower())
        resp = {
            "passed": len(lowercaseChars) >= self.numCharsMustSatisfyRule
        }
        return resp


class SpecialCharPasswordRule():

    def __init__(self, numCharsMustSatisfyRule):
        super().__init__()
        self.name = "SpecialCharPasswordRule"
        self.numCharsMustSatisfyRule = numCharsMustSatisfyRule
        self.specialChars = ['$', '#', '@', '%', '!', '&']
        self.desc = "Password should have at least {} special characters ({})".format(self.numCharsMustSatisfyRule,
                                                                                      self.specialChars)
        self.validationErrMsg = "{} rule failed: Password should have at least {} special characters ({})".format(
            self.name,
            self.numCharsMustSatisfyRule,
            self.specialChars)

    def validate(self, password):
        logging.debug(f'Attempting to validate password according to sub-rule {self.name}')
        specialChars = ''.join(c for c in password if c in self.specialChars)
        resp = {
            "passed": len(specialChars) >= self.numCharsMustSatisfyRule
        }
        return resp


class AlphaNumericCharPasswordRule():

    def __init__(self, numCharsMustSatisfyRule):
        super().__init__()
        self.name = "AlphanumericCharPasswordRule"
        self.numCharsMustSatisfyRule = numCharsMustSatisfyRule
        self.desc = "Password should have at least {} alphanumeric characters".format(self.numCharsMustSatisfyRule)
        self.validationErrMsg = "{} rule failed: Password should have at least {} alphanumeric characters".format(
            self.name,
            self.numCharsMustSatisfyRule)

    def validate(self, password):
        logging.debug(f'Attempting to validate password according to sub-rule {self.name}')
        alphabeticalChars = ''.join(c for c in password if c in string.ascii_letters)
        numericalChars = ''.join(c for c in password if c in string.digits)
        resp = {
            "passed": (len(alphabeticalChars) >= self.numCharsMustSatisfyRule and len(
                numericalChars) >= self.numCharsMustSatisfyRule)
        }
        return resp


class CharacterCategoriesPasswordRule():

    def __init__(self, numSubRulesMet):
        super().__init__()
        self.name = "CharacterCategoriesPasswordRule"
        self.numSubRulesMet = numSubRulesMet
        self.subRules = [
            UppercaseCharPasswordRule(1),
            LowercaseCharPasswordRule(1),
            SpecialCharPasswordRule(1),
            AlphaNumericCharPasswordRule(1)
        ]
        self.desc = "Password must meet at least {}  of the following subrules: {} ".format(self.numSubRulesMet,
                                                                                            [r.name for r in
                                                                                             self.subRules])
        self.validationErrMsg = "{} rule failed: Password must meet at least {}  of the following subrules: {}".format(
            self.name,
            self.numSubRulesMet, [r.name for r in self.subRules])

    def validate(self, password):
        logging.debug(f'Attempting to validate password according to rule {self.name}')
        numCategoriesWhereCriteriaSatisfied = 0
        subRulesPassedMap = {}
        for subrule in self.subRules:
            subRuleResp = subrule.validate(password)
            subRulesPassedMap[subrule.name] = subRuleResp["passed"]
            numCategoriesWhereCriteriaSatisfied += 1 if subRuleResp["passed"] else 0
        resp = {
            "passed": numCategoriesWhereCriteriaSatisfied >= self.numSubRulesMet,
            "subRulesMap": subRulesPassedMap
        }
        return resp


def captureAndValidatePassword(passwordRules, userName):
    """
    Capture and Validate Password

    :return:
    """
    passwordValid = False
    enteredPass = None
    while not passwordValid:
        # enteredPass = input(f'Please enter the password for user {userName}')
        enteredPass = getpass(f'Please enter the password for user {userName}')

        passwordValid = True

        # Must be 16+ chars, at least one char from 3+ of the following categories
        # 1) Uppercase
        # 2) Lowercase
        # 3) Alphanumeric
        # 4) Special chars
        for rule in passwordRules:
            ruleValidationResp = rule.validate(enteredPass)
            passedRule = ruleValidationResp["passed"]
            passwordValid = passwordValid and passedRule
            if not passedRule:
                print(rule.validationErrMsg)
                if "subRulesMap" in ruleValidationResp:
                    print("Sub-rule details: {}".format(json.dumps(
                        ruleValidationResp["subRulesMap"], indent=4
                    )))
                break

        if not passwordValid:
            print("Please enter a new password...")

    print("Password passed all checks")
    return enteredPass


def capturePassword():
    """
    Capture and Validate Password

    :return:
    """
    enteredPass = getpass(f'Please enter the password for automation agent')
    return enteredPass

def setPassword(projectId, newPass):
    """

    :param projectId:
    :param userName:
    :param dbName:
    :param newPass:
    :param omUrl:
    :return:
    """
    logging.info("Setting password for automation agent user")
    global opsMgrConnector

    # Get the existing user
    automationConfig = opsMgrConnector.getAutomationConfig(projectId, verifyBool=False)
    auth = automationConfig["auth"]
    auth["newAutoPwd"] = newPass

    # TODO -- wait until automation complete
    resp = opsMgrConnector.putAutomationConfig(projectId, automationConfig, verifyBool=False)
    logging.info("Got response: {}".format(json.dumps(resp, indent=4)))

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

    parser.add_argument('--projectName', required=False, action="store", dest='projectName', default=None,
                        help='The full name of the project.')
    parser.add_argument('--projectId', required=False, action="store", dest='projectId', default=None,
                        help='The id of the project in ops manager.')
    # parser.add_argument('--projectAppName',           required=False, action="store", dest='projectAppName',    default=None,                help='The Application pneumonic.')
    # parser.add_argument('--projectAppEnv',            required=False, action="store", dest='projectAppEnv',     default=None,                help='The application environment. One of ' + APPLICATION_ENVS.__str__() )

    parser.add_argument('--dryRun', required=False, action="store_true", dest='dryRun', default=False,
                        help='Include this flag to test out the password without actually creating it.')
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

    config = {
        # "projectAppEnv"  : args.projectAppEnv,
        # "projectAppName" : args.projectAppName,
        "projectId": args.projectId,
        "projectName": args.projectName
    }


    validatedPass = capturePassword()
    dryRun = False if args.dryRun is None else args.dryRun
    if not dryRun:
        logging.info("Setting automation agent password")
        setPassword(args.projectId, validatedPass)
    else:
        logging.info("DRY-RUN: Not Setting Password...")


# -------------------------------
if __name__ == "__main__":
    main()