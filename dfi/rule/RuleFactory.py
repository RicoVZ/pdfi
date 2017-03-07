from dfi.blacklist.rules.CommandLineRule import CommandLineRule
from dfi.blacklist.rules.FileDeletedRule import FileDeletedRule
from dfi.blacklist.rules.DirCreatedRule import DirCreatedRule
from dfi.blacklist.rules.DirEnumeratedRule import DirEnumeratedRule
from dfi.blacklist.rules.DirRemovedRule import DirRemovedRule
from dfi.blacklist.rules.FileOpenedRule import FileOpenedRule
from dfi.blacklist.rules.FileReadRule import FileReadRule
from dfi.blacklist.rules.FileWrittenRule import FileWrittenRule
from dfi.blacklist.rules.MutexRule import MutexRule
from dfi.blacklist.rules.ProcessNameRule import ProcessNameRule
from dfi.blacklist.rules.RegKeyDeletedRule import RegKeyDeletedRule
from dfi.blacklist.rules.RegKeyWrittenRule import RegKeyWrittenRule
from dfi.blacklist.rules.RegKeyReadRule import RegKeyReadRule
from dfi.blacklist.rules.SignatureNameRule import SignatureNameRule
from dfi.blacklist.rules.IPAddressInSubnet import IPAddressInSubnet
from dfi.blacklist.rules.IPAddressInRange import IPAddressInRange
from dfi.blacklist.rules.SignatureSeverityRule import SignatureSeverityRule
from dfi.blacklist.rules.RegKeyOpenedRule import RegKeyOpenedRule
from dfi.blacklist.rules.StringRule import StringRule
from dfi.blacklist.rules.TcpPortRule import TcpPortRule
from dfi.blacklist.rules.UdpPortRule import UdpPortRule
from dfi.blacklist.rules.HTTPPathRule import HTTPPathRule
from dfi.blacklist.rules.HTTPUserAgentRule import HTTPUserAgentRule
from dfi.blacklist.rules.VTScoreRule import VTScoreRule
from dfi.blacklist.rules.CuckooScoreRule import CuckooScoreRule
from dfi.blacklist.rules.DeadHostRule import DeadHostRule
from dfi.blacklist.rules.ThirdPartyIPCheck import ThirdPartyIPCheck

class RuleFactory(object):

    RULE_CLASS_MATCH = {
        "signature_name": SignatureNameRule,
        "signature_severity": SignatureSeverityRule,
        "registry_key_opened": RegKeyOpenedRule,
        "tcp_port": TcpPortRule,
        "udp_port": UdpPortRule,
        "ip_in_range": IPAddressInRange,
        "ip_in_subnet": IPAddressInSubnet,
        "http_path": HTTPPathRule,
        "http_user_agent": HTTPUserAgentRule,
        "vt_score": VTScoreRule,
        "cuckoo_score": CuckooScoreRule,
        "dead_host_amount": DeadHostRule,
        "dir_created": DirCreatedRule,
        "dir_enumerated": DirEnumeratedRule,
        "dir_removed": DirRemovedRule,
        "file_deleted": FileDeletedRule,
        "file_opened": FileOpenedRule,
        "file_read": FileReadRule,
        "file_written": FileWrittenRule,
        "mutex": MutexRule,
        "registry_key_read": RegKeyReadRule,
        "registry_key_deleted": RegKeyDeletedRule,
        "registry_key_written": RegKeyWrittenRule,
        "string": StringRule,
        "process_name": ProcessNameRule,
        "command_line": CommandLineRule,
        "3rd_party_blacklist": ThirdPartyIPCheck
    }

    @staticmethod
    def rule_key_exists(rule_key):
        if rule_key in RuleFactory.RULE_CLASS_MATCH:
            return True
        return False

    @staticmethod
    def get_rule_for_key(rule_key, filtered_cuckoo_report,
                         scoreboard, rules):
        """
        Finds the correct class for the rule key given and
        return an instance of that class.
        """
        rule_class = RuleFactory.RULE_CLASS_MATCH[rule_key]

        rule_object = rule_class(filtered_cuckoo_report, scoreboard,
                                 rule_key, rules)

        return rule_object
