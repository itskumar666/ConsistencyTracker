#!/usr/bin/env python3
"""
🔥 Consistency Tracker - Mac Menu Bar App
A beautiful menu bar app to track daily habits and maintain streaks!
"""

import subprocess
import sys

# Check and install rumps if needed
try:
    import rumps
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rumps", "-q"])
    import rumps

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Data file in user's home directory
DATA_DIR = Path.home() / ".consistency_tracker"
DATA_FILE = DATA_DIR / "data.json"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Preset activities
PRESETS = [
    ("💻 Coding", "code"),
    ("📚 Study", "study"),  
    ("📖 Reading", "reading"),
    ("🏃 Exercise", "exercise"),
    ("✍️ Writing", "writing"),
    ("🧘 Meditation", "meditation"),
    ("🎸 Music Practice", "music"),
    ("🎨 Drawing", "drawing"),
    ("🌍 Language Learning", "language"),
    ("🔧 Side Project", "project"),
]

BADGES = {
    1: ("⭐", "First Step"),
    7: ("🔥", "Week Warrior"),
    14: ("💪", "Fortnight Fighter"),
    30: ("🏆", "Month Master"),
    50: ("🌟", "Fifty & Fabulous"),
    100: ("💎", "Century Club"),
    365: ("👑", "Year Legend"),
}


