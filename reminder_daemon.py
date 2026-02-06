#!/usr/bin/env python3
"""
🔔 Consistency Tracker Reminder Daemon
Runs in the background and sends reminder notifications.
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

DATA_FILE = Path.home() / ".consistency_tracker_data.json"

def send_notification(title, message):
    """Send a Mac notification."""
    try:
        script = f'''
        display notification "{message}" with title "{title}" sound name "default"
        '''
        subprocess.run(['osascript', '-e', script], capture_output=True)
    except:
        pass


def load_data():
    """Load tracker data."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return None


def get_today():
    """Get today's date as string."""
    return datetime.now().strftime("%Y-%m-%d")


def check_pending_activities():
    """Check if any activities haven't been checked in today."""
    data = load_data()
    if not data or not data.get("activities"):
        return []
    
    today = get_today()
    pending = []
    
    for activity in data["activities"]:
        if today not in activity.get("checked_in_dates", []):
            pending.append(activity)
    
    return pending


def get_total_streak(data):
    """Get the maximum current streak."""
    if not data or not data.get("activities"):
        return 0
    return max((a["current_streak"] for a in data["activities"]), default=0)


def main():
    """Main reminder loop."""
    print("🔔 Consistency Tracker Reminder is running...")
    print("   Reminders will be sent at: 9:00 AM, 2:00 PM, 8:00 PM")
    print("   Press Ctrl+C to stop.\n")
    
    reminded_today = {
        "morning": False,
        "afternoon": False,
        "evening": False
    }
    
    last_date = get_today()
    
    while True:
        try:
            current_time = datetime.now()
            current_date = get_today()
            hour = current_time.hour
            
            # Reset reminders at midnight
            if current_date != last_date:
                reminded_today = {"morning": False, "afternoon": False, "evening": False}
                last_date = current_date
            
            pending = check_pending_activities()
            pending_count = len(pending)
            
            # Morning reminder (9 AM)
            if hour == 9 and not reminded_today["morning"]:
                if pending_count > 0:
                    send_notification(
                        "Good Morning! ☀️",
                        f"You have {pending_count} activities to check in today!"
                    )
                else:
                    send_notification(
                        "Good Morning! ☀️", 
                        "All activities checked! Keep the momentum going! 🔥"
                    )
                reminded_today["morning"] = True
                print(f"[{current_time.strftime('%H:%M')}] Morning reminder sent")
            
            # Afternoon reminder (2 PM)
            if hour == 14 and not reminded_today["afternoon"]:
                if pending_count > 0:
                    names = ", ".join([a["name"] for a in pending[:3]])
                    send_notification(
                        "Afternoon Check-in 📝",
                        f"Still pending: {names}"
                    )
                    reminded_today["afternoon"] = True
                    print(f"[{current_time.strftime('%H:%M')}] Afternoon reminder sent")
            
            # Evening warning (8 PM)
            if hour == 20 and not reminded_today["evening"]:
                if pending_count > 0:
                    data = load_data()
                    streak = get_total_streak(data)
                    send_notification(
                        "⚠️ Streak at Risk!",
                        f"{pending_count} activities pending! Don't lose your {streak}-day streak!"
                    )
                    reminded_today["evening"] = True
                    print(f"[{current_time.strftime('%H:%M')}] Evening warning sent")
            
            # Sleep for 5 minutes
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\n\n👋 Reminder service stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
