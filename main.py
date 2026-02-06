#!/usr/bin/env python3
"""
🔥 Consistency Tracker - A Beautiful Mac App
Track your daily habits and maintain streaks!
"""

import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QLineEdit, QMessageBox,
    QGridLayout, QSizePolicy, QSpacerItem, QInputDialog, QTextEdit,
    QComboBox, QColorDialog, QListWidget, QListWidgetItem, QSplitter,
    QDialog, QDialogButtonBox, QSpinBox, QSlider, QTabWidget, QCheckBox,
    QCalendarWidget
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QTextCharFormat, QTextCursor, QTextListFormat

# Data storage
DATA_DIR = Path.home() / ".consistency_tracker"
DATA_FILE = DATA_DIR / "data.json"
DATA_DIR.mkdir(exist_ok=True)

ICLOUD_DIR = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/ConsistencyTracker"
ICLOUD_FILE = ICLOUD_DIR / "data.json"

# Styles
STYLE = """
QMainWindow {
    background-color: #0f0f1a;
}
QWidget {
    color: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
}
QFrame#sidebar {
    background-color: #1a1a2e;
    border-right: 1px solid #2a2a4a;
}
QFrame#card {
    background-color: #1e1e3f;
    border-radius: 15px;
    padding: 15px;
}
QPushButton#nav {
    background-color: transparent;
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    text-align: left;
    font-size: 14px;
}
QPushButton#nav:hover {
    background-color: #2a2a5a;
}
QPushButton#nav:checked {
    background-color: #e94560;
}
QPushButton#primary {
    background-color: #e94560;
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton#primary:hover {
    background-color: #ff5a75;
}
QPushButton#checkin {
    background-color: #e94560;
    border: none;
    border-radius: 25px;
    font-size: 20px;
    font-weight: bold;
}
QPushButton#checkin:hover {
    background-color: #ff5a75;
}
QPushButton#done {
    background-color: #00bf63;
    border: none;
    border-radius: 25px;
}
QPushButton#preset {
    background-color: #1e1e3f;
    border: 2px solid #3a3a6a;
    border-radius: 12px;
    padding: 15px;
    font-size: 13px;
}
QPushButton#preset:hover {
    border-color: #e94560;
    background-color: #2a2a5a;
}
QLineEdit {
    background-color: #2a2a5a;
    border: 2px solid #3a3a6a;
    border-radius: 10px;
    padding: 12px;
    font-size: 14px;
}
QLineEdit:focus {
    border-color: #e94560;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    background-color: #1a1a2e;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background-color: #3a3a6a;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

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


class ConsistencyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Consistency Tracker")
        self.setMinimumSize(950, 700)
        self.resize(1000, 750)
        
        # Load data
        self.data = self.load_data()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create UI
        self.create_sidebar(main_layout)
        self.create_main_area(main_layout)
        
        # Apply styles
        self.setStyleSheet(STYLE)
        
        # Show home
        self.show_home()
        
        # Start reminder timer
        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(60000)  # Check every minute
        self.sent_reminders = {"morning": False, "afternoon": False, "evening": False, "date": self.get_today()}
    
    def load_data(self):
        def ensure_defaults(data):
            if "notes" not in data:
                data["notes"] = []
            if "calendar" not in data:
                data["calendar"] = {}
            else:
                # Normalize older calendar entries (list of strings) to dicts with time
                normalized = {}
                for date_key, items in data.get("calendar", {}).items():
                    if isinstance(items, list):
                        new_items = []
                        for item in items:
                            if isinstance(item, dict):
                                new_items.append({
                                    "title": item.get("title", ""),
                                    "time": item.get("time", "00:00")
                                })
                            else:
                                new_items.append({"title": str(item), "time": "00:00"})
                        normalized[date_key] = new_items
                if normalized:
                    data["calendar"] = normalized
            if "reminders" not in data:
                data["reminders"] = {
                    "enabled": True,
                    "times": {
                        "morning": "09:00",
                        "afternoon": "14:00",
                        "evening": "20:00"
                    }
                }
            return data

        # Prefer local data, fall back to iCloud if local missing
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return ensure_defaults(data)
        if ICLOUD_FILE.exists():
            with open(ICLOUD_FILE, 'r') as f:
                data = json.load(f)
                return ensure_defaults(data)
        return {
            "activities": {},
            "badges": [],
            "notes": [],
            "calendar": {},
            "reminders": {
                "enabled": True,
                "times": {
                    "morning": "09:00",
                    "afternoon": "14:00",
                    "evening": "20:00"
                }
            }
        }
    
    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
        # iCloud backup (best-effort)
        try:
            ICLOUD_DIR.mkdir(parents=True, exist_ok=True)
            with open(ICLOUD_FILE, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass
    
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
    
    def create_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 25, 15, 25)
        sidebar_layout.setSpacing(8)
        
        # Logo
        logo = QLabel("🔥")
        logo.setFont(QFont("Arial", 36))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo)
        
        title = QLabel("Consistency")
        title.setFont(QFont("SF Pro Display", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title)
        
        subtitle = QLabel("Tracker")
        subtitle.setFont(QFont("SF Pro Display", 12))
        subtitle.setStyleSheet("color: #8888aa;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(subtitle)
        
        sidebar_layout.addSpacing(30)
        
        # Navigation
        self.nav_buttons = {}
        nav_items = [
            ("🏠  Home", self.show_home),
            ("➕  Add Activity", self.show_add_activity),
            ("📝  Notes", self.show_notes),
            ("📅  Calendar", self.show_calendar),
            ("🏆  Badges", self.show_badges),
            ("📊  Statistics", self.show_stats),
            ("⚙️  Settings", self.show_settings),
        ]
        
        for text, callback in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("nav")
            btn.setCheckable(True)
            btn.setFont(QFont("SF Pro Display", 13))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)
            self.nav_buttons[text.split("  ")[1]] = btn
        
        sidebar_layout.addStretch()
        
        # Streak display
        streak_frame = QFrame()
        streak_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a5a;
                border-radius: 15px;
                padding: 10px;
            }
        """)
        streak_layout = QVBoxLayout(streak_frame)
        streak_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.streak_label = QLabel("🔥 0")
        self.streak_label.setFont(QFont("SF Pro Display", 24, QFont.Weight.Bold))
        self.streak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        streak_layout.addWidget(self.streak_label)
        
        streak_subtitle = QLabel("Best Streak")
        streak_subtitle.setFont(QFont("SF Pro Display", 11))
        streak_subtitle.setStyleSheet("color: #8888aa;")
        streak_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        streak_layout.addWidget(streak_subtitle)
        
        sidebar_layout.addWidget(streak_frame)
        
        parent_layout.addWidget(sidebar)
    
    def create_main_area(self, parent_layout):
        main = QFrame()
        main.setStyleSheet("background-color: #0f0f1a;")
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 20)
        
        self.header_title = QLabel("Dashboard")
        self.header_title.setFont(QFont("SF Pro Display", 26, QFont.Weight.Bold))
        header_layout.addWidget(self.header_title)
        
        date_label = QLabel(datetime.now().strftime("%A, %B %d, %Y"))
        date_label.setFont(QFont("SF Pro Display", 13))
        date_label.setStyleSheet("color: #8888aa;")
        header_layout.addWidget(date_label)
        
        main_layout.addWidget(header)
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 10, 0)
        self.content_layout.setSpacing(12)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.content)
        main_layout.addWidget(scroll)
        
        parent_layout.addWidget(main)
    
    def clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def update_streak_display(self):
        max_streak = 0
        for info in self.data.get("activities", {}).values():
            streak = self.get_streak(info.get("dates", []))
            max_streak = max(max_streak, streak)
        self.streak_label.setText(f"🔥 {max_streak}")
    
    def set_active_nav(self, name):
        for btn_name, btn in self.nav_buttons.items():
            btn.setChecked(btn_name == name)
    
    # ==================== HOME ====================
    def show_home(self):
        self.clear_content()
        self.set_active_nav("Home")
        self.header_title.setText("Dashboard")
        self.update_streak_display()
        
        activities = self.data.get("activities", {})
        
        if not activities:
            self.show_empty_state()
            return
        
        for name, info in activities.items():
            self.create_activity_card(name, info)
    
    def show_empty_state(self):
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet("""
            QFrame#card {
                background-color: #1e1e3f;
                border-radius: 20px;
                padding: 40px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        emoji = QLabel("🚀")
        emoji.setFont(QFont("Arial", 50))
        emoji.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(emoji)
        
        title = QLabel("Welcome to Consistency Tracker!")
        title.setFont(QFont("SF Pro Display", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Add your first activity to start building streaks")
        subtitle.setFont(QFont("SF Pro Display", 13))
        subtitle.setStyleSheet("color: #8888aa;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        btn = QPushButton("➕  Add Activity")
        btn.setObjectName("primary")
        btn.setFixedSize(180, 50)
        btn.setFont(QFont("SF Pro Display", 14, QFont.Weight.Bold))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self.show_add_activity)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.content_layout.addWidget(card)
    
    def create_activity_card(self, name, info):
        dates = info.get("dates", [])
        streak = self.get_streak(dates)
        longest = info.get("longest", 0)
        total = len(dates)
        checked_today = self.get_today() in dates
        color = info.get("color", "#e94560")
        sessions = info.get("sessions", [])
        
        # Calculate total time
        total_minutes = sum(s.get("minutes", 0) for s in sessions)
        total_hours = total_minutes // 60
        remaining_mins = total_minutes % 60
        time_str = f"{total_hours}h {remaining_mins}m" if total_hours > 0 else f"{remaining_mins}m"
        
        # Get today's session info
        today_session = next((s for s in sessions if s.get("date") == self.get_today()), None)
        
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1e1e3f;
                border-radius: 15px;
                border-left: 5px solid {color};
            }}
        """)
        card.setFixedHeight(120)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 12, 15, 12)
        
        # Info section
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        
        # Title row
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel(name)
        title.setFont(QFont("SF Pro Display", 16, QFont.Weight.Bold))
        title_layout.addWidget(title)
        
        # Status
        if checked_today:
            status = QLabel("✓ Done")
            status.setStyleSheet("color: #00bf63; font-weight: bold;")
        elif streak > 0:
            status = QLabel("⚠ At Risk")
            status.setStyleSheet("color: #ff9f1c; font-weight: bold;")
        else:
            status = QLabel("○ Start")
            status.setStyleSheet("color: #8888aa;")
        status.setFont(QFont("SF Pro Display", 12))
        title_layout.addWidget(status)
        title_layout.addStretch()
        
        info_layout.addWidget(title_widget)
        
        # Stats row
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(15)
        
        fire = "🔥" * min(streak // 7 + (1 if streak > 0 else 0), 5)
        streak_label = QLabel(f"🔥 {streak} days {fire}")
        streak_label.setFont(QFont("SF Pro Display", 12, QFont.Weight.Bold))
        streak_label.setStyleSheet(f"color: {'#ff6b35' if streak > 0 else '#8888aa'};")
        stats_layout.addWidget(streak_label)
        
        best_label = QLabel(f"🏆 {longest}")
        best_label.setFont(QFont("SF Pro Display", 11))
        best_label.setStyleSheet("color: #8888aa;")
        best_label.setToolTip("Best streak")
        stats_layout.addWidget(best_label)
        
        time_label = QLabel(f"⏱ {time_str}")
        time_label.setFont(QFont("SF Pro Display", 11))
        time_label.setStyleSheet("color: #4cc9f0;")
        time_label.setToolTip("Total time")
        stats_layout.addWidget(time_label)
        
        total_label = QLabel(f"📅 {total}")
        total_label.setFont(QFont("SF Pro Display", 11))
        total_label.setStyleSheet("color: #8888aa;")
        total_label.setToolTip("Total days")
        stats_layout.addWidget(total_label)
        
        stats_layout.addStretch()
        info_layout.addWidget(stats_widget)
        
        # Today's session note (if exists)
        if today_session and today_session.get("note"):
            note_preview = today_session.get("note", "")[:50]
            if len(today_session.get("note", "")) > 50:
                note_preview += "..."
            note_label = QLabel(f"📝 {note_preview}")
            note_label.setFont(QFont("SF Pro Display", 10))
            note_label.setStyleSheet("color: #9b5de5;")
            info_layout.addWidget(note_label)
        elif today_session:
            mins = today_session.get("minutes", 0)
            today_time = f"{mins // 60}h {mins % 60}m" if mins >= 60 else f"{mins}m"
            time_today = QLabel(f"✅ Today: {today_time}")
            time_today.setFont(QFont("SF Pro Display", 10))
            time_today.setStyleSheet("color: #00bf63;")
            info_layout.addWidget(time_today)
        
        layout.addWidget(info_widget, stretch=1)
        
        # History button
        history_btn = QPushButton("📋")
        history_btn.setFixedSize(40, 40)
        history_btn.setToolTip("View History")
        history_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        history_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a5a;
                border: none;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3a3a6a;
            }
        """)
        history_btn.clicked.connect(lambda: self.show_activity_history(name))
        layout.addWidget(history_btn)
        
        # Check-in button
        if checked_today:
            btn = QPushButton("✓")
            btn.setObjectName("done")
            btn.setToolTip("Already checked in!")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda: self.show_checkin_dialog(name, edit_mode=True))
        else:
            btn = QPushButton("+")
            btn.setObjectName("checkin")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda: self.show_checkin_dialog(name))
        
        btn.setFixedSize(50, 50)
        btn.setFont(QFont("SF Pro Display", 20, QFont.Weight.Bold))
        layout.addWidget(btn)
        
        # Delete button
        del_btn = QPushButton("×")
        del_btn.setFixedSize(30, 30)
        del_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666688;
                font-size: 18px;
            }
            QPushButton:hover {
                color: #e94560;
            }
        """)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.clicked.connect(lambda: self.delete_activity(name))
        layout.addWidget(del_btn)
        
        self.content_layout.addWidget(card)
    
    def show_checkin_dialog(self, name, edit_mode=False):
        """Show check-in dialog with time tracking and notes"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Check In: {name}")
        dialog.setFixedSize(790, 720)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
            }
            QLabel {
                color: white;
                background-color: transparent;
            }
            QWidget {
                color: white;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel(f"🎯 {name}")
        header.setFont(QFont("SF Pro Display", 20, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        today = self.get_today()
        activity = self.data["activities"].get(name, {})
        sessions = activity.get("sessions", [])
        existing_session = next((s for s in sessions if s.get("date") == today), None)
        
        # Time tracking section
        time_frame = QFrame()
        time_frame.setStyleSheet("background-color: #1e1e3f; border-radius: 15px;")
        time_layout = QVBoxLayout(time_frame)
        time_layout.setContentsMargins(15, 15, 15, 15)
        time_layout.setSpacing(10)
        
        time_label = QLabel("⏱️ Time Spent")
        time_label.setFont(QFont("SF Pro Display", 14, QFont.Weight.Bold))
        time_layout.addWidget(time_label)
        
        # Hours and minutes row
        time_input_widget = QWidget()
        time_input_widget.setStyleSheet("background-color: transparent;")
        time_input_layout = QHBoxLayout(time_input_widget)
        time_input_layout.setContentsMargins(0, 5, 0, 0)
        time_input_layout.setSpacing(10)
        
        duration_label = QLabel("Duration:")
        duration_label.setFont(QFont("SF Pro Display", 13))
        time_input_layout.addWidget(duration_label)

        default_minutes = existing_session.get("minutes", 30) if existing_session else 30
        default_hours = max(0, min(23, default_minutes // 60))
        default_mins = max(0, min(59, default_minutes % 60))

        time_input = QLineEdit()
        time_input.setInputMask("99:99")
        time_input.setFixedSize(130, 50)
        time_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_input.setFont(QFont("Menlo", 14, QFont.Weight.Bold))
        time_input.setText(f"{default_hours}:{default_mins:02d}")
        time_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a5a;
                border: 2px solid #3a3a6a;
                border-radius: 8px;
                color: white;
                padding: 6px 10px;
            }
            QLineEdit:focus { border-color: #e94560; }
        """)
        time_input_layout.addWidget(time_input)
        time_input_layout.addStretch()
        time_layout.addWidget(time_input_widget)
        
        # Quick time buttons
        quick_widget = QWidget()
        quick_widget.setStyleSheet("background-color: transparent;")
        quick_layout = QHBoxLayout(quick_widget)
        quick_layout.setContentsMargins(0, 5, 0, 0)
        quick_layout.setSpacing(8)
        
        quick_times = [(15, "15m"), (30, "30m"), (60, "1h"), (90, "1.5h"), (120, "2h")]
        for mins, label in quick_times:
            btn = QPushButton(label)
            btn.setFixedSize(55, 32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2a2a5a;
                    border: 1px solid #3a3a6a;
                    border-radius: 8px;
                    color: white;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #e94560;
                    border-color: #e94560;
                }
            """)
            btn.clicked.connect(lambda _, m=mins: time_input.setText(f"{m // 60}:{m % 60:02d}"))
            quick_layout.addWidget(btn)
        quick_layout.addStretch()
        time_layout.addWidget(quick_widget)
        
        layout.addWidget(time_frame)
        
        # Notes section
        notes_frame = QFrame()
        notes_frame.setStyleSheet("background-color: #1e1e3f; border-radius: 15px;")
        notes_layout = QVBoxLayout(notes_frame)
        notes_layout.setContentsMargins(15, 15, 15, 15)
        notes_layout.setSpacing(8)
        
        notes_label = QLabel("📝 Session Notes")
        notes_label.setFont(QFont("SF Pro Display", 14, QFont.Weight.Bold))
        notes_layout.addWidget(notes_label)
        
        notes_input = QTextEdit()
        notes_input.setPlaceholderText("What did you work on?")
        notes_input.setFixedHeight(80)
        notes_input.setText(existing_session.get("note", "") if existing_session else "")
        notes_input.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a5a;
                border: 2px solid #3a3a6a;
                border-radius: 10px;
                padding: 10px;
                color: white;
                font-size: 13px;
            }
            QTextEdit:focus { border-color: #e94560; }
        """)
        notes_layout.addWidget(notes_input)
        
        layout.addWidget(notes_frame)
        
        # Mood section
        mood_frame = QFrame()
        mood_frame.setStyleSheet("background-color: #1e1e3f; border-radius: 15px;")
        mood_layout = QVBoxLayout(mood_frame)
        mood_layout.setContentsMargins(15, 15, 15, 15)
        mood_layout.setSpacing(8)
        
        mood_label = QLabel("😊 How did it go?")
        mood_label.setFont(QFont("SF Pro Display", 14, QFont.Weight.Bold))
        mood_layout.addWidget(mood_label)
        
        mood_widget = QWidget()
        mood_widget.setStyleSheet("background-color: transparent;")
        mood_btn_layout = QHBoxLayout(mood_widget)
        mood_btn_layout.setContentsMargins(0, 5, 0, 0)
        mood_btn_layout.setSpacing(12)
        
        moods = [("1", "😩"), ("2", "😕"), ("3", "😐"), ("4", "😊"), ("5", "🤩")]
        selected_mood = [existing_session.get("mood", 3) if existing_session else 3]
        mood_buttons = []
        
        for value, emoji in moods:
            btn = QPushButton(emoji)
            btn.setFixedSize(50, 50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Apple Color Emoji", 22))
            btn.setProperty("mood_value", int(value))
            mood_buttons.append(btn)
            mood_btn_layout.addWidget(btn)
        
        def update_mood_buttons():
            for b in mood_buttons:
                val = b.property("mood_value")
                if val == selected_mood[0]:
                    b.setStyleSheet("""
                        QPushButton {
                            background-color: #e94560;
                            border: 2px solid #ff5a75;
                            border-radius: 12px;
                        }
                    """)
                else:
                    b.setStyleSheet("""
                        QPushButton {
                            background-color: #2a2a5a;
                            border: 2px solid #3a3a6a;
                            border-radius: 12px;
                        }
                        QPushButton:hover {
                            background-color: #3a3a6a;
                            border-color: #e94560;
                        }
                    """)
        
        for btn in mood_buttons:
            btn.clicked.connect(lambda checked, b=btn: (
                selected_mood.__setitem__(0, b.property("mood_value")),
                update_mood_buttons()
            ))
        
        update_mood_buttons()
        mood_btn_layout.addStretch()
        mood_layout.addWidget(mood_widget)
        
        layout.addWidget(mood_frame)
        layout.addStretch()
        
        # Buttons
        btn_widget = QWidget()
        btn_widget.setStyleSheet("background-color: transparent;")
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(0, 10, 0, 0)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(100, 45)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a5a;
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #3a3a6a; }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        btn_layout.addStretch()
        
        save_btn = QPushButton("✅ Check In" if not edit_mode else "💾 Update")
        save_btn.setFixedSize(140, 45)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #e94560;
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #ff5a75; }
        """)
        
        def save_checkin():
            raw = time_input.text().strip()
            try:
                parts = raw.split(":")
                hours = int(parts[0]) if parts[0] else 0
                mins = int(parts[1]) if len(parts) > 1 and parts[1] else 0
            except ValueError:
                hours, mins = 0, 30
            total_mins = max(0, hours) * 60 + max(0, mins)
            note = notes_input.toPlainText().strip()
            mood = selected_mood[0]
            self.check_in(name, total_mins, note, mood)
            dialog.accept()
        
        save_btn.clicked.connect(save_checkin)
        btn_layout.addWidget(save_btn)
        
        layout.addWidget(btn_widget)
        
        dialog.exec()
    
    def check_in(self, name, minutes=30, note="", mood=3):
        today = self.get_today()
        if name not in self.data["activities"]:
            return
        
        activity = self.data["activities"][name]
        
        # Add to dates if not already there
        if today not in activity.get("dates", []):
            activity.setdefault("dates", []).append(today)
        
        # Add or update session
        sessions = activity.setdefault("sessions", [])
        existing_idx = next((i for i, s in enumerate(sessions) if s.get("date") == today), None)
        
        session_data = {
            "date": today,
            "minutes": minutes,
            "note": note,
            "mood": mood,
            "time": datetime.now().strftime("%H:%M")
        }
        
        if existing_idx is not None:
            sessions[existing_idx] = session_data
        else:
            sessions.insert(0, session_data)
        
        streak = self.get_streak(activity["dates"])
        if streak > activity.get("longest", 0):
            activity["longest"] = streak
        
        self.save_data()
        self.check_badges(name, streak)
        
        time_str = f"{minutes // 60}h {minutes % 60}m" if minutes >= 60 else f"{minutes}m"
        self.send_notification("✅ Checked In!", f"{name}: 🔥 {streak} days | ⏱ {time_str}")
        self.show_home()
    
    def show_activity_history(self, name):
        """Show activity history dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"History: {name}")
        dialog.setFixedSize(500, 600)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
            }
            QLabel {
                color: white;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel(f"📋 {name} History")
        header.setFont(QFont("SF Pro Display", 18, QFont.Weight.Bold))
        layout.addWidget(header)
        
        activity = self.data["activities"].get(name, {})
        sessions = activity.get("sessions", [])
        
        # Stats summary
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e3f;
                border-radius: 12px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(15, 15, 15, 15)
        
        total_mins = sum(s.get("minutes", 0) for s in sessions)
        avg_mins = total_mins // len(sessions) if sessions else 0
        avg_mood = sum(s.get("mood", 3) for s in sessions) / len(sessions) if sessions else 3
        
        stats = [
            ("⏱", f"{total_mins // 60}h {total_mins % 60}m", "Total Time"),
            ("📅", str(len(sessions)), "Sessions"),
            ("⏳", f"{avg_mins}m", "Avg/Session"),
            ("😊", ['😩', '😕', '😐', '😊', '🤩'][min(int(avg_mood) - 1, 4)], "Avg Mood"),
        ]
        
        for icon, value, label in stats:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            stat_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_layout.setSpacing(2)
            
            val_label = QLabel(f"{icon} {value}")
            val_label.setFont(QFont("SF Pro Display", 14, QFont.Weight.Bold))
            val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_layout.addWidget(val_label)
            
            desc_label = QLabel(label)
            desc_label.setFont(QFont("SF Pro Display", 10))
            desc_label.setStyleSheet("color: #8888aa;")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_layout.addWidget(desc_label)
            
            stats_layout.addWidget(stat_widget)
        
        layout.addWidget(stats_frame)
        
        # Sessions list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        sessions_widget = QWidget()
        sessions_layout = QVBoxLayout(sessions_widget)
        sessions_layout.setContentsMargins(0, 0, 10, 0)
        sessions_layout.setSpacing(10)
        
        if not sessions:
            empty_label = QLabel("No sessions yet. Check in to start tracking!")
            empty_label.setStyleSheet("color: #8888aa;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sessions_layout.addWidget(empty_label)
        else:
            for session in sessions[:50]:  # Show last 50 sessions
                card = QFrame()
                card.setStyleSheet("""
                    QFrame {
                        background-color: #1e1e3f;
                        border-radius: 10px;
                    }
                """)
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(15, 12, 15, 12)
                card_layout.setSpacing(5)
                
                # Top row: date and time
                top_widget = QWidget()
                top_layout = QHBoxLayout(top_widget)
                top_layout.setContentsMargins(0, 0, 0, 0)
                
                date_str = session.get("date", "")
                time_str = session.get("time", "")
                mins = session.get("minutes", 0)
                duration = f"{mins // 60}h {mins % 60}m" if mins >= 60 else f"{mins}m"
                
                date_label = QLabel(f"📅 {date_str}")
                date_label.setFont(QFont("SF Pro Display", 12, QFont.Weight.Bold))
                top_layout.addWidget(date_label)
                
                if time_str:
                    time_label = QLabel(f"🕒 {time_str}")
                    time_label.setFont(QFont("SF Pro Display", 11))
                    time_label.setStyleSheet("color: #8888aa;")
                    top_layout.addWidget(time_label)
                
                top_layout.addStretch()
                
                duration_label = QLabel(f"⏱ {duration}")
                duration_label.setFont(QFont("SF Pro Display", 12, QFont.Weight.Bold))
                duration_label.setStyleSheet("color: #4cc9f0;")
                top_layout.addWidget(duration_label)
                
                mood = session.get("mood", 3)
                mood_emoji = ['😩', '😕', '😐', '😊', '🤩'][min(mood - 1, 4)]
                mood_label = QLabel(mood_emoji)
                mood_label.setFont(QFont("Arial", 16))
                top_layout.addWidget(mood_label)
                
                card_layout.addWidget(top_widget)
                
                # Note if exists
                if session.get("note"):
                    note_label = QLabel(session.get("note"))
                    note_label.setFont(QFont("SF Pro Display", 11))
                    note_label.setStyleSheet("color: #9b5de5;")
                    note_label.setWordWrap(True)
                    card_layout.addWidget(note_label)
                
                sessions_layout.addWidget(card)
        
        sessions_layout.addStretch()
        scroll.setWidget(sessions_widget)
        layout.addWidget(scroll)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(100, 40)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a5a;
                border: none;
                border-radius: 10px;
                color: white;
            }
            QPushButton:hover {
                background-color: #3a3a6a;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dialog.exec()
    
    def check_badges(self, name, streak):
        if streak in BADGES:
            badge_key = f"{name}_{streak}"
            if badge_key not in self.data.get("badges", []):
                self.data.setdefault("badges", []).append(badge_key)
                self.save_data()
                icon, badge_name, _ = BADGES[streak]
                self.send_notification("🏆 Badge Earned!", f"{icon} {badge_name}")
    
    def delete_activity(self, name):
        reply = QMessageBox.question(
            self, "Delete Activity",
            f"Delete '{name}'?\n\nThis will remove all streak data.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if name in self.data.get("activities", {}):
                del self.data["activities"][name]
                self.save_data()
                self.show_home()
    
    # ==================== ADD ACTIVITY ====================
    def show_add_activity(self):
        self.clear_content()
        self.set_active_nav("Add Activity")
        self.header_title.setText("Add Activity")
        
        # Presets label
        label = QLabel("Quick Add Presets")
        label.setFont(QFont("SF Pro Display", 15, QFont.Weight.Bold))
        self.content_layout.addWidget(label)
        
        # Preset grid
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(12)
        
        for i, (icon, name, color) in enumerate(PRESETS):
            full_name = f"{icon} {name}"
            exists = full_name in self.data.get("activities", {})
            
            btn = QPushButton(f"{icon}\n{name}")
            btn.setObjectName("preset")
            btn.setFixedSize(110, 85)
            btn.setFont(QFont("SF Pro Display", 12))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            if exists:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #00bf63;
                        border: 2px solid #00bf63;
                        border-radius: 12px;
                        color: white;
                    }
                """)
                btn.setText(f"{icon}\n✓ Added")
                btn.setEnabled(False)
            else:
                btn.clicked.connect(lambda _, ic=icon, n=name, c=color: self.add_preset(ic, n, c))
            
            grid.addWidget(btn, i // 5, i % 5)
        
        self.content_layout.addWidget(grid_widget)
        
        # Divider
        divider = QFrame()
        divider.setFixedHeight(2)
        divider.setStyleSheet("background-color: #2a2a5a;")
        self.content_layout.addSpacing(20)
        self.content_layout.addWidget(divider)
        self.content_layout.addSpacing(20)
        
        # Custom activity
        label2 = QLabel("Or Create Custom Activity")
        label2.setFont(QFont("SF Pro Display", 15, QFont.Weight.Bold))
        self.content_layout.addWidget(label2)
        
        custom_card = QFrame()
        custom_card.setStyleSheet("""
            QFrame {
                background-color: #1e1e3f;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        custom_layout = QVBoxLayout(custom_card)
        
        self.custom_input = QLineEdit()
        self.custom_input.setPlaceholderText("e.g., 🎯 Daily Goal")
        self.custom_input.setFixedHeight(50)
        custom_layout.addWidget(self.custom_input)
        
        add_btn = QPushButton("Add Activity")
        add_btn.setObjectName("primary")
        add_btn.setFixedHeight(50)
        add_btn.setFont(QFont("SF Pro Display", 14, QFont.Weight.Bold))
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_custom)
        custom_layout.addWidget(add_btn)
        
        self.content_layout.addWidget(custom_card)
        self.content_layout.addStretch()
    
    def add_preset(self, icon, name, color):
        full_name = f"{icon} {name}"
        if full_name not in self.data.get("activities", {}):
            self.data.setdefault("activities", {})[full_name] = {
                "dates": [], "longest": 0, "color": color
            }
            self.save_data()
            self.send_notification("✨ Activity Added!", f"{full_name}")
            self.show_add_activity()
    
    def add_custom(self):
        name = self.custom_input.text().strip()
        if name and name not in self.data.get("activities", {}):
            self.data.setdefault("activities", {})[name] = {
                "dates": [], "longest": 0, "color": "#e94560"
            }
            self.save_data()
            self.send_notification("✨ Activity Added!", name)
            self.show_home()
    
    # ==================== BADGES ====================
    def show_badges(self):
        self.clear_content()
        self.set_active_nav("Badges")
        self.header_title.setText("Badges")
        
        earned = self.data.get("badges", [])
        
        if earned:
            label = QLabel(f"🏆 Earned ({len(earned)})")
            label.setFont(QFont("SF Pro Display", 15, QFont.Weight.Bold))
            self.content_layout.addWidget(label)
            
            earned_widget = QWidget()
            earned_grid = QGridLayout(earned_widget)
            earned_grid.setSpacing(12)
            
            col = 0
            for badge_key in earned:
                parts = badge_key.rsplit("_", 1)
                if len(parts) == 2:
                    activity, days = parts
                    days = int(days)
                    if days in BADGES:
                        icon, name, _ = BADGES[days]
                        
                        badge = QFrame()
                        badge.setStyleSheet("""
                            QFrame {
                                background-color: #1e1e3f;
                                border-radius: 15px;
                                padding: 15px;
                            }
                        """)
                        badge.setFixedSize(130, 120)
                        badge_layout = QVBoxLayout(badge)
                        badge_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        
                        icon_lbl = QLabel(icon)
                        icon_lbl.setFont(QFont("Arial", 32))
                        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        badge_layout.addWidget(icon_lbl)
                        
                        name_lbl = QLabel(name)
                        name_lbl.setFont(QFont("SF Pro Display", 11, QFont.Weight.Bold))
                        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        badge_layout.addWidget(name_lbl)
                        
                        earned_grid.addWidget(badge, col // 5, col % 5)
                        col += 1
            
            self.content_layout.addWidget(earned_widget)
            self.content_layout.addSpacing(20)
        
        # All badges
        label2 = QLabel("📋 All Badges")
        label2.setFont(QFont("SF Pro Display", 15, QFont.Weight.Bold))
        self.content_layout.addWidget(label2)
        
        for days, (icon, name, desc) in BADGES.items():
            row = QFrame()
            row.setStyleSheet("""
                QFrame {
                    background-color: #1e1e3f;
                    border-radius: 12px;
                }
            """)
            row.setFixedHeight(70)
            
            row_layout = QHBoxLayout(row)
            
            icon_lbl = QLabel(icon)
            icon_lbl.setFont(QFont("Arial", 26))
            icon_lbl.setFixedWidth(50)
            row_layout.addWidget(icon_lbl)
            
            info = QWidget()
            info_layout = QVBoxLayout(info)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(2)
            
            name_lbl = QLabel(name)
            name_lbl.setFont(QFont("SF Pro Display", 13, QFont.Weight.Bold))
            info_layout.addWidget(name_lbl)
            
            desc_lbl = QLabel(desc)
            desc_lbl.setFont(QFont("SF Pro Display", 11))
            desc_lbl.setStyleSheet("color: #8888aa;")
            info_layout.addWidget(desc_lbl)
            
            row_layout.addWidget(info)
            row_layout.addStretch()
            
            self.content_layout.addWidget(row)
        
        self.content_layout.addStretch()
    
    # ==================== STATS ====================
    def show_stats(self):
        self.clear_content()
        self.set_active_nav("Statistics")
        self.header_title.setText("Statistics")
        
        activities = self.data.get("activities", {})
        
        total_days = sum(len(a.get("dates", [])) for a in activities.values())
        total_activities = len(activities)
        best_streak = max((a.get("longest", 0) for a in activities.values()), default=0)
        active_streaks = sum(1 for a in activities.values() if self.get_streak(a.get("dates", [])) > 0)
        badges_count = len(self.data.get("badges", []))
        
        stats = [
            ("📅", str(total_days), "Total Days"),
            ("📋", str(total_activities), "Activities"),
            ("🔥", str(active_streaks), "Active"),
            ("🏆", str(best_streak), "Best Streak"),
            ("⭐", str(badges_count), "Badges"),
        ]
        
        stats_widget = QWidget()
        stats_grid = QGridLayout(stats_widget)
        stats_grid.setSpacing(15)
        
        for i, (icon, value, label) in enumerate(stats):
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #1e1e3f;
                    border-radius: 15px;
                }
            """)
            card.setFixedHeight(120)
            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            icon_lbl = QLabel(icon)
            icon_lbl.setFont(QFont("Arial", 26))
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(icon_lbl)
            
            val_lbl = QLabel(value)
            val_lbl.setFont(QFont("SF Pro Display", 24, QFont.Weight.Bold))
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(val_lbl)
            
            lbl = QLabel(label)
            lbl.setFont(QFont("SF Pro Display", 11))
            lbl.setStyleSheet("color: #8888aa;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(lbl)
            
            stats_grid.addWidget(card, i // 3, i % 3)
        
        self.content_layout.addWidget(stats_widget)
        
        # Weekly heatmap
        self.content_layout.addSpacing(20)
        label = QLabel("📊 Last 7 Days")
        label.setFont(QFont("SF Pro Display", 15, QFont.Weight.Bold))
        self.content_layout.addWidget(label)
        
        today = datetime.now().date()
        
        for name, info in activities.items():
            row = QFrame()
            row.setStyleSheet("""
                QFrame {
                    background-color: #1e1e3f;
                    border-radius: 12px;
                }
            """)
            row.setFixedHeight(60)
            
            row_layout = QHBoxLayout(row)
            
            name_lbl = QLabel(name[:18])
            name_lbl.setFont(QFont("SF Pro Display", 12))
            name_lbl.setFixedWidth(160)
            row_layout.addWidget(name_lbl)
            
            dates = info.get("dates", [])
            for i in range(6, -1, -1):
                day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
                is_active = day in dates
                
                box = QFrame()
                box.setFixedSize(32, 32)
                box.setStyleSheet(f"""
                    QFrame {{
                        background-color: {'#00bf63' if is_active else '#2a2a5a'};
                        border-radius: 6px;
                    }}
                """)
                row_layout.addWidget(box)
            
            row_layout.addStretch()
            self.content_layout.addWidget(row)
        
        self.content_layout.addStretch()
    
    # ==================== SETTINGS ====================
    def show_settings(self):
        self.clear_content()
        self.set_active_nav("Settings")
        self.header_title.setText("Settings")
        
        # Notifications
        notif_card = QFrame()
        notif_card.setStyleSheet("""
            QFrame {
                background-color: #1e1e3f;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        notif_layout = QVBoxLayout(notif_card)
        
        title = QLabel("🔔 Notifications")
        title.setFont(QFont("SF Pro Display", 15, QFont.Weight.Bold))
        notif_layout.addWidget(title)
        
        test_btn = QPushButton("Send Test Notification")
        test_btn.setObjectName("primary")
        test_btn.setFixedHeight(45)
        test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        test_btn.clicked.connect(lambda: self.send_notification("🔔 Test", "Notifications work!"))
        notif_layout.addWidget(test_btn)
        
        self.content_layout.addWidget(notif_card)
        
        # Reminders
        remind_card = QFrame()
        remind_card.setStyleSheet("""
            QFrame {
                background-color: #1e1e3f;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        remind_layout = QVBoxLayout(remind_card)
        
        title2 = QLabel("⏰ Daily Reminders")
        title2.setFont(QFont("SF Pro Display", 15, QFont.Weight.Bold))
        remind_layout.addWidget(title2)
        
        reminder_data = self.data.get("reminders", {
            "enabled": True,
            "times": {"morning": "09:00", "afternoon": "14:00", "evening": "20:00"}
        })
        times_data = reminder_data.get("times", {})
        
        enable_row = QHBoxLayout()
        enable_label = QLabel("Enable reminders")
        enable_label.setFont(QFont("SF Pro Display", 13))
        enable_row.addWidget(enable_label)
        enable_row.addStretch()
        enable_toggle = QCheckBox()
        enable_toggle.setChecked(reminder_data.get("enabled", True))
        enable_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        enable_row.addWidget(enable_toggle)
        remind_layout.addLayout(enable_row)
        
        def build_time_row(label_text, key):
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setFont(QFont("SF Pro Display", 13))
            row.addWidget(label)
            row.addStretch()
            inp = QLineEdit()
            inp.setInputMask("99:99")
            inp.setFixedSize(90, 36)
            inp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            inp.setFont(QFont("Menlo", 12, QFont.Weight.Bold))
            inp.setText(times_data.get(key, "09:00" if key == "morning" else "14:00" if key == "afternoon" else "20:00"))
            inp.setStyleSheet("""
                QLineEdit {
                    background-color: #2a2a5a;
                    border: 2px solid #3a3a6a;
                    border-radius: 8px;
                    color: white;
                    padding: 4px 8px;
                }
                QLineEdit:focus { border-color: #e94560; }
            """)
            row.addWidget(inp)
            return row, inp
        
        morning_row, morning_input = build_time_row("Morning", "morning")
        remind_layout.addLayout(morning_row)
        afternoon_row, afternoon_input = build_time_row("Afternoon", "afternoon")
        remind_layout.addLayout(afternoon_row)
        evening_row, evening_input = build_time_row("Evening", "evening")
        remind_layout.addLayout(evening_row)
        
        save_reminders = QPushButton("Save Reminder Settings")
        save_reminders.setObjectName("primary")
        save_reminders.setFixedHeight(42)
        save_reminders.setCursor(Qt.CursorShape.PointingHandCursor)
        
        def _save_reminders():
            self.data.setdefault("reminders", {})
            self.data["reminders"]["enabled"] = enable_toggle.isChecked()
            self.data["reminders"]["times"] = {
                "morning": morning_input.text() or "09:00",
                "afternoon": afternoon_input.text() or "14:00",
                "evening": evening_input.text() or "20:00"
            }
            self.save_data()
            self.sent_reminders = {"morning": False, "afternoon": False, "evening": False, "date": self.get_today()}
            self.send_notification("⏰ Reminders Updated", "Your reminder schedule has been saved.")
        
        save_reminders.clicked.connect(_save_reminders)
        remind_layout.addSpacing(8)
        remind_layout.addWidget(save_reminders)
        
        self.content_layout.addWidget(remind_card)
        
        # Data
        data_card = QFrame()
        data_card.setStyleSheet("""
            QFrame {
                background-color: #1e1e3f;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        data_layout = QVBoxLayout(data_card)
        
        title3 = QLabel("📁 Data")
        title3.setFont(QFont("SF Pro Display", 15, QFont.Weight.Bold))
        data_layout.addWidget(title3)
        
        open_btn = QPushButton("Open Data Folder")
        open_btn.setObjectName("primary")
        open_btn.setStyleSheet("background-color: #2a2a5a;")
        open_btn.setFixedHeight(45)
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.clicked.connect(lambda: subprocess.run(["open", str(DATA_DIR)]))
        data_layout.addWidget(open_btn)
        
        self.content_layout.addWidget(data_card)
        
        # About
        about = QLabel("Consistency Tracker v1.0\nBuild streaks. Stay consistent.")
        about.setFont(QFont("SF Pro Display", 12))
        about.setStyleSheet("color: #8888aa;")
        about.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addSpacing(30)
        self.content_layout.addWidget(about)
        
        self.content_layout.addStretch()

    # ==================== CALENDAR ====================
    def show_calendar(self):
        self.clear_content()
        self.set_active_nav("Calendar")
        self.header_title.setText("Calendar")

        calendar_card = QFrame()
        calendar_card.setStyleSheet("""
            QFrame {
                background-color: #1e1e3f;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        calendar_layout = QVBoxLayout(calendar_card)
        calendar_layout.setSpacing(12)

        title = QLabel("📅 Plan Ahead")
        title.setFont(QFont("SF Pro Display", 16, QFont.Weight.Bold))
        calendar_layout.addWidget(title)

        calendar = QCalendarWidget()
        calendar.setGridVisible(True)
        calendar.setStyleSheet("""
            QCalendarWidget QWidget {
                background-color: #1e1e3f;
                color: white;
            }
            QCalendarWidget QToolButton {
                color: white;
                background-color: transparent;
            }
            QCalendarWidget QAbstractItemView {
                background-color: #2a2a5a;
                selection-background-color: #e94560;
                selection-color: white;
                border-radius: 8px;
            }
        """)
        calendar_layout.addWidget(calendar)

        list_title = QLabel("Planned items (all dates)")
        list_title.setFont(QFont("SF Pro Display", 14, QFont.Weight.Bold))
        calendar_layout.addWidget(list_title)

        items_list = QListWidget()
        items_list.setStyleSheet("""
            QListWidget {
                background-color: #2a2a5a;
                border: 2px solid #3a3a6a;
                border-radius: 10px;
                padding: 8px;
                color: white;
            }
            QListWidget::item:selected {
                background-color: #e94560;
            }
        """)
        calendar_layout.addWidget(items_list)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("Add Item")
        add_btn.setObjectName("primary")
        add_btn.setFixedHeight(40)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(add_btn)

        edit_btn = QPushButton("Edit Selected")
        edit_btn.setFixedHeight(40)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet("background-color: #2a2a5a;")
        btn_row.addWidget(edit_btn)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.setFixedHeight(40)
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setStyleSheet("background-color: #2a2a5a;")
        btn_row.addWidget(remove_btn)

        btn_row.addStretch()
        calendar_layout.addLayout(btn_row)

        row_map = []

        def selected_date_key():
            return calendar.selectedDate().toString("yyyy-MM-dd")

        def normalize_time(value):
            try:
                parts = value.strip().split(":")
                if len(parts) != 2:
                    return "00:00"
                hours = max(0, min(23, int(parts[0])))
                mins = max(0, min(59, int(parts[1])))
                return f"{hours:02d}:{mins:02d}"
            except ValueError:
                return "00:00"

        def refresh_list():
            items_list.clear()
            row_map.clear()
            calendar_data = self.data.get("calendar", {})
            for date_key in sorted(calendar_data.keys()):
                items = calendar_data.get(date_key, [])
                sorted_indices = sorted(range(len(items)), key=lambda i: items[i].get("time", "00:00"))
                for idx in sorted_indices:
                    item = items[idx]
                    title = item.get("title", "")
                    time_val = item.get("time", "00:00")
                    items_list.addItem(f"{date_key} · {time_val} — {title}")
                    row_map.append((date_key, idx))

        def add_item():
            date_key = selected_date_key()
            text, ok = QInputDialog.getText(self, "Add planned item", "What do you want to do?")
            if not (ok and text.strip()):
                return
            time_text, ok_time = QInputDialog.getText(self, "Add time", "Time (HH:MM)")
            if not ok_time:
                return
            time_val = normalize_time(time_text or "00:00")
            self.data.setdefault("calendar", {}).setdefault(date_key, []).append({
                "title": text.strip(),
                "time": time_val
            })
            self.save_data()
            refresh_list()

        def remove_item():
            selected = items_list.currentRow()
            if selected < 0 or selected >= len(row_map):
                return
            date_key, idx = row_map[selected]
            items = self.data.get("calendar", {}).get(date_key, [])
            if 0 <= idx < len(items):
                items.pop(idx)
                if items:
                    self.data["calendar"][date_key] = items
                else:
                    self.data["calendar"].pop(date_key, None)
                self.save_data()
                refresh_list()

        def edit_item():
            selected = items_list.currentRow()
            if selected < 0 or selected >= len(row_map):
                return
            date_key, idx = row_map[selected]
            items = self.data.get("calendar", {}).get(date_key, [])
            if not (0 <= idx < len(items)):
                return
            item = items[idx]
            current_title = item.get("title", "")
            current_time = item.get("time", "00:00")
            text, ok = QInputDialog.getText(self, "Edit planned item", "Update item", text=current_title)
            if not (ok and text.strip()):
                return
            time_text, ok_time = QInputDialog.getText(self, "Edit time", "Time (HH:MM)", text=current_time)
            if not ok_time:
                return
            item["title"] = text.strip()
            item["time"] = normalize_time(time_text or current_time)
            self.save_data()
            refresh_list()

        calendar.selectionChanged.connect(refresh_list)
        add_btn.clicked.connect(add_item)
        edit_btn.clicked.connect(edit_item)
        remove_btn.clicked.connect(remove_item)

        refresh_list()

        self.content_layout.addWidget(calendar_card)
        self.content_layout.addStretch()
    
    # ==================== NOTES ====================
    def show_notes(self):
        self.clear_content()
        self.set_active_nav("Notes")
        self.header_title.setText("Notes")
        
        # Main container with splitter
        main_container = QFrame()
        main_container.setStyleSheet("background-color: transparent;")
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)
        
        # Left panel - Notes list
        left_panel = QFrame()
        left_panel.setFixedWidth(280)
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #1e1e3f;
                border-radius: 15px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(10)
        
        # New note button
        new_btn = QPushButton("➕ New Note")
        new_btn.setObjectName("primary")
        new_btn.setFixedHeight(45)
        new_btn.setFont(QFont("SF Pro Display", 13, QFont.Weight.Bold))
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.clicked.connect(self.create_new_note)
        left_layout.addWidget(new_btn)
        
        # Notes list
        self.notes_list = QListWidget()
        self.notes_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background-color: #2a2a5a;
                border-radius: 10px;
                padding: 12px;
                margin-bottom: 8px;
                color: white;
            }
            QListWidget::item:selected {
                background-color: #e94560;
            }
            QListWidget::item:hover:!selected {
                background-color: #3a3a6a;
            }
        """)
        self.notes_list.currentRowChanged.connect(self.load_selected_note)
        left_layout.addWidget(self.notes_list)
        
        main_layout.addWidget(left_panel)
        
        # Right panel - Editor
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #1e1e3f;
                border-radius: 15px;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)
        
        # Note title input
        self.note_title_input = QLineEdit()
        self.note_title_input.setPlaceholderText("Note title...")
        self.note_title_input.setFixedHeight(50)
        self.note_title_input.setFont(QFont("SF Pro Display", 16, QFont.Weight.Bold))
        self.note_title_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a5a;
                border: 2px solid #3a3a6a;
                border-radius: 10px;
                padding: 10px 15px;
                font-size: 16px;
            }
            QLineEdit:focus {
                border-color: #e94560;
            }
        """)
        right_layout.addWidget(self.note_title_input)
        
        # Formatting toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #2a2a5a; border-radius: 10px;")
        toolbar.setFixedHeight(50)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        toolbar_layout.setSpacing(5)
        
        # Format buttons
        format_buttons = [
            ("B", self.toggle_bold, "Bold"),
            ("I", self.toggle_italic, "Italic"),
            ("U", self.toggle_underline, "Underline"),
            ("S", self.toggle_strikethrough, "Strikethrough"),
        ]
        
        for text, callback, tooltip in format_buttons:
            btn = QPushButton(text)
            btn.setFixedSize(35, 35)
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if text == "B":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a6a;
                        border: none;
                        border-radius: 8px;
                        color: white;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton:hover { background-color: #4a4a7a; }
                    QPushButton:pressed { background-color: #e94560; }
                """)
            elif text == "I":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a6a;
                        border: none;
                        border-radius: 8px;
                        color: white;
                        font-style: italic;
                        font-size: 14px;
                    }
                    QPushButton:hover { background-color: #4a4a7a; }
                    QPushButton:pressed { background-color: #e94560; }
                """)
            elif text == "U":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a6a;
                        border: none;
                        border-radius: 8px;
                        color: white;
                        text-decoration: underline;
                        font-size: 14px;
                    }
                    QPushButton:hover { background-color: #4a4a7a; }
                    QPushButton:pressed { background-color: #e94560; }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a6a;
                        border: none;
                        border-radius: 8px;
                        color: white;
                        font-size: 14px;
                    }
                    QPushButton:hover { background-color: #4a4a7a; }
                    QPushButton:pressed { background-color: #e94560; }
                """)
            btn.clicked.connect(callback)
            toolbar_layout.addWidget(btn)
        
        # Separator
        sep = QFrame()
        sep.setFixedWidth(2)
        sep.setStyleSheet("background-color: #4a4a7a;")
        toolbar_layout.addWidget(sep)
        
        # Heading dropdown
        self.heading_combo = QComboBox()
        self.heading_combo.addItems(["Normal", "H1", "H2", "H3"])
        self.heading_combo.setFixedSize(80, 35)
        self.heading_combo.setStyleSheet("""
            QComboBox {
                background-color: #3a3a6a;
                border: none;
                border-radius: 8px;
                padding: 5px 10px;
                color: white;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a5a;
                border: 1px solid #3a3a6a;
                selection-background-color: #e94560;
                color: white;
            }
        """)
        self.heading_combo.currentTextChanged.connect(self.apply_heading)
        toolbar_layout.addWidget(self.heading_combo)
        
        # Separator
        sep2 = QFrame()
        sep2.setFixedWidth(2)
        sep2.setStyleSheet("background-color: #4a4a7a;")
        toolbar_layout.addWidget(sep2)
        
        # Color buttons
        colors = [
            ("#ffffff", "White"),
            ("#e94560", "Red"),
            ("#00bf63", "Green"),
            ("#4361ee", "Blue"),
            ("#ffd166", "Yellow"),
            ("#9b5de5", "Purple"),
            ("#4cc9f0", "Cyan"),
            ("#ff6b35", "Orange"),
        ]
        
        for color, name in colors:
            btn = QPushButton()
            btn.setFixedSize(25, 25)
            btn.setToolTip(name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 2px solid #4a4a7a;
                    border-radius: 12px;
                }}
                QPushButton:hover {{
                    border-color: white;
                }}
            """)
            btn.clicked.connect(lambda checked, c=color: self.set_text_color(c))
            toolbar_layout.addWidget(btn)
        
        # Custom color picker
        color_picker_btn = QPushButton("🎨")
        color_picker_btn.setFixedSize(35, 35)
        color_picker_btn.setToolTip("Custom Color")
        color_picker_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        color_picker_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a6a;
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover { background-color: #4a4a7a; }
        """)
        color_picker_btn.clicked.connect(self.pick_custom_color)
        toolbar_layout.addWidget(color_picker_btn)
        
        toolbar_layout.addStretch()
        
        # List buttons
        bullet_btn = QPushButton("•")
        bullet_btn.setFixedSize(35, 35)
        bullet_btn.setToolTip("Bullet List")
        bullet_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bullet_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a6a;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #4a4a7a; }
        """)
        bullet_btn.clicked.connect(self.insert_bullet_list)
        toolbar_layout.addWidget(bullet_btn)
        
        num_btn = QPushButton("1.")
        num_btn.setFixedSize(35, 35)
        num_btn.setToolTip("Numbered List")
        num_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        num_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a6a;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #4a4a7a; }
        """)
        num_btn.clicked.connect(self.insert_numbered_list)
        toolbar_layout.addWidget(num_btn)
        
        right_layout.addWidget(toolbar)
        
        # Text editor
        self.note_editor = QTextEdit()
        self.note_editor.setPlaceholderText("Start writing your note...")
        self.note_editor.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a5a;
                border: 2px solid #3a3a6a;
                border-radius: 10px;
                padding: 15px;
                font-size: 14px;
                color: white;
                selection-background-color: #e94560;
            }
            QTextEdit:focus {
                border-color: #e94560;
            }
        """)
        self.note_editor.setFont(QFont("SF Pro Display", 14))
        right_layout.addWidget(self.note_editor)
        
        # Action buttons
        action_bar = QFrame()
        action_bar.setStyleSheet("background-color: transparent;")
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(10)
        
        # Note color selector
        note_color_label = QLabel("Note Color:")
        note_color_label.setFont(QFont("SF Pro Display", 12))
        note_color_label.setStyleSheet("color: #8888aa;")
        action_layout.addWidget(note_color_label)
        
        note_colors = [
            ("#e94560", "Red"),
            ("#4361ee", "Blue"),
            ("#00bf63", "Green"),
            ("#ffd166", "Yellow"),
            ("#9b5de5", "Purple"),
            ("#4cc9f0", "Cyan"),
        ]
        
        self.selected_note_color = "#e94560"
        self.note_color_buttons = []
        
        for color, name in note_colors:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setToolTip(name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("color", color)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 3px solid transparent;
                    border-radius: 15px;
                }}
                QPushButton:hover {{
                    border-color: white;
                }}
            """)
            btn.clicked.connect(lambda checked, c=color, b=btn: self.select_note_color(c, b))
            action_layout.addWidget(btn)
            self.note_color_buttons.append(btn)
        
        action_layout.addStretch()
        
        # Save button
        save_btn = QPushButton("💾 Save Note")
        save_btn.setObjectName("primary")
        save_btn.setFixedSize(140, 45)
        save_btn.setFont(QFont("SF Pro Display", 13, QFont.Weight.Bold))
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.save_current_note)
        action_layout.addWidget(save_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setFixedSize(100, 45)
        delete_btn.setFont(QFont("SF Pro Display", 13))
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a5a;
                border: 2px solid #3a3a6a;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #ff4757;
                border-color: #ff4757;
            }
        """)
        delete_btn.clicked.connect(self.delete_current_note)
        action_layout.addWidget(delete_btn)
        
        right_layout.addWidget(action_bar)
        
        main_layout.addWidget(right_panel)
        
        self.content_layout.addWidget(main_container)
        
        # Track current note
        self.current_note_index = -1
        
        # Load notes list
        self.refresh_notes_list()
    
    def refresh_notes_list(self):
        self.notes_list.clear()
        notes = self.data.get("notes", [])
        
        for i, note in enumerate(notes):
            title = note.get("title", "Untitled")
            color = note.get("color", "#e94560")
            date = note.get("updated", note.get("created", ""))
            
            item = QListWidgetItem(f"{title}\n📅 {date[:10] if date else 'No date'}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.notes_list.addItem(item)
    
    def create_new_note(self):
        self.current_note_index = -1
        self.note_title_input.clear()
        self.note_editor.clear()
        self.selected_note_color = "#e94560"
        self.note_title_input.setFocus()
    
    def load_selected_note(self, row):
        if row < 0:
            return
        
        notes = self.data.get("notes", [])
        if row >= len(notes):
            return
        
        note = notes[row]
        self.current_note_index = row
        self.note_title_input.setText(note.get("title", ""))
        self.note_editor.setHtml(note.get("content", ""))
        self.selected_note_color = note.get("color", "#e94560")
        
        # Update color button selection
        for btn in self.note_color_buttons:
            if btn.property("color") == self.selected_note_color:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.selected_note_color};
                        border: 3px solid white;
                        border-radius: 15px;
                    }}
                """)
            else:
                color = btn.property("color")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        border: 3px solid transparent;
                        border-radius: 15px;
                    }}
                    QPushButton:hover {{
                        border-color: white;
                    }}
                """)
    
    def save_current_note(self):
        title = self.note_title_input.text().strip()
        if not title:
            title = "Untitled Note"
        
        content = self.note_editor.toHtml()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        note_data = {
            "title": title,
            "content": content,
            "color": self.selected_note_color,
            "updated": now
        }
        
        if "notes" not in self.data:
            self.data["notes"] = []
        
        if self.current_note_index >= 0 and self.current_note_index < len(self.data["notes"]):
            # Update existing note
            note_data["created"] = self.data["notes"][self.current_note_index].get("created", now)
            self.data["notes"][self.current_note_index] = note_data
        else:
            # Create new note
            note_data["created"] = now
            self.data["notes"].insert(0, note_data)
            self.current_note_index = 0
        
        self.save_data()
        self.refresh_notes_list()
        self.send_notification("📝 Note Saved!", title)
        
        # Select the saved note
        if self.current_note_index >= 0:
            self.notes_list.setCurrentRow(self.current_note_index)
    
    def delete_current_note(self):
        if self.current_note_index < 0:
            return
        
        reply = QMessageBox.question(
            self, "Delete Note",
            "Are you sure you want to delete this note?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.current_note_index < len(self.data.get("notes", [])):
                del self.data["notes"][self.current_note_index]
                self.save_data()
                self.current_note_index = -1
                self.note_title_input.clear()
                self.note_editor.clear()
                self.refresh_notes_list()
    
    def select_note_color(self, color, button):
        self.selected_note_color = color
        for btn in self.note_color_buttons:
            btn_color = btn.property("color")
            if btn == button:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {btn_color};
                        border: 3px solid white;
                        border-radius: 15px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {btn_color};
                        border: 3px solid transparent;
                        border-radius: 15px;
                    }}
                    QPushButton:hover {{
                        border-color: white;
                    }}
                """)
    
    # Text formatting methods
    def toggle_bold(self):
        cursor = self.note_editor.textCursor()
        fmt = cursor.charFormat()
        if fmt.fontWeight() == QFont.Weight.Bold:
            fmt.setFontWeight(QFont.Weight.Normal)
        else:
            fmt.setFontWeight(QFont.Weight.Bold)
        cursor.mergeCharFormat(fmt)
        self.note_editor.setTextCursor(cursor)
    
    def toggle_italic(self):
        cursor = self.note_editor.textCursor()
        fmt = cursor.charFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        cursor.mergeCharFormat(fmt)
        self.note_editor.setTextCursor(cursor)
    
    def toggle_underline(self):
        cursor = self.note_editor.textCursor()
        fmt = cursor.charFormat()
        fmt.setFontUnderline(not fmt.fontUnderline())
        cursor.mergeCharFormat(fmt)
        self.note_editor.setTextCursor(cursor)
    
    def toggle_strikethrough(self):
        cursor = self.note_editor.textCursor()
        fmt = cursor.charFormat()
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        cursor.mergeCharFormat(fmt)
        self.note_editor.setTextCursor(cursor)
    
    def apply_heading(self, heading):
        cursor = self.note_editor.textCursor()
        fmt = cursor.charFormat()
        
        if heading == "H1":
            fmt.setFontPointSize(24)
            fmt.setFontWeight(QFont.Weight.Bold)
        elif heading == "H2":
            fmt.setFontPointSize(20)
            fmt.setFontWeight(QFont.Weight.Bold)
        elif heading == "H3":
            fmt.setFontPointSize(16)
            fmt.setFontWeight(QFont.Weight.Bold)
        else:  # Normal
            fmt.setFontPointSize(14)
            fmt.setFontWeight(QFont.Weight.Normal)
        
        cursor.mergeCharFormat(fmt)
        self.note_editor.setTextCursor(cursor)
    
    def set_text_color(self, color):
        cursor = self.note_editor.textCursor()
        fmt = cursor.charFormat()
        fmt.setForeground(QColor(color))
        cursor.mergeCharFormat(fmt)
        self.note_editor.setTextCursor(cursor)
    
    def pick_custom_color(self):
        color = QColorDialog.getColor(QColor("#ffffff"), self, "Pick Text Color")
        if color.isValid():
            self.set_text_color(color.name())
    
    def insert_bullet_list(self):
        cursor = self.note_editor.textCursor()
        cursor.insertList(QTextListFormat.Style.ListDisc)
    
    def insert_numbered_list(self):
        cursor = self.note_editor.textCursor()
        cursor.insertList(QTextListFormat.Style.ListDecimal)
    
    def check_reminders(self):
        now = datetime.now()
        today = self.get_today()
        
        if self.sent_reminders["date"] != today:
            self.sent_reminders = {"morning": False, "afternoon": False, "evening": False, "date": today}
        
        reminders = self.data.get("reminders", {})
        if not reminders.get("enabled", True):
            return

        checked_in = any(
            today in info.get("dates", [])
            for info in self.data.get("activities", {}).values()
        )
        
        if checked_in or not self.data.get("activities"):
            return
        
        times = reminders.get("times", {})
        now_str = now.strftime("%H:%M")

        def should_send(key, fallback):
            target = times.get(key, fallback)
            return target == now_str and not self.sent_reminders.get(key, False)

        if should_send("morning", "09:00"):
            self.send_notification("☀️ Good Morning!", "Ready to build your streak?")
            self.sent_reminders["morning"] = True
        elif should_send("afternoon", "14:00"):
            self.send_notification("📝 Afternoon Check-in", "Don't forget to log progress!")
            self.sent_reminders["afternoon"] = True
        elif should_send("evening", "20:00"):
            self.send_notification("⚠️ Streak at Risk!", "Check in before midnight!")
            self.sent_reminders["evening"] = True


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Consistency Tracker")
    
    window = ConsistencyApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
