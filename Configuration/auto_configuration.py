import os
from pathlib import Path
import datetime


timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d__UTC%H-%M-%S')


class Settings:

    PATH_TO_CHROMEDRIVER = r'C:\Users\assafa\AppData\Local\Programs\Python\Python38-32\chromedriver\chromedriver.exe'
    AP_HOME_PAGE = r'http://192.168.0.1/login.html'
    AP_WIRELESS_SETTINGS_PAGE = r'http://192.168.0.1/settings.html#Advanced/Wireless/WirelessSettings'

    wifi_profiles_parent_dir = os.getcwd()
    wifi_profiles_dir_name = 'Wi-Fi Profiles'
    wifi_profiles_dir = os.path.join(wifi_profiles_parent_dir, wifi_profiles_dir_name)
    wifi_profiles_filename = f''

    WIFI_PROFILES_DIR = os.path.join(wifi_profiles_dir, wifi_profiles_dir_name)

    EAGLE_HOME_PAGE_1 = r'https://192.168.100.199/'
    EAGLE_HOME_PAGE_2 = r'https://172.16.10.1/'
    TEST_RESOURCE = r'https://automatetheboringstuff.com'

    APPLICATION_MAIN_PATH = r'C:\myDirectory\uvApplication\UV_Application'


class Logger:
    APPLICATION_MAIN_PATH = str(Path(__file__).parent.parent)
    LOG_DIR_NAME = 'Logging'
    LOG_FILE_NAME = f'log__{timestamp}.log'
    LOG_FILE_PATH = os.path.join(APPLICATION_MAIN_PATH, LOG_DIR_NAME, LOG_FILE_NAME)
    LOG_FILE_MODE = 'w'  # a = append , w = overwrite

