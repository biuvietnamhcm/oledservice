"""Wake up timer functionality"""

import json
import time
from datetime import datetime
from config import WAKE_FILE, WAKE_DURATION


class WakeTimer:
    def __init__(self):
        self.wake_time = None
        self.is_active = False
        self.end_time = 0
        self.load()
    
    def load(self):
        """Load wake time from file"""
        try:
            with open(WAKE_FILE) as f:
                data = json.load(f)
                time_str = data.get("time", "")
                self.wake_time = datetime.strptime(time_str, "%H:%M")
        except Exception as e:
            print(f"Error loading wake time: {e}")
            self.wake_time = None
    
    def save(self, time_str):
        """Save wake time to file"""
        try:
            with open(WAKE_FILE, "w") as f:
                json.dump({"time": time_str}, f)
            self.load()
        except Exception as e:
            print(f"Error saving wake time: {e}")
    
    def get_wake_time_str(self):
        """Get wake time as formatted string"""
        if self.wake_time:
            return self.wake_time.strftime("%H:%M")
        return ""
    
    def check_alarm(self, current_time):
        """Check if alarm should trigger"""
        if self.wake_time and not self.is_active:
            current_str = current_time.strftime("%H:%M")
            wake_str = self.wake_time.strftime("%H:%M")
            
            if current_str == wake_str:
                self.activate()
    
    def activate(self):
        """Activate the alarm"""
        self.is_active = True
        self.end_time = time.time() + WAKE_DURATION
    
    def update(self):
        """Update alarm state"""
        if self.is_active:
            remaining = int(self.end_time - time.time())
            if remaining <= 0:
                self.is_active = False
            return remaining
        return None
    
    def get_remaining_time(self):
        """Get remaining time for active alarm"""
        if self.is_active:
            remaining = int(self.end_time - time.time())
            return max(0, remaining)
        return None
