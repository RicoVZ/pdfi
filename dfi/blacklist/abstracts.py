"""
When creating a new type, always override the handle_rules method
Use this method to implement the logic which calls the rule factory
creates scoreboards etc.

We need this because of some 'types' there can be more than one
in a Cuckoo report. We only blacklist one hash. But a report may
contain 20 malicious IP addresses. Each type, therefore needs its own
logic which calls the rules the correct number of times
"""

import re
import fnmatch

from dfi.Config import Config
from dfi.database.ESManager import ESManager


class BlacklistType(object):
    def __init__(self, type_name, filtered_cuckoo_report):
        self.type_name = type_name
        self.cuckoo_report = filtered_cuckoo_report
        self.es = ESManager()

    def blacklist_if_blacklistable(self, scoreboard):
        # if the calculated score is higher than the max configured score
        # then add to the blacklist of the type

        if scoreboard.score >= Config.BLACKLIST_SCORE:
            self.es.add_to_blacklist(scoreboard.type, scoreboard.value,
                                     scoreboard.reason, scoreboard.score)
            return True
        else:
            return False

    def handle_rules(self):
        """
        Handles the correct calling of the rules
        for this type.
        """
        pass


class Rule(object):
    def __init__(self, filtered_cuckoo_report, scoreboard,
                 rule_key, rules):
        self.cuckoo_report = filtered_cuckoo_report
        self.scoreboard = scoreboard
        self.rule_key = rule_key
        self.rules = rules
        self._regex_prefix = "!REGEX!"

    def match_found(self, match_data, rule_group_id, score):

        self.scoreboard.add_match(rule_group_id, self.rule_key, score,
                                  match_data)

    # If you have a rule for which you do not
    # have more than 1 rule object, or for some reason need
    # extra logic when matching rules, also override this method.
    def find_matches(self):
        """
        Runs the logic of this rule for each rule object in the 'rules'
        object list. Adds results to the ScoreBoard object in this class
        """

        for rule in self.rules:

            rule_group = self._get_group_id(rule)
            rule_data = rule["rules"]
            rule_score = rule["score"]

            rule_data_set = []

            # We create a list of rule values. So we can always iterate
            if isinstance(rule_data, list):
                rule_data_set.extend(rule_data)
            else:
                rule_data_set.append(rule_data)

            for sub_rule_data in rule_data_set:
                match_data = self.match_rule(sub_rule_data)

                if match_data is not None:
                    for match in match_data:
                        self.match_found(match, rule_group, rule_score)

    def _get_group_id(self, rule_obj):
        """
        Checks if this rule object has a group_id key. If it does not,
        it will return the default group 0.
        """

        group_id = 0
        if "group_id" in rule_obj:
            group_id = rule_obj["group_id"]

        return group_id

    # Override this method when inheriting this class. It must return None
    # if your rule does not find a match. It should return a ->list<- of
    # the values that match if it does find a match.
    # Rule data will always be a single value. So 1 IP, 1 string etc
    def match_rule(self, rule_data):
        """
        Runs the logic for this rule and returns the matching data if it
        finds a match. Returns None if it does not find a match.
        """

        return None

    def search_wildcard_regex(self, pattern, string):
        """
        Accepts a pattern and a string to search through.

        The pattern string can contain a regex or wildcards, in this case the
        pattern should have the "!REGEX!" prefix.

        If it does not have the prefix it is treated as a normal string
        with wildcards in it. Available wildcards are: * and ?

        returns True on a found match

        * = any amount of characters
        ? = single character

        Throws sre_constants.error on invalid regex
        """

        # If the pattern starts with the prefix in self._regex_prefix
        # act as if it is a regex and cut the prefix before using it
        if pattern.startswith(self._regex_prefix):
            reg_pattern = pattern.replace(self._regex_prefix, "", 1)
            if re.search(reg_pattern, string):
                return True
            else:
                return False

        # Find matches based on wildcards
        if fnmatch.fnmatch(string, pattern):
            return True

        return False

    def number_in_float_range(self, numrange, number):
        """"
        Checks if the given float number falls within the float
        range numrange. The change should be a string formatted like this:
        '2.4-5.0' and always be from low to high or two of the same numbers
        """

        numbers = numrange.split("-", 1)

        start = float(numbers[0])
        stop = float(numbers[1])

        if number >= start and number <= stop:
            return True
        else:
            return False

    def number_in_int_range(self, numrange, number):
        """"
        Checks if the given int number falls within the int
        range numrange. The change should be a string formatted like this:
        '2-5' and always be from low to high or two of the same numbers
        """

        numbers = numrange.split("-", 1)

        start = int(numbers[0])
        stop = int(numbers[1])

        if number >= start and number <= stop:
            return True
        else:
            return False

    def validate_number_range(self, numrange):
        """"
        Validates if the given range is formatted like:  1-5 or 1.0-5.0.
        from small to large.

        Returns False if the range is invalid, True if valid.
        """

        if "-" not in numrange:
            return False

        numbers = numrange.split("-", 1)
        if len(numbers) < 2:
            return False

        start = ""
        stop = ""

        num_valid = False
        try:
            start = int(numbers[0])
            stop = int(numbers[1])
            num_valid = True
        except ValueError:
            pass

        try:
            start = float(numbers[0])
            stop = float(numbers[1])
            num_valid = True
        except ValueError:
            pass

        if not num_valid:
            return False

        if start > stop:
            return False

        return True



