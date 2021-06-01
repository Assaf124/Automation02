import time
import logging
import ap_setup
import eagle_manager
import windows_wifi_manager

from Conf.wifi import network_setup_params
from Configuration.auto_configuration import Settings
from logger import init_logger


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def run_eagle_test():
    eagle = eagle_manager.EagleController(Settings.EAGLE_HOME_PAGE_1)
    eagle.login('admin', 'admin')
    time.sleep(8)
    eagle.navigate_to_sensors()
    time.sleep(10)
    eagle.start_scan()
    time.sleep(40)
    eagle.switch_main_view('table')
    time.sleep(5)
    eagle.run_search('network', 'E8', True)
    time.sleep(5)


    eagle.stop_scan()
    time.sleep(10)
    eagle.end_session()


def connect_laptop_to_access_point():
    ssid = 'Test_AP_OPEN_2.4'
    password = ''
    authentication = ''
    encryption = ''
    wfm = windows_wifi_manager.WiFiManager('wifi_profile_01.xml')
    wfm.create_wifi_profile('OPEN', ssid, password, authentication, encryption)
    wfm.add_wifi_profile()
    wfm.connect_to_wifi(ssid)


def configure_access_point():
    app = ap_setup.APManager()
    app.connect_to_ap_management()
    app.login_ap('admin')
    time.sleep(1)
    app.set_ap_parameters(network_setup_params[1])
    time.sleep(3)
    app.save_params()


if __name__ == '__main__':
    print('Starting ...')
    init_logger()

    connect_laptop_to_access_point()
    time.sleep(10)
    configure_access_point()
    time.sleep(10)
    run_eagle_test()
    print('Done')







