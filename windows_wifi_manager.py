import logging
from logger import init_logger
import xml.etree.cElementTree as XML
import subprocess
import time


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class WiFiManager:
    """
    This class use 'netsh' Windows cmd tool in order to create wifi profile file (xml).
    Note that end user is unable to connect Windows machine to a secured wifi network
    unless it has a saved profile.
    Once the profile file is created, it can be added to the profiles list.
    The next step is to connect the Windows machine to the secured network - this is done
    by the executing the 'netsh wlan connect' command.
    """

    def __init__(self, wifi_profile_filename):
        self.wifi_profile_filename = wifi_profile_filename
        self.ssid = ''
        self.root = ''
        self.ssid_config = ''
        self.ssid_sub = ''
        self.msm = ''
        self.security = ''
        self.auth_encryption = ''
        self.shared_key = ''
        self.add_profile_reply_msg = ''
        self.reply_msg2 = ''
        self.network_type = ''

    def create_wifi_profile(self, type, ssid, password, authentication, encryption):
        """
        This method create the profile.xml file.

        Args:
            ssid: The network name/ssid
            password: The network password/key
            authentication: authentication type. could be WPA2PSK | WPA2
            encryption: Should be set to 'AES'

        Returns:
            NA

        Raises:
            NA
        """

        self.ssid = ssid

        self.root = XML.Element("WLANProfile", attrib={'xmlns': 'http://www.microsoft.com/networking/WLAN/profile/v1'})
        XML.SubElement(self.root, "name").text = self.ssid
        self.ssid_config = XML.SubElement(self.root, "SSIDConfig")
        self.ssid_sub = XML.SubElement(self.ssid_config, "SSID")
        XML.SubElement(self.ssid_sub, "name").text = self.ssid
        XML.SubElement(self.root, "connectionType").text = 'ESS'
        XML.SubElement(self.root, "connectionMode").text = 'auto'
        self.msm = XML.SubElement(self.root, "MSM")
        self.security = XML.SubElement(self.msm, "security")

        self.network_type = type

        if self.network_type == 'SECURED':
            self.auth_encryption = XML.SubElement(self.security, "authEncryption")
            XML.SubElement(self.auth_encryption, "authentication").text = authentication
            XML.SubElement(self.auth_encryption, "encryption").text = encryption
            XML.SubElement(self.auth_encryption, "useOneX").text = 'false'

            self.shared_key = XML.SubElement(self.security, "sharedKey")
            XML.SubElement(self.shared_key, "keyType").text = 'passPhrase'
            XML.SubElement(self.shared_key, "protected").text = 'false'
            XML.SubElement(self.shared_key, "keyMaterial").text = password
        elif self.network_type == 'OPEN':
            self.auth_encryption = XML.SubElement(self.security, "authEncryption")
            XML.SubElement(self.auth_encryption, "authentication").text = 'open'
            XML.SubElement(self.auth_encryption, "encryption").text = 'none'
            XML.SubElement(self.auth_encryption, "useOneX").text = 'false'
            self.mac_random = XML.SubElement(self.root, "MacRandomization", attrib={'xmlns': 'http://www.microsoft.com/networking/WLAN/profile/v3'})
            XML.SubElement(self.mac_random, "enableRandomization").text = 'false'
            XML.SubElement(self.mac_random, "randomizationSeed").text = '10821901'
        else:
            LOGGER.error(f'A wrong input value for "network_type" parameter was delivered')
        try:
            tree = XML.ElementTree(self.root)
            tree.write(self.wifi_profile_filename)
            LOGGER.info(f'{self.wifi_profile_filename} was created successfully at {"TBD: add location"}')

        except:
            LOGGER.error(f'Was unable to create {self.wifi_profile_filename}')

    def add_wifi_profile(self):
        """
        This method adds the profile to the profile list using the next Windows cmd command:
        'netsh wlan add profile filename=<wifi_profile_xml_file>'
        for example:
        'netsh wlan add profile filename=wifi_profile.xml'

        Args:
            ssid:               The network name/ssid
            password:           The network password/key
            authentication:     Authentication type. could be WPA2PSK | WPA2
            encryption:         Should be set to 'AES'

        Returns:
            NA

        Raises:
            NA
        """

        args = ['netsh', 'wlan', 'add', 'profile', f'filename={self.wifi_profile_filename}']
        try:
            self.add_profile_reply_msg = subprocess.check_output(args, stdin=None, stderr=None, shell=False, universal_newlines=False)
            if b'added on interface' in self.add_profile_reply_msg:
                LOGGER.info(f'{self.add_profile_reply_msg}')
                # return self.ssid

        except():
            LOGGER.error(f'{self.add_profile_reply_msg}')

    def connect_to_wifi(self, ssid):
        """
        This method connects the windows machine to the wi-fi network using the next Windows cmd command:
        'netsh wlan connect name=<network_ssid>'

        Args:
            ssid: The network name/ssid

        Returns:
            NA

        Raises:
            NA
        """

        args = ['netsh', 'wlan', 'connect', f'name={ssid}']
        try:
            self.reply_msg2 = subprocess.check_output(args, stdin=None, stderr=None, shell=False, universal_newlines=False)
            if b'request was completed successfully' in self.reply_msg2:
                LOGGER.info(f'{self.reply_msg2}')

        except:
            LOGGER.error(f'{self.reply_msg2}')

