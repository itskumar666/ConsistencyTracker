#!/usr/bin/env python3
"""
🔥 Consistency Tracker - A Beautiful Mac App
Track your daily habits and maintain streaks!
"""

import customtkinter as ctk
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Data storage
DATA_DIR = Path.home() / ".consistency_tracker"
DATA_FILE = DATA_DIR / "data.json"
DATA_DIR.mkdir(exist_ok=True)

# Color palette
COLORS = {
    "bg": "#1a1a2e",
    "card": "#16213e",
    "accent": "#e94560",
    "accent2": "#0f3460",
    "success": "#00bf63",
    "warning": "#ff9f1c",
    "text": "#ffffff",
    "text_dim": "#a0a0a0",
    "fire": "#ff6b35",
}

PRESETS = [
    ("💻", "Coding", "#e94560"),
    ("📚", "Study", "#4361ee"),
    ("📖", "Reading", "#2ec4b6"),
    ("🏃", "Exercise", "#ff6b35"),
    ("✍️", "Writing", "#9b5de5"),
    ("🧘", "Meditation", "#00bf63"),
    ("🎸", "Music", "#f72585"),
    ("🎨", "Drawing", "#4cc9f0"),
    ("🌍", "Language", "#ffd166"),
    ("🔧", "Project", "#06d6a0"),
]

BADGES = {
    1: ("⭐", "First Step", "Complete your first day"),
    7: ("🔥", "Week Warrior", "7 day streak"),
    14: ("💪", "Fortnight Fighter", "14 day streak"),
    30: ("🏆", "Month Master", "30 day streak"),
    50: ("🌟", "Fifty & Fabulous", "50 day streak"),
    100: ("💎", "Century Club", "100 day streak"),
    365: ("👑", "Year Legend", "365 day streak"),
}


class ConsistencyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("Consistency Tracker")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Load data
        self.data = self.load_data()
        
        # Create UI
        self.create_sidebar()
        self.create_main_area()
        
        # Start reminder thread
        self.start_reminder_thread()
        
        # Show home by default
        self.show_home()
    
    def load_data(self):
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {"activities": {}, "badges": []}
    
    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_today(self):
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_streak(self, dates):
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
    
    def send_notification(self, title, message):
        script = f'display notification "{message}" with title "{title}" sound name "default"'
        subprocess.run(["osascript", "-e", script], capture_output=True)
    
    def create_sidebar(self):
        # Sidebar frame
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=COLORS["card"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)
        
        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(30, 20))
        
        ctk.CTkLabel(
            logo_frame, 
            text="🔥", 
            font=ctk.CTkFont(size=40)
        ).pack()
        
        ctk.CTkLabel(
            logo_frame, 
            text="Consistency", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text"]
        ).pack()
        
        ctk.CTkLabel(
            logo_frame, 
            text="Tracker", 
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_dim"]
        ).pack()
        
        # Navigation buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("🏠", "Home", self.show_home),
            ("➕", "Add Activity", self.show_add_activity),
            ("🏆", "Badges", self.show_badges),
            ("📊", "Statistics", self.show_stats),
            ("⚙️", "Settings", self.show_settings),
        ]
        
        for i, (icon, text, command) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}  {text}",
                font=ctk.CTkFont(size=14),
                anchor="w",
                height=45,
                corner_radius=10,
                fg_color="transparent",
                hover_color=COLORS["accent2"],
                command=command
            )
            btn.grid(row=i+1, column=0, padx=15, pady=5, sticky="ew")
            self.nav_buttons[text] = btn
        
        # Streak display at bottom
        self.streak_frame = ctk.CTkFrame(self.sidebar, fg_color=COLORS["accent2"], corner_radius=15)
        self.streak_frame.grid(row=7, column=0, padx=15, pady=20, sticky="ew")
        
        self.streak_label = ctk.CTkLabel(
            self.streak_frame,
            text="🔥 0",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.streak_label.pack(pady=10)
        
        ctk.CTkLabel(
            self.streak_frame,
            text="Current Best Streak",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_dim"]
        ).pack(pady=(0, 10))
    
    def create_main_area(self):
        # Main content area
        self.main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        self.header = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=80)
        self.header.grid(row=0, column=0, sticky="ew", padx=30, pady=20)
        self.header.grid_columnconfigure(1, weight=1)
        
        self.header_title = ctk.CTkLabel(
            self.header,
            text="Dashboard",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.header_title.grid(row=0, column=0, sticky="w")
        
        self.header_date = ctk.CTkLabel(
            self.header,
            text=datetime.now().strftime("%A, %B %d, %Y"),
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_dim"]
        )
        self.header_date.grid(row=1, column=0, sticky="w")
        
        # Content area (scrollable)
        self.content_frame = ctk.CTkScrollableFrame(
            self.main_frame, 
            fg_color="transparent",
            scrollbar_button_color=COLORS["accent2"]
        )
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self.content_frame.grid_columnconfigure(0, weight=1)
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_streak_display(self):
        max_streak = 0
        for info in self.data.get("activities", {}).values():
            streak = self.get_streak(info.get("dates", []))
            max_streak = max(max_streak, streak)
        self.streak_label.configure(text=f"🔥 {max_streak}")
    
    def set_active_nav(self, name):
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.configure(fg_color=COLORS["accent"])
            else:
                btn.configure(fg_color="transparent")
    
    # ==================== HOME ====================
    def show_home(self):
        self.clear_content()
        self.set_active_nav("Home")
        self.header_title.configure(text="Dashboard")
        self.update_streak_display()
        
        activities = self.data.get("activities", {})
        
        if not activities:
            # Empty state
            empty_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card"], corner_radius=20)
            empty_frame.pack(fill="x", pady=20)
            
            ctk.CTkLabel(
                empty_frame,
                text="🚀",
                font=ctk.CTkFont(size=60)
            ).pack(pady=(40, 10))
            
            ctk.CTkLabel(
                empty_frame,
                text="Welcome to Consistency Tracker!",
                font=ctk.CTkFont(size=20, weight="bold")
            ).pack(pady=5)
            
            ctk.CTkLabel(
                empty_frame,
                text="Add your first activity to start building streaks",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_dim"]
            ).pack(pady=5)
            
            ctk.CTkButton(
                empty_frame,
                text="➕  Add Activity",
                font=ctk.CTkFont(size=14, weight="bold"),
                height=45,
                corner_radius=10,
                fg_color=COLORS["accent"],
                hover_color="#c73e54",
                command=self.show_add_activity
            ).pack(pady=(20, 40))
            return
        
        # Activity cards
        for name, info in activities.items():
            self.create_activity_card(name, info)
    
    def create_activity_card(self, name, info):
        dates = info.get("dates", [])
        streak = self.get_streak(dates)
        longest = info.get("longest", 0)
        total = len(dates)
        checked_today = self.get_today() in dates
        color = info.get("color", COLORS["accent"])
        
        # Card frame
        card = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card"], corner_radius=15)
        card.pack(fill="x", pady=8)
        card.grid_columnconfigure(1, weight=1)
        
        # Left color bar
        color_bar = ctk.CTkFrame(card, width=6, fg_color=color, corner_radius=3)
        color_bar.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(15, 10), pady=15)
        
        # Main content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.grid(row=0, column=1, sticky="ew", padx=10, pady=15)
        content.grid_columnconfigure(0, weight=1)
        
        # Title row
        title_frame = ctk.CTkFrame(content, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew")
        title_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            title_frame,
            text=name,
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="w")
        
        # Status badge
        if checked_today:
            status_text = "✓ Done"
            status_color = COLORS["success"]
        elif streak > 0:
            status_text = "⚠ At Risk"
            status_color = COLORS["warning"]
        else:
            status_text = "Not Started"
            status_color = COLORS["text_dim"]
        
        status_label = ctk.CTkLabel(
            title_frame,
            text=status_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=status_color
        )
        status_label.grid(row=0, column=1, padx=10)
        
        # Stats row
        stats_frame = ctk.CTkFrame(content, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        # Fire streak
        fire_count = min(streak // 7 + (1 if streak > 0 else 0), 5)
        fire_text = "🔥" * fire_count if fire_count > 0 else ""
        
        ctk.CTkLabel(
            stats_frame,
            text=f"🔥 {streak} days {fire_text}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["fire"] if streak > 0 else COLORS["text_dim"]
        ).pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(
            stats_frame,
            text=f"Best: {longest}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"]
        ).pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(
            stats_frame,
            text=f"Total: {total}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"]
        ).pack(side="left")
        
        # Check-in button
        if checked_today:
            btn = ctk.CTkButton(
                card,
                text="✓",
                width=50,
                height=50,
                corner_radius=25,
                fg_color=COLORS["success"],
                hover_color=COLORS["success"],
                state="disabled",
                font=ctk.CTkFont(size=20, weight="bold")
            )
        else:
            btn = ctk.CTkButton(
                card,
                text="+",
                width=50,
                height=50,
                corner_radius=25,
                fg_color=COLORS["accent"],
                hover_color="#c73e54",
                font=ctk.CTkFont(size=24, weight="bold"),
                command=lambda n=name: self.check_in(n)
            )
        btn.grid(row=0, column=2, padx=20, pady=15)
        
        # Delete button (small)
        delete_btn = ctk.CTkButton(
            card,
            text="×",
            width=25,
            height=25,
            corner_radius=12,
            fg_color="transparent",
            hover_color="#4a0010",
            text_color=COLORS["text_dim"],
            font=ctk.CTkFont(size=16),
            command=lambda n=name: self.delete_activity(n)
        )
        delete_btn.grid(row=0, column=3, padx=(0, 10), pady=15, sticky="ne")
    
    def check_in(self, activity_name):
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
        self.send_notification("✅ Checked In!", f"{activity_name}: 🔥 {streak} day streak!")
        
        # Refresh
        self.show_home()
    
    def check_badges(self, activity_name, streak):
        if streak in BADGES:
            badge_key = f"{activity_name}_{streak}"
            if badge_key not in self.data.get("badges", []):
                self.data.setdefault("badges", []).append(badge_key)
                self.save_data()
                
                icon, name, _ = BADGES[streak]
                self.send_notification("🏆 Badge Earned!", f"{icon} {name} - {streak} days!")
    
    def delete_activity(self, name):
        dialog = ctk.CTkInputDialog(
            text=f"Type 'DELETE' to confirm deleting '{name}':",
            title="Delete Activity"
        )
        result = dialog.get_input()
        
        if result == "DELETE":
            if name in self.data.get("activities", {}):
                del self.data["activities"][name]
                self.save_data()
                self.show_home()
    
    # ==================== ADD ACTIVITY ====================
    def show_add_activity(self):
        self.clear_content()
        self.set_active_nav("Add Activity")
        self.header_title.configure(text="Add Activity")
        
        # Presets section
        preset_label = ctk.CTkLabel(
            self.content_frame,
            text="Quick Add Presets",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        preset_label.pack(fill="x", pady=(10, 15))
        
        # Preset grid
        preset_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        preset_frame.pack(fill="x")
        
        for i, (icon, name, color) in enumerate(PRESETS):
            exists = f"{icon} {name}" in self.data.get("activities", {})
            
            btn = ctk.CTkButton(
                preset_frame,
                text=f"{icon}\n{name}",
                width=100,
                height=80,
                corner_radius=15,
                fg_color=COLORS["card"] if not exists else COLORS["success"],
                hover_color=color if not exists else COLORS["success"],
                font=ctk.CTkFont(size=12),
                command=lambda ic=icon, n=name, c=color: self.add_preset_activity(ic, n, c) if f"{ic} {n}" not in self.data.get("activities", {}) else None
            )
            btn.grid(row=i // 5, column=i % 5, padx=8, pady=8)
            
            if exists:
                btn.configure(state="disabled")
        
        # Divider
        ctk.CTkFrame(self.content_frame, height=2, fg_color=COLORS["accent2"]).pack(fill="x", pady=30)
        
        # Custom activity
        custom_label = ctk.CTkLabel(
            self.content_frame,
            text="Or Create Custom Activity",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        custom_label.pack(fill="x", pady=(0, 15))
        
        custom_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card"], corner_radius=15)
        custom_frame.pack(fill="x", pady=10)
        
        # Name input
        ctk.CTkLabel(
            custom_frame,
            text="Activity Name",
            font=ctk.CTkFont(size=13),
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 5))
        
        self.custom_name_entry = ctk.CTkEntry(
            custom_frame,
            placeholder_text="e.g., 🎯 Daily Goal",
            height=45,
            corner_radius=10
        )
        self.custom_name_entry.pack(fill="x", padx=20, pady=(0, 20))
        
        # Add button
        ctk.CTkButton(
            custom_frame,
            text="Add Activity",
            height=45,
            corner_radius=10,
            fg_color=COLORS["accent"],
            hover_color="#c73e54",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.add_custom_activity
        ).pack(fill="x", padx=20, pady=(0, 20))
    
    def add_preset_activity(self, icon, name, color):
        full_name = f"{icon} {name}"
        if full_name not in self.data.get("activities", {}):
            self.data.setdefault("activities", {})[full_name] = {
                "dates": [],
                "longest": 0,
                "color": color
            }
            self.save_data()
            self.send_notification("✨ Activity Added!", f"{full_name} - Start your streak!")
            self.show_add_activity()  # Refresh
    
    def add_custom_activity(self):
        name = self.custom_name_entry.get().strip()
        if name and name not in self.data.get("activities", {}):
            self.data.setdefault("activities", {})[name] = {
                "dates": [],
                "longest": 0,
                "color": COLORS["accent"]
            }
            self.save_data()
            self.send_notification("✨ Activity Added!", f"{name} - Start your streak!")
            self.show_home()
    
    # ==================== BADGES ====================
    def show_badges(self):
        self.clear_content()
        self.set_active_nav("Badges")
        self.header_title.configure(text="Your Badges")
        
        earned = self.data.get("badges", [])
        
        # Earned section
        if earned:
            ctk.CTkLabel(
                self.content_frame,
                text=f"🏆 Earned ({len(earned)})",
                font=ctk.CTkFont(size=16, weight="bold"),
                anchor="w"
            ).pack(fill="x", pady=(10, 15))
            
            earned_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            earned_frame.pack(fill="x")
            
            col = 0
            for badge_key in earned:
                parts = badge_key.rsplit("_", 1)
                if len(parts) == 2:
                    activity, days = parts
                    days = int(days)
                    if days in BADGES:
                        icon, name, desc = BADGES[days]
                        
                        badge_card = ctk.CTkFrame(earned_frame, fg_color=COLORS["card"], corner_radius=15)
                        badge_card.grid(row=col // 4, column=col % 4, padx=8, pady=8)
                        
                        ctk.CTkLabel(badge_card, text=icon, font=ctk.CTkFont(size=40)).pack(pady=(15, 5))
                        ctk.CTkLabel(badge_card, text=name, font=ctk.CTkFont(size=12, weight="bold")).pack()
                        ctk.CTkLabel(badge_card, text=activity[:15], font=ctk.CTkFont(size=10), text_color=COLORS["text_dim"]).pack(pady=(0, 15))
                        
                        col += 1
        
        # All badges section
        ctk.CTkLabel(
            self.content_frame,
            text="📋 All Badges",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(30, 15))
        
        for days, (icon, name, desc) in BADGES.items():
            badge_row = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card"], corner_radius=10)
            badge_row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(badge_row, text=icon, font=ctk.CTkFont(size=30)).pack(side="left", padx=15, pady=10)
            
            info_frame = ctk.CTkFrame(badge_row, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, pady=10)
            
            ctk.CTkLabel(info_frame, text=name, font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(info_frame, text=desc, font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"], anchor="w").pack(fill="x")
    
    # ==================== STATISTICS ====================
    def show_stats(self):
        self.clear_content()
        self.set_active_nav("Statistics")
        self.header_title.configure(text="Statistics")
        
        activities = self.data.get("activities", {})
        
        # Calculate stats
        total_days = sum(len(a.get("dates", [])) for a in activities.values())
        total_activities = len(activities)
        best_streak = max((a.get("longest", 0) for a in activities.values()), default=0)
        active_streaks = sum(1 for a in activities.values() if self.get_streak(a.get("dates", [])) > 0)
        badges_count = len(self.data.get("badges", []))
        
        # Stats cards
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=20)
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        stats = [
            ("📅", str(total_days), "Total Days"),
            ("📋", str(total_activities), "Activities"),
            ("🔥", str(active_streaks), "Active Streaks"),
            ("🏆", str(best_streak), "Best Streak"),
            ("⭐", str(badges_count), "Badges"),
        ]
        
        for i, (icon, value, label) in enumerate(stats):
            card = ctk.CTkFrame(stats_frame, fg_color=COLORS["card"], corner_radius=15)
            card.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")
            
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=30)).pack(pady=(20, 5))
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=28, weight="bold")).pack()
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"]).pack(pady=(0, 20))
        
        # Weekly heatmap
        ctk.CTkLabel(
            self.content_frame,
            text="📊 Last 7 Days",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(30, 15))
        
        today = datetime.now().date()
        
        for name, info in activities.items():
            row_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card"], corner_radius=10)
            row_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                row_frame,
                text=name[:20],
                font=ctk.CTkFont(size=12),
                width=150,
                anchor="w"
            ).pack(side="left", padx=15, pady=10)
            
            dates = info.get("dates", [])
            for i in range(6, -1, -1):
                day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
                is_active = day in dates
                
                day_box = ctk.CTkFrame(
                    row_frame,
                    width=30,
                    height=30,
                    corner_radius=5,
                    fg_color=COLORS["success"] if is_active else COLORS["accent2"]
                )
                day_box.pack(side="left", padx=3, pady=10)
                day_box.pack_propagate(False)
    
    # ==================== SETTINGS ====================
    def show_settings(self):
        self.clear_content()
        self.set_active_nav("Settings")
        self.header_title.configure(text="Settings")
        
        # Notifications
        notif_card = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card"], corner_radius=15)
        notif_card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            notif_card,
            text="🔔 Notifications",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkButton(
            notif_card,
            text="Send Test Notification",
            height=40,
            corner_radius=10,
            fg_color=COLORS["accent2"],
            hover_color=COLORS["accent"],
            command=lambda: self.send_notification("🔔 Test", "Notifications are working!")
        ).pack(fill="x", padx=20, pady=(0, 20))
        
        # Reminders info
        reminder_card = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card"], corner_radius=15)
        reminder_card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            reminder_card,
            text="⏰ Daily Reminders",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            reminder_card,
            text="• 9:00 AM - Morning motivation\n• 2:00 PM - Afternoon check-in\n• 8:00 PM - Evening warning",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_dim"],
            anchor="w",
            justify="left"
        ).pack(fill="x", padx=20, pady=(0, 20))
        
        # Data
        data_card = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card"], corner_radius=15)
        data_card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            data_card,
            text="📁 Data",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkButton(
            data_card,
            text="Open Data Folder",
            height=40,
            corner_radius=10,
            fg_color=COLORS["accent2"],
            hover_color=COLORS["accent"],
            command=lambda: subprocess.run(["open", str(DATA_DIR)])
        ).pack(fill="x", padx=20, pady=(0, 20))
        
        # About
        about_card = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card"], corner_radius=15)
        about_card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            about_card,
            text="Consistency Tracker v1.0",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(20, 5))
        
        ctk.CTkLabel(
            about_card,
            text="Build streaks. Stay consistent. Achieve goals.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"]
        ).pack(pady=(0, 20))
    
    # ==================== REMINDERS ====================
    def start_reminder_thread(self):
        def reminder_loop():
            sent = {"morning": False, "afternoon": False, "evening": False, "date": self.get_today()}
            
            while True:
                try:
                    now = datetime.now()
                    today = self.get_today()
                    
                    if sent["date"] != today:
                        sent = {"morning": False, "afternoon": False, "evening": False, "date": today}
                    
                    # Check if checked in
                    checked_in = any(
                        today in info.get("dates", [])
                        for info in self.data.get("activities", {}).values()
                    )
                    
                    if not checked_in and self.data.get("activities"):
                        hour = now.hour
                        
                        if hour == 9 and not sent["morning"]:
                            self.send_notification("☀️ Good Morning!", "Ready to build your streak?")
                            sent["morning"] = True
                        elif hour == 14 and not sent["afternoon"]:
                            self.send_notification("📝 Afternoon Check-in", "Don't forget to log progress!")
                            sent["afternoon"] = True
                        elif hour == 20 and not sent["evening"]:
                            self.send_notification("⚠️ Streak at Risk!", "Check in before midnight!")
                            sent["evening"] = True
                    
                    time.sleep(60)
                except:
                    time.sleep(60)
        
        thread = threading.Thread(target=reminder_loop, daemon=True)
        thread.start()


if __name__ == "__main__":
    app = ConsistencyApp()
    app.mainloop()
