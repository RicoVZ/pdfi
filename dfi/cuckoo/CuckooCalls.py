import requests
import urllib2
import logging
import json
import sys

from dfi.Config import Config

logger = logging.getLogger(__name__)


class CuckooCalls(object):

    CONNECTION_TESTED = False

    def __init__(self):
        self.CUCKOO_API_ADDRESS = "%s:%s" % (Config.CUCKOO_SRV_IP,
                                             Config.CUCKOO_API_PORT)
        self._cuckoo_response = None

        if not CuckooCalls.CONNECTION_TESTED:
            self._test_connection()

    def _test_connection(self):

        CuckooCalls.CONNECTION_TESTED = True
        try:
            self.get_cuckoo_machines_amount()
        except Exception as e:
            logger.error("Error connecting to the Cuckoo server: %s", e)
            sys.exit(1)

    def _do_api_call(self, call):
        """Do http API call. Only specify the actual call. So tasks/list would
        be an example"""

        self._cuckoo_response = None
        url = "http://%s/%s" % (self.CUCKOO_API_ADDRESS, call)

        try:
            self._cuckoo_response = urllib2.urlopen(url)
        except urllib2.HTTPError as he:
            raise CuckooCallError(he.code, "%s" % he)

        if not self._cuckoo_response.getcode() == 200:
            raise CuckooCallError(self._cuckoo_response.getcode(),
                                  "Expected 200. Received HTTP: %s"
                                  % self._cuckoo_response.getcode())

    def download_cuckcoo_report(self, cuckoo_id):

        call = "tasks/report/%s" % cuckoo_id

        logger.debug("Download Cuckoo report with ID: %s", cuckoo_id)

        self._do_api_call(call)

        cuckoo_report_json = json.loads(self._cuckoo_response.read())
        return cuckoo_report_json

    def submit_to_cuckoo(self, filepath):
        """
        Submits the specified binary to the Cuckoo server
        with the default parameter: 'options: json.calls=0'

        Returns Cuckoo task id if successful
        """

        call = "tasks/create/file"
        url = "http://%s/%s" % (self.CUCKOO_API_ADDRESS, call)
        parameters = {
            "options": "json.calls=0"
        }
        logger.debug("Submitting binary to Cuckoo")
        with open(filepath, "rb") as sample:
            multipart_file = {"file": sample}
            response = requests.post(url, files=multipart_file,
                                     data=parameters)

            if not response.status_code == 200:
                raise CuckooCallError("Binary submission failed! Got status: HTTP %s" % response.status_code)

            json_response = response.json()
            return json_response["task_id"]

    def get_status_cuckoo_id(self, cuckoo_id):
        """Tries to get the Cuckoo status for a Cuckoo id"""

        call = "tasks/view/%s" % cuckoo_id

        logger.debug("Getting status for Cuckoo id: %s", cuckoo_id)
        self._do_api_call(call)
        status_report = json.loads(self._cuckoo_response.read())

        if not "status" in status_report["task"]:
            raise CuckooCallError("status key not in JSON response")

        return status_report["task"]["status"]

    def get_cuckoo_machines_amount(self):
        """ Returns the amount of machines available in Cuckoo """

        call = "machines/list"
        url = "http://%s/%s" % (self.CUCKOO_API_ADDRESS, call)

        logger.debug("Getting amount of VMs Cuckoo has")
        self._do_api_call(call)

        machine_list = json.loads(self._cuckoo_response.read())

        if not "machines" in machine_list:
            raise CuckooCallError("machines key missing in machine list JSON"
                                  "response")

        return len(machine_list["machines"])


class CuckooCallError(Exception):
    def __init__(self, http_code, value):
        
        super(CuckooCallError, self).__init__(value)
        self.http_code = http_code
