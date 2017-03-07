#!/usr/bin/env python

from elasticsearch import Elasticsearch, helpers
import urllib2
import argparse
import sys
import os
import requests
import json

# To import ESManager
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

from dfi.Config import Config


class ThirdPartyBlacklist(object):

    def __init__(self):

        self.ES_MAPPINGS = "../es-mappings"

        Config("../config.cfg").load_config()
        self.url_list = [
            ["https://zeustracker.abuse.ch/blocklist.php?download=badips",
             "C&C"],
            ["https://feodotracker.abuse.ch/blocklist/?download=ipblocklist",
             "C&C"],
            ["https://ransomwaretracker.abuse.ch/downloads/RW_IPBL.txt", "C&C"]
        ]

        self.SERVER_ADDRESS_THIRD_PARTY = "http://" + Config.ELASTICSEARCH_IP + ":" \
                             + str(Config.ELASTICSEARCH_PORT) + "/third_party_blacklist"

        self.SERVER_ADDRESS = "http://" + Config.ELASTICSEARCH_IP + ":" \
                             + str(Config.ELASTICSEARCH_PORT)


    def download_list(self):
        """
        Reads an List of elements and analyzes the urls for IP's.
        """
        for url in self.url_list:
            self.analyze_url(url[0], url[1])

    def clear(self):
        """
        Delete the third_party_blacklist indice.
        """
        r = requests.delete(self.SERVER_ADDRESS_THIRD_PARTY)
        if r.status_code == 200:
            print("SUCCES - deleted index")
            print("Building index..")
            with open(os.path.join(self.ES_MAPPINGS,
                                   "third_party_blacklist.json")) as fp:
                mapping = json.loads(fp.read())
                r = requests.post(self.SERVER_ADDRESS_THIRD_PARTY,
                                  headers={"Content-type": "application/json"},
                                  data=mapping)
                if r.status_code == 200:
                    print("Created empty index")
                else:
                    print("Error: %s" % r.status_code)

        else:
            print("ERROR - Something went wrong; check state of index")

    def validate_ip(self, s):
        """
        Function that verifies if the string that was found on a line from the URL
        is indeed an IP address. Returns True if it is an IP, false if not.
        """
        a = s.split('.')
        if len(a) != 4:
            return False
        for x in a:
            if not x.isdigit():
                return False
            i = int(x)
            if i < 0 or i > 255:
                return False
        return True

    def analyze_url(self, url, category):
        """
        Analyzed each URL, verifies the line from the URL and if it is an IP
        it will be posted to the ElasticSearch indice.
        """
        data = urllib2.urlopen(url)

        iplist = []

        for line in data:
            line = line.rstrip()
            if '#' not in line:
                if self.validate_ip(line):
                    submitdict = {
                        "_index": "third_party_blacklist",
                        "_type": category,
                        "_id": line,
                        "location": url
                    }
                    iplist.append(submitdict)

        esm = Elasticsearch(self.SERVER_ADDRESS)
        helpers.bulk(esm, iplist)


if __name__ == "__main__":

    optparser = argparse.ArgumentParser("Third-Party Blacklist Builder")
    optparser.add_argument("-r", "--run", help="Run the program; re-analyse all URL's ", action="store_true")
    optparser.add_argument("-c", "--clear", help="Clearing all records; dropping the indice", action="store_true")
    args = optparser.parse_args()

    if len(sys.argv) == 0:
        print "no args"
        optparser.print_help()
        sys.exit(0)

    if args.run:
        ThirdPartyBlacklist().download_list()

    if args.clear:
        ThirdPartyBlacklist().clear()
