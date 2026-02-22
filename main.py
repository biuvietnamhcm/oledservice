#!/usr/bin/env python3
"""
Main application - System monitoring and control with OLED display
Modular architecture for easy management and extension
"""

import time
import threading
from datetime import datetime

from config import WAKE_CHECK_INTERVAL
from display import DisplayManager
from system_monitor import get_system_stats
from weather import WeatherManager
from wifi_manager import WiFiManager
from wake_timer import WakeTimer
from web_server import WebServer


def main():
    """Main application"""
    
    print("🚀 Starting System Monitor...")
    
    # Initialize components
    display_mgr = DisplayManager()
    system_monitor = None
    weather_mgr = WeatherManager()
    wifi_mgr = WiFiManager()
    wake_timer = WakeTimer()
    web_server = WebServer(wake_timer)
    
    # Start background threads
    print("📡 Starting services...")
    web_server.start()
    
    def wifi_monitor():
        """Monitor WiFi connection in background"""
        while True:
            wifi_mgr.check_connection()
            time.sleep(5)
    
    def weather_monitor():
        """Update weather data in background"""
        while True:
            if weather_mgr.should_update():
                print("🌤️ Updating weather...")
                weather_mgr.fetch_weather()
            time.sleep(30)
    
    # Start background threads as daemons
    threading.Thread(target=wifi_monitor, daemon=True).start()
    threading.Thread(target=weather_monitor, daemon=True).start()
    
    print("✅ All services started")
    print("🎯 Main loop running...")
    
    try:
        while True:
            # Get current data
            now = datetime.now()
            stats = get_system_stats()
            ip_status = wifi_mgr.get_ip_status()
            
            # Get WiFi info
            signal_dbm = wifi_mgr.get_signal_strength()
            signal_icon = wifi_mgr.signal_to_icon(signal_dbm)
            wifi_name = wifi_mgr.get_wifi_name()
            
            network_info = {
                "ssid": wifi_name,
                "signal_icon": signal_icon,
                "dbm": signal_dbm
            }
            
            # Check wake alarm
            wake_timer.check_alarm(now)
            remaining = wake_timer.update()
            
            # Prepare display data
            display_data = {
                "now": now,
                "stats": stats,
                "weather": weather_mgr.weather_data,
                "ip_status": ip_status,
                "signal": network_info,
                "wake_active": wake_timer.is_active,
                "remaining_time": remaining or 0
            }
            
            # Render display
            display_mgr.render(display_data)
            
            time.sleep(WAKE_CHECK_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n⛔ Shutting down...")
        display_mgr.clear()
        web_server.stop()
        print("👋 Goodbye!")


if __name__ == "__main__":
    main()
