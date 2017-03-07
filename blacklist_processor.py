#!/usr/bin/env python

from dfi.task.BlacklistingTask import BlacklistingTask
from dfi.Logger import Logger
from dfi.rule.RuleLoad import RuleLoad
from dfi.Config import Config

"""
Downloads reports from Elasticsearch that have 'processed: false' and uses
different kinds of blacklisting rules to determine if a hash or IP should be
added to the blacklist. At this time it only blacklists hashes. It does so
based on the severity level of the Cuckoo signatures that were triggered.

It adds each blacklisted hash/ip to Elasticsearch/blacklist/<type> with the
id being either an IP or the sha256 hash. It will fill the 'reason' field with
information related to the blacklisting.
"""

if __name__ == "__name__":
    print("Starting blacklisting module. CTRL-C to stop.")
try:
    Config().load_config()
    Logger.setup_logger("blacklist_processor.log")
    RuleLoad().load_all_rules()
    task = BlacklistingTask()
    task.process_blacklisting()
except KeyboardInterrupt:
    print("Stopping..")
