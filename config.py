"""Configuration and constants"""

# File paths
WAKE_FILE = "/home/biu/wakeup.json"
CERT_FILE = "/home/biu/cert.pem"
KEY_FILE = "/home/biu/key.pem"
SETTINGS_FILE = "/home/biu/settings.json"

# WiFi settings
WIFI_TIMEOUT = 60
WIFI_CHECK_INTERVAL = 5

# Display settings
DISPLAY_I2C_PORT = 1
DISPLAY_I2C_ADDRESS = 0x3C
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64

# Web server
WEB_SERVER_PORT = 443

# Wake alarm
WAKE_DURATION = 10  # seconds
WAKE_CHECK_INTERVAL = 1  # seconds

# Weather API (using Open-Meteo free API - no key needed)
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_UPDATE_INTERVAL = 600  # Update every 10 minutes
WEATHER_TIMEOUT = 5

# Location (default: can be overridden)
DEFAULT_LATITUDE = 40.7128
DEFAULT_LONGITUDE = -74.0060

# Display cycle mode (disabled when using rotary encoder)
DISPLAY_CYCLE_INTERVAL = 3  # seconds per screen (legacy, disabled with rotary)

# Rotary Encoder GPIO Pins
ROTARY_ENCODER_PIN_PUSH = 25    # Push button
ROTARY_ENCODER_PIN_A = 26      # CLK
ROTARY_ENCODER_PIN_B = 16      # DT

# Display rendering
RENDER_INTERVAL = 0.1  # Refresh display every N seconds (faster for smooth animations)
TEXT_CHAR_WIDTH = 6  # pixels per character (for centered text)

# Tab display labels
TAB_LABELS = {
    "home": "●",
    "system": "⚙",
    "weather": "☁",
    "network": "📶",
    "power": "🔋",
    "timer": "⏱"
}

# Settings menu
BRIGHTNESS_MIN = 1
BRIGHTNESS_MAX = 10
CONTRAST_MIN = 10
CONTRAST_MAX = 100

# UI Colors & Symbols
WIFI_ICON_WEAK = "▁"
WIFI_ICON_MEDIUM = "▂"
WIFI_ICON_STRONG = "▃"
WIFI_ICON_EXCELLENT = "▄"

BATTERY_ICON_EMPTY = "🪫"
BATTERY_ICON_LOW = "🔋"
BATTERY_ICON_FULL = "🔋"

TEMP_HOT = "●"
TEMP_WARM = "◐"
TEMP_COOL = "◑"
TEMP_COLD = "○"
