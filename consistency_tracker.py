#!/usr/bin/env python3
"""
🔥 Consistency Tracker - Track your daily habits and maintain streaks!
A terminal-based app with Mac notifications.
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Data file location
DATA_FILE = Path.home() / ".consistency_tracker_data.json"

# Color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ORANGE = '\033[38;5;208m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Badge definitions
BADGES = {
    "first_day": {"name": "🌟 First Step", "description": "Complete your first day", "streak": 1},
    "week_warrior": {"name": "⚔️ Week Warrior", "description": "7 day streak", "streak": 7},
    "two_weeks": {"name": "🏃 Fortnight Fighter", "description": "14 day streak", "streak": 14},
    "month_master": {"name": "🎯 Month Master", "description": "30 day streak", "streak": 30},
    "fifty_days": {"name": "💪 Fifty & Fabulous", "description": "50 day streak", "streak": 50},
    "hundred_days": {"name": "💯 Century Club", "description": "100 day streak", "streak": 100},
    "year_legend": {"name": "👑 Year Legend", "description": "365 day streak", "streak": 365},
}

# Preset activities
PRESETS = [
    {"name": "Coding", "icon": "💻"},
    {"name": "Study", "icon": "📚"},
    {"name": "Reading", "icon": "📖"},
    {"name": "Exercise", "icon": "🏋️"},
    {"name": "Writing", "icon": "✍️"},
    {"name": "Meditation", "icon": "🧘"},
    {"name": "Language Learning", "icon": "🗣️"},
    {"name": "Music Practice", "icon": "🎵"},
    {"name": "Drawing", "icon": "🎨"},
    {"name": "Side Project", "icon": "🔧"},
]


def load_data():
    """Load data from file or return empty structure."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "activities": [],
        "badges": [],
        "freeze_tokens": 2
    }


def save_data(data):
    """Save data to file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def send_notification(title, message):
    """Send a Mac notification."""
    try:
        script = f'''
        display notification "{message}" with title "{title}" sound name "default"
        '''
        subprocess.run(['osascript', '-e', script], capture_output=True)
    except:
        pass  # Silently fail if notification doesn't work


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')


def print_header():
    """Print the app header."""
    print(f"""
{Colors.ORANGE}{Colors.BOLD}
   ██████╗ ██████╗ ███╗   ██╗███████╗██╗███████╗████████╗███████╗███╗   ██╗ ██████╗██╗   ██╗
  ██╔════╝██╔═══██╗████╗  ██║██╔════╝██║██╔════╝╚══██╔══╝██╔════╝████╗  ██║██╔════╝╚██╗ ██╔╝
  ██║     ██║   ██║██╔██╗ ██║███████╗██║███████╗   ██║   █████╗  ██╔██╗ ██║██║      ╚████╔╝ 
  ██║     ██║   ██║██║╚██╗██║╚════██║██║╚════██║   ██║   ██╔══╝  ██║╚██╗██║██║       ╚██╔╝  
  ╚██████╗╚██████╔╝██║ ╚████║███████║██║███████║   ██║   ███████╗██║ ╚████║╚██████╗   ██║   
   ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═══╝ ╚═════╝   ╚═╝   
{Colors.END}
    {Colors.CYAN}🔥 Track your habits. Build consistency. Achieve your goals.{Colors.END}
""")


def get_today():
    """Get today's date as string."""
    return datetime.now().strftime("%Y-%m-%d")


def get_streak_status(activity):
    """Get the current streak status of an activity."""
    if not activity.get("checked_in_dates"):
        return "no_streak", 0
    
    dates = sorted(activity["checked_in_dates"], reverse=True)
    today = get_today()
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    if dates[0] == today:
        return "checked_in_today", activity["current_streak"]
    elif dates[0] == yesterday:
        return "at_risk", activity["current_streak"]
    else:
        return "broken", 0


