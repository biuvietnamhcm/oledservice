"""Settings manager - JSON persistence for app configuration"""

import json
import os
from pathlib import Path


class SettingsManager:
    """Manages application settings with JSON persistence"""
    
    # Default settings path
    SETTINGS_FILE = "/home/biu/settings.json"
    
    # Default settings
    DEFAULTS = {
        "brightness": 5,           # 1-10, maps to contrast
        "contrast": 55,            # 0-100
        "favorites": [],           # List of favorite tab names
        "last_tab": "home",        # Last active tab (new home screen)
        "wake_time": "07:30",      # Wake alarm time (HH:MM)
        "temperature_unit": "C",   # C or F
        "wifi_enabled": True,
        "weather_enabled": True
    }
    
    def __init__(self, settings_file=None):
        """Initialize settings manager"""
        self.settings_file = settings_file or self.SETTINGS_FILE
        self.settings = self.DEFAULTS.copy()
        self.load()
    
    def load(self):
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults (keeps new defaults if file is old)
                    self.settings = {**self.DEFAULTS, **loaded}
                    print(f"Settings loaded from {self.settings_file}")
            else:
                print(f"Settings file not found, using defaults")
                self.settings = self.DEFAULTS.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = self.DEFAULTS.copy()
    
    def save(self):
        """Save settings to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print(f"Settings saved to {self.settings_file}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value and save"""
        self.settings[key] = value
        self.save()
    
    def update(self, updates):
        """Update multiple settings at once"""
        self.settings.update(updates)
        self.save()
    
    def get_all(self):
        """Get all settings"""
        return self.settings.copy()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.DEFAULTS.copy()
        self.save()
    
    def set_brightness(self, level):
        """Set brightness level (1-10) and corresponding contrast"""
        level = max(1, min(10, level))  # Clamp to 1-10
        contrast = 10 + (level - 1) * 10  # Map 1-10 to 10-100
        self.settings["brightness"] = level
        self.settings["contrast"] = contrast
        self.save()
    
    def get_brightness(self):
        """Get brightness level (1-10)"""
        return self.settings.get("brightness", 5)
    
    def get_contrast(self):
        """Get contrast value (0-100) for display"""
        return self.settings.get("contrast", 55)
    
    def add_favorite(self, tab_name):
        """Add tab to favorites"""
        if tab_name not in self.settings["favorites"]:
            self.settings["favorites"].append(tab_name)
            self.save()
    
    def remove_favorite(self, tab_name):
        """Remove tab from favorites"""
        if tab_name in self.settings["favorites"]:
            self.settings["favorites"].remove(tab_name)
            self.save()
    
    def is_favorite(self, tab_name):
        """Check if tab is in favorites"""
        return tab_name in self.settings.get("favorites", [])
    
    def get_favorites(self):
        """Get list of favorite tabs"""
        return self.settings.get("favorites", [])
    
    def set_last_tab(self, tab_name):
        """Set last active tab"""
        self.settings["last_tab"] = tab_name
        self.save()
    
    def get_last_tab(self):
        """Get last active tab"""
        return self.settings.get("last_tab", "system")
