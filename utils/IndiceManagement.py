#!/usr/bin/env python

import requests
import argparse
import sys
import glob
import os

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

from dfi.Config import Config

Config("../config.cfg").load_config()

SERVER_ADDRESS = "http://%s:%s/" % (Config.ELASTICSEARCH_IP,
                                   Config.ELASTICSEARCH_PORT)
PATH_JSON_MAPPINGS = "../es-mappings/"
ACTIVE_INDICES = ["blacklist", "cuckoo", "hashes", "queue", "third_party_blacklist", "whitelist"]


def verify_success(result):
    # Will verify if the result returned from any HTTP call.
    if result.status_code == 200:
        return True
    else:
        return False


def create_indice(indice):
    """
    Function creates indices based on a given name. This name will be
    looked up in the PATH_JSON_MAPPINGS and will be posted to ElasticSearch.
    Functions returns either False/True, False if it failed, True if it succeeded.
    """
    infile = open(PATH_JSON_MAPPINGS + indice + ".json", 'r')
    data = str(infile.read())
    if indice in ACTIVE_INDICES:
        result = requests.post(SERVER_ADDRESS + indice, headers={"Content-type": "application/json"}, data=data)
        return verify_success(result)
    else:
        print("Indice:" + indice + " is not marked as active.")
        return False


def delete_indice(indice):
    """
    Function wil delete indice based on a given name.
    Function returns either False/True, False if it failed to delete the indice,
    True if the indice was successfully deleted.
    """
    if indice in ACTIVE_INDICES:
        return verify_success(requests.delete(SERVER_ADDRESS + indice))
    else:
        print("Indice:" + indice + " is not marked as active.")
        return False

def delete_all():
    """
    Deletes all ElasticSearch indices based on the SERVER_ADDRESS variable.
    Function returns either False/True, False if it failed to delete the indice,
    True if the indice was successfully deleted.
    """
    for indice in ACTIVE_INDICES:
        if not verify_success(requests.delete(SERVER_ADDRESS + indice)):
            return False
    return True


def build_all():
    """
    Function build ElasticSearch indices based on the JSON files
    that are found in the PATH_JSON_MAPPINGS.
    """
    os.chdir(PATH_JSON_MAPPINGS)

    success_dict = {}

    for file in glob.glob("*.json"):
        file = file[:-5]
        if create_indice(file):
            success_dict[file] = True
        else:
            success_dict[file] = False

    for val in success_dict:
        if success_dict[val] == False:
            print(success_dict)
            return False

    return True



if __name__ == "__main__":

    optparser = argparse.ArgumentParser("Third-Party Blacklist Builder")
    optparser.add_argument("-da", "--delete-all", help="Delete's all indices", action="store_true")
    optparser.add_argument("-ba", "--build-all", help="Posts all indices to ElasticSearch", action="store_true")
    args = optparser.parse_args()

    if len(sys.argv) < 2:
        print("no args")
        optparser.print_help()

    if args.delete_all:
        if delete_all():
            print("All indices deleted")
        else:
            print("Failed to delete all indices")

    if args.build_all:
        if build_all():
            print("Indices created")
        else:
            print("Failed to build all indices")
