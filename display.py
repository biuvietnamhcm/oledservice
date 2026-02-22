"""OLED display management and rendering"""

from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.core.render import canvas
from datetime import datetime
from config import (
    DISPLAY_I2C_PORT,
    DISPLAY_I2C_ADDRESS,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
    DISPLAY_CYCLE_INTERVAL,
    TEXT_CHAR_WIDTH
)


class DisplayManager:
    """Manages OLED display without PIL/Pillow - optimized for 128x64"""
    
    def __init__(self, contrast=55):
        try:
            serial = i2c(port=DISPLAY_I2C_PORT, address=DISPLAY_I2C_ADDRESS)
            self.device = sh1106(serial)
            self.set_contrast(contrast)
        except Exception as e:
            print(f"Error initializing display: {e}")
            self.device = None
        
        self.current_screen = 0
        self.last_cycle_time = 0
        self.contrast_value = contrast
    
    def clear(self):
        """Clear the display"""
        if self.device:
            self.device.clear()
    
    def set_contrast(self, value):
        """Set display contrast (0-100)"""
        if self.device:
            # Normalize to device range (0-255)
            device_contrast = int((value / 100.0) * 255)
            self.device.contrast(device_contrast)
            self.contrast_value = value
    
    def draw_text(self, d, text, x, y):
        """Draw text at position"""
        d.text((x, y), text, fill=255)
    
    def draw_text_centered(self, d, text, y):
        """Draw centered text (6 pixels per character)"""
        text_width = len(text) * 6
        x = max(0, (DISPLAY_WIDTH - text_width) // 2)
        d.text((x, y), text, fill=255)
    
    def draw_divider(self, d, y):
        """Draw horizontal divider line"""
        d.line((0, y, DISPLAY_WIDTH - 1, y), fill=255)
    
    def draw_tab_header(self, d, tab_labels):
        """Draw tab header with active tab highlighted"""
        # Tab header at top: [SYS] WEA NET SET ABT
        self.draw_text_centered(d, tab_labels, 2)
        self.draw_divider(d, 12)
    
    def draw_progress_bar(self, d, value, min_val, max_val, x, y, width=50, height=6):
        """Draw a horizontal progress bar"""
        # Calculate fill percentage
        percent = (value - min_val) / (max_val - min_val)
        filled_width = int(width * percent)
        
        # Draw border
        d.rectangle((x, y, x + width, y + height), outline=255, fill=0)
        # Draw fill
        if filled_width > 0:
            d.rectangle((x, y, x + filled_width, y + height), fill=255)
    
    def draw_screen_time(self, d, now):
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%a %d %b")

        self.draw_text_centered(d, time_str, 8)
        self.draw_divider(d, 26)
        self.draw_text_centered(d, date_str, 30)
        self.draw_divider(d, 50)
        self.draw_text_centered(d, "Time", 54)
    
    def draw_screen_system(self, d, stats, ip_status):
        """Draw system - dual column compact layout"""
        self.draw_text(d, "SYSTEM", 2, 2)
        self.draw_divider(d, 12)
        
        y = 14
        line_h = 12
        
        # Row 1: CPU Temp | CPU Usage
        if stats.get("cpu_temp") or stats.get("cpu_usage"):
            temp_val = str(stats.get('cpu_temp', 'N/A'))
            cpu_val = str(stats.get('cpu_usage', 'N/A'))
            left = f"T:{temp_val}C"
            right = f"C:{cpu_val}%"
            self.draw_text(d, left, 2, y)
            self.draw_text(d, right, 70, y)
            y += line_h
        
        # Row 2: RAM | Disk
        if stats.get("memory_usage") or stats.get("disk_usage"):
            ram_val = str(stats.get('memory_usage', 'N/A'))
            disk_val = str(stats.get('disk_usage', 'N/A'))
            left = f"R:{ram_val}%"
            right = f"D:{disk_val}%"
            self.draw_text(d, left, 2, y)
            self.draw_text(d, right, 70, y)
            y += line_h
        
        # IP Address (truncated)
        self.draw_divider(d, 50)
        ip_short = str(ip_status)[:13] if len(str(ip_status)) > 13 else str(ip_status)
        self.draw_text(d, f"IP:{ip_short}", 2, 54)
    
    def draw_screen_weather(self, d, weather_data):
        self.draw_text(d, "WEATHER", 2, 2)
        self.draw_divider(d, 12)

        if weather_data.get("updated"):
            city = str(weather_data.get("city", "Unknown"))[:16]
            temp = str(weather_data.get("temp", "N/A"))
            condition = str(weather_data.get("condition", "N/A"))[:12]
            humidity = str(weather_data.get("humidity", "N/A"))
            wind = str(weather_data.get("wind_speed", "N/A"))

            # City
            self.draw_text_centered(d, city, 14)

            # Temperature (main focus)
            self.draw_text_centered(d, f"{temp}C", 24)

            # Condition
            self.draw_text_centered(d, condition, 34)

            # Humidity + Wind
            self.draw_divider(d, 44)
            stats_line = f"H:{humidity}% W:{wind}m/s"
            self.draw_text_centered(d, stats_line, 48)
        else:
            self.draw_text_centered(d, "Fetching...", 28)

        self.draw_text(d, "Weather", 2, 54)
    
    def draw_screen_network(self, d, ip_status, network_info):
        """Draw network - WiFi name and signal strength with icon"""
        self.draw_text(d, "NETWORK", 2, 2)
        self.draw_divider(d, 12)
        
        # WiFi SSID
        wifi_name = str(network_info.get("ssid", "N/A"))[:12]
        self.draw_text_centered(d, wifi_name, 14)
        
        # Signal strength with icon (bars instead of dBm)
        signal_icon = str(network_info.get("signal_icon", "N/A"))
        self.draw_text_centered(d, signal_icon, 24)
        
        # IP Address
        self.draw_divider(d, 35)
        ip_str = str(ip_status)
        ip_short = ip_str[:11] if len(ip_str) > 11 else ip_str
        self.draw_text_centered(d, ip_short, 40)
        
        # Status
        self.draw_divider(d, 50)
        self.draw_text_centered(d, "WiFi", 54)
    
    def draw_wake_alarm(self, d, remaining_time):
        """Draw wake alarm - large countdown"""
        self.draw_text_centered(d, "WAKE ALARM", 4)
        self.draw_divider(d, 12)
        countdown = f"{remaining_time}s"
        self.draw_text_centered(d, countdown, 22)
        self.draw_divider(d, 48)
        self.draw_text_centered(d, "Active", 53)
    
    def draw_screen_settings(self, d, menu_state):
        """Draw settings screen with menu navigation"""
        self.draw_text(d, "SETTINGS", 2, 2)
        self.draw_divider(d, 12)
        
        if menu_state["mode"] == "view":
            # Show all settings overview
            self.draw_text(d, "Brightness: " + str(menu_state.get("brightness", 5)), 2, 16)
            self.draw_text(d, "Contrast: " + str(menu_state.get("contrast", 55)), 2, 26)
            self.draw_text(d, "Wake Time: " + str(menu_state.get("wake_time", "07:30")), 2, 36)
            self.draw_divider(d, 48)
            self.draw_text_centered(d, "Press to edit", 52)
        
        elif menu_state["mode"] == "menu":
            # Show menu with selection indicator
            items = [
                "Brightness",
                "Contrast",
                "Favorites",
                "Wake Time",
                "Temp Unit"
            ]
            menu_idx = menu_state.get("menu_index", 0)
            
            y = 16
            for i, item in enumerate(items[:4]):  # Show 4 items max
                prefix = "> " if i == menu_idx else "  "
                self.draw_text(d, prefix + item, 2, y)
                y += 12
            
            self.draw_divider(d, 52)
            self.draw_text_centered(d, "Rotate/Press", 55)
        
        elif menu_state["mode"] == "edit":
            # Show value being edited
            item = menu_state.get("menu_item", {})
            label = item.get("label", "Unknown")
            value = menu_state.get("edit_value", 0)
            
            self.draw_text_centered(d, label, 16)
            self.draw_divider(d, 28)
            
            # Draw progress bar for sliders
            if item.get("type") == "slider":
                min_v = item.get("min", 0)
                max_v = item.get("max", 100)
                self.draw_progress_bar(d, value, min_v, max_v, 15, 36, width=98)
                self.draw_text_centered(d, str(value), 46)
            else:
                self.draw_text_centered(d, str(value), 36)
            
            self.draw_divider(d, 52)
            self.draw_text_centered(d, "Press to save", 55)
    
    def draw_screen_about(self, d):
        """Draw about screen"""
        self.draw_text(d, "ABOUT", 2, 2)
        self.draw_divider(d, 12)
        self.draw_text_centered(d, "OLED Monitor", 16)
        self.draw_text_centered(d, "v2.0", 26)
        self.draw_divider(d, 36)
        self.draw_text_centered(d, "GPIO 6/25/27", 40)
        self.draw_text_centered(d, "Interactive Tab UI", 50)
    
    def render(self, data):
        """Render display with tab-based navigation"""
        if not self.device:
            return
        
        # Update contrast if provided
        if "contrast" in data:
            self.set_contrast(data["contrast"])
        
        with canvas(self.device) as d:
            # Priority: Wake alarm takes over everything
            if data.get("wake_active"):
                self.draw_wake_alarm(d, data["remaining_time"])
            else:
                # Get menu state if available
                menu_state = data.get("menu_state", {})
                active_tab = data.get("active_tab", "system")
                
                # Draw tab header
                tab_labels = data.get("tab_labels", "SYS WEA NET SET ABT")
                self.draw_tab_header(d, tab_labels)
                
                # Draw content based on active tab
                if active_tab == "system":
                    self.draw_screen_system(d, data["stats"], data["ip_status"])
                elif active_tab == "weather":
                    self.draw_screen_weather(d, data["weather"])
                elif active_tab == "network":
                    self.draw_screen_network(d, data["ip_status"], data["signal"])
                elif active_tab == "settings":
                    # Merge settings data with menu state
                    settings_data = {
                        "mode": menu_state.get("mode", "view"),
                        "menu_index": menu_state.get("menu_index", 0),
                        "menu_item": menu_state.get("menu_item"),
                        "edit_value": menu_state.get("edit_value"),
                        "brightness": data.get("brightness", 5),
                        "contrast": data.get("contrast", 55),
                        "wake_time": data.get("wake_time", "07:30")
                    }
                    self.draw_screen_settings(d, settings_data)
                elif active_tab == "about":
                    self.draw_screen_about(d)
