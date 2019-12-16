import time
import logging
from selenium import webdriver
from Configuration.auto_configuration import Settings
from Conf.channels_map import wifi_channels_map
# from Conf.security_types_map import security_types_map
from Conf.wifi import security_types_map
from Conf.wifi import network_setup_params
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class APManager:
    """
    This class interact with the TP-Link Access Point in order to configure its Wi-Fi characteristics.
    Controlled characteristics are:
    ssid:       Network name/ssid
    Band:       2.4 | 5 GHz
    Channel:    Network channels (1,2 ...13 for 2.4GHz | 36, 40, 44, 48 for 5GHz)
    Mode:       11bgn mixed is currently the only acceptable
    Security:   Unsecured | AUTO | AES
    Password:   Network key/password
    """

    def __init__(self):
        self.parameters_list = ''
        self.ssid = ''
        self.band = ''
        self.channel = ''
        self.security = ''
        self.management_password = ''
        self.network_key = ''
        LOGGER.info(f'AccessPoint Setup object has been created')

    def connect_to_ap_management(self):
        LOGGER.info(f'Opening AccessPoint management portal')
        self.driver = webdriver.Chrome(Settings.PATH_TO_CHROMEDRIVER)
        self.driver.set_window_size(1280, 1024)
        time.sleep(1)
        self.driver.get(Settings.AP_HOME_PAGE)

    def login_ap(self, password):
        LOGGER.info(f'Performing login to AccessPoint management portal using password: {self.management_password}')
        self.management_password = password
        element = self.driver.find_element_by_id('password')
        element.click()
        element.send_keys(self.management_password)

        element = self.driver.find_element_by_id('loginBtn')
        element.click()

    def open_wireless_settings(self):
        wireless_settings_uri = '#Advanced/Wireless/WirelessSettings'
        if wireless_settings_uri not in self.driver.current_url:
            self.driver.get(Settings.AP_WIRELESS_SETTINGS_PAGE)

    def set_ap_parameters(self, params_list):

        self.parameters_list = params_list

        # Navigate to 'Wireless Settings' page
        self.open_wireless_settings()

        # Set ssid
        time.sleep(1)  # to replace with WaitPageToLoad()
        self.ssid = self.parameters_list[0]
        self.driver.find_element_by_id('ssidInput').clear()
        element = self.driver.find_element_by_id('ssidInput')
        element.send_keys(self.ssid)

        # Set WiFi band
        time.sleep(1)  # to replace with WaitPageToLoad()
        self.band = self.parameters_list[1]
        element = self.driver.find_element_by_xpath('//*[@id="wifiSettingsSection"]/div[4]/div')
        element.click()
        time.sleep(0.5)
        if self.band == 2.4:
            element = self.driver.find_element_by_xpath('//*[@id="wifiSettingsSection"]/div[4]/div/ul/li[1]')
        else:
            element = self.driver.find_element_by_xpath('//*[@id="wifiSettingsSection"]/div[4]/div/ul/li[2]')
        element.click()

        # Set Wi-Fi channel
        time.sleep(1)  # to replace with WaitPageToLoad()
        self.channel = self.parameters_list[2]
        element = self.driver.find_element_by_xpath('//*[@id="wifiSettingsSection"]/div[5]/div/span[1]')
        element.click()
        time.sleep(1)
        element = self.driver.find_element_by_xpath(
            f'//*[@id="wifiSettingsSection"]/div[5]/div/ul/li[{wifi_channels_map[self.channel]}]')
        element.click()

        # Set Wi-Fi mode
        # time.sleep(1)  # to replace with WaitPageToLoad()
        # self.mode = mode
        # element = self.driver.find_element_by_xpath('//*[@id="wifiSettingsSection"]/div[6]/div/span[1]')
        # element.click()

        # Set Security type
        time.sleep(1)  # to replace with WaitPageToLoad()
        self.security = self.parameters_list[4]
        self.network_key = self.parameters_list[5]
        element = self.driver.find_element_by_xpath('//*[@id="wifiSettingsSection"]/div[8]/div')
        element.click()

        time.sleep(1)  # to replace with WaitPageToLoad()
        # security_type_map = {'OPEN': 1, 'AUTO': 2, 'AES': 3}
        element = self.driver.find_element_by_xpath(f'//*[@id="wifiSettingsSection"]/div[8]/div/ul/li[{security_types_map[self.security]}]')
        element.click()

        if self.security != 'OPEN':
            self.driver.find_element_by_id('keyInput').clear()
            element = self.driver.find_element_by_id('keyInput')
            element.send_keys(self.network_key)

    def update_channel(self, desired_channel):
        self.connect_to_ap_management()
        self.login_ap('admin')
        self.open_wireless_settings()

        # Set Wi-Fi channel
        time.sleep(1)  # to replace with WaitPageToLoad()
        self.channel = desired_channel
        element = self.driver.find_element_by_xpath('//*[@id="wifiSettingsSection"]/div[5]/div/span[1]')
        element.click()
        time.sleep(1)
        element = self.driver.find_element_by_xpath(f'//*[@id="wifiSettingsSection"]/div[5]/div/ul/li[{wifi_channels_map[self.channel]}]')
        element.click()

    def save_params(self):
        element = self.driver.find_element_by_id('wirelessSettingsSave')
        element.click()
        time.sleep(1)
        element = self.driver.find_element_by_id('wifiRebootOK')
        # element = self.driver.find_element_by_id('wifiRebootCancel')
        element.click()
        time.sleep(2)
        self.driver.close()


if __name__ == '__main__':
    # Scenario-1
    # ap = APManager()
    # ap.connect_to_ap_management()
    # ap.login_ap('admin')
    # time.sleep(1)
    # ap.set_ap_parameters(network_setup_params[1])
    # time.sleep(3)
    # ap.save_params()

    # Scenario-2
    app = APManager()
    app.update_channel(11)
    time.sleep(2)
    app.save_params()
