import logging
import logger
import eagle_manager
import android_device_manager
import configure_ap
import ap_setup
import windows_wifi_manager
import time
import sys
from logger import init_logger
from Conf.wifi import network_setup_params
from Conf.wifi import eagle_wifi_params
from Conf.wifi import ap_wifi_params
from Conf.wifi import eagle_management_params
from Conf.page_elements_map import page_elements
from Conf.test_devices import test_device_list
from Configuration.auto_configuration import Settings


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
# LOGGER.setLevel(logging.INFO)


def run_eagle_test(username, password, network_name, devices_list):
    LOGGER.info(f'*** Starting run_eagle_test')

    if not eagle.start_scan():
        LOGGER.error(f'Failed to start scan ... stopping the test')
        exit()

    time.sleep(30)
    eagle.search_for_device(devices_list)
    # eagle.start_network_scan(network_name)
    # time.sleep(100)
    eagle.stop_scan()


def connect_windows_machine_to_wifi(wifi_args):
    LOGGER.info(f'*** Starting connect_windows_machine_to_wifi')

    sec_type = wifi_args['sec_type']
    ssid = wifi_args['ssid']
    password = wifi_args['password']
    authentication = wifi_args['authentication']
    encryption = wifi_args['encryption']

    wfm = windows_wifi_manager.WiFiManager('wifi_profile.xml')
    wfm.create_wifi_profile(sec_type, ssid, password, authentication, encryption)
    time.sleep(1)
    wfm.add_wifi_profile()
    time.sleep(1)
    wfm.connect_to_wifi(ssid)


def set_up_access_point(ap_management_password, ap_parameters):
    LOGGER.info(f'*** Starting set_up_access_point')
    access_point = ap_setup.APManager()
    access_point.connect_to_ap_management()
    access_point.login_ap(ap_management_password)
    time.sleep(1)
    access_point.set_ap_parameters(ap_parameters)
    time.sleep(1)
    access_point.save_params()


def update_ap_channel(ap_management_password, channel):
    LOGGER.info(f'*** Starting update_ap_channel')
    access_point = ap_setup.APManager()
    time.sleep(1)
    access_point.update_channel(channel)
    time.sleep(1)
    access_point.save_params()


def connect_device_to_ap(ssid, type, key):
    LOGGER.info(f' *** Starting connect_device_to_ap')
    android = android_device_manager.AndroidManager()
    is_connected_result = android.is_connected_to_wifi()
    if is_connected_result is False:
        LOGGER.error(f'Failed to connect Wi-Fi')
        sys.exit()
    elif is_connected_result is None:
        android.connect_to_wifi(ssid, type, key)
    elif is_connected_result != ssid:
        LOGGER.info(f'Currently Connected to {is_connected_result} - Need to disconnect from old AP')
        android.connect_to_wifi(ssid, type, key)
    elif is_connected_result == ssid:
        LOGGER.info(f'')


if __name__ == '__main__':
    # Pre-condition: connect Windows machine to access point
    connect_windows_machine_to_wifi(ap_wifi_params[1])
    init_logger()

    LOGGER.info(f'***  Starting Test  *** ')

    channel_list = [2, 3, 4, 5]
    list_of_devices_to_verify = test_device_list

    network_ssid = ap_wifi_params[1]['ssid']
    network_type = ap_wifi_params[1]['net_type']
    network_password = ap_wifi_params[1]['password']
    
    set_up_access_point('admin', network_setup_params[1])
    connect_device_to_ap(network_ssid, network_type, network_password)
    # eagle_wifi_params_list = ['box1018', 'android1']
    connect_windows_machine_to_wifi(eagle_wifi_params)

    user = eagle_management_params['username']
    password = eagle_management_params['password']

    eagle = eagle_manager.EagleController(Settings.EAGLE_HOME_PAGE_2)
    eagle.login(user, password)
    eagle.wait_element_to_load(page_elements['edit_session_pencil'])
    eagle.navigate_to_interception_page()

    try:
        eagle.switch_main_view('table')
    except:
        eagle.switch_main_view('grid')
        time.sleep(2)
        eagle.switch_main_view('table')

    for channel in channel_list:
        run_eagle_test('admin', 'admin', network_ssid, list_of_devices_to_verify)
        connect_windows_machine_to_wifi(ap_wifi_params[1])
        time.sleep(5)
        update_ap_channel('admin', channel)
        time.sleep(5)
        connect_windows_machine_to_wifi(eagle_wifi_params)
        time.sleep(5)


