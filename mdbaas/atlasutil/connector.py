import sys
sys.path.append('')
import requests
import logging
import json
import math
from requests.auth import HTTPDigestAuth

# Other constants
GROUPS_PER_PAGE = 100

# TODO -- ADD
MAX_GROUPS_PER_PAGE = 500

EXTERNAL_OPS_MANAGER_URL = "https://opsmanager.mongodb.com"

class AtlasConnector:
    """
    AtlasConnector class

    A wrapper class that sends requests to Atlas
    """
    def __init__(self, apiUser, apiKey):
        """
        Constructor to create an OpsMgrConnector object.

        :param opsMgrUri:   The uri to the target ops manager
        :param apiUser:     The api user with which we will authenticate to the target ops manager
        :param apiKey:      The api key for the api user with which we will authenticate to the target ops manager
        """
        self.atlasUri = "https://cloud.mongodb.com"
        self.staticDataUrl = "{}/static/".format(self.atlasUri)
        self.v1ApiURL = "{}/api/atlas/v1.0".format(self.atlasUri)
        self.v2ApiURL = "{}/api/atlas/v2.0".format(self.atlasUri)
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

    def construct_query_params(self, params_dict):
        """
        Construct Query Params

        :param params_dict:
        :return:
        """
        query_params = "?"
        for key in params_dict:
            if params_dict[key] is not None:
                query_params += f"{key}={params_dict[key]}&"
        query_params = query_params[0:len(query_params)-1]
        return query_params

    ############################################################################
    # Project Level Endpoints
    ############################################################################

    def get_project(self, group_id):
        """
        Get Project

        :param group_id:
        :return:
        """
        url = "{}/groups/{}".format(
            self.v1ApiURL,
            group_id
        )
        return self.get(url)



    ############################################################################
    # Cluster Level Endpoints
    ############################################################################

    def get_clusters_for_project(self, group_id):
        """
        Get Clusters For Project

        :param group_id:
        :return:
        """
        url = "{}/groups/{}/clusters".format(
            self.v1ApiURL,
            group_id
        )
        return self.get(url)


    ############################################################################
    # Process Level Endpoints
    ############################################################################

    def get_processes_for_project(self, group_id):
        """
        Get Processes For Project

        :param group_id:
        :return:
        """
        url = "{}/groups/{}/processes".format(
            self.v1ApiURL,
            group_id
        )
        return self.get(url)



    ############################################################################
    # Performance Advisor Endpoints
    ############################################################################

    def get_namespaces_for_host(self, group_id, process_id):
        """
        Get Namespaces for Host

        :param host_id:
        :return:
        """
        url = "{}/groups/{}/processes/{}/performanceAdvisor/namespaces".format(
            self.v1ApiURL,
            group_id,
            process_id
        )
        return self.get(url)

    def get_slow_queries(self, group_id, process_id):
        """
        Get Slow Queries

        :param host_id:
        :return:
        """
        url = "{}/groups/{}/processes/{}/performanceAdvisor/slowQueryLogs".format(
            self.v1ApiURL,
            group_id,
            process_id
        )
        return self.get(url)

    def get_suggested_indexes(self, group_id, process_id):
        """
        Get Suggested Indexes

        :param group_id:
        :param process_id:
        :return:
        """
        url = "{}/groups/{}/processes/{}/performanceAdvisor/suggestedIndexes".format(
            self.v1ApiURL,
            group_id,
            process_id
        )
        return self.get(url)

    ############################################################################
    # Measurements Endpoint
    ############################################################################

    def get_measurements_for_process_for_period(self, group_id, process_id, granularity=None, period=None):
        """
        Get Suggested Indexes

        https://cloud.mongodb.com/api/atlas/v1.0/groups/{groupId}/processes/{processId}/measurements

        :param group_id:
        :param process_id:
        :return:
        """
        url = "{}/groups/{}/processes/{}/measurements{}".format(
            self.v1ApiURL,
            group_id,
            process_id,
            self.construct_query_params({"granularity" : granularity, "period" : period})
        )
        return self.get(url)

    def get_measurements_for_process_for_time_range(self, group_id, process_id, granularity=None, start=None, end=None):
        """
        Get Suggested Indexes

        https://cloud.mongodb.com/api/atlas/v1.0/groups/{groupId}/processes/{processId}/measurements

        :param group_id:
        :param process_id:
        :return:
        """
        if (start is None and end is None) or (start is not None and end is not None):
            url = "{}/groups/{}/processes/{}/measurements{}".format(
                self.v1ApiURL,
                group_id,
                process_id,
                self.construct_query_params({"granularity" : granularity, "start" : start, "end" : end})
            )
        else:
            raise Exception("'start' and 'end' must both be null or non-null")
        return self.get(url)



