from dfi.blacklist.abstracts import Rule
"""
This rule checks if there are any triggered Cuckoo signatures
which have an equal severity as rule_data
"""


class SignatureSeverityRule(Rule):
    def match_rule(self, rule_data):

        matches = []
        for cuckoo_signature in self.cuckoo_report.signature:

            if cuckoo_signature["severity"] == rule_data:
                match = "%s - Severity: %s" % (cuckoo_signature["name"],
                                               cuckoo_signature["severity"])
                matches.append(match)

        if len(matches) > 0:
            return matches
        else:
            return None
