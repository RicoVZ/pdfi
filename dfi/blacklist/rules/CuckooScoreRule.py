import logging

from dfi.blacklist.abstracts import Rule

"""
rule data is a float range here. The seperator is a '-'
examples: 1.0-4.0, 0.5-2.0 etc

This rule matches if the Cuckoo score falls within
the specified range in rule_data
"""

logger = logging.getLogger(__name__)


class CuckooScoreRule(Rule):

    def match_rule(self, rule_data):

        matches = []

        if self.validate_number_range(rule_data):
            if self.number_in_float_range(rule_data,
                                        self.cuckoo_report.score):
                matches.append(self.cuckoo_report.score)

        else:
            logger.error("Invalid float range %s. A range should be formatted "
                         " like: 1.0-5.0", rule_data)

        if len(matches) > 0:
            return matches
        else:
            return None
