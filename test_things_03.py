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

    def test_it(self):
        self.headers = {'x-access-token': '92096e5152c61f0d3f5c64a3e89fa55e'}
        response = requests.get(f'{self.path}', headers=self.headers, verify=False)
        # LOGGER.info(f'\n1:  {response}\n2:  {response.content}\n3:  {response.json()}')
        LOGGER.info(f'{response.json()}')
        data = response.json()
        print(data['result'])


if __name__ == '__main__':
    init_logger()
    LOGGER.info('*** Staring ***')
    path = r'https://api.openuv.io/api/v1/uv?lat=31.162&lng=34.74&dt=2018-03-14T15:40:00.000Z'
    eagle = EagleManager(path)
    time.sleep(1)
    eagle.test_it()
