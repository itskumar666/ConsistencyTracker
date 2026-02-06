# Consistency Tracker 🔥

A Mac menu bar app to track daily activities, maintain streaks, and stay consistent with your habits.

## Features

### 📊 Multi-Activity Tracking
- Track **any** type of activity: Coding, Study, Reading, Exercise, etc.
- Preset activities for quick setup
- Create custom activities with your own icon and color

### 🔥 Streak System
- **Current streak** counter for each activity
- **Longest streak** records
- Visual status indicators (on fire, at risk, broken)
- Streak freeze tokens to skip days without losing progress

### 🏆 Reward System (Badges)
- **Milestone badges**: First Day, Week Warrior, Month Master, Century Club, Year Legend
- **Time-based badges**: Early Bird (before 8 AM), Night Owl (after 10 PM)
- **Special badges**: Weekend Warrior, Multi-Tasker, Comeback King

### 🔔 Smart Notifications
- **Morning reminder** (9 AM): Start your day right
- **Afternoon check-in** (2 PM): Don't forget to log progress
- **Evening warning** (8 PM): Streak at risk alert
- **Milestone celebrations**: When you hit 7, 30, 100 days, etc.
- Customizable reminder times in Settings

### 📈 Statistics
- Total days logged across all activities
- Weekly activity heatmap
- Consistency score
- Activity breakdown with progress bars

## Getting Started

### Requirements
- macOS 14.0 (Sonoma) or later
- Xcode 15.0 or later

### Installation

1. **Open in Xcode:**
   ```bash
   open ConsistencyTracker.xcodeproj
   ```

2. **Build and Run:**
   - Select your Mac as the target device
   - Press `Cmd + R` or click the Run button

3. **Allow Notifications:**
   - When prompted, allow notifications for reminders

4. **Menu Bar:**
   - The app lives in your menu bar showing your current streak
   - Click the 🔥 icon to open the main panel

## Usage

### Adding Activities
1. Click "Add" in the menu bar panel
2. Choose a preset activity OR
3. Expand "Custom Activity" to create your own

### Daily Check-in
1. Click the menu bar icon
2. Press the `+` button next to any activity to check in
3. The button turns green ✓ when completed for today

### Viewing Badges
- Click "Badges" to see earned and locked badges
- Hover over badges to see how to unlock them

### Settings
- Access via the gear icon or `Cmd + ,`
- Customize notification times
- Add freeze tokens
- View app statistics

## Project Structure

```
ConsistencyTracker/
├── ConsistencyTrackerApp.swift    # App entry point & setup
├── Models/
│   ├── Activity.swift              # Activity data model
│   └── Badge.swift                 # Badge types & definitions
├── Managers/
│   ├── StreakManager.swift         # Core logic & data persistence
│   └── NotificationManager.swift   # Notification scheduling
├── Views/
│   ├── MenuBarView.swift           # Main menu bar interface
│   ├── ActivityRowView.swift       # Individual activity display
│   ├── AddActivityView.swift       # Add new activity sheet
│   ├── BadgesView.swift            # Badge collection view
│   ├── StatsView.swift             # Statistics dashboard
│   └── SettingsView.swift          # App settings
└── Assets.xcassets/                # App icons & colors
```

## Future Ideas

- [ ] GitHub integration for auto-detecting commits
- [ ] iCloud sync across devices
- [ ] Apple Watch companion app
- [ ] Export streak data
- [ ] Home Screen widgets
- [ ] Social sharing
- [ ] Dark/Light theme options

## License

MIT License - Feel free to modify and use as you like!

---

**Made with ❤️ for consistent builders**
