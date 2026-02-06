#!/usr/bin/env python3
"""
🔥 Consistency Tracker - Track your daily habits and maintain streaks!
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Data file path
DATA_FILE = Path(__file__).parent / "streak_data.json"

# Colors for terminal
class Colors:
    ORANGE = '\033[38;5;208m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

# Preset activities
PRESETS = [
    ("💻 Coding", "coding"),
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

# Badges
BADGES = {
    1: ("⭐", "First Step", "Complete your first day"),
    7: ("🔥", "Week Warrior", "7 day streak"),
    14: ("💪", "Fortnight Fighter", "14 day streak"),
    30: ("🏆", "Month Master", "30 day streak"),
    50: ("🌟", "Fifty & Fabulous", "50 day streak"),
    100: ("💎", "Century Club", "100 day streak"),
    365: ("👑", "Year Legend", "365 day streak"),
}

def load_data():
    """Load data from JSON file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"activities": {}, "badges": [], "freeze_tokens": 2}

def save_data(data):
    """Save data to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def send_notification(title, message):
    """Send Mac notification."""
    script = f'display notification "{message}" with title "{title}" sound name "default"'
    subprocess.run(["osascript", "-e", script], capture_output=True)

def clear_screen():
    """Clear terminal screen."""
    os.system('clear')

def get_today():
    """Get today's date as string."""
    return datetime.now().strftime("%Y-%m-%d")

def get_streak(dates):
    """Calculate current streak from list of dates."""
    if not dates:
        return 0
    
    dates = sorted(set(dates), reverse=True)
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    # Check if checked in today or yesterday
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

def print_header():
    """Print app header."""
    print(f"""
{Colors.ORANGE}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗
║                   🔥 CONSISTENCY TRACKER 🔥                   ║
╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
""")

