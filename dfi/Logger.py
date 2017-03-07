import logging

from dfi.Config import Config


class Logger(object):

    @staticmethod
    def setup_logger(filename):
        logformat  = "[%(asctime)s %(levelname)s %(name)s] %(message)s"
        dateformat = "%d-%m-%y %H:%M:%S"
        logpath    = filename

        logging.basicConfig(filename=logpath, filemode='a',
                            format=logformat,  datefmt=dateformat,
                            level=Logger.get_log_level())

        console           = logging.StreamHandler()
        formatter         = logging.Formatter(logformat)
        formatter.datefmt = dateformat

        console.setFormatter(formatter)
        logging.getLogger().addHandler(console)

        # set other loggers to higher levels
        logging.getLogger("elasticsearch").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)

    @staticmethod
    def get_log_level():
        level = logging.INFO
        if Config.LOG_LEVEL.upper() in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            level = getattr(logging, Config.LOG_LEVEL.upper())
        else:
            print("Unknown log level %s. Using info level" % level)

        return level