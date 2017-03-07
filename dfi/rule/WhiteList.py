import time
import logging
import sys

from netaddr import IPSet, AddrFormatError

from dfi.database.ESManager import ESManager

""""
This class holds an in memory whitelist of IP subnets. It gets these
subnets from the ES server in the whitelist/subnet indice/doctype.

Every time the 'filter_out_whitelisted' is called, the last time the
list was refreshed is checked. If this is more than the configured seconds
ago, it will build a new list.
"""

logger = logging.getLogger(__name__)


class WhiteList(object):
    SUBNET_SET = []
    LAST_REFRESH = 0

    def __init__(self):
        self.es = ESManager()

    def _refresh_whitelist(self):
        """
        Asks elasticsearch for all whitelist IP subnets. It gets these
        in groups of 'step'. For this to work, the ES max window size must
        be large. (100000).

        The IP subnets are stored as an IPSet object in memory
        Each time the list is downloaded, the current time in stored
        """

        logger.info("Refreshing IP subnet whitelist")
        subnet_list = []

        step = 500
        start = 0

        WhiteList.LAST_REFRESH = time.time()

        while True:
            subnets = self.es.get_subnet_whitelist(start, step)

            if len(subnets) < 1:
                break

            subnet_list.extend(subnets)
            start += step

        try:
            WhiteList.SUBNET_SET = IPSet(subnet_list)
        except AddrFormatError as e:
            logger.error("Could not load whitelist because of error in"
                         " a IP subnet entry. Only use the API to add new"
                         " values. Exiting.. Error: %s", e)
            sys.exit(1)

    def _refresh_if_needed(self):
        """
        refreshes the whitelist in memory if the last refresh is more than
        'refresh_time' ago.
        """

        # refresh every hour
        # Time in seconds
        refresh_time = 3600

        if (time.time() - WhiteList.LAST_REFRESH) >= refresh_time:
            self._refresh_whitelist()

    def filter_out_whitelisted(self, ip_list):
        """
        Accepts a list of IP addresses, filters out all IPs that match
        a whitelisted subnet and returns the filtered list.
        """

        self._refresh_if_needed()

        filtered_list = []

        for ip in ip_list:
            if ip not in WhiteList.SUBNET_SET:
                filtered_list.append(ip)
            else:
                logger.debug("Skipping whitelisted IP: %s", ip)

        return filtered_list
