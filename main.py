import eagle_manager
import time
from Configuration.auto_configuration import Settings


def function01():
    # eagle = eagle_manager.EagleController(Settings.EAGLE_HOME_PAGE_2)
    # eagle.login_eagle('admin', 'admin')
    time.sleep(20)
    eagle.start_scan()
    time.sleep(20)
    clear_button = eagle.driver.find_element_by_xpath('//*[@id="app"]/div/div[3]/div[1]/div[1]/div[2]/div/div[2]/div[2]/div/div/div[1]/div[2]/div[2]/a')
    clear_button.click()
    time.sleep(20)
    eagle.stop_scan()


if __name__ == '__main__':
    print('Starting ...')

    eagle = eagle_manager.EagleController(Settings.EAGLE_HOME_PAGE_2)
    eagle.login_eagle('admin', 'admin')

    for number in range(5):
        function01()
        time.sleep(30)