def check_and_award_badges(data, activity):
    """Check if any new badges should be awarded."""
    streak = activity["current_streak"]
    new_badges = []
    
    for badge_id, badge_info in BADGES.items():
        if streak >= badge_info["streak"]:
            badge_key = f"{badge_id}_{activity['name']}"
            if badge_key not in data["badges"]:
                data["badges"].append(badge_key)
                new_badges.append(badge_info["name"])
    
    return new_badges


def display_activities(data):
    """Display all activities with their streaks."""
    activities = data["activities"]
    
    if not activities:
        print(f"\n  {Colors.YELLOW}No activities yet! Add one to get started.{Colors.END}\n")
        return
    
    print(f"\n  {Colors.BOLD}📋 YOUR ACTIVITIES{Colors.END}")
    print("  " + "─" * 60)
    
    for i, activity in enumerate(activities, 1):
        status, streak = get_streak_status(activity)
        
        # Status indicator
        if status == "checked_in_today":
            status_icon = f"{Colors.GREEN}✅ Done!{Colors.END}"
            streak_color = Colors.GREEN
        elif status == "at_risk":
            status_icon = f"{Colors.YELLOW}⚠️ Check in!{Colors.END}"
            streak_color = Colors.YELLOW
        elif status == "broken":
            status_icon = f"{Colors.RED}💔 Broken{Colors.END}"
            streak_color = Colors.RED
        else:
            status_icon = f"{Colors.BLUE}🆕 Start!{Colors.END}"
            streak_color = Colors.BLUE
        
        icon = activity.get("icon", "📌")
        name = activity["name"]
        current = activity["current_streak"]
        longest = activity["longest_streak"]
        total = activity["total_days"]
        
        print(f"""
  {Colors.BOLD}[{i}]{Colors.END} {icon} {Colors.BOLD}{name}{Colors.END}
      {streak_color}🔥 {current} day streak{Colors.END} | 🏆 Best: {longest} | 📅 Total: {total} days
      Status: {status_icon}""")
    
    print("\n  " + "─" * 60)


def display_stats(data):
    """Display overall statistics."""
    activities = data["activities"]
    total_days = sum(a["total_days"] for a in activities)
    max_streak = max((a["current_streak"] for a in activities), default=0)
    badge_count = len(set(b.split('_')[0] + '_' + b.split('_')[1] for b in data["badges"])) if data["badges"] else 0
    
    print(f"""
  {Colors.BOLD}📊 QUICK STATS{Colors.END}
  ┌────────────────┬────────────────┬────────────────┐
  │ 🔥 Top Streak  │ 📅 Total Days  │ 🏆 Badges      │
  │    {Colors.ORANGE}{max_streak:^10}{Colors.END}  │    {Colors.CYAN}{total_days:^10}{Colors.END}  │    {Colors.YELLOW}{badge_count:^10}{Colors.END}  │
  └────────────────┴────────────────┴────────────────┘
  ❄️ Freeze Tokens: {data['freeze_tokens']}
""")


def add_activity(data):
    """Add a new activity."""
    clear_screen()
    print(f"\n  {Colors.BOLD}➕ ADD ACTIVITY{Colors.END}\n")
    
    print("  Quick Add (type number):")
    for i, preset in enumerate(PRESETS, 1):
        print(f"    [{i}] {preset['icon']} {preset['name']}")
    
    print(f"\n    [0] Custom activity")
    print(f"    [b] Back to menu\n")
    
    choice = input("  Your choice: ").strip().lower()
    
    if choice == 'b':
        return
    
    if choice == '0':
        name = input("  Activity name: ").strip()
        icon = input("  Emoji icon (or press Enter for 📌): ").strip() or "📌"
    elif choice.isdigit() and 1 <= int(choice) <= len(PRESETS):
        preset = PRESETS[int(choice) - 1]
        name = preset["name"]
        icon = preset["icon"]
    else:
        print(f"\n  {Colors.RED}Invalid choice!{Colors.END}")
        input("  Press Enter to continue...")
        return
    
    # Check if activity already exists
    if any(a["name"].lower() == name.lower() for a in data["activities"]):
        print(f"\n  {Colors.YELLOW}Activity '{name}' already exists!{Colors.END}")
        input("  Press Enter to continue...")
        return
    
    activity = {
        "name": name,
        "icon": icon,
        "current_streak": 0,
        "longest_streak": 0,
        "total_days": 0,
        "checked_in_dates": [],
        "created_at": get_today()
    }
    
    data["activities"].append(activity)
    save_data(data)
    
    print(f"\n  {Colors.GREEN}✅ Added '{icon} {name}' successfully!{Colors.END}")
    send_notification("Activity Added! 🎉", f"{icon} {name} is now being tracked!")
    input("  Press Enter to continue...")


