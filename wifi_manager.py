"""WiFi and network management"""

import subprocess
import time
from config import WIFI_TIMEOUT, WIFI_CHECK_INTERVAL


class WiFiManager:
    def __init__(self):
        self.ap_started = False
        self.start_time = time.time()
        self.connected = False
    
    def get_ip(self):
        """Get the current IP address"""
        try:
            result = subprocess.check_output(
                "hostname -I | awk '{print $1}'",
                shell=True
            ).decode().strip()
            return result if result else None
        except Exception as e:
            print(f"Error getting IP: {e}")
            return None
    
    def is_connected(self):
        """Check if WiFi is connected"""
        ip = self.get_ip()
        self.connected = bool(ip)
        return self.connected
    
    def get_ip_status(self):
        """Get IP or AP mode status"""
        ip = self.get_ip()
        return ip or "AP MODE"
    
    def start_ap(self):
        """Start Access Point mode"""
        if self.ap_started:
            return
        
        try:
            print("Starting AP mode...")
            subprocess.call("sudo systemctl stop wpa_supplicant", shell=True)
            subprocess.call("sudo systemctl stop dhcpcd", shell=True)
            subprocess.call("sudo systemctl start hostapd", shell=True)
            subprocess.call("sudo systemctl start dnsmasq", shell=True)
            self.ap_started = True
            print("AP mode started")
        except Exception as e:
            print(f"Error starting AP mode: {e}")
    
    def should_start_ap(self):
        """Determine if AP mode should be started"""
        if not self.is_connected():
            elapsed = time.time() - self.start_time
            return elapsed > WIFI_TIMEOUT
        return False
    
    def check_connection(self):
        """Check WiFi connection and start AP if needed"""
        if self.should_start_ap():
            self.start_ap()
        return self.is_connected()
    
    def get_signal_strength(self):
        """Get WiFi signal strength in dBm (-30 to -90, higher is better)"""
        try:
            result = subprocess.check_output(
                "iwconfig wlan0 2>/dev/null | grep 'Signal level' | awk -F'=' '{print $3}' | awk '{print $1}'",
                shell=True
            ).decode().strip()
            if result:
                try:
                    return int(result)
                except:
                    return None
            return None
        except:
            return None
    
    def get_wifi_name(self):
        """Get connected WiFi network name (SSID)"""
        try:
            result = subprocess.check_output(
                "iwconfig wlan0 2>/dev/null | grep 'ESSID' | awk -F'\"' '{print $2}'",
                shell=True
            ).decode().strip()
            return result if result else "N/A"
        except:
            return "N/A"
    
    def signal_to_icon(self, dbm):
        """Convert dBm to signal strength icon"""
        if dbm is None:
            return "???"
        # dBm scale: -30 to -90 (higher is better)
        # -30 to -50: Excellent, -50 to -60: Good, -60 to -70: Fair, -70 to -80: Weak, -80+: Very Weak
        if dbm >= -50:
            return "▓▓▓▓▓"  # 5 bars
        elif dbm >= -60:
            return "▓▓▓▓░"  # 4 bars
        elif dbm >= -70:
            return "▓▓▓░░"  # 3 bars
        elif dbm >= -80:
            return "▓▓░░░"  # 2 bars
        else:
            return "▓░░░░"  # 1 bar
