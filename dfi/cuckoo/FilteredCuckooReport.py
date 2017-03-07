from dfi.cuckoo.CuckooReport import CuckooReport
from dfi.rule.WhiteList import WhiteList

"""
This class is used to store cuckoo report values that were retrieved from
Elasticsearch. Each key from the report has a seperate attribute so it can
be directly retrieved in rule classes.
"""


class FilteredCuckooReport(CuckooReport):
    def __init__(self, report_json):

        self._report = report_json

        self.score = self._read_data(["score"], 0.0)
        self.date = self._read_data(["date"], "")
        self.cuckoo_version = self._read_data(["cuckoo_version"], "")
        self.cuckoo_options = self._read_data(["cuckoo_options"], "")
        self.binary_name = self._read_data(["binary_name"], "")
        self.file_type = self._read_data(["file_type"], "")
        self.md5 = self._read_data(["md5"], "")
        self.sha1 = self._read_data(["sha1"], "")
        self.sha256 = self._read_data(["sha256"], "")
        self.sha512 = self._read_data(["sha512"], "")
        self.machine_info = self._read_data(["machine_info"], {})
        self.signature = self._read_data(["signature"], [])
        self.vt_matched = self._read_data(["vt_matched"], 0)
        self.dll_loaded = self._read_data(["dll_loaded"], [])
        self.mutex = self._read_data(["mutex"], [])
        self.file_opened = self._read_data(["file_opened"], [])
        self.file_deleted = self._read_data(["file_deleted"], [])
        self.file_written = self._read_data(["file_written"], [])
        self.file_read = self._read_data(["file_read"], [])
        self.dir_created = self._read_data(["dir_created"], [])
        self.dir_enumerated = self._read_data(["dir_enumerated"], [])
        self.dir_removed = self._read_data(["dir_removed"], [])
        self.regkey_opened = self._read_data(["regkey_opened"], [])
        self.regkey_read = self._read_data(["regkey_read"], [])
        self.regkey_written = self._read_data(["regkey_written"], [])
        self.regkey_deleted = self._read_data(["regkey_deleted"], [])
        self.process = self._read_data(["process"], [])
        self.api_call = self._read_data(["api_call"], [])

        # the IP list is filtered by the whitelist class
        wl = WhiteList()
        self.ip_wl_filtered = wl.filter_out_whitelisted(self._read_data(["ip"],
                                                                     []))
        self.ip = self._read_data(["ip"], [])
        self.domain = self._read_data(["domain"], [])
        self.tcp = self._read_data(["tcp"], [])
        self.udp = self._read_data(["udp"], [])
        self.http = self._read_data(["http"], [])
        self.http_ex = self._read_data(["http_ex"], [])
        self.dead_host = self._read_data(["dead_host"], [])
        self.string = self._read_data(["string"], [])
