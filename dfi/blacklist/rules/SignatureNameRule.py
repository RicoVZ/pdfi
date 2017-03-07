from dfi.blacklist.abstracts import Rule

"""
Interates over the 'signature' field and checks
if the stored Cuckoo signature names match the rule data
"""


class SignatureNameRule(Rule):

    def match_rule(self, rule_data):

        matches = []
        for cuckoo_sig in self.cuckoo_report.signature:

            sig_name = cuckoo_sig["name"]

            if sig_name == rule_data:
                matches.append(sig_name)

        if len(matches) > 0:
            return matches
        else:
            return None