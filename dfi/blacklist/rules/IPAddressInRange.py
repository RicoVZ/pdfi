from dfi.blacklist.abstracts import Rule

"""
Checks if a given IP Address is in a certain range.
Returns one IP if the range is a single IP, returns
a list of more IP's when a range of more than two
possible IP addresses are given.
"""


class IPAddressInRange(Rule):
    def match_rule(self, data):
        ip_list = []
        rule_range = data
        ip_return_list = []

        ip_list = self.cuckoo_report.ip_wl_filtered

        if "-" not in rule_range:
            for ip in ip_list:
                if ip in rule_range:
                    ip_return_list.append(ip)
                    return ip_return_list
        else:
            separator = rule_range.find("-")
            first_ip = rule_range[:separator]
            second_ip = rule_range[separator + 1:]

            for address in self.rangeIPv4(first_ip, second_ip):
                if address in ip_list:
                    ip_return_list.append(address)

            if len(ip_return_list) > 0:
                return ip_return_list
            else:
                return

    def undotIPv4(self, dotted):
        return sum(int(octet) << ((3 - i) << 3) for i, octet in
                   enumerate(dotted.split('.')))

    def dotIPv4(self, addr):
        return '.'.join(str(addr >> off & 0xff) for off in (24, 16, 8, 0))

    def rangeIPv4(self, start, stop):
        for addr in range(self.undotIPv4(start), self.undotIPv4(stop)):
            yield self.dotIPv4(addr)
