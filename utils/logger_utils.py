import logging
from logging.handlers import RotatingFileHandler

FORMATTER = logging.Formatter(fmt='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
                              datefmt='%m-%d-%Y %H:%M:%S %Z')
LOG_FILE = 'logging.log'


def get_console_handler():
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler(filename: str = LOG_FILE):
    file_handler = RotatingFileHandler(filename=filename, maxBytes=50000000, backupCount=3)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    # logger.addHandler(get_console_handler())
    # logger.addHandler(get_file_handler())
    return logger
