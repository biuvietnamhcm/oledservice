"""Menu and tab navigation manager"""

from enum import Enum


class Mode(Enum):
    """Navigation mode"""
    VIEW = "view"           # Navigating between tabs
    MENU = "menu"           # In settings/submenu
    EDIT = "edit"           # Editing a value


class TabManager:
    """Manages tab/screen navigation and state"""
    
    # Define all available tabs
    TABS = [
        {"name": "system", "label": "SYS", "index": 0},
        {"name": "weather", "label": "WEA", "index": 1},
        {"name": "network", "label": "NET", "index": 2},
        {"name": "settings", "label": "SET", "index": 3},
        {"name": "about", "label": "ABT", "index": 4},
    ]
    
    # Settings menu items
    SETTINGS_ITEMS = [
        {"name": "brightness", "label": "Brightness", "type": "slider", "min": 1, "max": 10},
        {"name": "contrast", "label": "Contrast", "type": "slider", "min": 0, "max": 100},
        {"name": "favorites", "label": "Favorites", "type": "toggle"},
        {"name": "wake_time", "label": "Wake Time", "type": "time"},
        {"name": "temp_unit", "label": "Temp Unit", "type": "toggle"},
    ]
    
    def __init__(self, settings_mgr):
        """
        Initialize tab manager
        
        Args:
            settings_mgr: SettingsManager instance
        """
        self.settings_mgr = settings_mgr
        self.current_mode = Mode.VIEW
        self.active_tab_index = 0
        self.menu_index = 0
        self.edit_value = None
        self.edit_item = None
        
        # Load last tab from settings
        last_tab = settings_mgr.get_last_tab()
        for tab in self.TABS:
            if tab["name"] == last_tab:
                self.active_tab_index = tab["index"]
                break
    
    def get_active_tab(self):
        """Get currently active tab"""
        return self.TABS[self.active_tab_index]
    
    def get_tab_name(self):
        """Get active tab name"""
        return self.get_active_tab()["name"]
    
    def get_tab_label(self):
        """Get active tab label (short 3-char)"""
        return self.get_active_tab()["label"]
    
    def get_all_tab_labels(self):
        """Get all tab labels for display"""
        labels = []
        for i, tab in enumerate(self.TABS):
            label = f"[{tab['label']}]" if i == self.active_tab_index else tab['label']
            labels.append(label)
        return " ".join(labels)
    
    def rotate_tabs(self, direction):
        """
        Rotate to next/previous tab
        
        Args:
            direction: 1 for right (next), -1 for left (previous)
        """
        if self.current_mode == Mode.VIEW:
            self.active_tab_index = (self.active_tab_index + direction) % len(self.TABS)
            self.settings_mgr.set_last_tab(self.get_tab_name())
            print(f"Switched to tab: {self.get_tab_name()}")
    
    def enter_settings_menu(self):
        """Enter settings menu (if in settings tab)"""
        if self.get_tab_name() == "settings":
            self.current_mode = Mode.MENU
            self.menu_index = 0
            print("Entered settings menu")
    
    def exit_settings_menu(self):
        """Exit settings menu back to view"""
        self.current_mode = Mode.VIEW
        self.menu_index = 0
        self.edit_item = None
        self.edit_value = None
        print("Exited settings menu")
    
    def rotate_menu(self, direction):
        """
        Navigate menu items
        
        Args:
            direction: 1 for down, -1 for up
        """
        if self.current_mode == Mode.MENU:
            self.menu_index = (self.menu_index + direction) % len(self.SETTINGS_ITEMS)
            print(f"Menu item: {self.SETTINGS_ITEMS[self.menu_index]['label']}")
    
    def get_current_menu_item(self):
        """Get currently selected menu item"""
        if self.current_mode == Mode.MENU:
            return self.SETTINGS_ITEMS[self.menu_index]
        return None
    
    def enter_edit_mode(self):
        """Enter edit mode for current menu item"""
        if self.current_mode == Mode.MENU:
            item = self.get_current_menu_item()
            if item:
                self.current_mode = Mode.EDIT
                self.edit_item = item
                self.edit_value = self.settings_mgr.get(item["name"])
                print(f"Editing: {item['label']}")
    
    def exit_edit_mode(self):
        """Exit edit mode and save"""
        if self.current_mode == Mode.EDIT and self.edit_item:
            # Save the value
            if self.edit_item["type"] == "slider":
                value = max(self.edit_item["min"], min(self.edit_item["max"], self.edit_value))
                self.edit_value = value
                
                # Handle brightness specially - it affects contrast
                if self.edit_item["name"] == "brightness":
                    self.settings_mgr.set_brightness(value)
                else:
                    self.settings_mgr.set(self.edit_item["name"], value)
            else:
                self.settings_mgr.set(self.edit_item["name"], self.edit_value)
            
            print(f"Saved {self.edit_item['label']}: {self.edit_value}")
            self.current_mode = Mode.MENU
            self.edit_item = None
            self.edit_value = None
    
    def rotate_edit_value(self, direction):
        """
        Change value in edit mode
        
        Args:
            direction: 1 to increase, -1 to decrease
        """
        if self.current_mode == Mode.EDIT and self.edit_item:
            item = self.edit_item
            if item["type"] == "slider":
                step = 1
                self.edit_value += direction * step
                self.edit_value = max(item["min"], min(item["max"], self.edit_value))
                print(f"{item['label']}: {self.edit_value}")
            elif item["type"] == "toggle":
                if isinstance(self.edit_value, bool):
                    self.edit_value = not self.edit_value
                else:
                    self.edit_value = True
                print(f"{item['label']}: {'ON' if self.edit_value else 'OFF'}")
            elif item["type"] == "time":
                # Simple time increment (would need better handling)
                print(f"{item['label']}: {self.edit_value}")
    
    def handle_button_press(self):
        """
        Handle button press based on current mode
        
        Returns:
            action: String describing what happened
        """
        if self.current_mode == Mode.VIEW:
            if self.get_tab_name() == "settings":
                self.enter_settings_menu()
                return "entered_settings"
            else:
                # Could expand to show more details for other tabs
                return "button_pressed"
        
        elif self.current_mode == Mode.MENU:
            self.enter_edit_mode()
            return "entered_edit"
        
        elif self.current_mode == Mode.EDIT:
            self.exit_edit_mode()
            return "saved_edit"
        
        return "no_action"
    
    def get_state(self):
        """Get full navigation state for display"""
        return {
            "mode": self.current_mode.value,
            "active_tab": self.get_tab_name(),
            "tab_labels": self.get_all_tab_labels(),
            "menu_index": self.menu_index if self.current_mode == Mode.MENU else None,
            "menu_item": self.get_current_menu_item(),
            "edit_item": self.edit_item,
            "edit_value": self.edit_value,
        }
