#!/usr/bin/env python3
"""
Main application - Interactive System Monitor with Rotary Encoder Control
Tab-based navigation with settings and brightness control
"""

import time
import threading
from datetime import datetime

from config import WAKE_CHECK_INTERVAL, RENDER_INTERVAL
from display import DisplayManager
from rotary_encoder import RotaryEncoderHandler
from menu_manager import TabManager
from settings_manager import SettingsManager
from system_monitor import get_system_stats
from weather import WeatherManager
from wifi_manager import WiFiManager
from wake_timer import WakeTimer
from web_server import WebServer


def main():
    print("Starting Interactive OLED Monitor with Rotary Encoder...")

    # ==============================
    # Initialize managers
    # ==============================
    settings_mgr = SettingsManager()
    display_mgr = DisplayManager(contrast=settings_mgr.get_contrast())
    menu_mgr = TabManager(settings_mgr)

    weather_mgr = WeatherManager()
    wifi_mgr = WiFiManager()
    wake_timer = WakeTimer()
    web_server = WebServer(wake_timer)

    # ==============================
    # Initialize rotary encoder
    # ==============================
    rotary = RotaryEncoderHandler(
        pin_push=25,
        pin_a=26,
        pin_b=16
    )

    # ==============================
    # Rotary Callbacks
    # ==============================
    def on_rotate(direction, steps):
        print(f"[Encoder] Rotated: {'CW' if direction > 0 else 'CCW'}")

        if menu_mgr.current_mode.value == "view":
            menu_mgr.rotate_tabs(direction)

        elif menu_mgr.current_mode.value == "menu":
            menu_mgr.rotate_menu(direction)

        elif menu_mgr.current_mode.value == "edit":
            menu_mgr.rotate_edit_value(direction)

    def on_button_press():
        print("[Encoder] Button pressed")
        action = menu_mgr.handle_button_press()
        print(f"[Action] {action}")

    rotary.on_rotation(on_rotate)
    rotary.on_button_press(on_button_press)

    # ==============================
    # Start background services
    # ==============================
    print("Starting services...")
    web_server.start()

    def wifi_monitor():
        while True:
            try:
                wifi_mgr.check_connection()
                time.sleep(5)
            except Exception as e:
                print(f"WiFi monitor error: {e}")
                time.sleep(5)

    def weather_monitor():
        while True:
            try:
                if weather_mgr.should_update():
                    print("Updating weather...")
                    weather_mgr.fetch_weather()
                time.sleep(600)  # 10 minutes instead of 30 seconds
            except Exception as e:
                print(f"Weather monitor error: {e}")
                time.sleep(600)

    threading.Thread(target=wifi_monitor, daemon=True).start()
    threading.Thread(target=weather_monitor, daemon=True).start()

    print("All services started")
    print("Main loop running...")

    last_render_time = 0

    try:
        while True:
            now = datetime.now()

            # Throttle rendering
            current_time = time.time()
            if current_time - last_render_time < RENDER_INTERVAL:
                time.sleep(0.05)
                continue

            last_render_time = current_time

            # ==============================
            # Collect System Data
            # ==============================
            stats = get_system_stats()
            ip_status = wifi_mgr.get_ip_status()
            signal_dbm = wifi_mgr.get_signal_strength()
            signal_icon = wifi_mgr.signal_to_icon(signal_dbm)
            wifi_name = wifi_mgr.get_wifi_name()

            network_info = {
                "ssid": wifi_name,
                "signal_icon": signal_icon,
                "dbm": signal_dbm
            }

            wake_timer.check_alarm(now)
            remaining = wake_timer.update()

            menu_state = menu_mgr.get_state()

            # ==============================
            # Prepare display data
            # ==============================
            display_data = {
                "now": now,
                "stats": stats,
                "weather": weather_mgr.weather_data,
                "ip_status": ip_status,
                "signal": network_info,
                "wake_active": wake_timer.is_active,
                "remaining_time": remaining or 0,
                "active_tab": menu_mgr.get_tab_name(),
                "tab_labels": menu_mgr.get_all_tab_labels(),
                "menu_state": menu_state,
                "brightness": settings_mgr.get_brightness(),
                "contrast": settings_mgr.get_contrast(),
                "wake_time": settings_mgr.get("wake_time", "07:30"),
                # Additional data for new screens
                "battery_percent": max(5, 100 - (stats.get('uptime_hours', 0) % 48) * 2),
            }

            display_mgr.render(display_data)

            time.sleep(WAKE_CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nShutting down...")
        rotary.cleanup()
        display_mgr.clear()
        web_server.stop()
        print("Goodbye!")


if __name__ == "__main__":
    main()
