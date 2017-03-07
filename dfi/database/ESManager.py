import logging
import time
import sys
from elasticsearch import Elasticsearch, helpers
from elasticsearch import ElasticsearchException

from dfi.Config import Config

logger = logging.getLogger(__name__)


class ESManager(object):

    CONNECTION_TESTED = False

    def __init__(self):
        self.es_url = "%s:%s" % (Config.ELASTICSEARCH_IP,
                                 Config.ELASTICSEARCH_PORT)
        self.es = Elasticsearch(self.es_url, timeout=30)

        if not ESManager.CONNECTION_TESTED:
            self.es_test_connection()

    def es_test_connection(self):

        ESManager.CONNECTION_TESTED = True

        try:
            self.es.info()
        except Exception as e:
            logger.error("Error connecting to ES. Exiting.. Error: %s", e)
            sys.exit(1)

    def store_json_object(self, index, doc_type, id, json_body):
        """
        Stores the given json dictionary as the given type in the
        given index. Return True on success, False on fail
        """

        success = False
        try:
            self.es.index(
                index=index,
                doc_type=doc_type,
                id=id,
                body=json_body
            )
            success = True

            logger.info("Stored new %s in %s", doc_type, index)
        except ElasticsearchException as e:
            logger.error("Error storing json object: %s", e)

        return success

    def update_count(self, id):
        """
        Fetches the count field in the 'hashes' indice, adds 1 to this value and updates the field.
        Returns True if the operation gone normal. Returns False on any error occasion.
        """
        try:
            result = self.es.get(
                index="hashes",
                doc_type="item",
                id=id,
                fields="counter"
            )

            old_value = str(result["fields"]["counter"]).strip("[]")
            new_value = int(old_value) + 1

            result = self.es.update(
                index="hashes",
                doc_type="item",
                id=id,
                body={
                    "doc": {
                        "counter": new_value
                    }
                }
            )
            return True
        except:
            logger.error("Failed updating count variable in 'hashes' indice of id %s", id)
            return False

    def exists(self, index, doctype, id):
        result = self.es.exists(index=index, doc_type=doctype, id=id)
        return result

    def delete(self, index, doctype, id):
        try:
            self.es.delete(index=index, doc_type=doctype, id=id)
            logging.info("Deleted ID %s (doctype: %s, indice: %s", id, doctype, index)
            return True
        except:
            logging.error("Deleted failed from ID %s (doctype: %s, indice: %s", id, doctype, index)
            return False

    def all_id(self, index):
        IDList = []

        result = self.es.search(
            index=index,
            fields="_id",
            size=10000
        )

        for item in result["hits"]["hits"]:
            IDList.append(str(item["_id"]).strip("[]"))

        return IDList

    def id_time_range(self, index, from_time):
        IDList = []

        result = self.es.search(
            index=index,
            fields="_id",
            size=10000,
            body={
                "query": {
                    "range": {
                        "last_change": {
                            "gte": str(from_time * 1000),
                            "lte": str(int(time.time() * 1000))
                        }
                    }
                }
            }
        )

        for item in result["hits"]["hits"]:
            IDList.append(str(item["_id"]).strip("[]"))

        return IDList

    def new_queue_item(self, binaryhash, taskid):
        try:
            result = self.es.index(index="queue", doc_type="item",
                                   id=binaryhash, body={
                    "timestamp": int(time.time() * 1000),
                    "task_id": taskid
                })
            return True
        except ElasticsearchException as e:
            # Log if somethings goes wrong.
            logger.error("Error creating queue item: %s", e)
            return False

    def get_queue_length(self):
        """
        returns the length of the queue
        """

        json_ans = self.es.count(index="queue", doc_type="item")

        return json_ans["count"]

    def get_cuckoo_queue_items(self, max_items):
        """
        Gets most recent queuing items with a max of max_items
        """

        # get count before query. Es has issues with sorting if results is 0
        # it will not simple return 0. Instead the lib throws an exception
        json_ans = self.es.count(index="queue", doc_type="item")

        if json_ans["count"] < 1:
            return []

        cuckoo_id_list = []
        result = self.es.search(
            index="queue",
            doc_type="item",
            sort="timestamp:asc",
            size=max_items,
            fields="task_id",
            _source=False
        )

        for item in result["hits"]["hits"]:
            cuckoo_id_list.extend(item["fields"]["task_id"])
        return cuckoo_id_list

    def get_cuckoo_queue_item_ids(self, cuckoo_id):
        """
        Searches for all queue items containing the specified cuckoo id
        and returns a list containing their document IDs
        """

        queue_item_ids = []

        results = self.es.search(
            index="queue",
            doc_type="item",
            fields="_id",
            body={
                "query": {
                    "match": {
                        "task_id": cuckoo_id
                    }
                }
            }
        )

        for result in results["hits"]["hits"]:
            queue_item_ids.append(result["_id"])
        return queue_item_ids

    def count_items(self, index, doctype):
        """
        Counts all items in an index.
        doctype can be empty to select all documents in an index
        """
        if "all" in doctype:
            doctype = ""

        result = self.es.count(
            index=index,
            doc_type=doctype
        )

        return str(result["count"])

    def cuckoo_reports_per_hour(self):
        """ Returns the amount of saved cuckoo reports per hour """

        result = self.es.count(
            index="cuckoo",
            doc_type="report",
            body={
                "query": {
                    "range": {
                        "date": {
                            "gte": "now-1h",
                            "lte": "now"
                        }
                    }
                }
            }
        )

        return str(result["count"])

    def blacklist_per_hour(self, doctype):
        """
        Calculates items(hashes or IP's) that were changed in the last hour and returns this JSON format.
        """
        result = self.es.count(
            index="blacklist",
            doc_type=doctype,
            body={
                "query": {
                    "filtered": {
                        "filter": {
                            "range": {
                                "last_change": {
                                    "gte": "now-1h",
                                    "lte": "now"
                                }
                            }
                        }
                    }
                }
            }
        )

        return str(result["count"])

    def get_unprocessed_reports_source(self, amount):

        results = {}
        try:
            results = self.es.search(
                index="cuckoo",
                doc_type="report",
                body={
                    "query": {
                        "match": {
                            "processed": False
                        }
                    }
                },
                size=amount
            )
        except ElasticsearchException as e:
            logger.error("Error getting unprocessed reports: %s", e)

        source_results = []

        for result in results["hits"]["hits"]:
            source_results.append(
                result["_source"]
            )

        return source_results


    def get_unprocessed_reports(self, amount,
                                fields=["md5", "signature.name", "signature.severity", "ip"]):
        """
        Returns a list of unprocessed Cuckoo reports only containing
        the specified fields in fields
        """

        results = {}

        try:
            results = self.es.search(
                index="cuckoo",
                doc_type="report",
                body={
                    "query": {
                        "match": {
                            "processed": False
                        }
                    }
                },
                fields=",".join(fields),
                size=amount
            )

        except ElasticsearchException as e:
            logger.error("Error getting unprocessed reports: %s", e)

        result_list = []
        for report in results["hits"]["hits"]:
            result = {
                "_id": report["_id"]
            }

            if not "fields" in report:
                continue

            for field in report["fields"]:
                if field in fields:
                    result[field] = report["fields"][field]

            result_list.append(result)

        return result_list

    def set_processed_bulk(self, id_list):
        """
        Update processed to True for the specified list
        of Cuckoo ids.
        """

        success = False
        processed_ids = []

        for id in id_list:
            processed_id = {
                "_op_type": "update",
                "_index": "cuckoo",
                "_type": "report",
                "_id": id,
                "doc": {
                    "processed": True
                }
            }

            processed_ids.append(processed_id)
        try:
            helpers.bulk(self.es, processed_ids)
            success = True

            logger.info("Updated %s reports to processed" % len(processed_ids))

        except ElasticsearchException as e:
            logger.error("Error setting processed to True in bulk: %s" % e)

        return success

    def add_to_blacklist(self, doc_type, id, reason, score):
        """
        Add specified ID to specified Doc_type with blacklisted value to True
        """
        if self.exists("blacklist", doc_type, id):
            logger.info("%s %s already blacklisted", doc_type, id)
        else:
            return self.store_json_object("blacklist", doc_type, id,
                                          {
                                              "last_change": int(time.time() * 1000),
                                              "reason": reason,
                                              "score": score
                                          }
                                          )

    def add_whitelist_subnet(self, subnet, owner):
        """
        Adds the specified ip subnet to the whitelist indice in ES.
        The expected format is CIDR. So 192.168.0.0/24
        """

        whitelist_item = {
            "owner": owner
        }

        return self.store_json_object("whitelist", "subnet",
                                      subnet, whitelist_item)

    def delete_whitelist_subnet(self, subnet):
        """
        Deletes the specified subnet from the whitelist
        """

        return self.delete("whitelist", "subnet", subnet)

    def get_subnet_whitelist(self, start, limit):

        try:
            results = self.es.search(
                index="whitelist",
                doc_type="subnet",
                fields="_id",
                from_=start,
                size=limit
            )

            subnet_list = []

            for subnet in results["hits"]["hits"]:
                subnet_list.append(subnet["_id"])

            return subnet_list

        except ElasticsearchException as e:
            logger.error("Error getting whitelisted subnets: %s", e)
