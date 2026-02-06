import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var streakManager: StreakManager
    
    @AppStorage("morningReminderHour") private var morningHour = 9
    @AppStorage("afternoonReminderHour") private var afternoonHour = 14
    @AppStorage("eveningReminderHour") private var eveningHour = 20
    @AppStorage("notificationsEnabled") private var notificationsEnabled = true
    @AppStorage("launchAtLogin") private var launchAtLogin = false
    
    var body: some View {
        TabView {
            // General Settings
            Form {
                Section("Startup") {
                    Toggle("Launch at Login", isOn: $launchAtLogin)
                        .onChange(of: launchAtLogin) { _, newValue in
                            // Note: Actual launch at login requires additional setup
                            print("Launch at login: \(newValue)")
                        }
                }
                
                Section("Data") {
                    LabeledContent("Activities") {
                        Text("\(streakManager.activities.count)")
                    }
                    
                    LabeledContent("Badges Earned") {
                        Text("\(streakManager.badges.count)")
                    }
                    
                    LabeledContent("Freeze Tokens") {
                        HStack {
                            Text("\(streakManager.freezeTokens)")
                            Button("+") {
                                streakManager.addFreezeToken()
                            }
                            .buttonStyle(.bordered)
                        }
                    }
                    
                    Button("Reset All Data", role: .destructive) {
                        // Would show confirmation dialog in production
                    }
                }
            }
            .tabItem {
                Label("General", systemImage: "gear")
            }
            
            // Notification Settings
            Form {
                Section {
                    Toggle("Enable Notifications", isOn: $notificationsEnabled)
                        .onChange(of: notificationsEnabled) { _, newValue in
                            if newValue {
                                NotificationManager.shared.scheduleDailyReminders()
                            } else {
                                NotificationManager.shared.cancelAllReminders()
                            }
                        }
                }
                
                if notificationsEnabled {
                    Section("Reminder Times") {
                        Picker("Morning Reminder", selection: $morningHour) {
                            ForEach(5..<12, id: \.self) { hour in
                                Text("\(hour):00").tag(hour)
                            }
                        }
                        
                        Picker("Afternoon Reminder", selection: $afternoonHour) {
                            ForEach(12..<18, id: \.self) { hour in
                                Text("\(hour):00").tag(hour)
                            }
                        }
                        
                        Picker("Evening Warning", selection: $eveningHour) {
                            ForEach(18..<24, id: \.self) { hour in
                                Text("\(hour):00").tag(hour)
                            }
                        }
                        
                        Button("Update Reminders") {
                            NotificationManager.shared.updateReminderTimes(
                                morning: morningHour,
                                afternoon: afternoonHour,
                                evening: eveningHour
                            )
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    
                    Section {
                        Button("Send Test Notification") {
                            NotificationManager.shared.sendTestNotification()
                        }
                    }
                }
            }
            .tabItem {
                Label("Notifications", systemImage: "bell")
            }
            
            // About
            VStack(spacing: 20) {
                Image(systemName: "flame.fill")
                    .font(.system(size: 60))
                    .foregroundStyle(
                        LinearGradient(
                            colors: [.orange, .red],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                
                Text("Consistency Tracker")
                    .font(.title)
                    .fontWeight(.bold)
                
                Text("Version 1.0.0")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Divider()
                    .frame(width: 200)
                
                Text("Build consistent habits.\nTrack any activity.\nStay motivated.")
                    .multilineTextAlignment(.center)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Text("Made with ❤️")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding(40)
            .tabItem {
                Label("About", systemImage: "info.circle")
            }
        }
        .frame(width: 450, height: 350)
    }
}

#Preview {
    SettingsView()
        .environmentObject(StreakManager.shared)
}
