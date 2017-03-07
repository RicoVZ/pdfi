import logging
import sys

from dfi.blacklist.abstracts import BlacklistType
from dfi.rule.RuleLoad import RuleLoad
from dfi.blacklist.ScoreBoard import ScoreBoard
from dfi.rule.RuleFactory import RuleFactory
from dfi.Config import Config

logger = logging.getLogger(__name__)


class HashType(BlacklistType):

    def handle_rules(self):

        if not self.type_name in RuleLoad.rules:
            logger.error("No rules for type name: %s Cannot run.",
                         self.type_name)
            sys.exit("Exiting..")

        scoreboard = ScoreBoard(self.type_name,
                                self.cuckoo_report.md5)

        logger.info("Applying rules to report %s",
                     self.cuckoo_report.sha256)
        for rule_key in RuleLoad.rules[self.type_name]:

            # Check if the rule key is valid
            if not RuleFactory.rule_key_exists(rule_key):
                logging.error("Invalid rule key \"%s\". Skipping it.")
                continue

            rule_data_set = RuleLoad.rules[self.type_name][rule_key]

            # Ask the factory to create a rule object for the given key
            rule = RuleFactory.get_rule_for_key(rule_key, self.cuckoo_report,
                                                scoreboard, rule_data_set)

            rule.find_matches()

        scoreboard.calc_group_scores()
        logger.info("End score: %s", scoreboard.score)
        if self.blacklist_if_blacklistable(scoreboard):
            logger.info("Blacklist score reached."
                         " Adding md5 hash %s to blacklist",
                         self.cuckoo_report.md5)
        else:
            logger.debug("Blacklist score not reached. Not blacklisting")

        return True
