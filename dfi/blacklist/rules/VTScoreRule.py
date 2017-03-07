import logging

from dfi.blacklist.abstracts import Rule

"""
rule data is an integer range here. The seperator is a '-'
examples: 10-20, 1-1, 5-15 etc

This rule matches if the amount of positive virus total detections
falls within the specified range in rule_data
"""

logger = logging.getLogger(__name__)


class VTScoreRule(Rule):

    def match_rule(self, rule_data):

        matches = []

        if self.validate_number_range(rule_data):
            if self.number_in_int_range(rule_data,
                                        self.cuckoo_report.vt_matched):
                matches.append(self.cuckoo_report.vt_matched)

        else:
            logger.error("Invalid int range %s. A range should be formatted "
                         " like: 1-5", rule_data)

        if len(matches) > 0:
            return matches
        else:
            return None