def check_in(data):
    """Check in for an activity."""
    activities = data["activities"]
    
    if not activities:
        print(f"\n  {Colors.YELLOW}No activities to check in! Add one first.{Colors.END}")
        input("  Press Enter to continue...")
        return
    
    clear_screen()
    print(f"\n  {Colors.BOLD}✅ CHECK IN{Colors.END}\n")
    
    for i, activity in enumerate(activities, 1):
        icon = activity.get("icon", "📌")
        status, _ = get_streak_status(activity)
        check_mark = "✅" if status == "checked_in_today" else "⬜"
        print(f"    [{i}] {check_mark} {icon} {activity['name']}")
    
    print(f"\n    [a] Check in ALL")
    print(f"    [b] Back to menu\n")
    
    choice = input("  Your choice: ").strip().lower()
    
    if choice == 'b':
        return
    
    if choice == 'a':
        indices = range(len(activities))
    elif choice.isdigit() and 1 <= int(choice) <= len(activities):
        indices = [int(choice) - 1]
    else:
        print(f"\n  {Colors.RED}Invalid choice!{Colors.END}")
        input("  Press Enter to continue...")
        return
    
    today = get_today()
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    for idx in indices:
        activity = activities[idx]
        
        # Already checked in today
        if today in activity["checked_in_dates"]:
            if len(indices) == 1:
                print(f"\n  {Colors.YELLOW}Already checked in for {activity['name']} today!{Colors.END}")
            continue
        
        # Update streak
        if activity["checked_in_dates"] and activity["checked_in_dates"][-1] == yesterday:
            activity["current_streak"] += 1
        else:
            activity["current_streak"] = 1
        
        # Update records
        activity["total_days"] += 1
        if activity["current_streak"] > activity["longest_streak"]:
            activity["longest_streak"] = activity["current_streak"]
        
        activity["checked_in_dates"].append(today)
        
        # Check for badges
        new_badges = check_and_award_badges(data, activity)
        
        icon = activity.get("icon", "📌")
        streak = activity["current_streak"]
        
        print(f"\n  {Colors.GREEN}🔥 {icon} {activity['name']} - Day {streak}!{Colors.END}")
        
        # Notifications for milestones
        if streak in [7, 14, 30, 50, 100, 365]:
            send_notification(
                f"🎉 Milestone: {streak} Days!",
                f"Incredible! You've hit {streak} days of {activity['name']}!"
            )
            print(f"  {Colors.YELLOW}🎉 MILESTONE: {streak} day streak!{Colors.END}")
        else:
            send_notification(
                "Check-in Complete! ✅",
                f"{icon} {activity['name']} - Day {streak} streak!"
            )
        
        # Show new badges
        for badge in new_badges:
            print(f"  {Colors.YELLOW}🏆 NEW BADGE: {badge}{Colors.END}")
            send_notification("🏆 Badge Earned!", badge)
    
    save_data(data)
    input("\n  Press Enter to continue...")


