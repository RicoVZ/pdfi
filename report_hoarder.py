#!/usr/bin/env python

from dfi.task.ReportProcessTask import ReportProcessTask
from dfi.Logger import Logger
from dfi.Config import Config

"""
    Starts a report processing task. This task gets sets of Cuckoo task IDs
    from Elasticsearch/queue and uses these 'queue items' to ask Cuckoo for the
    status of the analysis belonging to the ID.

    If the status is reported, it will download the report, filter it, store it
    in Elasticsearch/cuckoo/report/sha256ID, and remove the queue item from the
    queue index in Elasticsearch.
"""

if __name__== "__main__":
    print("Starting report hoarder! CTRL+C to stop")

    try:
        Config().load_config()
        Logger.setup_logger("report_hoarder.log")
        task = ReportProcessTask()
        task.process_reports()
    except KeyboardInterrupt:
        print("Stopping!")