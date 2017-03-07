from dfi.blacklist.abstracts import Rule
from dfi.database.ESManager import ESManager

"""
Checks if an single IP exists in the IP blacklist
database which is build from external sources.

Rule data is the name of the doc_type within the indice third_party_blacklist.
This means that you can add any doc_type and use this rule to check if it exists.

A rule_data example would be "C&C" which you would give a high score.
"""


class ThirdPartyIPCheck(Rule):
    def match_rule(self, rule_data):
        ip_list = self.cuckoo_report.ip_wl_filtered

        esm = ESManager()
        final_ip_list = []

        for ip in ip_list:
            if esm.exists("third_party_blacklist", rule_data, ip):
                final_ip_list.append(ip)

        if len(final_ip_list) > 0:
            return final_ip_list
        else:
            return None