def view_badges(data):
    """View all earned badges."""
    clear_screen()
    print(f"\n  {Colors.BOLD}🏆 YOUR BADGES{Colors.END}\n")
    
    earned = set()
    for badge in data["badges"]:
        parts = badge.rsplit('_', 1)
        if len(parts) >= 2:
            badge_type = '_'.join(parts[:-1])
            earned.add(badge_type)
    
    print(f"  {Colors.GREEN}Earned:{Colors.END}")
    if earned:
        for badge_id in earned:
            if badge_id in BADGES:
                info = BADGES[badge_id]
                print(f"    {info['name']} - {info['description']}")
    else:
        print(f"    {Colors.YELLOW}No badges yet! Keep going!{Colors.END}")
    
    print(f"\n  {Colors.BLUE}Locked:{Colors.END}")
    for badge_id, info in BADGES.items():
        if badge_id not in earned:
            print(f"    🔒 {info['name']} - {info['description']}")
    
    input("\n  Press Enter to continue...")


def delete_activity(data):
    """Delete an activity."""
    activities = data["activities"]
    
    if not activities:
        print(f"\n  {Colors.YELLOW}No activities to delete!{Colors.END}")
        input("  Press Enter to continue...")
        return
    
    clear_screen()
    print(f"\n  {Colors.BOLD}🗑️ DELETE ACTIVITY{Colors.END}\n")
    
    for i, activity in enumerate(activities, 1):
        icon = activity.get("icon", "📌")
        print(f"    [{i}] {icon} {activity['name']}")
    
    print(f"\n    [b] Back to menu\n")
    
    choice = input("  Your choice: ").strip().lower()
    
    if choice == 'b':
        return
    
    if choice.isdigit() and 1 <= int(choice) <= len(activities):
        idx = int(choice) - 1
        activity = activities[idx]
        confirm = input(f"\n  Delete '{activity['name']}'? (y/n): ").strip().lower()
        
        if confirm == 'y':
            del activities[idx]
            save_data(data)
            print(f"\n  {Colors.GREEN}Deleted!{Colors.END}")
        else:
            print(f"\n  {Colors.YELLOW}Cancelled.{Colors.END}")
    else:
        print(f"\n  {Colors.RED}Invalid choice!{Colors.END}")
    
    input("  Press Enter to continue...")


def main_menu(data):
    """Display the main menu."""
    print_header()
    display_stats(data)
    display_activities(data)
    
    print(f"""
  {Colors.BOLD}MENU{Colors.END}
  ────────────────────────────────
  [1] ✅ Check In
  [2] ➕ Add Activity
  [3] 🏆 View Badges
  [4] 🗑️ Delete Activity  
  [5] 🔔 Test Notification
  [q] 👋 Quit
  ────────────────────────────────
""")


def main():
    """Main application loop."""
    data = load_data()
    
    # Update broken streaks on startup
    for activity in data["activities"]:
        status, _ = get_streak_status(activity)
        if status == "broken":
            activity["current_streak"] = 0
    save_data(data)
    
    # Welcome notification
    send_notification("Consistency Tracker 🔥", "Let's build some streaks today!")
    
    while True:
        clear_screen()
        main_menu(data)
        
        choice = input("  Your choice: ").strip().lower()
        
        if choice == '1':
            check_in(data)
        elif choice == '2':
            add_activity(data)
        elif choice == '3':
            view_badges(data)
        elif choice == '4':
            delete_activity(data)
        elif choice == '5':
            send_notification("🔔 Test Notification", "Notifications are working! You'll get streak reminders.")
            print(f"\n  {Colors.GREEN}Notification sent!{Colors.END}")
            input("  Press Enter to continue...")
        elif choice == 'q':
            clear_screen()
            print(f"\n  {Colors.CYAN}👋 Keep building those streaks! See you tomorrow!{Colors.END}\n")
            break
        
        # Reload data in case of changes
        data = load_data()


if __name__ == "__main__":
    main()
