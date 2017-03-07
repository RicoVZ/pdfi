"""
Here rule_data should be a string that resembles a registry key.
This rule will search through all read registry keys to
see if any of them match with rule_data

rule_data can have wildcards -> or <- be a regular expression in the
python lib re format.
"""

import logging
import sre_constants

from dfi.blacklist.abstracts import Rule

logger = logging.getLogger(__name__)


class RegKeyReadRule(Rule):

    def match_rule(self, rule_data):

        matches = []

        for key_read in self.cuckoo_report.regkey_read:

            try:
                if self.search_wildcard_regex(rule_data, key_read):
                    matches.append(key_read)
            except sre_constants.error as e:
                logger.error("Invalid regex %s. Error: %s", rule_data, e)

        if len(matches) > 0:
            return matches

        return None
