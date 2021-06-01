import logging
import requests
import time
import typing
import re

from Conf.page_elements_map import load_page_element

from action_results import ActionResults
from datetime import datetime
from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine
from logger import init_logger
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from Conf.page_elements_map import page_elements
from Configuration.auto_configuration import Settings


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
# LOGGER.setLevel(logging.INFO)


# @dataclass
# class EagleData:
#     username: str
#     password: str
#
#
# class EagleController:
#     def __init__(self, data: EagleData):
#         self.eagle_data = eagle_data


class EagleController:
    def __init__(self, path):
        self.session: typing.Optional[requests.Session] = None
        self.driver = None
        self.device_mac_address = None
        self.network_ssid = None
        self.network_id: int = None
        self.network_key = None
        self.asset_id: int = None
        self.username: str = 'admin'
        self.password: str = 'admin'
        self.element_to_wait_for = None
        self.reverse_element_to_wait_for = None
        self.view_type = None
        self.path = path
        self.page_element: typing.Optional[str] = None
        self.page_state: typing.Optional[str] = None
        self.network_mac_list = list()
        self.networks_info = list()
        self.networks_data_map = {}
        self.probe_info = dict()
        self.wifi_network_info = dict()
        self.tested_network_info = {}
        self.mac_to_asset = {}
        # Next code is for enable Chrome certificate-ignorance
        options = Options()
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--ignore-certificate-errors')
        self.driver = webdriver.Chrome(Settings.PATH_TO_CHROMEDRIVER, chrome_options=options)
        # self.driver.set_window_size(1800, 1024)
        self.driver.maximize_window()
        self.driver.get(self.path)
        LOGGER.debug(f'EagleController object was created')
        # time.sleep(6)

    def click_by_pos(self, x_pos: int, y_pos: int):
        """

        """
        LOGGER.info(f'Click at: {x_pos}, {y_pos}')
        ActionChains(self.driver).move_by_offset(x_pos, y_pos).click().perform()
        # ActionChains(self.driver).move_by_offset(x_pos, y_pos).click().perform().release()

    def verify_login_page_loaded(self):
        """
        Verify that logain page has been loaded successfully
        :return:    True
                    False
        """
        try:
            LOGGER.info(f'Navigating UI to Targets page')
            login_text = self.driver.find_element_by_class_name("form-title font-green").text
            return login_text

        except Exception as error:
            LOGGER.error(f'Login page was not loaded. Got error: {error}')
            return False

    def login(self, username: str, password: str):
        """
        Calling for two sub methods which perform two types of login:
            - login_eagle()
            - login_background()
        :param username: Username
        :param password: Password
        :return:    True for successful login
                    False for unsuccessful login
        """
        self.username = username
        self.password = password
        LOGGER.debug('Performing general login')
        if self.login_eagle(self.username, self.password):
            if self.login_background(self.username, self.password):
                LOGGER.info(f'Performed a successful login')
                return True
        LOGGER.error(f'Failed to perform login')
        return False

    def login_background(self, username: str, password: str):
        """
        Performs login to the Eagle 'in the background' using 'requests' module.
        :param username: Username
        :param password: Password
        :return:    True for successful login
                    False for unsuccessful login
        """
        self.username = username
        self.password = password

        with requests.Session() as self.session:
            data = {"username": self.username, "password": self.password}
            url = f'{self.path}/api/auth/login'
            response = self.session.post(url, json=data, verify=False)
            # Verifying login status
            LOGGER.debug(f'{response}')
            json = response.json()
            if json['status'] == 'Success':
                LOGGER.info(f'Performed a successful background login:  {response.json()}')
                return True
            else:
                LOGGER.error(f'Failed to performed background login:  {response.json()}')
                return False

    def login_eagle(self, username: str, password: str):
        """
        This methos perform login to th eagle managment using selenium.
        :param username: Username
        :param password: Password
        :return:    True for successful login
                    False for unsuccessful login
        """
        try:
            LOGGER.debug(f'performing login (username) using the next username: {self.username}')
            element = self.driver.find_element_by_id('username')
            element.click()
            element.send_keys(self.username)

            LOGGER.debug(f'performing login (password) using the next password: {self.password}')
            element = self.driver.find_element_by_id('password')
            element.click()
            element.send_keys(self.password)
            time.sleep(1)

            LOGGER.debug(f'performing login submit')
            element = self.driver.find_element_by_xpath('//*[@id="app"]/div/form/div[4]/button')
            element.click()
            LOGGER.info(f'Performed a successful UI login')
            time.sleep(1)
            return True

        except Exception as error:
            LOGGER.error(f'Was unable to perform UI login using the username: {self.username} and password: {self.password}.  Got error: {error}')
            return False

    def wait_page_load(self, page_name):
        """

        """
        LOGGER.info(f'Waiting for page to load...')
        self.page_element = load_page_element[page_name]
        LOGGER.debug(f'Verifying page has been loaded according to: {page_name}: {self.page_element}')
        try:
            for i in range(100):
                self.page_state = self.driver.execute_script(f'return document.getElementsByTagName("{self.page_element}");')
                if not self.page_state:
                    time.sleep(0.5)
                    LOGGER.debug(f'Iterator value is: {i}, Page load state is: {self.page_state}')
                else:
                    break
            LOGGER.info(f'Page load state is: {self.page_state}')
            return True

        except Exception as error:
            LOGGER.error(f'Got error: {error}')
            return False

    def navigate_to_home(self):
        """
        Navigates UI to #/Home
        :return:    True for successful operation
                    False for unsuccessful operation
        """
        try:
            LOGGER.info(f'Navigate to Home page')
            self.driver.find_element_by_link_text('Home').click()
            time.sleep(1)
            return True

        except Exception as error:
            LOGGER.error(f'Failed to navigate "Sensors" page. Got error: {error}')
            return False

    def navigate_to_targets(self):
        """
        Navigates UI to #/project/1
        :return:    True for successful operation
                    False for unsuccessful operation
        """
        try:
            LOGGER.info(f'Navigating UI to Targets page')
            self.driver.find_element_by_link_text('Targets').click()
            # self.wait_element_to_load(page_elements['edit_session_pencil'])
            time.sleep(1)
            return True

        except Exception as error:
            LOGGER.error(f'Failed to navigate Targets page. Got error: {error}')
            return False

    def navigate_to_sensors(self):
        """
        Navigates UI to #/interception/devices page
        :return:    True
                    False
        """
        try:
            LOGGER.info(f'Navigate to Sensors page')
            self.driver.find_element_by_css_selector('[data-test="sensor"]').click()
            time.sleep(1)
            return True

        except Exception as error:
            LOGGER.error(f'Failed to navigate "Sensors" page. Got error: {error}')
            return False

    def navigate_to_remote_infections(self):
        """
        Navigates UI to #/remote-infections
        :return:    True for successful operation
                    False for unsuccessful operation
        """
        try:
            LOGGER.info(f'Navigating UI to Remote Infections page')
            self.driver.find_element_by_css_selector('[data-test="remote"]').click()
            time.sleep(1)
            return True

        except Exception as error:
            LOGGER.error(f'Failed to navigate "Remote Infections" page. Got error: {error}')
            return False

    def navigate_to_settings(self):
        """
        Navigates UI to #/maintenance/
        :return:    True for successful operation
                    False for unsuccessful operation
        """
        try:
            LOGGER.info(f'Navigating UI to Settings page')
            self.driver.find_element_by_css_selector('a[data-test="setting"]').click()
            time.sleep(1)
            return True

        except Exception as error:
            LOGGER.error(f'Failed to navigate "Settings" page. Got error: {error}')
            return False

    def open_sensor_interception_page(self):
        """
        Navigates UI to the sensor's interception page
        :return:    True for successful operation
                    False for unsuccessful operation
        """
        try:
            LOGGER.info(f"Opening the sensor's interception page")
            element = self.driver.find_element_by_tag_name("button")
            element.click()
            return True

        except Exception as error:
            LOGGER.error(f'Failed to open interception page. Got error: {error}')
            return False

    def switch_to_new_tab(self):
        """
        Switch the robot focus to the sensor's page
        :return:    True for successful operation
                    False for unsuccessful operation
        """
        try:
            LOGGER.info(f'switching focus to interception page')
            self.driver.switch_to.window(self.driver.window_handles[1])
            time.sleep(3)
            print(f'Current tab title is: {self.driver.title}')
            return True

        except Exception as error:
            LOGGER.error(f'Failed to switch focus. Got error: {error}')
            return False

    def start_scan(self):
        """
        Performing system scan start operation
        :return:    True for successful operation
                    False for unsuccessful operation
        """
        url = f'{self.path}api/interception/scan/start'
        LOGGER.info(f'Sending request to start system scan:  {url}')
        response = self.session.get(url, verify=False)
        # Verifying operation status
        if response.status_code != 200:
            LOGGER.error(f'Did no receive status 200 as expected: {response.status_code}')
            return False
        json = response.json()
        if json['status'] == 'Success':
            LOGGER.info(f'System scan started successfully:  {response.json()}')
            return True
        else:
            LOGGER.error(f'Failed to start System scan:  {response.json()}')
            return False

    def is_scan_running(self):
        """
        Check if system scan is in progress
        :return:    1   system scan is in progress
                    2   no system scan is in progress
                    3   no indication for system scan. maybe because method was executed on the wrong page
                    4   failed to check scan status
        """
        LOGGER.info(f'Checking system scan status...')
        try:
            page_source = self.driver.page_source
            # element = self.driver.find_element_by_css_selector('[data-test="stop_scan"]')
            if re.search('data-test="stop_scan"', page_source) is not None:
                LOGGER.info('System scan is in progress')
                return 1
            if re.search('data-test="start_scan"', page_source) is not None:
                LOGGER.info('No System scan is in progress')
                return 2
            else:
                return 3

        except Exception as error:
            LOGGER.error(f'Failed to check system scan status. Got error: {error}')
            return 4

    def start_scan_ui(self):
        """
        Start system scan by clicking the UI "start Scan" button
        :return:    True
                    False
        """
        try:
            LOGGER.info(f'Starting system scan...')
            self.driver.find_element_by_css_selector('[data-test="start_scan"]').click()
            time.sleep(1)
            return True

        except Exception as error:
            LOGGER.error(f'Was unable to run system scan. Got error: {error}')
            return False

    def stop_scan(self):
        """
        Performing system scan stop operation
        :return:    True for successful operation
                    False for unsuccessful operation
        """
        url = f'{self.path}api/interception/scan/stop'
        LOGGER.info(f'Got request to stop system scan: {url}')
        response = self.session.get(url, verify=False)
        # Verifying operation status
        if response.status_code != 200:
            LOGGER.error(f'Did no receive status 200 as expected: {response.status_code}')
            return False
        json = response.json()
        if json['status'] == 'Success':
            LOGGER.info(f'System scan stopped successfully:  {response.json()}')
            return True
        else:
            LOGGER.error(f'Failed to stop System scan:  {response.json()}')
            return False

    def stop_scan_ui(self):
        """
        Stops system scan by clicking the UI "stop Scan" button
        :return:    True
                    False
        """
        try:
            LOGGER.info(f'Stopping system scan...')
            self.driver.find_element_by_css_selector('[data-test="stop_scan"]').click()
            time.sleep(1)
            return True

        except Exception as error:
            LOGGER.error(f'Was unable to stop system scan. Got error: {error}')
            return False

    def switch_main_view(self, view_type: str):
        """
        Switch the device list page view - can be table view or grid view
        :param  view_type: table | grid
        :return:    True
                    False
        """
        self.view_type = view_type
        LOGGER.info(f'Got request to switch to: {self.view_type} view')
        try:
            if self.view_type == 'table':
                # element = self.driver.find_element_by_xpath(page_elements['table'])
                element = self.driver.find_element_by_css_selector('[data-test="table_view"]')
                element.click()
                LOGGER.info(f'Switching to table view')
                return True
            elif self.view_type == 'grid':
                element = self.driver.find_element_by_css_selector('[data-test="grid_view"]')
                element.click()
                LOGGER.info(f'Switching to grid view')
            else:
                LOGGER.warning(f'the requested view: {self.view_type} is not supported')
                return False

        except Exception as error:
            LOGGER.error(f'Failed to switch view. Got error: {error}')
            return False

    def run_search(self, search_field: str, search_string: str, clear_search: bool):
        """
        Run search in accordance with 'field_name'
        :param:     search_field    accept the next strings: device | network
        :param:     search_string   the searched string
        :param:     clear_search    if True, clear search field once done with search. otherwise leave field with text
        :return:    True
                    False
        """
        LOGGER.info(f'Run {search_field} search on next string: {search_string}')
        try:
            if search_field == 'device':
                data_test_field_string = '[data-test="device_search"] input'
            elif search_field == 'network':
                data_test_field_string = '[data-test="network_search"]'
            else:
                LOGGER.error(f'The input parameter: {search_field} - is not supported')
                return False
            element = self.driver.find_element_by_css_selector(data_test_field_string)
            element.click()
            time.sleep(1)
            element.send_keys(search_string)
            time.sleep(1)
            element.send_keys(Keys.RETURN)
            time.sleep(1)
            if search_field == 'device':
                time.sleep(10)
                elements = self.driver.find_elements_by_css_selector('[data-test="device_item"]')
                LOGGER.debug(f'elements long is: {len(elements)}\n{elements}')
                if len(elements) == 1:
                    LOGGER.info(f'The tested device, {search_string}, was detected')
                    if clear_search:
                        self._clear_search_field('device')
                    return True
                else:
                    LOGGER.info(f'Was not able to detect {search_string} device')
                    if clear_search:
                        self._clear_search_field('device')
                    return False

            if search_field == 'network':
                elements = self.driver.find_elements_by_css_selector('[data-test="network_item"]')
                if len(elements) == 2:
                    LOGGER.info(f'The tested network, {search_string}, was detected')
                    if clear_search:
                        self._clear_search_field('network')
                    return True
                else:
                    LOGGER.info(f'Was not able to detect {search_string} network')
                    if clear_search:
                        self._clear_search_field('network')
                    return False

        except Exception as error:
            LOGGER.error(f'Failed to run {search_field} search for {search_string} string. Got error: {error}')
            return False

    def _clear_search_field(self, field_name: str):
        """
        Clear search field according to 'field_name'
        :param:     field_name      accept the next strings: device | network
        :return:    True
                    False
        """
        LOGGER.info(f'Clearing the {field_name} search field')
        try:
            if field_name == 'device':
                data_test_string = '[data-test="clear_search"]'
                self.driver.find_element_by_css_selector(data_test_string).click()
            elif field_name == 'network':
                data_test_string = '[data-test="network_search"]'
                element = self.driver.find_element_by_css_selector(data_test_string)
                element.click()
                time.sleep(1)
                element.send_keys(Keys.CONTROL, 'a')
                time.sleep(1)
                element.send_keys(Keys.DELETE)
            else:
                LOGGER.error(f'The input parameter: {field_name} - is not supported')
                return False
            return True

        except Exception as error:
            LOGGER.error(f'Failed to clear {field_name} search field. Got error: {error}')
            return False

    def click_top_device(self):
        """
        Click on the device at list top
        :return:    True
                    False
        """
        LOGGER.info(f'Fetching top list device')
        try:
            elements = self.driver.find_elements_by_css_selector('[data-test="device_item"]')
            # LOGGER.debug(f'Found the next {len(elements)} device items:\n{elements}')
            elements[0].click()
            LOGGER.info(f'Clicked on top list device')
            return True

        except Exception as error:
            LOGGER.error(f'Failed to fetch device top list info. Got error: {error}')
            return False

    def navigate_to_device_info(self):
        """
        Navigate to a selected device info page
        :param:     TBD
        :return:    True | False
        """
        try:
            LOGGER.info(f'Navigating to device info page')
            # self.driver.find_element_by_link_text('Device Information').click()
            self.driver.find_element_by_xpath('/html/body/div[2]/div/div/div[3]/div[1]/div[1]/div[2]/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div[1]/button').click()
            return True

        except Exception as error:
            LOGGER.error(f'{error}')
            return False

    def fetch_network_data(self, network_bssid: str):
        """
        Fetches /api/interception/networks json response and parse it.
        Search for the tested Access Point details.
        :return:    True
                    False
        """
        LOGGER.info(f'Trying to fetch tested network data')
        url = f'{self.path}api/interception/networks'
        LOGGER.debug(f'Sending request:  {url}')

        try:
            response = self.session.get(f'{url}', verify=False)
            LOGGER.debug(f'received response: {response}')
            # Verifying server status code
            if response.status_code != 200:
                LOGGER.info(f'Did not receive code 200, but the next status code:  {response.status_code}')
                return False
            # Verifying json status
            json = response.json()
            if json['status'] == 'Success':
                LOGGER.debug(f'Was able to fetch networks data:  {response.json()}')
                for i in json["networks"]:
                    if i["bssid"] == network_bssid:
                        self.tested_network_info['channel'] = [i['channel']]
                        self.tested_network_info['ssid'] = [i['ssid']]
                        self.tested_network_info['encryption'] = [i['encryption']]
                    return True
            else:
                LOGGER.error(f'Did not receive "Success" status:\n  {response.json()}')
                return False

        except Exception as error:
            LOGGER.error(f'Failed to fetch networks data. Got error: {error}')
            return False

    def fetch_data_from_db(self):
        """
        Fetch all data which is relevant for automation (such as Networks ssid, devices's MAC's etc ...) from database
        :param:
        :return:    True
                    False
        """
        LOGGER.info(f'Query DB for data')
        try:
            server = SSHTunnelForwarder(
                (Settings.SSH_TUNNEL_HOST, Settings.SSH_TUNNEL_PORT),
                ssh_password=Settings.SSH_TUNNEL_PASSWORD,
                ssh_username=Settings.SSH_TUNNEL_USERNAME,
                remote_bind_address=(Settings.LOCAL_DB_IP, Settings.LOCAL_DB_PORT)
            )

            server.start()

            # db parameters
            user = Settings.LOCAL_DB_USERNAME
            password = Settings.LOCAL_DB_PASSWORD
            host = Settings.LOCAL_DB_HOST
            port = server.local_bind_port
            db = Settings.LOCAL_DB_NAME

            # connect to db and run queries
            uri = f'mysql+mysqldb://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4'
            engine = create_engine(uri, echo=False, pool_pre_ping=True)
            con = engine.connect()

            # Build MAC to Asset correlation
            result = con.execute("SELECT id, mac_address FROM device;").fetchall()
            LOGGER.debug(f'Successfully queried device info')
            for pair in result:
                self.mac_to_asset[pair[1]] = pair[0]
            LOGGER.debug(f'Successfully populated MAC to Asset data structure')

            # Build probe_info data structure {'ssid': ['id', 'asset_id', 'ssid', did_connect, wifi_network_id]}
            probe_info = con.execute('SELECT * FROM apollo.probe;').fetchall()
            LOGGER.debug(f'Successfully queried probe info')
            for item in probe_info:
                self.probe_info[item[2]] = item
            LOGGER.debug(f'Successfully populated probe_info data structure')

            # Build wifi_network_info data structure {'ssid': [id, bssid, ssid, encryption, key, channel]}
            wifi_network_info = con.execute('SELECT id, bssid, ssid, encryption, channel FROM apollo.wifi_network;').fetchall()
            LOGGER.debug(f'Successfully queried wifi_network info')
            for item in wifi_network_info:
                self.wifi_network_info[item[2]] = item
            LOGGER.debug(f'Successfully populated wifi_network_info data structure')

            # close connection
            con.invalidate()
            con.close()
            server.stop()
            return True

        except Exception as error:
            LOGGER.error(f'Failed to fetch data from DB. Got error: {error}')
            return False

    def start_network_scan(self, id):
        """
        TBD...
        :param ssid:
        :return:
        """
        try:
            LOGGER.info(f'Sending request to start network scan on network id: {id}')
            url = f'{self.path}api/interception/network/scan/start'
            payload = {"network_id": id}
            response = self.session.post(url, json=payload, verify=False)
            LOGGER.debug(f'Sent request to start network scan on network id: {id}. Got response: {response}')
            time.sleep(1)
            return True

        except Exception as error:
            LOGGER.error(f'failed to start network scan on network id {id}. Got error; {error}')
            return False

    def stop_network_scan(self, id):
        """
        TBD...
        """
        try:
            LOGGER.info(f'Sending request to stop network scan on network id: {id}')
            url = f'{self.path}api/interception/network/scan/stop'
            payload = {"network_id": id}
            response = self.session.post(url, json=payload, verify=False)
            LOGGER.debug(f'Sent request to stop network scan on network id: {id}. Got response: {response}')
            time.sleep(1)
            return True

        except Exception as error:
            LOGGER.error(f'Failed to stop network scan. Got error: {error}')
            return False

    def _fetch_network_id(self, network_ssid):
        """
        Fetch network id
        :param:     network_ssid
        :return:    network_id
                    None
        """
        LOGGER.info(f'Query DB for network id info')
        try:
            server = SSHTunnelForwarder(
                (Settings.SSH_TUNNEL_HOST, Settings.SSH_TUNNEL_PORT),
                ssh_password=Settings.SSH_TUNNEL_PASSWORD,
                ssh_username=Settings.SSH_TUNNEL_USERNAME,
                remote_bind_address=(Settings.LOCAL_DB_IP, Settings.LOCAL_DB_PORT)
            )

            server.start()

            # db parameters
            user = Settings.LOCAL_DB_USERNAME
            password = Settings.LOCAL_DB_PASSWORD
            host = Settings.LOCAL_DB_HOST
            port = server.local_bind_port
            db = Settings.LOCAL_DB_NAME

            # connect to db and run query
            uri = f'mysql+mysqldb://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4'
            engine = create_engine(uri, echo=False, pool_pre_ping=True)
            con = engine.connect()
            result = con.execute(f"SELECT id FROM apollo.wifi_network WHERE ssid = '{network_ssid}';").fetchall()

            # close connection
            con.invalidate()
            con.close()
            server.stop()
            return result

        except Exception as error:
            LOGGER.error(f'{error}')
            return None

    def acquire_device(self, device_mac: str, network_ssid: str):
        """
        Acquire device
        :param device_mac: device MAC address
        :param network_ssid: network identifier
        :return:    True
                    False
        """
        try:
            self.asset_id = self.mac_to_asset[device_mac]
            # self.network_id = network_id
            network_id = self.probe_info[network_ssid][0]
            LOGGER.info(f'Acquiring device. MAC: {device_mac}/asset id: {self.asset_id} on network {network_id}')
            data = dict(
                acquire_method=0,
                asset_id=self.asset_id,
                network_id=network_id,
                network_name='',
                encryption_type='',
                key='',
                is_current='true',
                phishing=0,
                silent=0
            )
            url = f'{self.path}api/acquire'
            LOGGER.debug(f'Issuing POST request: {url}  and body: {data}')
            response = self.session.post(url, json=data, verify=False)
            if response.status_code != 200:
                LOGGER.error(f'Did not receive the expected status code 200. Got {response.status_code}')
                return False
            if not response.ok:
                raise IOError(f'Request failed {response}')
            json = response.json()
            LOGGER.debug(f'Got response: {json}')
            LOGGER.debug(f'Successfully acquired device: {device_mac}')
            return json['status'] == 'Success'

        except Exception as error:
            LOGGER.error(f'failed to acquire device. Gor error: {error}')
            return False

    def acquire_device_ui(self):
        """
        Acquire device by clicking the 'acquire' button
        :return:    True
                    False
        """
        try:
            pass
            return True

        except Exception as error:
            LOGGER.error(f'{error}')
            return False

    def stop_acquire(self, device_mac: str):
        """
        Release device mitm
        :param device_mac: device MAC address
        :return: True | False
        """
        self.asset_id = self.mac_to_asset[device_mac]
        LOGGER.info(f'Let go device - asset id: {self.asset_id}')
        try:
            data = dict()
            data['asset_id'] = self.asset_id

            url = f'{self.path}api/acquire/let-go'
            LOGGER.debug(f'Issuing POST request: {url}  and body: {data}')
            response = self.session.post(url, json=data, verify=False)
            json = response.json()
            LOGGER.debug(f'Got response: {json}')
            # if not response.ok:
            #     raise IOError(f'Let-Go request failed {response}')
            LOGGER.debug(f'Successfully let-go device: {device_mac}')
            return json['status'] == 'Success'

        except Exception as error:
            LOGGER.error(f'Got error: {error}')
            return False

    def is_browsing_history(self, verify_url=False, url_to_verify=None):
        """
        Verify if browsing history is active. If verify_url=True than method will verify if url_to_verify is exist
        in browsing history list. in case verify_url=True then url_to_verify has to be supplied too.
        :return:    True
                    False
        """
        LOGGER.info(f'Navigating to Browsing History...')
        try:
            self.driver.find_element_by_link_text('Browsing History').click()
            time.sleep(1)
            elements = self.driver.find_elements_by_tag_name('tr td')
            LOGGER.debug(f'Found the next history elements: {[x.text for x in elements[::3]]}')
            LOGGER.info(f'Last url was {elements[0].text} at: {elements[2].text}')
            # elements[2].text holds timestamp in the format of 'YYYY-MM-DD HH-MM-SS'
            epoch_time_value = self._convert_str_to_epoch(elements[2].text)
            time_diff = self._verify_time_difference(epoch_time_value)
            if time_diff == ActionResults.VALID_TIME_DIFFERENCE:
                return True
            elif time_diff == ActionResults.INVALID_TIME_DIFFERENCE:
                return False
            if verify_url:
                self._is_exist_url(elements, url_to_verify)
                return True

        except Exception as error:
            LOGGER.error(f'Got error: {error}')
            return False

    def _verify_time_difference(self, timestamp: float):
        """
        :param:     timestamp               in the format of epoch time
        :return:    enum: ReturnValue.YES   in case the time difference between input timestamp and local time <60 sec
                    enum: ReturnValue.NO    in case the time difference between input timestamp and local time >60 sec
                    enum: ReturnValue.ERROR in case of exception
        """
        try:
            local_time = datetime.now()
            LOGGER.info(f'Current local time is: {local_time}')
            LOGGER.debug(f'Input timestamp: {timestamp}  |  Local time is: {datetime.now().timestamp()}')

            if datetime.now().timestamp() - timestamp < 60:
                LOGGER.info(f'Found time difference between last URL timestamp and local time <60 seconds')
                return ActionResults.VALID_TIME_DIFFERENCE
            else:
                LOGGER.info(f'Found time difference between last URL timestamp and local time >60 seconds')
                return ActionResults.INVALID_TIME_DIFFERENCE

        except Exception as error:
            LOGGER.error(f'Was not able to calculate time difference. Got error: {error}')
            return ActionResults.ERROR

    def _convert_str_to_epoch(self, timestamp: str):
        """
        :return:    epoch_time  an epoch time value (float)
                    None
        """
        try:
            time_stamp = timestamp.split()
            date_value = time_stamp[0].split('-')
            time_value = time_stamp[1].split(':')
            epoch_time = datetime(int(date_value[0]), int(date_value[1]), int(date_value[2]), int(time_value[0]), int(time_value[1]), int(time_value[2])).timestamp()
            LOGGER.info(f'Converted the timestamp: {timestamp} to epoch format: {epoch_time}')
            return epoch_time

        except Exception as error:
            LOGGER.error(f'')
            return None

    def _is_exist_url(self, selenium_elements: list, url: str):
        """
        Match input url with browsing history urls
        :param:     selenium_elements   a list of selenium elements in the form of 'url | type | timestamp'
        :param:     url                 the url to be matched with.
        :return:    tuple (url, timestamp)
                    None
        """
        pass

    def verify_network_key(self, network_id: int, network_key: str):
        """
        TBD...
        :param network_id:
        :param network_key:
        :return:
        """
        LOGGER.info('Verifying network key')
        self.network_id = network_id
        self.network_key = network_key
        try:
            url = f'{self.path}interception/encryption/verify?network_id={self.network_id}&key={self.network_key}'
            LOGGER.debug(f'Sending request:  {url}')
            response = self.session.get(url, verify=False)
            json = response.json()
            LOGGER.debug(f'Got response: {json}')
            if json['status'] == 'Success':
                url = f'{self.path}interception/encryption/key?network_id={self.network_id}&key={self.network_key}'
                LOGGER.debug(f'Sending request:  {url}')
                response = self.session.get(url, verify=False)
                json = response.json()
                LOGGER.debug(f'Got response: {json}')
                if json['status'] == 'Success':
                    return True
                else:
                    LOGGER.error('Got error while verifying network key')
                    return False
        except:
            LOGGER.error(f'failed to verify network key')
            return False

    def refresh(self):
        """
        Refreshing the web page
        """
        LOGGER.debug(f'Refreshing page')
        try:
            self.driver.refresh()
            return True

        except Exception as error:
            LOGGER.debug(f'Failed to refresh web page. Got error: {error}')
            return False

    def is_detecting_ap(self, network_ssid):
        """
        Check if a specific access point was detected and displayed on Eagle managment
        :param:     network_ssid
        :return:    True
                    False
        """
        try:
            LOGGER.debug(f'Checking if network {network_ssid} was detected by Eagle')
            element = self.driver.find_element_by_xpath(page_elements['network_search_box'])
            element.click()
            element.send_keys(network_ssid)
            try:
                element = self.driver.find_element_by_css_selector("(//div[@class='clearfix mt-list-item network-item'])[1]")
                LOGGER.debug(f'Network {network_ssid} was found')
                return True
            except Exception as error:
                LOGGER.error(f'Did not find network: {network_ssid}')
                return False

        except Exception as error:
            LOGGER.error(f'Got error: {error}')
            return False

    def end_session(self):
        """

        """
        try:
            self.driver.quit()
            LOGGER.info(f'Ended Chrome session')
            return True

        except Exception as error:
            LOGGER.error(f'Was unable to close Chrome session. Got Error: {error}')
            return False


