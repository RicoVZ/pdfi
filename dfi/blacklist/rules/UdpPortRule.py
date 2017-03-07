from dfi.blacklist.abstracts import Rule

"""
Rule data is a UDP port number here.
This rule checks if the UDP port number in rule_data was connected to
It searches the UDP traffic object list in the Cuckoo report.
If it finds a match, it adds the IP connected to and the port to a matches list
"""


class UdpPortRule(Rule):
    def match_rule(self, rule_data):

        matches = []

        for udp_conn_obj in self.cuckoo_report.udp:
            if udp_conn_obj["dport"] == rule_data:
                dst_ip = udp_conn_obj["dst"]

                # only add the match if it is in the IP list
                # filtered by the whitelist
                if dst_ip in self.cuckoo_report.ip_wl_filtered:
                    match = "%s:%s" % (dst_ip, udp_conn_obj["dport"])
                    matches.append(match)

        if len(matches) > 1:
            return matches

        return None