def print_activity(name, data, index):
    """Print a single activity with streak info."""
    dates = data.get("dates", [])
    streak = get_streak(dates)
    longest = data.get("longest", 0)
    total = len(dates)
    today = get_today()
    checked_today = today in dates
    
    # Status indicator
    if checked_today:
        status = f"{Colors.GREEN}✓ Done{Colors.RESET}"
        streak_color = Colors.GREEN
    elif streak > 0:
        status = f"{Colors.YELLOW}⚠ At Risk{Colors.RESET}"
        streak_color = Colors.YELLOW
    else:
        status = f"{Colors.DIM}○ Not started{Colors.RESET}"
        streak_color = Colors.DIM
    
    # Streak fire emojis
    fire = "🔥" * min(streak // 7 + (1 if streak > 0 else 0), 5)
    
    print(f"""  {Colors.BOLD}[{index}]{Colors.RESET} {name}
      {streak_color}Streak: {streak} days{Colors.RESET} {fire}  │  Best: {longest}  │  Total: {total}  │  {status}
""")

def print_menu():
    """Print main menu options."""
    print(f"""
{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
  {Colors.BOLD}[C]{Colors.RESET} Check In    {Colors.BOLD}[A]{Colors.RESET} Add Activity    {Colors.BOLD}[B]{Colors.RESET} Badges    {Colors.BOLD}[S]{Colors.RESET} Stats
  {Colors.BOLD}[R]{Colors.RESET} Reminders   {Colors.BOLD}[D]{Colors.RESET} Delete          {Colors.BOLD}[Q]{Colors.RESET} Quit
{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
""")

def show_activities(data):
    """Display all activities."""
    activities = data.get("activities", {})
    
    if not activities:
        print(f"""
  {Colors.DIM}No activities yet! Add one to get started.{Colors.RESET}
""")
        return
    
    print(f"  {Colors.BOLD}Your Activities:{Colors.RESET}\n")
    for i, (name, info) in enumerate(activities.items(), 1):
        print_activity(name, info, i)

def check_in(data):
    """Check in for an activity."""
    activities = data.get("activities", {})
    
    if not activities:
        print(f"\n  {Colors.YELLOW}No activities yet! Add one first.{Colors.RESET}")
        input("\n  Press Enter to continue...")
        return data
    
    print(f"\n  {Colors.BOLD}Select activity to check in:{Colors.RESET}\n")
    activity_list = list(activities.keys())
    
    for i, name in enumerate(activity_list, 1):
        dates = activities[name].get("dates", [])
        checked = "✓" if get_today() in dates else " "
        print(f"    [{i}] {checked} {name}")
    
    print(f"\n    [0] Cancel")
    
    try:
        choice = input(f"\n  {Colors.CYAN}Enter number: {Colors.RESET}")
        idx = int(choice) - 1
        
        if idx == -1:
            return data
        
        if 0 <= idx < len(activity_list):
            name = activity_list[idx]
            today = get_today()
            
            if today in activities[name].get("dates", []):
                print(f"\n  {Colors.YELLOW}Already checked in for {name} today!{Colors.RESET}")
            else:
                activities[name].setdefault("dates", []).append(today)
                
                # Update longest streak
                streak = get_streak(activities[name]["dates"])
                if streak > activities[name].get("longest", 0):
                    activities[name]["longest"] = streak
                
                save_data(data)
                
                # Check for new badges
                check_badges(data, name, streak)
                
                print(f"\n  {Colors.GREEN}✓ Checked in for {name}! Streak: {streak} days 🔥{Colors.RESET}")
                send_notification("Consistency Tracker", f"✓ Checked in for {name}! Streak: {streak} days 🔥")
    except (ValueError, IndexError):
        print(f"\n  {Colors.RED}Invalid choice.{Colors.RESET}")
    
    input("\n  Press Enter to continue...")
    return data

def check_badges(data, activity_name, streak):
    """Check and award new badges."""
    if streak in BADGES:
        badge_key = f"{activity_name}_{streak}"
        if badge_key not in data.get("badges", []):
            data.setdefault("badges", []).append(badge_key)
            icon, name, desc = BADGES[streak]
            save_data(data)
            print(f"\n  {Colors.YELLOW}🏆 NEW BADGE: {icon} {name} - {desc}!{Colors.RESET}")
            send_notification("🏆 Badge Earned!", f"{icon} {name} - {desc}")

def add_activity(data):
    """Add a new activity."""
    print(f"\n  {Colors.BOLD}Add New Activity{Colors.RESET}\n")
    print(f"  {Colors.DIM}Quick presets:{Colors.RESET}\n")
    
    for i, (name, key) in enumerate(PRESETS, 1):
        exists = name in data.get("activities", {})
        status = f"{Colors.DIM}(added){Colors.RESET}" if exists else ""
        print(f"    [{i:2}] {name} {status}")
    
    print(f"\n    [{len(PRESETS)+1}] ✨ Custom activity")
    print(f"    [0] Cancel")
    
    try:
        choice = input(f"\n  {Colors.CYAN}Enter number: {Colors.RESET}")
        idx = int(choice)
        
        if idx == 0:
            return data
        
        if 1 <= idx <= len(PRESETS):
            name, key = PRESETS[idx - 1]
        elif idx == len(PRESETS) + 1:
            name = input(f"\n  {Colors.CYAN}Enter activity name: {Colors.RESET}")
            if not name.strip():
                print(f"\n  {Colors.RED}Name cannot be empty.{Colors.RESET}")
                input("\n  Press Enter to continue...")
                return data
        else:
            print(f"\n  {Colors.RED}Invalid choice.{Colors.RESET}")
            input("\n  Press Enter to continue...")
            return data
        
        if name in data.get("activities", {}):
            print(f"\n  {Colors.YELLOW}'{name}' already exists!{Colors.RESET}")
        else:
            data.setdefault("activities", {})[name] = {"dates": [], "longest": 0}
            save_data(data)
            print(f"\n  {Colors.GREEN}✓ Added '{name}'!{Colors.RESET}")
    except ValueError:
        print(f"\n  {Colors.RED}Invalid input.{Colors.RESET}")
    
    input("\n  Press Enter to continue...")
    return data

def delete_activity(data):
    """Delete an activity."""
    activities = data.get("activities", {})
    
    if not activities:
        print(f"\n  {Colors.YELLOW}No activities to delete.{Colors.RESET}")
        input("\n  Press Enter to continue...")
        return data
    
    print(f"\n  {Colors.BOLD}Delete Activity{Colors.RESET}\n")
    activity_list = list(activities.keys())
    
    for i, name in enumerate(activity_list, 1):
        print(f"    [{i}] {name}")
    
    print(f"\n    [0] Cancel")
    
    try:
        choice = input(f"\n  {Colors.CYAN}Enter number: {Colors.RESET}")
        idx = int(choice) - 1
        
        if idx == -1:
            return data
        
        if 0 <= idx < len(activity_list):
            name = activity_list[idx]
            confirm = input(f"\n  {Colors.RED}Delete '{name}'? This cannot be undone! (y/n): {Colors.RESET}")
            
            if confirm.lower() == 'y':
                del activities[name]
                save_data(data)
                print(f"\n  {Colors.GREEN}✓ Deleted '{name}'.{Colors.RESET}")
            else:
                print(f"\n  {Colors.DIM}Cancelled.{Colors.RESET}")
    except (ValueError, IndexError):
        print(f"\n  {Colors.RED}Invalid choice.{Colors.RESET}")
    
    input("\n  Press Enter to continue...")
    return data

def show_badges(data):
    """Show all badges."""
    clear_screen()
    print_header()
    
    print(f"  {Colors.BOLD}🏆 Your Badges{Colors.RESET}\n")
    
    earned = data.get("badges", [])
    
    if not earned:
        print(f"  {Colors.DIM}No badges yet. Keep building your streaks!{Colors.RESET}\n")
    else:
        print(f"  {Colors.GREEN}Earned ({len(earned)}):{Colors.RESET}\n")
        for badge_key in earned:
            parts = badge_key.rsplit("_", 1)
            if len(parts) == 2:
                activity, days = parts
                days = int(days)
                if days in BADGES:
                    icon, name, desc = BADGES[days]
                    print(f"    {icon} {Colors.BOLD}{name}{Colors.RESET} - {activity}")
    
    print(f"\n  {Colors.DIM}Available Badges:{Colors.RESET}\n")
    for days, (icon, name, desc) in BADGES.items():
        print(f"    {icon} {name}: {desc}")
    
    input("\n  Press Enter to continue...")

def show_stats(data):
    """Show statistics."""
    clear_screen()
    print_header()
    
    activities = data.get("activities", {})
    
    print(f"  {Colors.BOLD}📊 Statistics{Colors.RESET}\n")
    
    if not activities:
        print(f"  {Colors.DIM}No data yet. Start tracking to see stats!{Colors.RESET}")
        input("\n  Press Enter to continue...")
        return
    
    # Calculate totals
    total_days = sum(len(a.get("dates", [])) for a in activities.values())
    total_activities = len(activities)
    best_streak = max((a.get("longest", 0) for a in activities.values()), default=0)
    active_streaks = sum(1 for a in activities.values() if get_streak(a.get("dates", [])) > 0)
    
    print(f"""
    📅 Total Days Logged:    {Colors.BOLD}{total_days}{Colors.RESET}
    📋 Activities Tracked:   {Colors.BOLD}{total_activities}{Colors.RESET}
    🔥 Active Streaks:       {Colors.BOLD}{active_streaks}{Colors.RESET}
    🏆 Best Streak Ever:     {Colors.BOLD}{best_streak} days{Colors.RESET}
    ⭐ Badges Earned:        {Colors.BOLD}{len(data.get('badges', []))}{Colors.RESET}
""")
    
    # Weekly view
    print(f"  {Colors.BOLD}Last 7 Days:{Colors.RESET}\n")
    
    today = datetime.now().date()
    header = "    "
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        header += f" {day.strftime('%a'):^5}"
    print(header)
    
    for name, info in activities.items():
        dates = info.get("dates", [])
        row = f"    "
        for i in range(6, -1, -1):
            day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            if day in dates:
                row += f" {Colors.GREEN}  ■  {Colors.RESET}"
            else:
                row += f" {Colors.DIM}  ·  {Colors.RESET}"
        print(f"{row}  {name[:15]}")
    
    input("\n  Press Enter to continue...")

def setup_reminders():
    """Setup reminder information."""
    clear_screen()
    print_header()
    
    print(f"""  {Colors.BOLD}🔔 Setting Up Reminders{Colors.RESET}

  To get daily reminders, you can set up a cron job or use the reminder script.
  
  {Colors.CYAN}Option 1: Quick Reminder (runs in background){Colors.RESET}
  
  Run this in a separate terminal:
  
    {Colors.BOLD}python3 reminder.py &{Colors.RESET}
  
  {Colors.CYAN}Option 2: Schedule with cron (persistent){Colors.RESET}
  
  Run this command to edit your crontab:
  
    {Colors.BOLD}crontab -e{Colors.RESET}
  
  Then add these lines for reminders at 9am, 2pm, and 8pm:
  
    {Colors.DIM}0 9 * * * osascript -e 'display notification "Time to check in!" with title "🔥 Consistency Tracker"'
    0 14 * * * osascript -e 'display notification "Don\\'t forget to log progress!" with title "📝 Afternoon Check-in"'  
    0 20 * * * osascript -e 'display notification "Check in before midnight!" with title "⚠️ Streak at Risk"'{Colors.RESET}
  
  {Colors.GREEN}Tip: The app will also send a notification when you check in!{Colors.RESET}
""")
    
    input("  Press Enter to continue...")

def main():
    """Main application loop."""
    data = load_data()
    
    while True:
        clear_screen()
        print_header()
        
        # Show today's date
        print(f"  {Colors.DIM}{datetime.now().strftime('%A, %B %d, %Y')}{Colors.RESET}\n")
        
        show_activities(data)
        print_menu()
        
        choice = input(f"  {Colors.CYAN}Enter choice: {Colors.RESET}").strip().lower()
        
        if choice == 'c':
            data = check_in(data)
        elif choice == 'a':
            data = add_activity(data)
        elif choice == 'd':
            data = delete_activity(data)
        elif choice == 'b':
            show_badges(data)
        elif choice == 's':
            show_stats(data)
        elif choice == 'r':
            setup_reminders()
        elif choice == 'q':
            clear_screen()
            print(f"\n  {Colors.ORANGE}Keep the streak going! 🔥{Colors.RESET}\n")
            break
        elif choice.isdigit():
            # Quick check-in by number
            idx = int(choice) - 1
            activities = list(data.get("activities", {}).keys())
            if 0 <= idx < len(activities):
                name = activities[idx]
                today = get_today()
                if today not in data["activities"][name].get("dates", []):
                    data["activities"][name].setdefault("dates", []).append(today)
                    streak = get_streak(data["activities"][name]["dates"])
                    if streak > data["activities"][name].get("longest", 0):
                        data["activities"][name]["longest"] = streak
                    save_data(data)
                    check_badges(data, name, streak)
                    print(f"\n  {Colors.GREEN}✓ Checked in for {name}! Streak: {streak} days 🔥{Colors.RESET}")
                    send_notification("Consistency Tracker", f"✓ {name}: {streak} days 🔥")
                else:
                    print(f"\n  {Colors.YELLOW}Already checked in for {name} today!{Colors.RESET}")
                input("\n  Press Enter to continue...")

if __name__ == "__main__":
    main()
