import logging
import eagle_manager
import time
import requests
from logger import init_logger
from Configuration.auto_configuration import Settings
from Conf.page_elements_map import page_elements

from selenium import webdriver


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


if __name__ == "__main__":
    init_logger()
    eagle = eagle_manager.EagleController(Settings.EAGLE_HOME_PAGE_2)
    for i in range(10):
        try:
            eagle.login('admin', 'admin')
            break
        except:
            time.sleep(1)

    eagle.navigate_to_interception_page()
    eagle.wait_element_to_load(page_elements['edit_session_pencil'])
    print('OK')
    eagle.switch_main_view('table')

    time.sleep(3)

    if eagle.is_scan_running():
        pass
    else:
        print(f'Scan is NOT in progress ... will start scan now')
        eagle.start_scan()

    eagle.run_search('B3:99')

