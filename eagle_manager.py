import logging
import requests
import time
from logger import init_logger
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from Conf.page_elements_map import page_elements
from selenium.webdriver.common.keys import Keys
from Configuration.auto_configuration import Settings
import subprocess
import re
# import org.openqa.selenium.Keys


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
# LOGGER.setLevel(logging.INFO)


class EagleController:
    def __init__(self, path):
        self.session = ''
        self.driver = ''
        self.device_mac_address = ''
        self.network_ssid = ''
        self.username = 'admin'
        self.password = 'admin'
        self.element_to_wait_for = ''
        self.reverse_element_to_wait_for = ''
        self.view_type = ''
        self.element_to_look_for = ''
        self.path = path
        self.driver = webdriver.Chrome(Settings.PATH_TO_CHROMEDRIVER)
        self.driver.set_window_size(1800, 1024)
        # self.driver.maximize_window()
        # self.driver.get(Settings.EAGLE_HOME_PAGE_1)
        self.driver.get(self.path)
        LOGGER.info(f'EagleController object was created')
        time.sleep(1)

    def login(self, username, password):
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
        if self.login_eagle(self.username, self.password):
            if self.login_background(self.username, self.password):
                LOGGER.info(f'Performed a successful login')
                return True
        LOGGER.error(f'Failed to perform login')
        return False

    def login_background(self, username, password):
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
            response = self.session.post(f'{self.path}/auth/login', json=data, verify=False)
            # Verifying login status
            json = response.json()
            if json['status'] == 'Success':
                LOGGER.info(f'Performed a successful background login:  {response.json()}')
                return True
            else:
                LOGGER.error(f'Failed to performed background login:  {response.json()}')
                return False

    def login_eagle(self, username, password):
        """
        This methos perform login to th eagle managment using selenium.
        :param username: Username
        :param password: Password
        :return:    True for successful login
                    False for unsuccessful login
        """
        try:
            LOGGER.info(f'performing login (username) using the next username: {self.username}')
            element = self.driver.find_element_by_id('username')
            element.click()
            element.send_keys(self.username)

            LOGGER.info(f'performing login (password) using the next password: {self.password}')
            element = self.driver.find_element_by_id('password')
            element.click()
            element.send_keys(self.password)
            time.sleep(1)

            LOGGER.info(f'performing login submit')
            element = self.driver.find_element_by_xpath('//*[@id="app"]/div/form/div[4]/button')
            element.click()
            LOGGER.info(f'Performed a successful UI login')
            time.sleep(1)

            return True

        except:
            LOGGER.error(f'Was unable to perform UI login using the username: {self.username} and password: {self.password}')
            return False

    def wait_element_to_load(self, element):
        """
        TBD ...
        :param element: The name of the element we are waiting for ... which is the
        :return:
        """
        self.element_to_wait_for = element

        reverse_load_element_map = {v: k for k, v in page_elements.items()}
        self.reverse_element_to_wait_for = reverse_load_element_map[self.element_to_wait_for]

        LOGGER.info(f'Waiting for element to load: {self.reverse_element_to_wait_for} -> {self.element_to_wait_for}')

        wait = WebDriverWait(self.driver, 60)
        wait.until(ec.presence_of_element_located((By.XPATH, self.element_to_wait_for)))
        LOGGER.debug(f'Element loaded successfully:  {self.element_to_wait_for}')
        time.sleep(2)

    def start_scan(self):
        """
        Performing system scan start operation
        :return:    True for successful operation
                    False for unsuccessful operation
        """
        LOGGER.info(f'Got request to start system scan')
        response = self.session.get(f'{self.path}/interception/scan/start', verify=False)
        # Verifying operation status
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
        :return:    True
                    False
        """
        LOGGER.debug(f'Searching if "Stop Scan" button is displayed')
        try:
            element = self.driver.find_element_by_css_selector('.btn.btn-lg.capitalize.btn-loading.red')
            LOGGER.info(f'Found a "Stop Scan" button - system scan is in progress')
            return True
        except:
            LOGGER.error(f'Did not find a "Stop Scan" button - no system scan in progress')
            return False

    def start_scan_ui(self):
        """
        Deprecated
        :return:
        """

        try:
            element = self.driver.find_element_by_xpath(page_elements['start_stop_scan_button'])
            element.click()
            LOGGER.info(f'Clicked the "Start Scan" button')

            # Next code is verifying the Scan indeed started
            self.element_to_look_for = page_elements['start_scan_button_verifier_new']
            LOGGER.debug(f'Looking for element: {self.element_to_look_for}')
            self.wait_element_to_load(self.element_to_look_for)
            wait = WebDriverWait(self.driver, 120)
            wait.until(ec.presence_of_element_located((By.XPATH, self.element_to_look_for)))
            LOGGER.info(f'System scan in progress...')
            time.sleep(1)

        except:
            LOGGER.error(f'Was unable to run system scan')

    def stop_scan(self):
        """
        Performing system scan stop operation
        :return:    True for successful operation
                    False for unsuccessful operation
        """
        LOGGER.info(f'Got request to stop system scan')
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

    def stop_scan_ui(self):
        """
        Deprecated

        Will edit this method in a way the request for start scan will be done
        by executing the next GET request:
        https://192.168.100.206/interception/scan/start
        :return: Conf {"status": "Success"}
        """

        try:
            element = self.driver.find_element_by_xpath(page_elements['stop_scan_button_verifier_new'])
            element.click()
            LOGGER.info(f'Clicked the "Stop Scan" button')

            # Next code is verifying the Scan indeed stopped
            self.element_to_look_for = page_elements['start_scan_button_verifier']
            LOGGER.debug(f'Looking for element: {self.element_to_look_for}')
            self.wait_element_to_load(self.element_to_look_for)
            wait = WebDriverWait(self.driver, 120)
            wait.until(ec.presence_of_element_located((By.XPATH, self.element_to_look_for)))
            LOGGER.info(f'System scan was stopped')
            time.sleep(1)

        except:
            LOGGER.error(f'Was unable to stop system scan')

    def switch_main_view(self, view_type):
        """
        Switch the device list page view - can be table view or grid view
        :param  view_type: table | grid
        :return:    True
                    False
        """
        self.view_type = view_type
        LOGGER.info(f'Got request to switch view to: {self.view_type}')
        try:
            if self.view_type == 'table':
                element = self.driver.find_element_by_xpath(page_elements['table'])
                element.click()
                LOGGER.info(f'Switching to table view')
                return True
            elif self.view_type == 'grid':
                element = self.driver.find_element_by_xpath(page_elements['grid'])
                element.click()
                LOGGER.info(f'Switching to grid view')
            else:
                LOGGER.warning(f'Got undefined request to switch to {self.view_type} view')
                return False
        except:
            LOGGER.error(f'Failed to switch view')
            return False

    def search_for_device(self, mac_list):
        """
        TBD ...
        :param mac_list
        :return:
        """
        for device_mac in mac_list:
            self.device_mac_address = device_mac
            LOGGER.info(f'Searching for device by its MAC address: {self.device_mac_address}')
            try:
                element = self.driver.find_element_by_id('autosuggest__input')
                element.click()
                element.send_keys(self.device_mac_address)
                time.sleep(1)
                element.send_keys(Keys.RETURN)
                time.sleep(2)

                try:
                    self.element_to_look_for = page_elements['device_resultset']
                    LOGGER.info(f'Waiting for element to load: {self.element_to_look_for}')
                    wait = WebDriverWait(self.driver, 20)
                    wait.until(ec.presence_of_element_located((By.XPATH, self.element_to_look_for)))
                    text = self.driver.find_element_by_xpath(self.element_to_look_for).text
                    if text == 'No devices to display':
                        LOGGER.error(f'The required device was not found:  {self.device_mac_address}')
                    else:
                        LOGGER.info(f'The required device was found:  {self.device_mac_address}')

                    # clicking the 'Clear' button
                    self.clear_search_device_field()

                except:
                    # clicking the 'Clear' button
                    self.clear_search_device_field()
                    LOGGER.error(f'Was unable to run search-for-device operation')

            except:
                LOGGER.error(f'Was unable to find device by its MAC address: {self.device_mac_address}')
                self.clear_search_device_field()
                time.sleep(2)

    def run_search(self, search_string):
        """
        Run search in the 'Search Device' field
        :return:    True
                    False
        """
        try:
            element = self.driver.find_element_by_id('autosuggest__input')
            element.click()
            element.send_keys(search_string)
            time.sleep(1)
            element.send_keys(Keys.RETURN)
            time.sleep(2)
            LOGGER.info(f'Running search for string: {search_string}')
            return True
        except:
            LOGGER.error(f'Got an error. was unable to run search for: {search_string}')
            return False

    def clear_search_device_field(self):
        """
        Clears the UI search device field
        :return:    True
                    False
        """
        try:
            LOGGER.info(f'Clearing the search device field')
            time.sleep(1)
            # clear_button = self.driver.find_element_by_css_selector('.clear-search')
            clear_button = self.driver.find_element_by_css_selector('[data-test="clear_search"]')
            clear_button.click()
            time.sleep(1)
            return True
        except:
            LOGGER.error(f'Failed to clear search device field')
            return False

    def has_device_to_display(self):
        """
        Checks if any device is displayed on list following applying a filtering string.
        :return:    True
                    False
        """
        LOGGER.info(f'Check if device appears in list')
        try:
            text = self.driver.find_element_by_xpath(page_elements['empty_device_list']).text
            print(text)
            return True
        except:
            LOGGER.error(f'')
            return False

    def fetch_top_device(self):
        """
        Fetch info of the device at list top
        :return:    True
                    False
        """
        LOGGER.info(f'Fetching device list top info')
        try:
            element = self.driver.find_element_by_xpath(page_elements['device_list_top'])
            element.click()
            LOGGER.info(f'Clicked on list top device')
            return True

        except:
            LOGGER.error(f'Failed to fetch device top list info')
            return False

    def navigate_to_device_info(self):
        pass

    def navigate_to_interception_page(self):
        """
        Navigates UI to #/interception/devices page
        :return:    True for successful operation
                    False for unsuccessful operation
        """
        try:
            LOGGER.info(f'Navigating UI to #/interception/devices')
            path = f'{self.path}#/interception/devices'
            self.driver.get(path)
            self.wait_element_to_load(page_elements['edit_session_pencil'])
            time.sleep(1)
            return True
        except:
            LOGGER.error(f'Failed to navigate UI to #/interception/devices')
            return False

    def fetch_network_data(self, network_ssid):
        """
        Fetches a dictionary of the next format:
        {ssid: "DoNotConnect", bssid: "84:16:f9:7d:b0:43",…}
        and returns the corresponding MAC address of the ssid
        :return:    Network MAC address
                    None
        """
        LOGGER.info(f'Trying to fetch networks data')
        response = self.session.get(f'{self.path}/interception/networks/data', verify=False)
        # Verifying operation status
        json = response.json()
        if json['status'] == 'Success':
            LOGGER.info(f'Was able to fetch networks data:  {response.json()}')

            return True
        else:
            LOGGER.error(f'Failed to ... :  {response.json()}')
            return None

    def start_network_scan(self, ssid):
        """
        TBD...
        :param ssid:
        :return:
        """

        self.network_ssid = ssid

    def stop_network_scan(self):
        pass

    def acquire_device(self):
        pass

    def stop_acquire(self):
        pass

    def is_browsing_history(self):
        pass


if __name__ == '__main__':
    init_logger()
    mac1 = ''
    mac2 = ''
    eagle = EagleController(Settings.EAGLE_HOME_PAGE_1)
    eagle.login('admin', 'admin')
    eagle.navigate_to_interception_page()
    eagle.wait_element_to_load(page_elements['edit_session_pencil'])
    print('OK')
    eagle.switch_main_view('table')

    # eagle.login_background('admin', 'admin')
    # eagle.login_eagle('admin', 'admin')
    # eagle.login('admin', 'admin')
    # eagle.navigate_to_interception_page()
    #
    # eagle.switch_main_view('table')
    eagle.start_scan()
    time.sleep(10)
    # eagle.fetch_top_device()
    # eagle.run_search('dddddd')
    # eagle.has_device_to_display()
    #
    # eagle.search_for_device(['8c:f5:a3:6b:17:1c', '8c:f5:a3:2d:12:e1'])
    # time.sleep(10)
    # eagle.switch_main_view('grid')
    # time.sleep(10)
    # eagle.stop_scan()
    print(eagle.fetch_network_data(''))
