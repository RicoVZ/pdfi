import logging
from netaddr import IPSet, AddrFormatError

from dfi.blacklist.abstracts import Rule

"""
Checks if a given IP Address is in a certain subnet.
"""

logger = logging.getLogger(__name__)


class IPAddressInSubnet(Rule):

    def match_rule(self, data):
        ip_list = self.cuckoo_report.ip_wl_filtered
        ip_return_list = []

        try:
            ip_set = IPSet([data])
        except AddrFormatError as e:
            logger.error("Error in subnet in rule file. Value: %s. Error: %s",
                         data, e)
            return None

        for ip in ip_list:
            if ip in ip_set:
                ip_return_list.append(ip)

        if len(ip_return_list) == 0:
            return None

        else:
            return ip_return_list
