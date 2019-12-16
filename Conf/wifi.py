network_setup_params = {0: ['SSID', 'frequency', 'channel', '', 'TYPE', 'password'],
                       1: ['Test_AP_OPEN_2.4', 2.4, 1, '', 'OPEN', ''],
                       2: ['Test_AP_SECURED_2.4', 2.4, 1, '', 'AES', '00088888'],
                       3: ['Test_AP_OPEN_5', 5, 36, '', 'OPEN', ''],
                       4: ['Test_AP_SECURED_5', 5, 36, '', 'AES', '00088888']}


ap_wifi_params = {0: {'ssid': 'network_ssid'},
                  1: {'ssid': 'Test_AP_OPEN_2.4', 'band': 2.4, 'channel': 1, 'net_type': 'Open network', 'sec_type': 'OPEN', 'secured': 'OPEN', 'password': '', 'authentication': 'open', 'encryption': 'none'},
                  2: {'ssid': 'Test_AP_SECURED_2.4', 'band': 2.4, 'channel': 1, 'net_type': 'Secure network', 'sec_type': 'SECURED', 'secured': 'AES', 'password': '00088888', 'authentication': 'WPA2PSK', 'encryption': 'AES'},
                  3: {'ssid': 'Test_AP_OPEN_5', 'band': 5, 'channel': 36, 'net_type': 'Open network', 'sec_type': 'OPEN', 'secured': 'OPEN', 'password': '', 'authentication': 'open', 'encryption': 'none'},
                  4: {'ssid': 'Test_AP_SECURED_5', 'band': 5, 'channel': 36, 'net_type': 'Secure network', 'sec_type': 'SECURED', 'secured': 'AES', 'password': '00088888', 'authentication': 'WPA2PSK', 'encryption': 'AES'}
                  }


eagle_wifi_params = {'sec_type': 'SECURED',
                     'ssid': 'box1034',
                     'password': 'android1',
                     'authentication': 'WPA2PSK',
                     'encryption': 'AES'}


eagle_management_params = {'username': 'admin', 'password': 'admin'}


security_types_map = {'OPEN': 1, 'AUTO': 2, 'AES': 3}


wifi_signal_levels = {1: 'Wifi one bar.', 2: 'Wifi two bars.', 3: 'Wifi three bars.', 4: 'Wifi signal full.'}