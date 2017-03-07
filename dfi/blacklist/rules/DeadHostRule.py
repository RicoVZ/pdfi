import logging

from dfi.blacklist.abstracts import Rule

"""
rule data is an integer range here. The seperator is a '-'
examples: 10-20, 1-1, 5-15 etc

This rule matches if the amount of dead hosts falls
with the int range specified in rule_data
"""

logger = logging.getLogger(__name__)


class DeadHostRule(Rule):

    def match_rule(self, rule_data):

        wl_filter_deadhost = []
        matches = []

        for ip in self.cuckoo_report.dead_host:
            if ip in self.cuckoo_report.ip_wl_filtered:
                wl_filter_deadhost.append(ip)

        if self.validate_number_range(rule_data):

            num_dead_hosts = len(wl_filter_deadhost)
            if self.number_in_int_range(rule_data, num_dead_hosts):
                matches.append("Number of dead hosts: %s" % num_dead_hosts)
        else:
            logger.error("Invalid int range %s. A range should be formatted "
                         " like: 1-5", rule_data)

        if len(matches) > 0:
            return matches
        else:
            return None
