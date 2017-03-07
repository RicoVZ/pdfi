"""
Here rule_data should be a string that resembles a directory.
This rule will search through all removed directories to
see if any of them match with rule_data

rule_data can have wildcards -> or <- be a regular expression in the
python lib re format.
"""

import sre_constants
import logging

from dfi.blacklist.abstracts import Rule


logger = logging.getLogger(__name__)


class DirRemovedRule(Rule):

	def match_rule(self, rule_data):

		matches = []

		for dir_removed in self.cuckoo_report.dir_removed:

			try:
				if self.search_wildcard_regex(rule_data, dir_removed):
					matches.append(dir_removed)

			except sre_constants.error as e:
				logger.error("Invalid regex %s. Error: %s", rule_data, e)

		if len(matches) > 0:
			return matches

		return None
