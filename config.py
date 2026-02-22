"""Configuration and constants"""

# File paths
WAKE_FILE = "/home/biu/wakeup.json"
CERT_FILE = "/home/biu/cert.pem"
KEY_FILE = "/home/biu/key.pem"

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

# Display cycle mode
DISPLAY_CYCLE_INTERVAL = 3  # seconds per screen
