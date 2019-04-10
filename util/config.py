from enum import Enum
from collections import defaultdict

from PyQt5.QtCore import QSettings


# Default file name to save.
DEFAULT_FILE = "loeser.php"
# Default fallback template file.
TEMPLATE_FILE = "template.php"
# Default file for the last saved application state.
SAVED_APP_STATE_FILE = "savedApplicationState.dat"
# Default settings file.
SETTINGS_FILE = "preferences.ini"

# General section name for QSettings
GENERAL_SECTION = "general"


class LaunchMode(Enum):
    WEBSITE = 0
    FILE = 1
    RESTORE = 2
    TEMPLATE = 3

    def __str__(self):
        return self.name.lower().capitalize()


class Map(defaultdict):
    """
    defaultdict subclass which allows accessing members by using the . syntax.
    """
    __getattr__ = defaultdict.get
    __setattr__ = defaultdict.__setitem__
    __delattr__ = defaultdict.__delitem__


def load_settings():
    """
    Load all settings and store them inside of a dictionary.
    """
    settings = QSettings(SETTINGS_FILE, QSettings.IniFormat)

    # Settings key: (type, default value)
    key_types_dict = {
        "launch_mode": (int, 0),
        "website_url": (str, "http://monoid.mathematik.uni-mainz.de/loeser.php"),
        "file_path": (str, ""),
        "save_interval": (int, 60),
        "enable_splashscreen": (bool, True),
        "Header/name_field": (str, "Name"),
        "Header/sum_field": (str, "Summe"),
        "Header/point_indices": (range, range(3,7))
    }

    # Construct a dictionary with subdictionaries for each section.
    prefs_dict = Map(Map)

    for k, v in key_types_dict.items():
        split_k = k.split("/")
        if len(split_k) == 2:
            section, key = split_k
        else:
            section, key = GENERAL_SECTION, k
        prefs_dict[section.lower()][key] = settings.value(k, v[1], type=v[0])

    return prefs_dict


def save_settings(prefs_dict):
    """
    Save all settings to a file.
    :param prefs_dict: all settings as dictionary
    """
    settings = QSettings(SETTINGS_FILE, QSettings.IniFormat)

    for section, values in prefs_dict.items():
        for key, val in values.items():
            if section == GENERAL_SECTION:
                settings.setValue(key, val)
            else:
                settings.setValue(section.capitalize() + "/" + key, val)

    # Flush settings to the disc
    del settings
