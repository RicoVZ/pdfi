"""
Here rule_data should be a string that resembles a filename.
This rule will search through all files written to,
to see if any of them match with rule_data

rule_data can have wildcards -> or <- be a regular expression in the
python lib re format.
"""

import sre_constants
import logging

from dfi.blacklist.abstracts import Rule


logger = logging.getLogger(__name__)


class FileWrittenRule(Rule):

	def match_rule(self, rule_data):

		matches = []

		for file_written in self.cuckoo_report.file_written:

			try:
				if self.search_wildcard_regex(rule_data, file_written):
					matches.append(file_written)

			except sre_constants.error as e:
				logger.error("Invalid regex %s. Error: %s", rule_data, e)

		if len(matches) > 0:
			return matches

		return None
