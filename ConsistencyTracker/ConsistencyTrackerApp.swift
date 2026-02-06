import SwiftUI
import UserNotifications

@main
struct ConsistencyTrackerApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    @StateObject private var streakManager = StreakManager.shared
    
    var body: some Scene {
        MenuBarExtra {
            MenuBarView()
                .environmentObject(streakManager)
        } label: {
            HStack(spacing: 4) {
                Image(systemName: "flame.fill")
                Text("\(streakManager.totalStreak)")
            }
        }
        .menuBarExtraStyle(.window)
        
        Settings {
            SettingsView()
                .environmentObject(streakManager)
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate, UNUserNotificationCenterDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Request notification permissions
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            if granted {
                print("Notification permission granted")
            }
        }
        UNUserNotificationCenter.current().delegate = self
        
        // Schedule daily reminders
        NotificationManager.shared.scheduleDailyReminders()
    }
    
    // Show notifications even when app is in foreground
    func userNotificationCenter(_ center: UNUserNotificationCenter, willPresent notification: UNNotification, withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        completionHandler([.banner, .sound])
    }
}
