from dfi.rule.RuleLoad import RuleLoad

"""
This class is used to keep track of the matched
rules for one value of a certain type. So 1 hash, 1 IP etc.

The same ScoreBoard should be passed to each new instance of a rule object
for 1 value of a type.

So: when running all the rules for a hash type. The same ScoreBoard will be
used.
When running all rules for each IP in a Cuckoo report. A new ScoreBoard must
be used for each IP.
"""


class ScoreBoard(object):
    def __init__(self, type, value):
        self.score = 0.0
        self.type = type
        self.value = value
        self.reason = []
        self.matched_rules = {}

    def add_match(self, group_id, signature_name, score, reason):
        """
        Adds the given matched signature name and score to the
        correct group.
        """

        if group_id not in self.matched_rules:
            self.matched_rules[group_id] = []

        match = {
            "name": signature_name,
            "score": score,
            "reason": {
                "reason": signature_name,
                "data": reason
            }
        }

        self.matched_rules[group_id].append(match)

    def _increment_scores_for_group(self, group_id):
        """
        Read the scores for a group id and increment the
        overall score with the score of the total score of
        a group id.
        """

        for match in self.matched_rules[group_id]:
            self.score += match["score"]

    def _add_reasons_for_group(self, group_id):

        for match in self.matched_rules[group_id]:
            self.reason.append(match["reason"])

    def calc_group_scores(self):
        """
        Calculate the total score per group id and
        add it to the total overall score.
        """

        for group_id in self.matched_rules:

            if group_id == 0:
                self._increment_scores_for_group(0)
                self._add_reasons_for_group(0)
                continue

            names = RuleLoad.get_sigdata_for_group(self.type, group_id)

            # Check if all signature names for a group id
            # are in the matched rules. Remove a found name
            # from the list of all signatures in that group
            for match in self.matched_rules[group_id]:
                sig_name = match["name"]
                if sig_name in names:
                    names.remove(sig_name)

            # if the names list is emtpy, all rules in a certain group
            # were matched. So we add the total score of that group
            if len(names) == 0:
                self._increment_scores_for_group(group_id)
                self._add_reasons_for_group(group_id)
