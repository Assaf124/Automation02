import eagle_manager as egmngr
import time
import logging
from logger import init_logger
from Configuration.auto_configuration import Settings
from test_plan_config import TestPlanParameters


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

if __name__ == '__main__':
    init_logger()

    test_device_mac = TestPlanParameters.device_mac
    network_ssid = TestPlanParameters.tested_network_ssid
    probe_id: int = None

    eagle = egmngr.EagleController(Settings.EAGLE_HOME_PAGE_2)
    eagle.login('admin', 'admin')
    eagle.navigate_to_interception_page()
    eagle.switch_main_view('table')
    eagle.start_scan()
    eagle.refresh()
    time.sleep(30)
    eagle.fetch_data_from_db()
    print(eagle.networks_info)

    flag: int = 0
    for item in eagle.networks_info:
        if item[2] == network_ssid:
            print('Starting network scan')
            eagle.start_network_scan_new(item[0])
            flag = 1
            probe_id = item[3]
            break
    if flag == 0:
        print('Did not find network')

    time.sleep(30)
    # eagle.build_mac_to_asset()
    eagle.acquire_device(TestPlanParameters.device_mac, probe_id)
    time.sleep(45)
    eagle.stop_acquire(TestPlanParameters.device_mac)
    print('Done')

