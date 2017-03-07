#!/usr/bin/env python

from dfi.task.CuckooBinarySubmitTask import CuckooBinarySubmitTask
from dfi.Logger import Logger
from dfi.Config import Config

"""
    Reads the binaries from the configured directory, checks
    if they have ever been analyzed before, submits to Cuckoo if not seen
    before and adds the Cuckoo submission to the queue in Elasticsearch
"""

if __name__ == "__main__":
    print("Starting binary submitter CTRL+C to stop")

    try:
        Config().load_config()
        Logger.setup_logger("submit_binary.log")
        task = CuckooBinarySubmitTask()
        task.process_binaries()
    except KeyboardInterrupt:
        print("Stopping!")
