import json
import os.path
import logging
import sys

from dfi.rule.RuleFactory import RuleFactory

logger = logging.getLogger(__name__)


class RuleLoad(object):
    rules = {}

    expected_types = ["hash"]
    base_keys = ["info", "rules"]
    minimum_rule_keys = ["rules", "score"]
    path = "rules"

    def _add_rule_data(self, rules, rule_key, typename):

        if self.validate_ruledata(rules):

            if rule_key not in RuleLoad.rules:
                RuleLoad.rules[typename][rule_key] = rules
            else:
                RuleLoad.rules[typename][rule_key].append(rules)
        else:
            logging.error("Skipping invalid rule %s in type %s",
                          rule_key, typename)


    def load_rules(self, ruleset, filename):

        typename = ruleset["info"]["type"]

        if typename not in RuleLoad.rules:
            RuleLoad.rules[typename] = {}

        for rule_key in ruleset["rules"]:
            if not RuleFactory.rule_key_exists(rule_key):
                logger.warning("Unknown rule key: %s", rule_key)
            else:
                self._add_rule_data(ruleset["rules"][rule_key], rule_key,
                                    typename)

    def validate_ruledata(self, ruledata):

        for rule_obj in ruledata:

            if "group_id" not in rule_obj:
                rule_obj["group_id"] = 0

            for key in RuleLoad.minimum_rule_keys:
                if not key in rule_obj:
                    logger.error("Missing minimum rule key: %s in %s",
                                 key, rule_obj)
                    return False

            return True


    def vality_check(self, ruleset, filename):

        for key in RuleLoad.base_keys:
            if not key in ruleset:
                logger.error("%s is missing the basic key %s",
                             filename, key)
                return False

        if "type" not in ruleset["info"]:
            logger.error("%s is missing the type key in its info field")
            return False

        typename = ruleset["info"]["type"]
        if typename not in RuleLoad.expected_types:
            logger.error("Invalid type %s", typename)
            return False

        return True

    def load_all_rules(self):

        if not os.path.exists(self.path):
            logger.error("Rule file path %s does not exist! Exiting..",
                         self.path)
            sys.exit(1)

        file_list = os.listdir(self.path)
        for file in file_list:

            file_path = os.path.join(self.path, file)

            try:
                with open(file_path, "r") as rule_file:
                    ruleset = json.loads(rule_file.read())

            except (OSError, IOError, ValueError) as e:
                logger.error("Error loading rule file: %s Error: %s",
                             file, e)
                sys.exit(1)

            if self.vality_check(ruleset, file):
                self.load_rules(ruleset, file)

    @staticmethod
    def get_sigdata_for_group(type, group_id):

        rule_names = []

        for rule in RuleLoad.rules[type]:

            rule_data = RuleLoad.rules[type][rule]

            for rule_obj in rule_data:

                if "group_id" in rule_obj:
                    if rule_obj["group_id"] == group_id:
                        rule_names.append(rule)

        return rule_names

