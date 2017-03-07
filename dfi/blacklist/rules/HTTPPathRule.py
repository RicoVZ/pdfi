import logging
import sre_constants

from dfi.blacklist.abstracts import Rule

"""
Retrieves all HTTP requests paths from a Cuckoo report, function
checks with a regular expression if it comes across a match.
Returns list with paths with matches. If no matches are found
it returns none.
"""

logger = logging.getLogger(__name__)


class HTTPPathRule(Rule):
    def match_rule(self, rule_data):
        path_list = []
        return_list = []
        # retrieve all paths from cuckoo report
        cuckoo_report_data = self.cuckoo_report.http

        for record in cuckoo_report_data:
            path_list.append(record["path"])

        for item in path_list:
            try:
                if Rule.search_wildcard_regex(self, rule_data, item):
                    return_list.append(item)

            except sre_constants.error as e:
                logger.error("Invalid regex %s. Error: %s", rule_data, e)

        if len(return_list) > 0:
            return return_list
        else:
            return None
