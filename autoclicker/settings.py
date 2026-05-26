import json
import os
import sys
from pathlib import Path


def get_settings_path():
    try:
        sys._MEIPASS
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            folder = Path(appdata) / "tungtungclicker"
            folder.mkdir(parents=True, exist_ok=True)
            return folder / "settings.json"
    except AttributeError:
        pass
    return Path(__file__).parent / "settings.json"


DEFAULT_SETTINGS = {
    "clicker": {
        "clicks_per_unit": 20,
        "unit": "s",
        "button": "left",
        "mode": "toggle",
        "duty_cycle": 45,
        "speed_variation": 35,
        "double_click": False,
        "click_limit_enabled": False,
        "click_limit": 1000,
        "time_limit_enabled": False,
        "time_limit": 60,
        "corner_stop_enabled": False,
        "corner_stop_px": 25,
        "edge_stop_enabled": False,
        "edge_stop_px": 40,
        "position_enabled": False,
        "target_position": [0, 0]
    },
    "panels": {
        "duty_cycle": True,
        "speed_variation": True,
        "double_click": True,
        "click_limit": True,
        "time_limit": True,
        "corner_stop": True,
        "edge_stop": True,
        "position": True
    },
    "hotkey": {
        "current_hotkey": "f6"
    },
    "gui": {
        "theme": "dark"
    }
}


class SettingsManager:
    def __init__(self):
        self.settings_path = get_settings_path()
        self.settings = {}
        self.load()

    def load(self):
        if self.settings_path.exists():
            try:
                with open(self.settings_path, "r") as f:
                    self.settings = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.settings = DEFAULT_SETTINGS.copy()
        else:
            self.settings = DEFAULT_SETTINGS.copy()

    def save(self):
        try:
            with open(self.settings_path, "w") as f:
                json.dump(self.settings, f, indent=4)
        except IOError:
            pass

    def get(self, *keys, default=None):
        val = self.settings
        for key in keys:
            if isinstance(val, dict):
                val = val.get(key)
                if val is None:
                    return default
            else:
                return default
        return val

    def set(self, value, *keys):
        if len(keys) == 0:
            return
        target = self.settings
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value
        self.save()

    def reset(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.save()


settings = SettingsManager()