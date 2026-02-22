"""System monitoring utilities"""

import subprocess
import psutil
import json
from datetime import datetime


def get_cpu_temperature():
    """Get CPU temperature in Celsius"""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_raw = int(f.read().strip())
            return round(temp_raw / 1000.0, 1)  # Convert millidegrees to degrees
    except Exception as e:
        print(f"Error reading CPU temp: {e}")
        return None


def get_cpu_usage():
    """Get CPU usage percentage"""
    try:
        return round(psutil.cpu_percent(interval=0.5), 1)
    except Exception as e:
        print(f"Error reading CPU usage: {e}")
        return None


def get_memory_usage():
    """Get memory usage percentage"""
    try:
        return round(psutil.virtual_memory().percent, 1)
    except Exception as e:
        print(f"Error reading memory usage: {e}")
        return None


def get_disk_usage():
    """Get disk usage percentage"""
    try:
        return round(psutil.disk_usage("/").percent, 1)
    except Exception as e:
        print(f"Error reading disk usage: {e}")
        return None


def get_uptime():
    """Get system uptime as formatted string"""
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = int(float(f.read().split()[0]))
            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    except Exception as e:
        print(f"Error reading uptime: {e}")
        return "Unknown"


def get_uptime_hours():
    """Get system uptime in hours as float"""
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.read().split()[0])
            return uptime_seconds / 3600.0
    except Exception as e:
        print(f"Error reading uptime: {e}")
        return 0.0


def get_disk_free_percent():
    """Get free disk space percentage"""
    try:
        total, used, free = psutil.disk_usage("/")
        return round((free / total) * 100, 1)
    except Exception as e:
        print(f"Error reading disk free: {e}")
        return 0


def get_system_stats():
    """Get all system statistics"""
    return {
        "cpu_temp": get_cpu_temperature(),
        "cpu_usage": get_cpu_usage(),
        "memory_usage": get_memory_usage(),
        "disk_usage": get_disk_usage(),
        "disk_free": get_disk_free_percent(),
        "uptime": get_uptime(),
        "uptime_hours": get_uptime_hours(),
        "timestamp": datetime.now().isoformat()
    }


def get_network_stats():
    """Get network statistics"""
    try:
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
    except Exception as e:
        print(f"Error reading network stats: {e}")
        return None
