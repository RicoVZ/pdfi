import ConfigParser
import os.path
import sys

""""
Contains all the configuration constants used by this application
Other classes get their settings from here.

The config should only be loaded at -> startup <- and -> before <- the
logger is set up. This is because the logger needs the logging level that
is configured in the config file.
"""


class Config(object):

    # The score at which a value(ip, hash, etc) is added to the blacklist
    # -> Should be a floating point number <-
    BLACKLIST_SCORE = 2.0

    # The IP this application's API will listen op
    API_LISTEN_IP = "0.0.0.0"

    # The IP this application's API will listen op
    API_LISTEN_PORT = 8081

    # The Cuckoo server IP used to submit binaries to
    CUCKOO_SRV_IP = "127.0.0.1"

    # The Cuckoo server's API port. (Cuckoo default is 8090)
    CUCKOO_API_PORT = 8090

    # The Elasticsearch server used to stored all data for this application
    # Queues, blacklists, filtered Cuckoo reports, list of hashes etc
    ELASTICSEARCH_IP = "127.0.0.1"

    # The Elasticsearch API port
    ELASTICSEARCH_PORT = 9200

    # The directory where the binary submitter will look for binaries
    # to submit to the Cuckoo server
    BINARY_DIR = "binaries"

    # The minimum logging level. Debug shows a lot of information.
    # You only want to enable debug if you actually are debugging.
    # It is recommended to use an info level in a production environment
    # Possible levels: debug, info, warning, error
    LOG_LEVEL = "debug"

    def __init__(self, path=None):

        if path is not None:
            self.cfg_name = path
        else:
            self.cfg_name = "config.cfg"
        self.cfg_p = ConfigParser.RawConfigParser()
        self.srv_sec = "Servers"
        self.app_cfg_sec = "Settings"

    def _create_default_config(self):
        """
        Creates a default config file
        """

        print("No config found, creating default config")

        self.cfg_p.add_section(self.srv_sec)

        self.cfg_p.set(self.srv_sec, "cuckoo_server_ip", "127.0.0.1")
        self.cfg_p.set(self.srv_sec, "cuckoo_api_port", "8090")

        self.cfg_p.set(self.srv_sec, "elasticsearch_server_ip", "127.0.0.1")
        self.cfg_p.set(self.srv_sec, "elasticsearch_port", "9200")

        self.cfg_p.add_section(self.app_cfg_sec)

        self.cfg_p.set(self.app_cfg_sec, "api_listen_ip", "0.0.0.0")
        self.cfg_p.set(self.app_cfg_sec, "api_listen_port", "8081")

        self.cfg_p.set(self.app_cfg_sec, "blacklist_score", "2.0")

        self.cfg_p.set(self.app_cfg_sec, "binary_directory", "binaries")

        self.cfg_p.set(self.app_cfg_sec, "log_level", "debug")

        with open(self.cfg_name, "wb") as fw:
            self.cfg_p.write(fw)

    def load_config(self):
        """
        Loads the config file into the values in the Config class. It
        creates a default config file if it is not present.
        """

        # If the config does not exist yet, generate it.
        if not os.path.isfile(self.cfg_name):
            self._create_default_config()

        try:
            # Load the config file that already existed or we
            # just generated
            self.cfg_p.read(self.cfg_name)

            Config.CUCKOO_SRV_IP = self.cfg_p.get(self.srv_sec,
                                                  "cuckoo_server_ip")
            Config.CUCKOO_API_PORT = self.cfg_p.get(self.srv_sec,
                                                    "cuckoo_api_port")

            Config.ELASTICSEARCH_IP = self.cfg_p.get(self.srv_sec,
                                                     "elasticsearch_server_ip")
            Config.ELASTICSEARCH_PORT = self.cfg_p.get(self.srv_sec,
                                                       "elasticsearch_port")
            Config.API_LISTEN_IP = self.cfg_p.get(self.app_cfg_sec,
                                                  "api_listen_ip")
            Config.API_LISTEN_PORT = self.cfg_p.getint(self.app_cfg_sec,
                                                    "api_listen_port")
            Config.BLACKLIST_SCORE = self.cfg_p.getfloat(self.app_cfg_sec,
                                                    "blacklist_score")
            Config.BINARY_DIR = self.cfg_p.get(self.app_cfg_sec,
                                               "binary_directory")
            Config.LOG_LEVEL = self.cfg_p.get(self.app_cfg_sec,
                                              "log_level")
        except ConfigParser.Error as e:
            print("Error in config file %s: %s" % (self.cfg_name, e))
            sys.exit(1)
