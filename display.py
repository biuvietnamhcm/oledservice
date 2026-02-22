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
    DISPLAY_CYCLE_INTERVAL
)


class DisplayManager:
    """Manages OLED display without PIL/Pillow - optimized for 128x64"""
    
    def __init__(self):
        try:
            serial = i2c(port=DISPLAY_I2C_PORT, address=DISPLAY_I2C_ADDRESS)
            self.device = sh1106(serial)
        except Exception as e:
            print(f"Error initializing display: {e}")
            self.device = None
        
        self.current_screen = 0
        self.last_cycle_time = 0
    
    def clear(self):
        """Clear the display"""
        if self.device:
            self.device.clear()
    
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
    
    def render(self, data):
        """Render display with cycling screens"""
        if not self.device:
            return
        
        import time
        current_time = time.time()
        
        # Check if we should cycle screens
        if current_time - self.last_cycle_time >= DISPLAY_CYCLE_INTERVAL:
            self.current_screen = (self.current_screen + 1) % 4
            self.last_cycle_time = current_time
        
        with canvas(self.device) as d:
            if data.get("wake_active"):
                self.draw_wake_alarm(d, data["remaining_time"])
            elif self.current_screen == 0:
                self.draw_screen_time(d, data["now"])
            elif self.current_screen == 1:
                self.draw_screen_system(d, data["stats"], data["ip_status"])
            elif self.current_screen == 2:
                self.draw_screen_weather(d, data["weather"])
            elif self.current_screen == 3:
                self.draw_screen_network(d, data["ip_status"], data["signal"])
