class CuckooReport(object):
    def __init__(self, cuckoo_report_json):

        self._report = cuckoo_report_json
        self.filtered_report = {}

        # This will be used as the 'primary key' in ES
        self.sha256 = self._read_data(["target", "file", "sha256"],
                                      "DEFAULT_KEY")

    def filter_cuckoo_report(self):
        """Filters out the data we want to stores and returns
        the filtered report"""

        self.filtered_report = {
            "processed": False,
            "score": self._read_data(["info","score"], ""),
            "date": self._read_data(["info","machine", "shutdown_on"], ""),
            "cuckoo_version" : self._read_data(["info","version"], ""),
            "cuckoo_options": self._read_data(["info", "options"], ""),
            "binary_name": self._read_data(["target","file","name"], ""),
            "file_type": self._read_data(["target", "file", "type"], ""),
            "md5": self._read_data(["target","file","md5"],""),
            "sha1": self._read_data(["target","file","sha1"],""),
            "sha256": self._read_data(["target","file","sha256"],""),
            "sha512": self._read_data(["target","file","sha512"],""),
            "machine_info": {
                "name": self._read_data(["info", "machine", "name"], ""),
                "label": self._read_data(["info", "machine", "label"], ""),
                "manager": self._read_data(["info", "machine", "manager"], "")
            },
            "signature": self.read_json_object_list(
                self._read_data(["signatures"], []),
                ["name", "severity", "description"],
                [str, int, str]
            ),
            "vt_matched": self._read_data(["virustotal", "positives"], 0),
            "dll_loaded": self._read_data(["behavior","summary","dll_loaded"], []),
            "mutex": self._read_data(["behavior","summary","mutex"], []),
            "file_opened": self._read_data(["behavior","summary","file_opened"], []),
            "file_read": self._read_data(["behavior","summary","file_read"], []),
            "file_written": self._read_data(["behavior","summary","file_written"], []),
            "file_deleted": self._read_data(["behavior","summary","file_deleted"], []),
            "dir_created": self._read_data(["behavior","summary","directory_created"], []),
            "dir_enumerated": self._read_data(["behavior","summary","directory_enumerated"], []),
            "dir_removed": self._read_data(["behavior","summary","directory_removed"], []),
            "regkey_opened": self._read_data(["behavior","summary","regkey_opened"], []),
            "regkey_read": self._read_data(["behavior","summary","regkey_read"], []),
            "regkey_written": self._read_data(["behavior","summary","regkey_written"], []),
            "regkey_deleted": self._read_data(["behavior","summary","regkey_deleted"], []),
            "process": self.read_json_object_list(
                self._read_data(["behavior", "processes"], []),
                ["process_name", "command_line"],
                [str, str]
            ),
            "api_call": self._dict_to_object_list(
                self._combine_api_call_stats(),
                "name",
                "times"
            ),
            "ip": self._read_data(["network", "hosts"], []),
            "domain": self.read_json_object_list(
                self._read_data(["network", "domains"], []),
                ["ip", "domain"],
                [str, str]
            ),
            "tcp": self.read_json_object_list(
                self._read_data(["network", "tcp"], []),
                ["src", "dst", "dport"],
                [str, str, int]
            ),
            "udp": self.read_json_object_list(
                self._read_data(["network", "udp"], []),
                ["src", "dst", "dport"],
                [str, str, int]
            ),
            "http": self.read_json_object_list(
                self._read_data(["network", "http"], []),
                ["uri", "user-agent", "method", "body", "host", "path"],
                [str, str, str, str, str, str]
            ),
            "http_ex": self.read_json_object_list(
                self._read_data(["network", "http_ex"], []),
                ["src", "dst", "host", "dport", "uri", "request", "response"],
                [str, str, str, int, str, str, str]
            ),
            "dead_host": self._read_data_from_list_list(0,
                                                        self._read_data(["network", "dead_hosts"],
                                                                        [])),
            "string": self._read_data(["strings"], [])
        }

        return self.filtered_report

    def _read_data(self, key_list, default_value):
        """
        Checks the existence of each key and returns the
        value of the last key. If one key is not found, return default
        value.

        The keys in key_list need to be in the order of depth
        """

        current = self._report

        for key in key_list:
            if not key in current:
                return default_value

            if isinstance(current[key], dict):
                current = current[key]

                if key == key_list[-1]:
                    return current

        return current[key]

    def _combine_api_call_stats(self):
        """
        Combines all the api call stats of all process IDs.
        Returns a dictionary of api call names and amount of times called
        """

        api_calls = {}

        pids = self._read_data(["behavior", "apistats"], {})

        for pid in pids:
            for call in pids[pid]:

                if call in api_calls:
                    api_calls[call] += pids[pid][call]
                else:
                    api_calls[call] = pids[pid][call]

        return api_calls

    def _dict_to_object_list(self, json_dict, key_key_name, value_key_name):
        """
        Creates a json object list. Each key/value pair will be an object.
        The specified key_key_name will be used to store each original key
        The value_key_name will be used store each value for an original key
        """

        object_list = []

        for key in json_dict:
            new_object = {}
            new_object[key_key_name] = key
            new_object[value_key_name] = json_dict[key]

            object_list.append(new_object)

        return object_list

    def read_json_object_list(self, json_object_list, key_list,
                              type_list):
        """
        Reads the specified keys from the specified object dictionary list
        and returns a list of all newly created filtered JSON objects.
        If a key was missing it uses the empty version of the specified type

        you MUST specify the type
        """

        # This is used to set a missing reports field to the correct
        # empty datatype. To please ES and the rule engine
        typedict = {
                 int: 0,
                 long: 0,
                 dict: {},
                 float: 0.0,
                 list: [],
                 str: "",
                 unicode: ""
                }

        filtered_object_list = []

        for json_object in json_object_list:
            filtered_object = {}

            for index, key in enumerate(key_list):
                if key in json_object:
                    filtered_object[key] = json_object[key]
                else:
                    d_type = type_list[index]
                    if d_type in typedict:
                        filtered_object[key] = typedict[d_type]

            if len(filtered_object) > 0:
                filtered_object_list.append(filtered_object)

        return filtered_object_list

    def _read_data_from_list_list(self, index_to_read, list_list):

        data_list = []

        for l in list_list:
            if len(l) > index_to_read:
                data_list.append(l[index_to_read])

        return data_list
