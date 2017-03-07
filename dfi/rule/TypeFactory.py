from dfi.blacklist.types.HashType import HashType

class TypeFactory(object):

    TYPE_CLASS_MATCH = {
        "hash": HashType
    }

    @staticmethod
    def type_key_exists(rule_key):
        if rule_key in TypeFactory.TYPE_CLASS_MATCH:
            return True
        return False

    @staticmethod
    def get_type_for_key(type_key, filtered_cuckoo_report):
        """
        Finds the correct class for the type key given and
        return an instance of that class.
        """
        type_class = TypeFactory.TYPE_CLASS_MATCH[type_key]

        type_object = type_class(type_key, filtered_cuckoo_report)
        return type_object
