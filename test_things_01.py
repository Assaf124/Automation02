import logging
import logger
import eagle_manager
import android_device_manager
import configure_ap
import ap_setup
import windows_wifi_manager
import time
from logger import init_logger
from Conf.wifi import network_setup_params
from Conf.wifi import eagle_wifi_params
from Conf.wifi import ap_wifi_params
from Conf.page_elements_map import page_elements
from Configuration.auto_configuration import Settings


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
# LOGGER.setLevel(logging.INFO)


def run_eagle_test(username, password, network_name, devices_list):
    LOGGER.info(f'*** Starting run_eagle_test')

    try:
        eagle.start_scan()
    except:
        eagle.stop_scan()
        eagle.wait_element_to_load(page_elements['start_stop_scan_button'])
        eagle.start_scan()

    time.sleep(20)
    eagle.search_for_device(devices_list)
    # eagle.start_network_scan(network_name)
    # time.sleep(100)
    eagle.stop_scan()
    time.sleep(10)


if __name__ == '__main__':
    init_logger()
    LOGGER.debug(f'*** Starting test ***')
    # parameters
    list_of_devices_to_verify = ['8c:f5:a3:6b:17:1c', '8c:f5:a3:2d:12:e1']
    network_ssid = ap_wifi_params[1]['ssid']
    user = 'admin'
    password = 'admin'

    # code:
    eagle = eagle_manager.EagleController(Settings.EAGLE_HOME_PAGE_2)
    eagle.login_eagle(user, password)
    el = page_elements['session_name']
    eagle.wait_element_to_load(el)

    LOGGER.info(f'*** Starting phase 2 ***')
    try:
        LOGGER.debug(f'try to switch to table view')
        eagle.switch_main_view('table')
        eagle.wait_element_to_load(page_elements['network_list_view'])
    except:
        LOGGER.debug(f'switching to grid and then to table view')
        eagle.switch_main_view('grid')
        eagle.wait_element_to_load(page_elements['network_list_view'])
        eagle.switch_main_view('table')

    LOGGER.info(f'*** Starting phase 3 ***')
    run_eagle_test('admin', 'admin', network_ssid, list_of_devices_to_verify)