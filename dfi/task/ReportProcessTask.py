import logging
import time
import sys
import setproctitle

from dfi.cuckoo.CuckooCalls import CuckooCalls, CuckooCallError
from dfi.cuckoo.CuckooReport import CuckooReport
from dfi.database.ESManager import ESManager

logger = logging.getLogger(__name__)
setproctitle.setproctitle("ReportProcessTask")


class ReportProcessTask(object):

    WAIT_TIME_UNFINISHED = 30
    MAX_WAIT_TIME = 300
    PROCESS_REPORTS = True

    def __init__(self):
        self._wait_times = {}
        self._tasks_pending = 0
        self._sub_queue = []
        self._remove_queue = []

        self.es = ESManager()

    def _handle_status_check_failed(self, cuckoo_id, exception):
        '''Override this with code for Cuckoo status check failure
        failure'''

        if exception.http_code == 404:
            logging.warning("Cannot get status for id: %s. It does not exist",
                          cuckoo_id)
            self._remove_queue.append(cuckoo_id)

        else:
            logging.error("Cuckoo task (%s) status check failed: %s. Waiting 2 min",
                          cuckoo_id, exception)
            time.sleep(120)


    def _handle_report_download_failed(self, cuckoo_id, exception):
        '''Override this with code for Cuckoo report download
        failure'''

        if exception.http_code == 404:
            logging.warning("Report download failed because id %s does not exist",
                            cuckoo_id)
            self._remove_queue.append(cuckoo_id)

        else:
            logging.error("Report downloading for Cuckoo task %s failed: %s Waiting 2 min",
                          cuckoo_id, exception)
            time.sleep(120)


    def _handle_status_reported(self, cuckoo_id, cuckoo_report):
        '''Override this with code for Cuckoo analysis
        status reported'''

        cuckoo_report = CuckooReport(cuckoo_report)
        report_filtered = cuckoo_report.filter_cuckoo_report()

        esm = ESManager()
        if not esm.exists("cuckoo", "report", cuckoo_report.sha256):
            success = esm.store_json_object("cuckoo","report", cuckoo_report.sha256,
                                  report_filtered)

            if success:
                logging.info("Stored Cuckoo report for %s", cuckoo_report.sha256)
        else:
            logger.info("Cuckoo report %s already exists", cuckoo_report.sha256)

        if cuckoo_id in self._wait_times:
            del self._wait_times[cuckoo_id]

        self._remove_queue.append(cuckoo_id)

    def _handle_status_running_completed(self, cuckoo_id, status):
        '''Override this with code for Cuckoo analysis
        status running or completed'''

        logger.debug("Cuckoo task %s has status %s. Waiting for it to finish",
              cuckoo_id, status)
        self._handle_waiting_time(cuckoo_id)

    def _handle_status_pending(self, cuckoo_id):
        '''Override this with code for Cuckoo analysis
        status pending'''

        self._tasks_pending += 1

        logger.debug("Cuckoo task %s has status pending", cuckoo_id)

    def _handle_status_analysis_failed(self, cuckoo_id):
        '''Override this with code for Cuckoo analysis
        status analysis_failed'''

        logging.warning("Cuckoo task %s has status analysis_failed",
                        cuckoo_id)
        self._remove_queue.append(cuckoo_id)

    def _handle_status_unknown_status(self, cuckoo_id, status):
        '''Override this with code for Cuckoo analysis
        status unknown status'''

        logging.error("Cuckoo task %s has unknown status %s",
                      cuckoo_id, status)

        self._remove_queue.append(cuckoo_id)

    def _handle_analysis(self, cuckoo_id):
        '''Asks Cuckoo for the analysis status of specified id
        and uses returned status to perform actions'''

        # Download the Cuckoo analysis status for Cuckoo id
        try:
            status = CuckooCalls().get_status_cuckoo_id(cuckoo_id)
        except CuckooCallError as e:
            self._handle_status_check_failed(cuckoo_id, e)
            return

        # Download the Cuckoo report for this Cuckoo id
        if status == "reported":
            try:
                call = CuckooCalls()
                cuckoo_report = call.download_cuckcoo_report(cuckoo_id)
            except CuckooCallError as e:
                self._handle_report_download_failed(cuckoo_id, e)
                return

            self._handle_status_reported(cuckoo_id, cuckoo_report)

        elif status in ["running", "completed"]:
            self._handle_status_running_completed(cuckoo_id, status)

        elif status == "pending":
            self._handle_status_pending(cuckoo_id)

        elif status == "failed_analysis":
            self._handle_status_analysis_failed(cuckoo_id)

        else:
            self._handle_status_unknown_status(cuckoo_id, status)

    def _handle_waiting_time(self, cuckoo_id):
        '''Updates dict with waiting times per cuckoo id
        adds cuckoo id to remove queue if max time is exceeded'''

        logger.debug("Waiting queue dict: %s", self._wait_times)
        if not cuckoo_id in self._wait_times:
            self._wait_times[cuckoo_id] = 0
            self._remove_queue.append(cuckoo_id)

        elif self._wait_times[cuckoo_id] >= ReportProcessTask.MAX_WAIT_TIME:
            logging.info("Max wait time exceeded Cuckoo task %s. Removing..",
                        cuckoo_id)

            del self._wait_times[cuckoo_id]
            self._remove_queue.append(cuckoo_id)

        elif cuckoo_id not in self._sub_queue:
            del self._wait_times[cuckoo_id]

    def _handle_remove_queue(self):

        if len(self._remove_queue) > 0:

            logger.debug("Removing Cuckoo ids added to remove queue")

            for cuckoo_id in self._remove_queue:

                if cuckoo_id not in self._wait_times:
                    self._sub_queue.remove(cuckoo_id)
                document_ids = self.es.get_cuckoo_queue_item_ids(cuckoo_id)

                for id in document_ids:
                    logger.debug("deleting %s", id)
                    self.es.delete("queue", "item", id)

            # we sleep after deleting stuff in ES.
            # For some reason ES still returns deleted values if you request
            # them in the same second as when you delete them. This should
            # 'fix' that
            # if ES keeps returning deleted IDs, increase this time a little
            time.sleep(1)
            self._remove_queue = []


    def process_reports(self):
        """
        Starts the downloading of reports with the IDs
        stored in the queue in Elasticsearch.

        Stores each report in ES
        and removes queue item from ES if successful or if Cuckoo id
        does not exist.
        """

        num_vms = 0

        try:
            logging.debug("Asking Cuckoo for number of VMs")
            call = CuckooCalls()
            num_vms = call.get_cuckoo_machines_amount()
        except CuckooCallError as e:
            logger.error("Error asking Cuckoo the number of VMs: %s", e)

        if num_vms < 1:
            logger.error("Exiting, number of Cuckoo VMs is 0")
            sys.exit(1)

        logger.info("Starting to process queue")
        while ReportProcessTask.PROCESS_REPORTS:
            room_in_queue = num_vms - len(self._sub_queue)
            if room_in_queue > 0:
                new = self.es.get_cuckoo_queue_items(room_in_queue)
                logger.debug("Got new queue items: %s", new)
                self._sub_queue.extend(new)

            if len(self._sub_queue) < 1:

                logger.info("No items in queue. Sleeping for 5 minutes")
                time.sleep(300)
                # this somehow helps to keep it from timeouting even though
                # the ES server is online
                self.es = ESManager()

            else:
                logger.debug("Current in memory queue: %s", self._sub_queue)
                for cuckoo_id in self._sub_queue:
                    self._handle_analysis(cuckoo_id)

                end_of_queue = False
                if len(self._sub_queue) == 1:
                    if self.es.get_queue_length() <= 1:
                        end_of_queue = True

                # See the amount of unfinished tasks matches the number
                # of Cuckoo VMs. We wait a specified amount
                if (len(self._wait_times) + self._tasks_pending) >= num_vms or end_of_queue:

                    logger.info("No reported Cuckoo analysis yet. Waiting %s seconds",
                                ReportProcessTask.WAIT_TIME_UNFINISHED)
                    time.sleep(ReportProcessTask.WAIT_TIME_UNFINISHED)

                    self._tasks_pending = 0

                    for wait_id in self._wait_times:
                        self._wait_times[wait_id] += ReportProcessTask.WAIT_TIME_UNFINISHED

                self._handle_remove_queue()
