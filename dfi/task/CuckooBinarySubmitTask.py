import hashlib
import logging
import os
import sys
import time
import setproctitle

from dfi.Config import Config
from dfi.cuckoo.CuckooCalls import CuckooCalls, CuckooCallError
from dfi.database.ESManager import ESManager

logger = logging.getLogger(__name__)
setproctitle.setproctitle("CuckooBinarySubmitTask")

class CuckooBinarySubmitTask(object):

    SUBMIT_BINARIES = True

    def __init__(self):

        self.binary_path = Config.BINARY_DIR

    def process_binaries(self):

        ESman = ESManager()

        if not os.path.isdir(self.binary_path):
            logger.error("Binary directory \'%s\' does not exist",
                         self.binary_path)
            sys.exit(1)

        while CuckooBinarySubmitTask.SUBMIT_BINARIES:

            all_files = os.listdir(self.binary_path)

            if len(all_files) < 1:

                logger.info("No new binaries to submit. Sleeping 5 minutes")
                time.sleep(300)
                # this somehow helps to keep it from timeouting even though
                # the ES server is online
                ESman = ESManager()

            for file in all_files:
                filepath = os.path.join(self.binary_path, file)

                if not os.path.isfile(filepath):
                    continue

                # Calculate file hash
                sha256 = hashlib.sha256()
                with open(filepath, "r") as fp:
                    while True:
                        chunk = fp.read(4096)
                        if not chunk:
                            break
                        sha256.update(chunk)

                sha256_binary = sha256.hexdigest()

                remove_binary = True

                # check if hash exists in ES database or current Cuckoo reports
                if not ESman.exists("hashes", "item", sha256_binary):
                    if not ESman.exists("queue", "item", sha256_binary):
                        logger.debug("Submitting %s sha256=%s", filepath, sha256_binary)

                        try:
                            cuckoocall = CuckooCalls()
                            task_id = cuckoocall.submit_to_cuckoo(filepath)
                            if not ESman.new_queue_item(sha256_binary, task_id):

                                remove_binary = False
                                logger.warning("Failed create new queue item at ES. task id: %s",
                                               task_id)
                            else:
                                logger.debug("Creating hash: %s in hashes indice", sha256_binary)
                                body = {
                                    "timestamp": int(time.time() * 1000),
                                    "counter": 1
                                }

                                ESman.store_json_object("hashes",
                                                        "item",
                                                        sha256_binary,
                                                        body)
                        except CuckooCallError as e:
                            remove_binary = False
                            logger.error("Binary submission failed: %s ", e)
                else:
                    logger.debug("Encountered binary with hash: %s , which is already in queue of hashes indice",
                                 sha256_binary)
                    ESman.update_count(sha256_binary)

                # if already queued, already reported or submitted: delete binary
                if remove_binary:
                    logger.debug("Removing binary..")
                    os.remove(filepath)
