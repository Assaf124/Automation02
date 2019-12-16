import logging
import os
from Configuration.auto_configuration import Logger


LOG_FILE_PATH = Logger.LOG_FILE_PATH
LOG_MODE = Logger.LOG_FILE_MODE


def init_logger(*args):

    if not os.path.exists(Logger.APPLICATION_MAIN_PATH):
        os.makedirs(Logger.APPLICATION_MAIN_PATH)

    log_files_dir = os.path.join(Logger.APPLICATION_MAIN_PATH, Logger.LOG_DIR_NAME)

    if not os.path.exists(log_files_dir):
        os.makedirs(log_files_dir)
        os.mknod(LOG_FILE_PATH)


    logFormatter = logging.Formatter('%(asctime)s - %(levelname)-12s - %(name)-20s - %(filename)-24s - %(lineno)-4d - %(message)s')
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler(LOG_FILE_PATH, mode=LOG_MODE)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
