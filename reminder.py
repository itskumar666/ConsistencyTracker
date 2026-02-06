#!/usr/bin/env python3
"""
🔔 Reminder daemon for Consistency Tracker
Run this in the background: python3 reminder.py &
"""

import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "streak_data.json"

def send_notification(title, message, sound="default"):
    """Send Mac notification."""
    script = f'display notification "{message}" with title "{title}" sound name "{sound}"'
    subprocess.run(["osascript", "-e", script], capture_output=True)

def load_data():
    """Load streak data."""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"activities": {}}

def get_today():
    """Get today's date string."""
    return datetime.now().strftime("%Y-%m-%d")

def check_if_checked_in():
    """Check if user has checked in today for any activity."""
    data = load_data()
    today = get_today()
    
    for name, info in data.get("activities", {}).items():
        if today in info.get("dates", []):
            return True, name
    return False, None

def main():
    """Main reminder loop."""
    print("🔔 Consistency Tracker Reminder running...")
    print("   Press Ctrl+C to stop\n")
    
    # Track which reminders we've sent today
    sent_today = {"morning": False, "afternoon": False, "evening": False, "date": get_today()}
    
    while True:
        try:
            now = datetime.now()
            today = get_today()
            
            # Reset sent flags if it's a new day
            if sent_today["date"] != today:
                sent_today = {"morning": False, "afternoon": False, "evening": False, "date": today}
            
            checked_in, activity = check_if_checked_in()
            hour = now.hour
            
            # Morning reminder (9 AM)
            if hour == 9 and not sent_today["morning"]:
                if not checked_in:
                    send_notification(
                        "☀️ Good Morning!",
                        "Ready to build your streak today? Open Consistency Tracker!"
                    )
                    print(f"[{now.strftime('%H:%M')}] Sent morning reminder")
                sent_today["morning"] = True
            
            # Afternoon reminder (2 PM)
            elif hour == 14 and not sent_today["afternoon"]:
                if not checked_in:
                    send_notification(
                        "📝 Afternoon Check-in",
                        "Don't forget to log your progress today!"
                    )
                    print(f"[{now.strftime('%H:%M')}] Sent afternoon reminder")
                sent_today["afternoon"] = True
            
            # Evening warning (8 PM)
            elif hour == 20 and not sent_today["evening"]:
                if not checked_in:
                    send_notification(
                        "⚠️ Streak at Risk!",
                        "You haven't checked in today. Your streak might break at midnight!"
                    )
                    print(f"[{now.strftime('%H:%M')}] Sent evening warning")
                sent_today["evening"] = True
            
            # Check every minute
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n\n🔔 Reminder stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
