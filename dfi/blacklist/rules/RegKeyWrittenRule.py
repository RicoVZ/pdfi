"""
Here rule_data should be a string that resembles a registry key.
This rule will search through all registry keys written to,
to see if any of them match with rule_data

rule_data can have wildcards -> or <- be a regular expression in the
python lib re format.
"""

import logging
import sre_constants

from dfi.blacklist.abstracts import Rule

logger = logging.getLogger(__name__)

class RegKeyWrittenRule(Rule):

    def match_rule(self, rule_data):

        matches = []

        for key_written in self.cuckoo_report.regkey_written:

            try:
                if self.search_wildcard_regex(rule_data, key_written):
                    matches.append(key_written)
            except sre_constants.error as e:
                logger.error("Invalid regex %s. Error: %s", rule_data, e)

        if len(matches) > 0:
            return matches

        return None
