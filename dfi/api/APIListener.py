import time
import logging
import psutil

from flask import request
from flask import Flask
from netaddr import IPSet, AddrFormatError

from dfi.database.ESManager import ESManager
from dfi.Config import Config

Config().load_config()
esm = ESManager()
app = Flask(__name__)

API_DEBUG = False

logger = logging.getLogger(__name__)


def start_api():
    app.run(Config.API_LISTEN_IP, Config.API_LISTEN_PORT, API_DEBUG)


# GET METHODS
@app.route("/hash/get/<string:since>", methods=['GET'])
def return_hashes(since):
    """
    Function returns hashes;
    Use variable since to give a time period in seconds
    or use the "all" to return all hashes.
    """

    if "all" == since:
        return str(esm.all_id("blacklist"))

    else:
        from_time = int(time.time()) - int(since)
        # return str(from_time) + " = from time, time now = " + str(int(time.time()))
        return str(esm.id_time_range("blacklist", from_time))


@app.route("/count/<string:index>/<string:doctype>", methods=['GET'])
def count(index, doctype):
    """ Can count the rows of any index and any doc_type
        Can use 'all' as doctype variable to use any doc_type in the selected index
    """
    return esm.count_items(index, doctype)


@app.route("/stats/hashes", methods=['GET'])
def blacklist_hash_hour():
    """ returns amount of blacklisted Hashes per hour based on the last_change value of the blacklist item """
    return esm.blacklist_per_hour("hash")


@app.route("/stats/ip", methods=['GET'])
def blacklist_ip_hour():
    """ returns amount of blacklisted IP's per hour based on the last_change value of the blacklist item """
    return esm.blacklist_per_hour("ip")


@app.route("/blacklist/exist/<string:doc_type>/", methods=['GET'])
def exist_blacklist_item(doc_type):
    """
        Parameters:
        ?id= <ID>

        Checks whether a item with a certain id is present.
    """

    if "id" in request.args:
        id = request.args.get("id")
        return str(esm.exists("blacklist", doc_type, id))
    else:
        return "Missing 'id' variable in request"


@app.route("/blacklist/create/<string:doc_type>/", methods=['GET'])
def create_blacklist_item(doc_type):
    """
        Parameters:
        ?id= <ID>
        ?reason = <reason>

        Creates blacklist item based on a given doc_type, id and reason.
    """

    if "id" in request.args:
        if "reason" in request.args:

            id = request.args.get("id")
            reason = request.args.get("reason")

            reason_l = [
                {
                    "reason": "Blacklisted through API",
                    "data": reason
                }
            ]

            return str(esm.add_to_blacklist(doc_type, id, reason_l, 0.0))
        else:
            "Missing 'reason' variable in request"
    else:
        "Missing 'id' variable in request"


@app.route("/blacklist/delete/<string:doc_type>/", methods=['GET'])
def delete_blacklist_item(doc_type):
    """
        Parameters:
        ?id= <ID>

        Deletes blacklist item based on a given doc_type and id
        Returns True or False if acknowledged
    """

    if "id" in request.args:
        id = request.args.get("id")
        return str(esm.delete("blacklist", doc_type, id))
    else:
        "Missing 'id' variable in request"


@app.route("/cuckoo/get/hour", methods=['GET'])
def cuckoo_saved_hour():
    """ Returns the amount of Cuckoo reports that get saved per hour """
    return esm.cuckoo_reports_per_hour()

@app.route("/whitelist/subnet/add", methods=['POST'])
def add_whitelist_subnet():
    """"
    POST call
    Adds the single subnet to the whitelist. Both the form fields
    'subnet' and 'owner' are required.
    """
    message = ""

    if "subnet" in request.form.keys() and "owner" in request.form.keys():

        subnet = request.form.get("subnet")
        owner = request.form.get("owner")

        try:
            IPSet([subnet])
            if esm.add_whitelist_subnet(subnet, owner):
                message = "success"
                logger.info("Added subnet %s to whitelist", subnet)
            else:
                message = "failed to add to ES. See API log"
                logger.error("Failed to add subnet %s to whitelist", subnet)

        except AddrFormatError as e:
            message = "Invalid subnet format. CIDR notation is required"
            logger.warning("Invalid subnet format %s. Info: %s", subnet, e)
    else:
        message = "owner or subnet field missing"
        logger.warning("Missing owner or subnet field in whitelist add call")

    return "{'message': '%s'}" % message

@app.route("/whitelist/subnet/delete", methods=['POST'])
def delete_whitelist_subnet():
    """"
    POST call
    Deletes the specified single subnet from the whitelist.
    The 'subnet' form field is required.
    """

    message = ""

    if "subnet" in request.form.keys():

        subnet = request.form.get("subnet")
        if esm.delete_whitelist_subnet(subnet):
            message = "success"
            logger.info("Deleted subnet %s from whitelist", subnet)
        else:
            message = "failed to delete subnet from whitelist. See API log"
            logger.error("Failed to delete subnet %s from whitelist", subnet)

    else:
        message = "missing subnet field"
        logger.warning("Missing subnet field in whitelist delete call")

    return "{'message': '%s'}" % message

@app.route("/health_check", methods=['GET'])
def health_check():
        processes = {"BlacklistingTask": "False",
                     "CuckooBinarySubmitTask": "False",
                     "ReportProcessTask": "False",
                     "APIListener": "False"}

        for item in processes:
            for proc in psutil.process_iter():
                if item in proc.cmdline():
                    processes[item] = "True"

        return str(processes)
