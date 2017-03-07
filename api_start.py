#!/usr/bin/env python
import setproctitle

from dfi.Logger import Logger
from dfi.Config import Config
import dfi.api.APIListener

"""
    Starts the API Listener on the port number that is defined with the
    API_PORT variable. The API listens on several calls which enables
    the user to recieve information from ElasticSearch.

    This API returns statistic information about the program. This
    API should be used to retrieve information about the performance and
    status of the program. Besides the retrieval of information, several
    API calls to manually edit the databases are present.
"""

setproctitle.setproctitle("APIListener")

if __name__ == "__main__":
    print("Starting web API CTRL+C to stop")

    try:
        Config().load_config()
        Logger.setup_logger("api_log.log")
        dfi.api.APIListener.start_api()
    except KeyboardInterrupt:
        print("Stopping!")
