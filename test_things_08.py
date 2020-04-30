import time
import logging
import eagle_manager
from test_plan_config import TestPlanParameters
from logger import init_logger
from Configuration.auto_configuration import Settings

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


if __name__ == "__main__":
    init_logger()
    network_bssid = TestPlanParameters.tested_network_bssid

    eagle = eagle_manager.EagleController(Settings.EAGLE_HOME_PAGE_2)
    eagle.login('admin', 'admin')
    eagle.navigate_to_interception_page()
    eagle.start_scan()
    time.sleep(20)
    eagle.fetch_network_data(network_bssid)
    print(f'SSID: {eagle.tested_network_info["ssid"]}\nChannel: {eagle.tested_network_info["channel"]}')