import logging
import os


class Log:
    def __init__(self, args, destination):
        """
        Create logger instance and selective_copy.log file
        in the destination folder if logging is turned on
        in command line arguments. If not create only logger instance.
        :param args: Namespace. Command line arguments.
        :param destination: str. Destination folder path.
        """
        self.logger = logging.getLogger("selective_copy")
        self.logger.setLevel(logging.CRITICAL)
        self.log = args.log
        if self.log:
            self.logger.setLevel(logging.INFO)
            fh = logging.FileHandler(
                os.path.join(destination, "selective_copy.log"), encoding="utf-8"
            )
            formatter = logging.Formatter(
                "%(asctime)s %(message)s", "%d.%m.%Y %H:%M:%S"
            )
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

    def close_log(self):
        """
        Close selective_copy.log file and remove it from logger
        file handlers if logging is turned on in command line arguments.
        :return: NoneType.
        """
        if self.log:
            self.logger.handlers[0].close()
            self.logger.handlers = []
            print("Log saved")