class ConsistencyTracker(rumps.App):
    def __init__(self):
        super().__init__("🔥 0", quit_button=None)
        self.data = self.load_data()
        self.update_menu()
        
        # Schedule reminder checks
        self.reminder_timer = rumps.Timer(self.check_reminders, 60)
        self.reminder_timer.start()
        
        # Track sent reminders
        self.sent_reminders = {"morning": False, "afternoon": False, "evening": False, "date": self.get_today()}
    
    def load_data(self):
        """Load data from JSON file."""
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {"activities": {}, "badges": [], "settings": {"morning": 9, "afternoon": 14, "evening": 20}}
    
    def save_data(self):
        """Save data to JSON file."""
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_today(self):
        """Get today's date as string."""
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_streak(self, dates):
        """Calculate current streak from list of dates."""
        if not dates:
            return 0
        
        dates = sorted(set(dates), reverse=True)
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        last_date = datetime.strptime(dates[0], "%Y-%m-%d").date()
        if last_date != today and last_date != yesterday:
            return 0
        
        streak = 0
        expected = last_date
        
        for date_str in dates:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if date == expected:
                streak += 1
                expected = date - timedelta(days=1)
            elif date < expected:
                break
        
        return streak
    
    def update_title(self):
        """Update menu bar title with max streak."""
        max_streak = 0
        for info in self.data.get("activities", {}).values():
            streak = self.get_streak(info.get("dates", []))
            max_streak = max(max_streak, streak)
        
        fire = "🔥" if max_streak > 0 else "○"
        self.title = f"{fire} {max_streak}"
    
    def update_menu(self):
        """Rebuild the menu."""
        self.menu.clear()
        
        # Header
        today = datetime.now().strftime("%A, %B %d")
        self.menu.add(rumps.MenuItem(f"📅 {today}", callback=None))
        self.menu.add(rumps.separator)
        
        # Activities section
        activities = self.data.get("activities", {})
        
        if not activities:
            self.menu.add(rumps.MenuItem("No activities yet!", callback=None))
        else:
            for name, info in activities.items():
                dates = info.get("dates", [])
                streak = self.get_streak(dates)
                checked_today = self.get_today() in dates
                longest = info.get("longest", 0)
                
                # Status emoji
                if checked_today:
                    status = "✅"
                elif streak > 0:
                    status = "⚠️"
                else:
                    status = "⬜"
                
                # Activity item
                title = f"{status} {name}  —  🔥 {streak} days"
                item = rumps.MenuItem(title)
                
                # Submenu for activity
                if not checked_today:
                    check_in = rumps.MenuItem("✓ Check In", callback=lambda sender, n=name: self.check_in(n))
                    item.add(check_in)
                else:
                    item.add(rumps.MenuItem("✓ Done for today!", callback=None))
                
                item.add(rumps.separator)
                item.add(rumps.MenuItem(f"Current: {streak} days", callback=None))
                item.add(rumps.MenuItem(f"Longest: {longest} days", callback=None))
                item.add(rumps.MenuItem(f"Total: {len(dates)} days", callback=None))
                item.add(rumps.separator)
                
                delete = rumps.MenuItem("🗑 Delete Activity", callback=lambda sender, n=name: self.delete_activity(n))
                item.add(delete)
                
                self.menu.add(item)
        
        self.menu.add(rumps.separator)
        
        # Quick check-in buttons for unchecked activities
        unchecked = [(n, i) for n, i in activities.items() if self.get_today() not in i.get("dates", [])]
        if unchecked:
            quick_menu = rumps.MenuItem("⚡ Quick Check-in")
            for name, _ in unchecked:
                quick_menu.add(rumps.MenuItem(name, callback=lambda sender, n=name: self.check_in(n)))
            self.menu.add(quick_menu)
            self.menu.add(rumps.separator)
        
        # Add activity
        add_menu = rumps.MenuItem("➕ Add Activity")
        
        # Presets submenu
        presets_menu = rumps.MenuItem("📋 Presets")
        for display_name, key in PRESETS:
            exists = display_name in activities
            title = f"{display_name} {'✓' if exists else ''}"
            presets_menu.add(rumps.MenuItem(title, callback=None if exists else lambda sender, n=display_name: self.add_preset(n)))
        add_menu.add(presets_menu)
        
        add_menu.add(rumps.separator)
        add_menu.add(rumps.MenuItem("✨ Custom Activity...", callback=self.add_custom_activity))
        
        self.menu.add(add_menu)
        
        # Stats
        self.menu.add(rumps.MenuItem("📊 Statistics", callback=self.show_stats))
        
        # Badges
        badges = self.data.get("badges", [])
        badges_title = f"🏆 Badges ({len(badges)})"
        self.menu.add(rumps.MenuItem(badges_title, callback=self.show_badges))
        
        self.menu.add(rumps.separator)
        
        # Settings submenu
        settings_menu = rumps.MenuItem("⚙️ Settings")
        settings_menu.add(rumps.MenuItem("🔔 Send Test Notification", callback=self.test_notification))
        settings_menu.add(rumps.separator)
        settings_menu.add(rumps.MenuItem("🚀 Open at Login", callback=self.setup_login_item))
        settings_menu.add(rumps.MenuItem("📁 Open Data Folder", callback=self.open_data_folder))
        self.menu.add(settings_menu)
        
        # About
        self.menu.add(rumps.MenuItem("ℹ️ About", callback=self.show_about))
        
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("Quit", callback=rumps.quit_application))
        
        self.update_title()
    
    def check_in(self, activity_name):
        """Check in for an activity."""
        today = self.get_today()
        
        if activity_name not in self.data["activities"]:
            return
        
        if today in self.data["activities"][activity_name].get("dates", []):
            return
        
        self.data["activities"][activity_name].setdefault("dates", []).append(today)
        
        # Update longest streak
        streak = self.get_streak(self.data["activities"][activity_name]["dates"])
        if streak > self.data["activities"][activity_name].get("longest", 0):
            self.data["activities"][activity_name]["longest"] = streak
        
        self.save_data()
        
        # Check for badges
        self.check_badges(activity_name, streak)
        
        # Notification
        rumps.notification(
            title="✅ Checked In!",
            subtitle=activity_name,
            message=f"🔥 {streak} day streak!",
            sound=True
        )
        
        self.update_menu()
    
    def check_badges(self, activity_name, streak):
        """Check and award badges."""
        if streak in BADGES:
            badge_key = f"{activity_name}_{streak}"
            if badge_key not in self.data.get("badges", []):
                self.data.setdefault("badges", []).append(badge_key)
                self.save_data()
                
                icon, name = BADGES[streak]
                rumps.notification(
                    title="🏆 Badge Earned!",
                    subtitle=f"{icon} {name}",
                    message=f"{streak} day streak for {activity_name}!",
                    sound=True
                )
    
    def add_preset(self, name):
        """Add a preset activity."""
        if name not in self.data.get("activities", {}):
            self.data.setdefault("activities", {})[name] = {"dates": [], "longest": 0}
            self.save_data()
            self.update_menu()
            
            rumps.notification(
                title="✨ Activity Added!",
                subtitle=name,
                message="Start building your streak!",
                sound=True
            )
    
    def add_custom_activity(self, sender):
        """Add a custom activity."""
        response = rumps.Window(
            title="Add Custom Activity",
            message="Enter a name for your new activity:",
            default_text="",
            ok="Add",
            cancel="Cancel",
            dimensions=(300, 24)
        ).run()
        
        if response.clicked and response.text.strip():
            name = response.text.strip()
            if name not in self.data.get("activities", {}):
                self.data.setdefault("activities", {})[name] = {"dates": [], "longest": 0}
                self.save_data()
                self.update_menu()
                
                rumps.notification(
                    title="✨ Activity Added!",
                    subtitle=name,
                    message="Start building your streak!",
                    sound=True
                )
    
    def delete_activity(self, name):
        """Delete an activity."""
        response = rumps.alert(
            title="Delete Activity?",
            message=f"Are you sure you want to delete '{name}'?\n\nThis will delete all streak data and cannot be undone.",
            ok="Delete",
            cancel="Cancel"
        )
        
        if response == 1:
            if name in self.data.get("activities", {}):
                del self.data["activities"][name]
                self.save_data()
                self.update_menu()
    
    def show_stats(self, sender):
        """Show statistics."""
        activities = self.data.get("activities", {})
        
        if not activities:
            rumps.alert("No Statistics", "Add some activities and start tracking!")
            return
        
        total_days = sum(len(a.get("dates", [])) for a in activities.values())
        total_activities = len(activities)
        best_streak = max((a.get("longest", 0) for a in activities.values()), default=0)
        current_streaks = sum(1 for a in activities.values() if self.get_streak(a.get("dates", [])) > 0)
        badges = len(self.data.get("badges", []))
        
        stats = f"""📊 Your Consistency Stats

📅 Total Days Logged: {total_days}
📋 Activities Tracked: {total_activities}
🔥 Active Streaks: {current_streaks}
🏆 Best Streak Ever: {best_streak} days
⭐ Badges Earned: {badges}

Keep going! 💪"""
        
        rumps.alert("Statistics", stats)
    
    def show_badges(self, sender):
        """Show badges."""
        earned = self.data.get("badges", [])
        
        if not earned:
            message = "No badges yet!\n\nKeep building your streaks to earn badges:\n\n"
            for days, (icon, name) in BADGES.items():
                message += f"{icon} {name}: {days} day streak\n"
            rumps.alert("Badges", message)
            return
        
        message = f"🏆 Badges Earned ({len(earned)}):\n\n"
        for badge_key in earned:
            parts = badge_key.rsplit("_", 1)
            if len(parts) == 2:
                activity, days = parts
                days = int(days)
                if days in BADGES:
                    icon, name = BADGES[days]
                    message += f"{icon} {name} - {activity}\n"
        
        rumps.alert("Your Badges", message)
    
    def test_notification(self, sender):
        """Send a test notification."""
        rumps.notification(
            title="🔔 Test Notification",
            subtitle="Consistency Tracker",
            message="Notifications are working! You'll receive daily reminders.",
            sound=True
        )
    
    def setup_login_item(self, sender):
        """Show instructions for opening at login."""
        rumps.alert(
            title="Open at Login",
            message="""To have Consistency Tracker start automatically:

1. Open System Settings
2. Go to General → Login Items
3. Click '+' under 'Open at Login'
4. Navigate to Applications
5. Select 'Consistency Tracker'

The app will now start when you log in!"""
        )
    
    def open_data_folder(self, sender):
        """Open the data folder in Finder."""
        subprocess.run(["open", str(DATA_DIR)])
    
    def show_about(self, sender):
        """Show about dialog."""
        rumps.alert(
            title="🔥 Consistency Tracker",
            message="""Version 1.0.0

Track your daily habits and maintain streaks!

Features:
• Track multiple activities
• Streak tracking with fire 🔥
• Badge rewards system
• Daily reminder notifications

Keep building those streaks! 💪"""
        )
    
    def check_reminders(self, sender):
        """Check if we need to send reminders."""
        now = datetime.now()
        today = self.get_today()
        
        # Reset for new day
        if self.sent_reminders["date"] != today:
            self.sent_reminders = {"morning": False, "afternoon": False, "evening": False, "date": today}
        
        # Check if already checked in today
        checked_in = any(
            today in info.get("dates", [])
            for info in self.data.get("activities", {}).values()
        )
        
        if checked_in:
            return
        
        # Only send reminders if there are activities
        if not self.data.get("activities"):
            return
        
        hour = now.hour
        settings = self.data.get("settings", {})
        
        # Morning reminder
        if hour == settings.get("morning", 9) and not self.sent_reminders["morning"]:
            rumps.notification(
                title="☀️ Good Morning!",
                subtitle="Consistency Tracker",
                message="Ready to build your streak today?",
                sound=True
            )
            self.sent_reminders["morning"] = True
        
        # Afternoon reminder
        elif hour == settings.get("afternoon", 14) and not self.sent_reminders["afternoon"]:
            rumps.notification(
                title="📝 Afternoon Check-in",
                subtitle="Consistency Tracker",
                message="Don't forget to log your progress!",
                sound=True
            )
            self.sent_reminders["afternoon"] = True
        
        # Evening warning
        elif hour == settings.get("evening", 20) and not self.sent_reminders["evening"]:
            rumps.notification(
                title="⚠️ Streak at Risk!",
                subtitle="Consistency Tracker",
                message="You haven't checked in today!",
                sound=True
            )
            self.sent_reminders["evening"] = True


if __name__ == "__main__":
    app = ConsistencyTracker()
    app.run()