if __name__ == '__main__':
    print(f'{time.localtime()} Start...')
    init_logger()
    mac1 = 'ac:5f:3e:60:28:3c'
    mac2 = 'b5:e8:74'
    mac3 = 'a:'
    eagle = EagleController(Settings.EAGLE_HOME_PAGE_1)
    eagle.wait_page_load('login_page')
    eagle.login('admin', 'admin')
    eagle.wait_page_load('cube_page')
    time.sleep(5)
    eagle.navigate_to_sensors()
    # eagle.wait_page_load('sensors_page')
    time.sleep(15)
    # eagle.start_scan_ui()
    # time.sleep(30)
    eagle.switch_main_view('table')
    # print(eagle.is_scan_running())
    time.sleep(5)
    # eagle.run_search('network', 'Test', True)
    # time.sleep(5)
    # eagle.run_search('device', mac1, True)
    # time.sleep(5)

    eagle.click_top_device()
    time.sleep(5)
    eagle.navigate_to_device_info()

    time.sleep(5)
    eagle.is_browsing_history()
    # time.sleep(10)
    # print(eagle.is_scan_running())
    # time.sleep(5)
    # eagle.navigate_to_home()
    # time.sleep(5)
    # print(eagle.is_scan_running())
    # eagle.search_network('Test_AP')
    # eagle.open_sensor_interception_page()
    # time.sleep(10)
    # eagle.switch_to_new_tab()
    # time.sleep(3)
    # eagle.switch_main_view('table')
    # time.sleep(5)
    # eagle.search_device('04:d6:aa:e0:f7:83')
    # time.sleep(5)
    # eagle.stop_scan_ui()

    # eagle.click_by_pos(220, 20)
    # time.sleep(10)
    # eagle.click_by_pos(110, 20)
    # time.sleep(10)
    # eagle.click_by_pos(30, 20)
    # time.sleep(5)
    # eagle.stop_scan_ui()
    time.sleep(5)
    eagle.end_session()
    print('End')
