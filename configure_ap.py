import time
import logging
from selenium import webdriver
from Configuration.auto_configuration import Settings
from Conf.channels_map import wifi_channels_map
from Conf.wifi import security_types_map
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
        self.driver = webdriver.Chrome(Settings.PATH_TO_CHROMEDRIVER)
        self.driver.set_window_size(1280, 1024)
        time.sleep(1)
        self.driver.get(Settings.AP_HOME_PAGE)

    def login_ap(self, password):
        self.password = password
        element = self.driver.find_element_by_id('password')
        element.click()
        element.send_keys(self.password)

        element = self.driver.find_element_by_id('loginBtn')
        element.click()

    def open_wireless_settings(self):
        wireless_settings_uri = '#Advanced/Wireless/WirelessSettings'
        if wireless_settings_uri not in self.driver.current_url:
            self.driver.get(Settings.AP_WIRELESS_SETTINGS_PAGE)

    def set_ap_params(self, ssid, band, channel, mode, security, password):
        # Navigate to 'Wireless Settings' page
        self.open_wireless_settings()

        # Set ssid
        time.sleep(1)   # to replace with WaitPageToLoad()
        self.ssid = ssid
        self.driver.find_element_by_id('ssidInput').clear()
        element = self.driver.find_element_by_id('ssidInput')
        element.send_keys(self.ssid)

        # Set WiFi band
        time.sleep(1)  # to replace with WaitPageToLoad()
        self.band = band
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
        self.channel = channel
        element = self.driver.find_element_by_xpath('//*[@id="wifiSettingsSection"]/div[5]/div/span[1]')
        element.click()
        time.sleep(1)
        element = self.driver.find_element_by_xpath(f'//*[@id="wifiSettingsSection"]/div[5]/div/ul/li[{wifi_channels_map[self.channel]}]')
        element.click()

        # Set Wi-Fi mode
        # time.sleep(1)  # to replace with WaitPageToLoad()
        # self.mode = mode
        # element = self.driver.find_element_by_xpath('//*[@id="wifiSettingsSection"]/div[6]/div/span[1]')
        # element.click()

        # Set Security type
        time.sleep(1)  # to replace with WaitPageToLoad()
        self.security = security
        self.password = password
        element = self.driver.find_element_by_xpath('//*[@id="wifiSettingsSection"]/div[8]/div')
        element.click()

        time.sleep(1)  # to replace with WaitPageToLoad()
        # security_type_map = {'OPEN': 1, 'AUTO': 2, 'AES': 3}
        element = self.driver.find_element_by_xpath(f'//*[@id="wifiSettingsSection"]/div[8]/div/ul/li[{security_types_map[self.security]}]')
        element.click()
        if self.security != 'OPEN':
            self.driver.find_element_by_id('keyInput').clear()
            element = self.driver.find_element_by_id('keyInput')
            element.send_keys(self.password)

    def save_params(self):
        element = self.driver.find_element_by_id('wirelessSettingsSave')
        element.click()
        time.sleep(1)
        # element = self.driver.find_element_by_id('wifiRebootOK')
        element = self.driver.find_element_by_id('wifiRebootCancel')
        element.click()


if __name__ == '__main__':
    '''
    driver = webdriver.Chrome(Settings.PATH_TO_CHROMEDRIVER)
    driver.set_window_size(1280, 1024)
    time.sleep(1)
    driver.get(Settings.AP_HOME_PAGE)
    driver.get('http://192.168.0.1/settings.html#Advanced/Wireless/WirelessSettings')

    driver.find_element_by_xpath("//select[@id='securitySelect']/following-sibling::span").click()
    b = driver.find_element_by_xpath("//select[@id='securitySelect']/parent::div/ul")
    dropdown_options = b.find_elements_by_xpath('.//li')
    for i in dropdown_options:
        if i.text == 'Unsecured':
            i.click()
            break
            
    # [y.text for y in b.find_elements_by_xpath('.//li')]
    '''
    ap = APManager()
    ap.login_ap('admin')
    time.sleep(1)
    ap.set_ap_params('Emil_Zatopek_5_OPEN', 2.4, 8, '', 'AES', '00099999')
    time.sleep(3)
    ap.save_params()
