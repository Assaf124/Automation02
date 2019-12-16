import time
import requests
import logging
from Configuration.auto_configuration import Settings
from logger import init_logger


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
# LOGGER.setLevel(logging.INFO)


class EagleManager:
    def __init__(self, path):
        self.path = path
        self.username = ''
        self.password = ''

    def login(self, username, password):
        """
        Performs login to the Eagle management
        :param username: Username
        :param password: Password
        :return:    True for successful login
                    False for unsuccessful login
        """
        self.username = username
        self.password = password

        with requests.Session() as self.session:
            data = {"username": self.username, "password": self.password}
            response = self.session.post(f'{self.path}/auth/login', json=data, verify=False)
            # Verifying login status
            json = response.json()
            if json['status'] == 'Success':
                LOGGER.info(f'Logged-in successfully to the system:  {response.json()}')
                return True
            else:
                LOGGER.error(f'Failed to login the system:  {response.json()}')
                return False

    def start_scan(self):
        """
        Performing system scan start operation
        :return:    True for successful operation
                    False for unsuccessful operation
        """
        response = self.session.get(f'{self.path}/interception/scan/start', verify=False)
        # Verifying operation status
        json = response.json()
        if json['status'] == 'Success':
            LOGGER.info(f'System scan started successfully:  {response.json()}')
            return True
        else:
            LOGGER.error(f'Failed to start System scan:  {response.json()}')
            return False

    def stop_scan(self):
        """
        Performing system scan stop operation
        :return:    True for successful operation
                    False for unsuccessful operation
        """
        response = self.session.get(f'{self.path}/interception/scan/stop', verify=False)
        # LOGGER.info(f'\n1:  {response}\n2:  {response.content}\n3:  {response.json()}')
        # Verifying operation status
        json = response.json()
        if json['status'] == 'Success':
            LOGGER.info(f'System scan stopped successfully:  {response.json()}')
            return True
        else:
            LOGGER.error(f'Failed to stop System scan:  {response.json()}')
            return False


if __name__ == '__main__':
    init_logger()
    LOGGER.info('*** Staring ***')
    path = r'https://172.16.10.1'
    eagle = EagleManager(path)
    time.sleep(3)
    LOGGER.info('Log-in')
    eagle.login('admin', 'admin')
    time.sleep(5)
    LOGGER.info('Starting scan')
    eagle.start_scan()
    time.sleep(30)
    LOGGER.info('Stopping scan')
    eagle.stop_scan()