import logging
from logger import init_logger
import re
import subprocess
import time
import random
from appium import webdriver
from Conf.wifi import wifi_signal_levels
from appium.webdriver.common.touch_action import TouchAction


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
# LOGGER.setLevel(logging.INFO)


class AndroidManager:
    def __init__(self):
        LOGGER.info(f'AndroidManager object has been created')
        self.udid_reply_msg = ''
        self.udid = ''
        self.model_reply_msg = ''
        self.device_model = ''
        self.platform_reply_msg = ''
        self.platform_version = ''
        self.desired_caps = dict()
        self.wifi_enable_reply_msg = ''
        self.wifi_disable_reply_msg = ''
        self.driver = ''
        self.ssid = ''
        self.wifi_pattern = ''
        self.ssid_status = ''
        self.security_type = ''
        self.wifi_signal_level = ''
        self.wifi_password = ''
        self.wifi_connect_success = ''

    def get_device_udid(self):
        """
        Fetches device's UDID value
        :return:    UDID value in case of success
                    None in case of failure
        """
        args = ['adb', 'devices']
        try:
            self.udid_reply_msg = subprocess.check_output(args, stdin=None, stderr=None, shell=False, universal_newlines=False)
            LOGGER.debug(f'{self.udid_reply_msg}')
            pattern = re.search('attached\r\n(.+?)\tdevice', self.udid_reply_msg.decode("utf-8"))

            if pattern:
                LOGGER.info(f'Device UDID is: {pattern.group(1)}')
                self.udid = pattern.group(1)
                return self.udid
        except:
            LOGGER.error(f'Got exception while trying to run "adb devices" command. Got next reply: {self.udid_reply_msg()}')
            return None

    def get_device_model(self):
        """
        This method extract the DEVICE MODEL by running the next 'adb' command:
        adb devices -l

        :return:    int:    device model
                    None
        """
        args = ['adb', 'devices', '-l']
        try:
            self.model_reply_msg = subprocess.check_output(args, stdin=None, stderr=None, shell=False, universal_newlines=False)
            LOGGER.debug(f'{self.model_reply_msg}')
            # Extract the DEVICE MODEL from reply:
            pattern = re.search('model:(.+?)device:', self.model_reply_msg.decode("utf-8"))

            if pattern:
                LOGGER.info(f'Device Model is: {pattern.group(1)}')
                self.device_model = pattern.group(1)
                return self.device_model

        except:
            LOGGER.error(f'Got exception while trying to run "adb devices -l" command. Got next reply: {self.model_reply_msg}')
            return None

    def get_device_platform_version(self):
        """
        This method extract the device platform version by running the next 'adb' command:
        adb shell getprop ro.build.version.release

        :return:    string: platform_version
                    None
        """
        args = ['adb', 'shell', 'getprop', 'ro.build.version.release']
        try:
            self.platform_reply_msg = subprocess.check_output(args, stdin=None, stderr=None, shell=False, universal_newlines=False)
            LOGGER.debug(f'{self.platform_reply_msg}')
            # Extract the PLATFORM VERSION from reply:
            pattern = re.search('(.+?)\r\n', self.platform_reply_msg.decode("utf-8"))

            if pattern:
                LOGGER.info(f'Device OS version: Android {pattern.group(1)}')
                self.platform_version = pattern.group(1)
                return self.platform_version

        except:
            LOGGER.error(f'Got exception while tried to run "adb shell getprop ro.build.version.release" command. Got next reply: {self.platform_reply_msg}')
            return None

    def create_desire_capabilities(self, type):
        """
        This method creates a dictionary which is the desired capabilities, which in turn, used
        by Appium to control the android device
        :param type:    chrome - for launching chrome by appium
                        settings - for launching settings app
        :return:    desired capabilities (dictionary)
                    None
        """
        self.desired_caps["platformName"] = "Android"
        self.desired_caps["deviceName"] = self.get_device_model()
        self.desired_caps["udid"] = self.get_device_udid()
        self.desired_caps["platformVersion"] = self.get_device_platform_version()

        if type == 'chrome':
            self.desired_caps["browserName"] = "Chrome"
            LOGGER.info(f'Created successfully desired capabilities dictionary for chrome: {self.desired_caps}')
        elif type == 'settings':
            self.desired_caps["appPackage"] = "com.android.settings"
            self.desired_caps["appActivity"] = ".Settings"
            LOGGER.info(f'Created successfully desired capabilities dictionary for settings: {self.desired_caps}')
        else:
            pass

        return self.desired_caps

    def turn_wifi_on(self):
        """
        Turns device Wi-Fi on
        :return:    True
                    False
        """
        self.get_device_udid()
        args = ['adb', '-s', self.udid, 'shell', 'svc wifi enable']
        try:
            self.wifi_enable_reply_msg = subprocess.check_output(args, stdin=None, stderr=None, shell=False, universal_newlines=False)
            LOGGER.debug(f'The reply message for command: adb -s {self.udid} shell svc wifi enabled -> {self.wifi_enable_reply_msg}')
            LOGGER.info('Turned Wi-Fi on')
            return True

        except:
            LOGGER.error(f"Got exception while trying to turn on device's wi-fi. Got next reply: {self.wifi_enable_reply_msg}")
            return False

    def turn_wifi_off(self):
        """
        This method turns 'OFF' the Wi-Fi button on the Android device
        :return:    True
                    False
        """
        self.get_device_udid()
        args = ['adb', '-s', self.udid, 'shell', 'svc wifi disable']
        try:
            self.wifi_disable_reply_msg = subprocess.check_output(args, stdin=None, stderr=None, shell=False, universal_newlines=False)
            LOGGER.debug(f'{self.wifi_disable_reply_msg}')
            LOGGER.info('Turned Wi-Fi off')
            return True
        except:
            LOGGER.error(f"Got exception while trying to turn off device's wi-fi. Got next reply: {self.wifi_disable_reply_msg()}")
            return False

    def open_wifi_menu(self):
        """
        Navigates to Android Wi-Fi menu
        :return:    True
                    False
        """
        try:
            self.create_desire_capabilities('settings')
            self.driver = webdriver.Remote("http://localhost:4723/wd/hub", self.desired_caps)
            LOGGER.debug(f'Open settings menu')
            time.sleep(1)
            el = self.driver.find_element_by_id('com.android.settings:id/dashboard_tile')
            el.click()
            LOGGER.debug(f'Open Network & Internet menu')
            time.sleep(1)
            LOGGER.debug(f'Open Wi-Fi menu')
            el = self.driver.find_element_by_id('com.android.settings:id/icon_frame')
            el.click()
            time.sleep(1)
            LOGGER.info(f'Successfully opened Wi-Fi menu')
            return True
        except:
            LOGGER.error(f"Was unable to navigates to device's Wi-Fi menu")
            return False

    def is_connected_to_ap(self):
        """
        Checks if device is connected to a Wi-Fi network
        :return:    SSID of the connected network
                    None in case the device is idle.
        """
        LOGGER.info(f'Checking if device connected to Wi-Fi')
        self.turn_wifi_on()
        self.open_wifi_menu()
        try:
            # Searching if the 'gear' icon is displayed (which means device is connected to some Wi-Fi)
            el = self.driver.find_element_by_id('com.android.settings:id/settings_button_no_background')
            time.sleep(1)
            TouchAction(self.driver).tap(x=600, y=600).perform()
            time.sleep(1)
            el = self.driver.find_element_by_id('com.android.settings:id/entity_header_title')
            ssid_string = el.text
            LOGGER.info(f'Found that device is connected to network: {ssid_string}')
            self.ssid_status = ssid_string
            # Go back to 'Wi-Fi' menu
            el = self.driver.find_element_by_class_name('android.widget.ImageButton')
            el.click()
            return ssid_string
        except:
            LOGGER.info(f'Found that device is not connected to any Wi-Fi network')
            self.ssid_status = None
            return None

    def generate_wifi_pattern(self, saved_ap):
        """
        Generates a Wi-Fi pattern.
        Pattern is:
        ssid,status(optional),strength,type
        for example:
        - BurgerKing,Saved,Wifi two bars.,Secure network
        - Sheraton,Check password and try again,Wifi two bars.,Secure network
        - Subway,Connected,Wifi signal full.,Open network
        - Hilton,Wifi signal full.,Open network

        :return:    String, wifi_pattern
        """
        if saved_ap:
            self.wifi_pattern = f'{self.ssid},Saved,{self.wifi_signal_level},{self.security_type}'
        else:
            self.wifi_pattern = f'{self.ssid},{self.wifi_signal_level},{self.security_type}'
        return self.wifi_pattern

    def connect_to_ap(self, ssid, security, password):
        """
        Connects the device to a network which its name given as input parameter
        :param ssid:        Wi-Fi ssid, string
        :param security:
        :param password:    Network key, string
        :return:    True
                    False
        """
        self.ssid = ssid
        self.security_type = security
        self.wifi_password = password
        self.wifi_connect_success = False
        self.wifi_signal_level = 'Wifi signal full.'

        # self.is_connected_to_ap()
        try:
            if self.ssid_status == self.ssid:
                LOGGER.info(f'Already connected to {self.ssid}. No further action need to be taken')
                return True
            elif self.ssid_status is None:
                LOGGER.info(f'Device is idle. Will try to connect it to {self.ssid}')
            elif self.ssid_status != self.ssid:
                LOGGER.info(f'...bla...')
                time.sleep(2)
                success_flag = False
                for i in range(30):
                    try:
                        el = self.driver.find_element_by_xpath(f'//*[@content-desc="{self.ssid},{self.wifi_signal_level},{self.security_type}"]')
                        el.click()
                        success_flag = True
                        LOGGER.info(f'Succeeded to connect device to {self.ssid} network')
                        break
                    except:
                        LOGGER.debug(f'Did not succeed to connect device. will try a new pattern: "{self.ssid},{self.wifi_signal_level},{self.security_type}"')
                        time.sleep(1)
                if not success_flag:
                    LOGGER.info(f'Failed to connect device to {self.ssid} network')
                    return False
        except:
            LOGGER.error(f'An error occurred while trying to connect device to {self.ssid}')
            return False

    def connect_to_wifi(self, ssid, security, password):
        """
        This method connects the android device to a Wi-Fi network which its ssid named in the method input argument.
        :param ssid:        Wi-Fi ssid
        :param security:
        :param password:
        :return:    True:   If connecting to Wi-Fi was successful
                    False:  If was unable to connect the Wi-Fi network or if stated SSID was not found.
        """
        self.ssid = ssid
        self.security_type = security
        self.wifi_password = password
        self.wifi_connect_success = False
        self.wifi_signal_level = 'Wifi signal full.'
        self.create_desire_capabilities('settings')

        # Verifying the device's Wi-Fi is 'On'
        try:
            self.turn_wifi_on()
            time.sleep(1)
        except:
            pass

        try:
            LOGGER.info(f'Will try to connect Wi-Fi network:  {self.ssid}')
            self.driver = webdriver.Remote("http://localhost:4723/wd/hub", self.desired_caps)
            LOGGER.debug(f'Open settings menu')
            time.sleep(1)
            el = self.driver.find_element_by_id('com.android.settings:id/dashboard_tile')
            el.click()
            LOGGER.debug(f'Open Network & Internet menu')

            time.sleep(1)
            LOGGER.debug(f'Open Wi-Fi menu')
            el = self.driver.find_element_by_id('com.android.settings:id/icon_frame')
            el.click()
            time.sleep(1)
            LOGGER.debug(f'Trying to click the {self.ssid} button')
            LOGGER.debug(f'Trying the next pattern:  {self.ssid},{self.wifi_signal_level},{self.security_type}')
            for j in range(3):
                for i in range(30):
                    try:
                        el = self.driver.find_element_by_xpath(f'//*[@content-desc="{self.ssid},{self.wifi_signal_level},{self.security_type}"]')
                        el.click()
                        LOGGER.debug(f'Clicked the {self.ssid} button!')
                        if self.security_type == 'Secure network':
                            LOGGER.debug(f'Applying password to {self.ssid} network')
                            time.sleep(2)
                            el = self.driver.find_element_by_id('com.android.settings:id/password')
                            el.click()
                            el.send_keys(self.wifi_password)
                            time.sleep(1)
                            TouchAction(self.driver).tap(None, 1170, 1340, 1).perform()
                            self.wifi_connect_success = True
                        self.wifi_connect_success = True
                        break
                    except:
                        random_int = random.randint(1, 4)
                        self.wifi_signal_level = wifi_signal_levels[random_int]
                        LOGGER.debug(f'Was unable to click the {self.ssid} button')
                        LOGGER.debug(f'Trying new pattern: {self.ssid},{self.wifi_signal_level},{self.security_type}')
                        time.sleep(2)
                if self.wifi_connect_success:
                    LOGGER.info(f'Was able to connect {self.ssid} network')
                    break
                LOGGER.debug(f'Scrolling down')
                TouchAction(self.driver).press(x=300, y=1500).move_to(x=300, y=1320).release().perform()
                time.sleep(1)
            return True

        except:
            LOGGER.error(f'Failed to perform Wi-Fi network selection')
            return False

    def browse_to(self, url):
        """
        This method navigates the chrome browser to the selected 'url' in the method input argument.
        :param url: a valid url
        :return:
        """
        self.create_desire_capabilities('chrome')
        try:
            self.driver = webdriver.Remote("http://localhost:4723/wd/hub", self.desired_caps)
            LOGGER.info(f'Launching chrome')
            time.sleep(1)
            self.driver.get(url)
            LOGGER.info(f'Navigating chrome to: {url}')
            time.sleep(3)
            self.driver.close()
        except:
            LOGGER.error(f'Was unable to  run chrome')


