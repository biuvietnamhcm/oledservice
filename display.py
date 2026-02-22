"""OLED display management and rendering - Modern Mobile UI"""

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
    TEXT_CHAR_WIDTH,
    WIFI_ICON_WEAK,
    WIFI_ICON_MEDIUM,
    WIFI_ICON_STRONG,
    WIFI_ICON_EXCELLENT
)


class DisplayManager:
    """Manages OLED display with modern mobile UI for 128x64"""
    
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
        self.animation_frame = 0  # For animated elements
    
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
    
    def draw_status_bar(self, d, signal_strength, battery_percent, is_wifi_connected):
        """Draw modern status bar at top"""
        # Left: WiFi icon
        if is_wifi_connected:
            if signal_strength > -50:
                wifi_str = "█"
            elif signal_strength > -70:
                wifi_str = "▓"
            elif signal_strength > -85:
                wifi_str = "▒"
            else:
                wifi_str = "░"
        else:
            wifi_str = "✕"
        
        d.text((2, 0), wifi_str, fill=255)
        
        # Right: Battery indicator
        battery_str = f"{battery_percent}%"
        battery_x = DISPLAY_WIDTH - len(battery_str) * 6 - 2
        d.text((battery_x, 0), battery_str, fill=255)
        
        # Divider
        d.line((0, 8, DISPLAY_WIDTH, 8), fill=255)
    
    def draw_progress_bar(self, d, value, min_val, max_val, x, y, width=50, height=4):
        """Draw a compact horizontal progress bar"""
        # Clamp value
        value = max(min_val, min(max_val, value))
        # Calculate fill percentage
        percent = (value - min_val) / (max_val - min_val) if max_val > min_val else 0
        filled_width = int(width * percent)
        
        # Draw border
        d.rectangle((x, y, x + width, y + height), outline=255, fill=0)
        # Draw fill
        if filled_width > 0:
            d.rectangle((x, y, x + filled_width, y + height), fill=255)
    
    def draw_battery_bar(self, d, percent, x, y):
        """Draw battery indicator (vertical bar)"""
        height = 10
        width = 3
        filled = int(height * (percent / 100.0))
        d.rectangle((x, y, x + width, y + height), outline=255, fill=0)
        if filled > 0:
            d.rectangle((x, y + height - filled, x + width, y + height), fill=255)
        # Nipple
        d.rectangle((x, y - 2, x + width, y - 1), fill=255)
    
    def draw_status_indicator(self, d, x, y, status, size=4):
        """Draw status indicator dot"""
        if status:
            d.ellipse((x, y, x + size, y + size), fill=255)
        else:
            d.ellipse((x, y, x + size, y + size), outline=255, fill=0)
    
    def draw_home_screen(self, d, now, stats):
        """Draw beautiful home screen with time and basic info"""
        # Time - large and centered
        time_str = now.strftime("%H:%M")
        self.draw_text_centered(d, time_str, 14)
        
        # Date
        date_str = now.strftime("%a, %d %b")
        self.draw_text_centered(d, date_str, 28)
        
        # Divider
        self.draw_divider(d, 38)
        
        # Bottom status: CPU Temp + Memory
        cpu_temp = stats.get('cpu_temp', '?')
        mem = stats.get('memory_usage', '?')
        bottom_str = f"T:{cpu_temp}° M:{mem}%"
        self.draw_text_centered(d, bottom_str, 44)
        
        # Uptime
        uptime = stats.get('uptime', '?')
        uptime_str = f"Up: {uptime}"
        self.draw_text_centered(d, uptime_str, 54)
    
    def draw_system_screen(self, d, stats, ip_status):
        """Draw system monitor with visual progress bars"""
        self.draw_text(d, "● SYSTEM", 2, 10)
        self.draw_divider(d, 20)
        
        y = 22
        line_h = 11
        
        # CPU Temperature
        cpu_temp = stats.get('cpu_temp', 0)
        temp_str = f"CPU:{cpu_temp}°C"
        self.draw_text(d, temp_str, 2, y)
        self.draw_progress_bar(d, cpu_temp, 0, 100, 70, y + 2, width=55, height=3)
        y += line_h
        
        # Memory Usage
        mem_usage = stats.get('memory_usage', 0)
        mem_str = f"RAM:{mem_usage}%"rot
        self.draw_text(d, mem_str, 2, y)
        self.draw_progress_bar(d, mem_usage, 0, 100, 70, y + 2, width=55, height=3)
        y += line_h
        
        # Disk Usage
        disk_usage = stats.get('disk_usage', 0)
        disk_str = f"DSK:{disk_usage}%"
        self.draw_text(d, disk_str, 2, y)
        self.draw_progress_bar(d, disk_usage, 0, 100, 70, y + 2, width=55, height=3)
    
    def draw_weather_screen(self, d, weather_data):
        """Draw weather with large temperature display"""
        self.draw_text(d, "☁ WEATHER", 2, 10)
        self.draw_divider(d, 20)

        if weather_data.get("updated"):
            city = str(weather_data.get("city", "Unknown"))[:14]
            temp = str(weather_data.get("temp", "N/A"))
            condition = str(weather_data.get("condition", "N/A"))[:13]
            humidity = str(weather_data.get("humidity", "N/A"))
            wind = str(weather_data.get("wind_speed", "N/A"))

            # Location
            self.draw_text_centered(d, city, 24)

            # Large Temperature
            temp_display = f"{temp}°C"
            self.draw_text_centered(d, temp_display, 32)

            # Condition and details
            self.draw_divider(d, 45)
            self.draw_text_centered(d, condition, 48)
            
            # Humidity and Wind
            detail_str = f"H:{humidity}% W:{wind}m/s"
            self.draw_text_centered(d, detail_str, 57)
        else:
            self.draw_text_centered(d, "Loading...", 28)
    
    def draw_network_screen(self, d, ip_status, network_info):
        """Draw network info with signal strength visualization"""
        self.draw_text(d, "📶 NETWORK", 2, 10)
        self.draw_divider(d, 20)
        
        # WiFi SSID
        wifi_name = str(network_info.get("ssid", "No WiFi"))[:16]
        self.draw_text_centered(d, wifi_name, 24)
        
        # Signal strength bars
        dbm = network_info.get("dbm", -100)
        if dbm > -50:
            signal_bar = "████"
            quality = "Excellent"
        elif dbm > -70:
            signal_bar = "███░"
            quality = "Good"
        elif dbm > -85:
            signal_bar = "██░░"
            quality = "Fair"
        else:
            signal_bar = "█░░░"
            quality = "Weak"
        
        self.draw_text_centered(d, signal_bar, 33)
        self.draw_text_centered(d, quality, 42)
        
        # IP Address
        self.draw_divider(d, 50)
        ip_str = str(ip_status)[:13]
        self.draw_text_centered(d, ip_str, 54)
    
    def draw_power_screen(self, d, stats):
        """Draw power/battery information"""
        self.draw_text(d, "🔋 POWER", 2, 10)
        self.draw_divider(d, 20)
        
        # Battery simulation from system uptime
        uptime_hours = stats.get('uptime_hours', 0)
        battery_pct = max(5, 100 - (uptime_hours % 48) * 2)  # Simulate battery drain
        
        # Battery percentage
        self.draw_text_centered(d, f"Battery: {battery_pct}%", 24)
        
        # Battery bar
        self.draw_progress_bar(d, battery_pct, 0, 100, 15, 32, width=98, height=6)
        
        # Uptime
        uptime = stats.get('uptime', '?')
        self.draw_text_centered(d, f"Uptime: {uptime}", 42)
        
        # Status
        if battery_pct > 20:
            status = "Charging"
        else:
            status = "Low Battery!"
        self.draw_text_centered(d, status, 54)
    
    def draw_settings_screen(self, d, menu_state):
        """Draw settings with modern menu interface"""
        self.draw_text(d, "⚙ SETTINGS", 2, 10)
        self.draw_divider(d, 20)
        
        if menu_state["mode"] == "view":
            # Overview
            self.draw_text(d, f"Brightness: {menu_state.get('brightness', 5)}/10", 2, 24)
            self.draw_text(d, f"Contrast: {menu_state.get('contrast', 55)}%", 2, 34)
            self.draw_text(d, f"Wake: {menu_state.get('wake_time', '07:30')}", 2, 44)
            self.draw_divider(d, 52)
            self.draw_text_centered(d, "Press Button", 56)
        
        elif menu_state["mode"] == "menu":
            # Menu selection
            items = [
                "Brightness",
                "Contrast",
                "Wake Time",
                "Temp Unit",
                "Favorites"
            ]
            menu_idx = menu_state.get("menu_index", 0)
            
            # Show 3 items with indicator
            start_idx = max(0, menu_idx - 1)
            y = 24
            for i in range(3):
                idx = (start_idx + i) % len(items)
                prefix = "► " if idx == menu_idx else "  "
                self.draw_text(d, prefix + items[idx], 4, y)
                y += 11
            
            self.draw_divider(d, 52)
            self.draw_text_centered(d, "↕ Rotate | Press Select", 56)
        
        elif menu_state["mode"] == "edit":
            # Edit mode
            item = menu_state.get("menu_item") or {}

            if not isinstance(item, dict):
                item = {}

            label = item.get("label", "Unknown")
            value = menu_state.get("edit_value", 0)
                        
            self.draw_text_centered(d, label, 22)
            self.draw_divider(d, 32)
            
            if item.get("type") == "slider":
                min_v = item.get("min", 0)
                max_v = item.get("max", 100)
                self.draw_progress_bar(d, value, min_v, max_v, 10, 38, width=108, height=5)
                self.draw_text_centered(d, str(value), 48)
            else:
                self.draw_text_centered(d, str(value), 42)
            
            self.draw_divider(d, 52)
            self.draw_text_centered(d, "Press to Save", 56)
    
    def draw_timer_screen(self, d, wake_timer_data):
        """Draw timer/alarm screen"""
        self.draw_text(d, "⏱ TIMER", 2, 10)
        self.draw_divider(d, 20)
        
        is_active = wake_timer_data.get('active', False)
        remaining = wake_timer_data.get('remaining', 0)
        wake_time = wake_timer_data.get('time', '07:30')
        
        if is_active:
            # Alarm is ringing
            countdown = f"{remaining}s"
            self.draw_text_centered(d, "⏰ ALARM!", 22)
            self.draw_text_centered(d, countdown, 36)
            self.draw_divider(d, 50)
            self.draw_text_centered(d, "Press to Stop", 56)
        else:
            # Show next wake time
            self.draw_text_centered(d, "Next Alarm", 24)
            self.draw_text_centered(d, wake_time, 34)
            self.draw_divider(d, 46)
            
            # Status
            self.draw_text_centered(d, "Alarm Armed", 54)
    
    def draw_about_screen(self, d):
        """Draw about/info screen"""
        self.draw_text(d, "ℹ ABOUT", 2, 10)
        self.draw_divider(d, 20)
        self.draw_text_centered(d, "OLED Monitor", 26)
        self.draw_text_centered(d, "v3.0 Mobile UI", 36)
        self.draw_divider(d, 46)
        self.draw_text_centered(d, "Rotary: GPIO 6/25/27", 52)
        self.draw_text_centered(d, "Press for more info", 60)
    
    def render(self, data):
        """Render display with modern mobile UI and tab navigation"""
        if not self.device:
            return
        
        # Update contrast if provided
        if "contrast" in data:
            self.set_contrast(data["contrast"])
        
        with canvas(self.device) as d:
            # Get base data
            menu_state = data.get("menu_state", {})
            active_tab = data.get("active_tab", "home")
            stats = data.get("stats", {})
            signal_dbm = data.get("signal", {}).get("dbm", -100)
            
            # Draw status bar at top
            is_connected = signal_dbm > -100
            battery_pct = max(5, 100 - (stats.get('uptime_hours', 0) % 48) * 2)
            self.draw_status_bar(d, signal_dbm, battery_pct, is_connected)
            
            # Priority: Wake alarm takes over everything
            if data.get("wake_active"):
                wake_data = {
                    'active': True,
                    'remaining': data.get("remaining_time", 0),
                    'time': data.get("wake_time", "07:30")
                }
                self.draw_timer_screen(d, wake_data)
            else:
                # Draw content based on active tab
                if active_tab == "home":
                    self.draw_home_screen(d, data["now"], stats)
                elif active_tab == "system":
                    self.draw_system_screen(d, stats, data.get("ip_status", "N/A"))
                elif active_tab == "weather":
                    self.draw_weather_screen(d, data.get("weather", {}))
                elif active_tab == "network":
                    self.draw_network_screen(d, data.get("ip_status", "N/A"), data.get("signal", {}))
                elif active_tab == "power":
                    self.draw_power_screen(d, stats)
                elif active_tab == "settings":
                    # Prepare settings data
                    settings_data = {
                        "mode": menu_state.get("mode", "view"),
                        "menu_index": menu_state.get("menu_index", 0),
                        "menu_item": menu_state.get("menu_item"),
                        "edit_value": menu_state.get("edit_value"),
                        "brightness": data.get("brightness", 5),
                        "contrast": data.get("contrast", 55),
                        "wake_time": data.get("wake_time", "07:30")
                    }
                    self.draw_settings_screen(d, settings_data)
                elif active_tab == "timer":
                    wake_data = {
                        'active': data.get("wake_active", False),
                        'remaining': data.get("remaining_time", 0),
                        'time': data.get("wake_time", "07:30")
                    }
                    self.draw_timer_screen(d, wake_data)
                else:
                    self.draw_about_screen(d)
            
            # Animate
            self.animation_frame = (self.animation_frame + 1) % 10