'''
class WiFiManagerOpen(WiFiManager):
    """
    The subClass 'WiFiManagerOpen' implements the method:
    create_open_wifi_profile
    Which is used in order to create profile of OPEN network.
    """
    def create_open_wifi_profile(self, ssid):
        """
        This method create the profile.xml file.

        Args:
            ssid: The network name/ssid
            password: The network password/key
            authentication: authentication type. could be WPA2PSK | WPA2
            encryption: Should be set to 'AES'

        Returns:
            NA

        Raises:
            NA
        """

        self.root = XML.Element("WLANProfile", attrib={'xmlns': 'http://www.microsoft.com/networking/WLAN/profile/v1'})
        XML.SubElement(self.root, "name").text = ssid
        self.ssid_config = XML.SubElement(self.root, "SSIDConfig")
        self.ssid_sub = XML.SubElement(self.ssid_config, "SSID")
        XML.SubElement(self.ssid_sub, "name").text = ssid
        XML.SubElement(self.root, "connectionType").text = 'ESS'
        XML.SubElement(self.root, "connectionMode").text = 'manual'

        self.msm = XML.SubElement(self.root, "MSM")
        self.security = XML.SubElement(self.msm, "security")
        self.auth_encryption = XML.SubElement(self.security, "authEncryption")
        XML.SubElement(self.auth_encryption, "authentication").text = 'open'
        XML.SubElement(self.auth_encryption, "encryption").text = 'none'
        XML.SubElement(self.auth_encryption, "useOneX").text = 'false'

        try:
            tree = XML.ElementTree(self.root)
            tree.write(self.wifi_profile_filename)
            LOGGER.info(f'{self.wifi_profile_filename} was created successfully at {"TBD: add location"}')

        except:
            LOGGER.error(f'Was unable to create {self.wifi_profile_filename}')


class WiFiManagerSecured(WiFiManager):
    """
    The subClass 'WiFiManagerSecured' implements the method:
    create_secured_wifi_profile
    Which is used in order to create profile of SECURED network.
    """
    def create_secured_wifi_profile(self, ssid, password, authentication, encryption):
        """
        This method create the profile.xml file.

        Args:
            ssid: The network name/ssid
            password: The network password/key
            authentication: authentication type. could be WPA2PSK | WPA2
            encryption: Should be set to 'AES'

        Returns:
            NA

        Raises:
            NA
        """

        self.root = XML.Element("WLANProfile", attrib={'xmlns': 'http://www.microsoft.com/networking/WLAN/profile/v1'})
        XML.SubElement(self.root, "name").text = ssid
        self.ssid_config = XML.SubElement(self.root, "SSIDConfig")
        self.ssid_sub = XML.SubElement(self.ssid_config, "SSID")
        XML.SubElement(self.ssid_sub, "name").text = ssid
        XML.SubElement(self.root, "connectionType").text = 'ESS'
        XML.SubElement(self.root, "connectionMode").text = 'auto'

        self.msm = XML.SubElement(self.root, "MSM")
        self.security = XML.SubElement(self.msm, "security")
        self.auth_encryption = XML.SubElement(self.security, "authEncryption")
        XML.SubElement(self.auth_encryption, "authentication").text = authentication
        XML.SubElement(self.auth_encryption, "encryption").text = encryption
        XML.SubElement(self.auth_encryption, "useOneX").text = 'false'

        self.shared_key = XML.SubElement(self.security, "sharedKey")
        XML.SubElement(self.shared_key, "keyType").text = 'passPhrase'
        XML.SubElement(self.shared_key, "protected").text = 'false'
        XML.SubElement(self.shared_key, "keyMaterial").text = password

        try:
            tree = XML.ElementTree(self.root)
            tree.write(self.wifi_profile_filename)
            LOGGER.info(f'{self.wifi_profile_filename} was created successfully at {"TBD: add location"}')

        except:
            LOGGER.error(f'Was unable to create {self.wifi_profile_filename}')
'''


if __name__ == '__main__':
    init_logger()
    ssid = 'OpenWiFi4' #'SuperPharm'
    password = 'Aa123456'
    authentication = 'WPA2PSK'
    encryption = 'AES'

    wfm = WiFiManager('wifi_profile_01.xml')
    wfm.create_wifi_profile('OPEN', ssid, password, authentication, encryption)
    wfm.add_wifi_profile()
    wfm.connect_to_wifi(ssid)
