import time
import logging
import setproctitle

from dfi.database.ESManager import ESManager
from dfi.rule.TypeFactory import TypeFactory
from dfi.cuckoo.FilteredCuckooReport import FilteredCuckooReport

logger = logging.getLogger(__name__)
setproctitle.setproctitle("BlacklistingTask")

class BlacklistingTask(object):

    PROCESS_BLACKLIST = True

    def process_blacklisting(self):

        es = ESManager()

        while BlacklistingTask.PROCESS_BLACKLIST:
            logger.debug("Getting new set of reports to process")
            reports = es.get_unprocessed_reports_source(8)
            if len(reports) < 1:
                logger.info("No unprocessed reports, waiting 3 minutes")
                time.sleep(180)
                # this somehow helps to keep it from timeouting even though
                # the ES server is online
                es = ESManager()

            processed_reports = []

            for report in reports:

                filtered_report = FilteredCuckooReport(report)

                hashtype = TypeFactory.get_type_for_key("hash",
                                                        filtered_report)

                if hashtype.handle_rules():
                    processed_reports.append(filtered_report.sha256)

            if len(processed_reports) > 0:
                logger.info("Setting to processed")
                es.set_processed_bulk(processed_reports)

            # ES will return processed reports if we don't
            # give it some time
            time.sleep(1)