if __name__ == '__main__':
    init_logger()
    android = AndroidManager()
    android.is_connected_to_ap()
    # ssid1 = 'ibiza'
    # result = android.connect_to_ap(ssid1, '', '')


    # udid = android.get_device_udid()
    # model = android.get_device_model()
    # platform_version = android.get_device_platform_version()
    # print(f'UDID: {udid}\nMODEL: {model}\nPlatform: {platform_version}')

    # aaa = android.create_desire_capabilities('chrome')
    # print(aaa)

    # url1 = 'http://www.bbc.com'
    # url2 = 'http://www.bbc.com/culture'
    # android.browse_to(url2)

    # android.clear_browser_history()

    # android.turn_wifi_off()
    # time.sleep(5)
    # android.turn_wifi_on()

    # is_connected_result = android.is_connected_to_wifi()
    # if is_connected_result is False:
    #     print('Failed')
    # elif is_connected_result is None:
    #     android.connect_to_wifi('Test_AP_OPEN_2.4', 'Open network', '')
    # elif is_connected_result != 'Test_AP_OPEN_2.4':
    #     print(f'Connect to {is_connected_result} - Need to disconnect from old AP')
    #     android.connect_to_wifi('Test_AP_OPEN_2.4', 'Open network', '')
    # elif is_connected_result == 'Test_AP_OPEN_2.4':
    #     print('OK')

    # android.connect_to_wifi('Test_AP_OPEN_2.4', 'Open network', '')
    # android.connect_to_wifi('box1019', 'Secure network', 'android1')
    # android.connect_to_wifi('RadissonBlu_24_OPEN', 'Open network', '')
    # android.connect_to_wifi('Assaf24', 'Open network', '')
    # android.connect_to_wifi('Hilton', 'Secure network', '12345679')
    # android.connect_to_wifi('aqwszxca', 'Open network', '')
    # print(android.is_connected_to_wifi())

    # android.open_wifi_menu()
    # result = android.is_connected_to_ap()

    # if result == ssid:
    #     pass
    #
    # elif result is not None:
    #     if result != '':
    #         android.connect_to_wifi()
    # else:
    #     android.connect_to_wifi('SuperPharm', 'Secure network', 'Aa123456')
