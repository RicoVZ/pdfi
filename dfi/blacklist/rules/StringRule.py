"""
Here rule_data should be a string that resembles another string from the report.
This rule will search through all reported strings to
see if any of them match with rule_data

rule_data can have wildcards -> or <- be a regular expression in the
python lib re format.
"""

import sre_constants
import logging

from dfi.blacklist.abstracts import Rule


logger = logging.getLogger(__name__)


class StringRule(Rule):

	def match_rule(self, rule_data):

		matches = []

		for string in self.cuckoo_report.string:

			try:
				if self.search_wildcard_regex(rule_data, string):
					matches.append(string)

			except sre_constants.error as e:
				logger.error("Invalid regex %s. Error: %s", rule_data, e)

		if len(matches) > 0:
			return matches

		return None
