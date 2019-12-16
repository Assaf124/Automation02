import logging
import os
from pathlib import Path
from logger import init_logger
import re
from Configuration.auto_configuration import Settings
import subprocess
import time


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
# LOGGER.setLevel(logging.INFO)


class CSVManager:
    def __init__(self, file_name):
        """
        The __init__ method create a .csv file which holds the tests results.
        :param file_name:   the .csv file file
        """
        self.file_name = file_name
        self.entry_params = ''

        path = Path('./CSVs')
        path.mkdir(parents=True, exist_ok=True)
        self.file_path = os.path.join(path, self.file_name)

        self.file = open(self.file_path, "w")
        self.file.write('Test Start Time,Test Name,Result\n')
        self.file.close()
        LOGGER.info(f'csv file {self.file_name} was created successfully')

    def add_entry(self, file_name, entry_params):
        self.file_name = file_name
        self.entry_params = entry_params
        self.file = open(self.file_path, "w")
        self.file.write(f'{self.entry_params}\n')
        self.file.close()
        LOGGER.info(f'csv file {self.file_name} was created successfully')


if __name__ == '__main__':
    test_file = CSVManager('test_01.csv')

