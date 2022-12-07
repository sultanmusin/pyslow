__author__ = "Sultan Musin"
__copyright__ = "2022, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "musin@inr.ru"
__status__ = "Development"

import sys, os
from PyQt5.QtWidgets import QFileDialog, QApplication
import configparser

sys.path.append('control')
import gui2

settings_path = os.path.expanduser('~/.slow_control/')
settings_file = 'settings.ini'

def UIGetConfigName(config_name : str = '') -> str:
    """Get config name from UI window.

        Args:
            config_name(str): Default config name or directory where the window opens.

        Returns:
            str: Config filename to use slow control with.
    """
    app = QApplication([])
    selected_config = QFileDialog.getOpenFileName(None, 
        "Select config file to open", 
        config_name, 
        "(*.xml)")
    app.exit()
    if selected_config and selected_config[0].endswith('.xml'):
        return selected_config[0]

def GetLastUsedConfig() -> str: 
    """Searches the settings file in user's directory to find the last used config path

        Returns:
            str: Full path to config file from settings.
    """
    if not os.path.exists(settings_path):
        return None
    if not settings_file in os.listdir(settings_path):
        return None
    settings = configparser.ConfigParser()
    settings.read(settings_path+settings_file)
    if not settings['DEFAULT']:
        return None
    if settings['DEFAULT']['Last_used_config']:
        return settings['DEFAULT']['Last_used_config'] 

def SaveConfigAsLastUsed(config_name : str) -> None:
    """Saves current config file as the last used and updates settings

        Args:
            config_name(str): Current config file name.
            
    """
    if not config_name.endswith(".xml"):
        return
    if not os.path.exists(settings_path):
        print(f"Creating settings directory:\n {settings_path}")
        os.makedirs(settings_path)
    settings = configparser.ConfigParser()
    if settings_file in os.listdir(settings_path):
        settings.read(settings_file)
    if not settings['DEFAULT']:
        settings['DEFAULT'] = {}
    settings['DEFAULT']['Last_used_config'] = config_name
    with open(settings_path+settings_file, 'w') as cfg:
        settings.write(cfg)

def StartProgram(config_name : str, argv : list = []):
    """Start slow control.

        Args:
            config_name(str): Current config file name.
            argv(list): Command line attributes passed to start.py except [-c, filename].
    """
    try:
        SaveConfigAsLastUsed(config_name)
    except:
        pass
    argv = ['-c', config_name] + argv
    gui2.start(argv)

def main(argv : list = []):
    config_name = "config/"
    # TODO: Check if -c configfile is in arguments list
    if False:
        # config_name = [from argv]
        pass
    else:
        try:
            last_used = GetLastUsedConfig()
            if last_used and last_used.endswith(".xml"):
                config_name = last_used
        except:
            pass
        config_name = UIGetConfigName(config_name)
    StartProgram(config_name, argv)

if __name__ == "__main__":
    main(sys.argv[1:])