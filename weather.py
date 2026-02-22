"""Weather data fetching and caching"""

import requests
from datetime import datetime
from config import (
    WEATHER_API_URL,
    WEATHER_UPDATE_INTERVAL,
    WEATHER_TIMEOUT
)
from functools import lru_cache


class WeatherManager:
    def __init__(self):
        location = self._get_location_from_ip()

        if location:
            self.latitude = location["lat"]
            self.longitude = location["lon"]
            self.city = location["city"]
        else:
            self.latitude = 0
            self.longitude = 0
            self.city = "Unknown"

        # Improve city accuracy using reverse geocoding
        self.city = self._resolve_city_from_coords()

        self.last_update = None
        self.weather_data = {
            "city": self.city,
            "temp": "N/A",
            "condition": "N/A",
            "humidity": "N/A",
            "wind_speed": "N/A",
            "updated": False
        }

    # ---------------- LOCATION ----------------

    @lru_cache(maxsize=1)
    def _get_location_from_ip(self):
        """Get real latitude/longitude from public IP"""
        try:
            response = requests.get(
                "https://ipapi.co/json/",
                timeout=5
            )
            response.raise_for_status()
            data = response.json()

            return {
                "lat": data.get("latitude"),
                "lon": data.get("longitude"),
                "city": data.get("city", "Unknown")
            }
        except Exception as e:
            print(f"IP location error: {e}")
            return None

    @lru_cache(maxsize=1)
    def _resolve_city_from_coords(self):
        """Resolve city name from latitude/longitude"""
        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={
                    "lat": self.latitude,
                    "lon": self.longitude,
                    "format": "json"
                },
                headers={"User-Agent": "oled-weather"},
                timeout=5
            )
            response.raise_for_status()
            address = response.json().get("address", {})
            return (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or self.city
            )
        except Exception as e:
            print(f"City resolve error: {e}")
            return self.city

    # ---------------- WEATHER ----------------

    def fetch_weather(self):
        """Fetch weather data from Open-Meteo API"""
        try:
            params = {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "timezone": "auto"
            }

            response = requests.get(
                WEATHER_API_URL,
                params=params,
                timeout=WEATHER_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()
            current = data.get("current", {})

            weather_code = current.get("weather_code", 0)
            condition = self._get_weather_condition(weather_code)

            self.weather_data = {
                "city": self.city,
                "temp": round(current.get("temperature_2m", 0)),
                "condition": condition,
                "humidity": current.get("relative_humidity_2m", 0),
                "wind_speed": round(current.get("wind_speed_10m", 0), 1),
                "updated": True
            }

            self.last_update = datetime.now()
            return self.weather_data

        except Exception as e:
            print(f"Weather fetch error: {e}")
            self.weather_data["updated"] = False
            return None

    # ---------------- UTILS ----------------

    def _get_weather_condition(self, code):
        """Convert WMO weather code to description"""
        weather_codes = {
            0: "Clear",
            1: "Mostly Clear",
            2: "Partly Cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Foggy",
            51: "Drizzle",
            53: "Drizzle",
            55: "Drizzle",
            61: "Rain",
            63: "Rain",
            65: "Rain",
            71: "Snow",
            73: "Snow",
            75: "Snow",
            77: "Snow",
            80: "Showers",
            81: "Showers",
            82: "Showers",
            85: "Snow Showers",
            86: "Snow Showers",
            95: "Thunderstorm",
            96: "Thunderstorm",
            99: "Thunderstorm"
        }
        return weather_codes.get(code, "Unknown")

    def should_update(self):
        """Check if weather data should be updated"""
        if self.last_update is None:
            return True

        elapsed = (datetime.now() - self.last_update).total_seconds()
        return elapsed >= WEATHER_UPDATE_INTERVAL

    def get_display_string(self):
        """Get formatted weather string for display"""
        if not self.weather_data["updated"]:
            return "Weather: No Data"

        return (
            f"{self.weather_data['city']} "
            f"{self.weather_data['temp']}C "
            f"{self.weather_data['condition']} "
            f"{self.weather_data['humidity']}%"
        )
