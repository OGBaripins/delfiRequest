import logging
import os
import os.path


def get_logger(name, log_config=None):

    log_filename = "logs.log"
    log_format = "%(asctime)s from %(name)s:%(message)s"
    log_datefmt = "%d %b %Y %H:%M:%S"
    log_level = logging.INFO

    logging.basicConfig(
        filename=log_filename,
        format=log_format,
        datefmt=log_datefmt,
        level=log_level
    )

    return logging.getLogger(name)
