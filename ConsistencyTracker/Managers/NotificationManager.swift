import Foundation
import UserNotifications

class NotificationManager {
    static let shared = NotificationManager()
    
    private let reminderIdentifier = "daily_reminder"
    private let warningIdentifier = "streak_warning"
    
    // MARK: - Schedule Reminders
    
    func scheduleDailyReminders() {
        let center = UNUserNotificationCenter.current()
        
        // Remove existing reminders
        center.removePendingNotificationRequests(withIdentifiers: [
            "\(reminderIdentifier)_morning",
            "\(reminderIdentifier)_afternoon",
            "\(reminderIdentifier)_evening",
            warningIdentifier
        ])
        
        // Morning reminder (9 AM)
        scheduleReminder(
            identifier: "\(reminderIdentifier)_morning",
            title: "Good Morning! ☀️",
            body: "Ready to build your streak today? Check in when you start!",
            hour: 9,
            minute: 0
        )
        
        // Afternoon reminder (2 PM) - only if not checked in
        scheduleReminder(
            identifier: "\(reminderIdentifier)_afternoon",
            title: "Afternoon Check-in 📝",
            body: "Don't forget to log your progress today!",
            hour: 14,
            minute: 0
        )
        
        // Evening warning (8 PM) - urgent
        scheduleReminder(
            identifier: "\(reminderIdentifier)_evening",
            title: "⚠️ Streak at Risk!",
            body: "You haven't checked in today. Your streak might break at midnight!",
            hour: 20,
            minute: 0
        )
    }
    
    private func scheduleReminder(identifier: String, title: String, body: String, hour: Int, minute: Int) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        content.interruptionLevel = .timeSensitive
        
        var dateComponents = DateComponents()
        dateComponents.hour = hour
        dateComponents.minute = minute
        
        let trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: true)
        let request = UNNotificationRequest(identifier: identifier, content: content, trigger: trigger)
        
        UNUserNotificationCenter.current().add(request) { error in
            if let error = error {
                print("Error scheduling reminder: \(error)")
            }
        }
    }
    
    // MARK: - Instant Notifications
    
    func showMilestoneNotification(activity: String, streak: Int) {
        let content = UNMutableNotificationContent()
        content.title = "🎉 Milestone Reached!"
        content.body = "Incredible! You've hit \(streak) days of \(activity)!"
        content.sound = .default
        
        let request = UNNotificationRequest(
            identifier: "milestone_\(UUID().uuidString)",
            content: content,
            trigger: UNTimeIntervalNotificationTrigger(timeInterval: 1, repeats: false)
        )
        
        UNUserNotificationCenter.current().add(request)
    }
    
    func showBadgeNotification(badge: BadgeType) {
        let content = UNMutableNotificationContent()
        content.title = "🏆 New Badge Earned!"
        content.body = "You've earned the \"\(badge.name)\" badge! \(badge.description)"
        content.sound = .default
        
        let request = UNNotificationRequest(
            identifier: "badge_\(UUID().uuidString)",
            content: content,
            trigger: UNTimeIntervalNotificationTrigger(timeInterval: 1, repeats: false)
        )
        
        UNUserNotificationCenter.current().add(request)
    }
    
    func showStreakBrokenNotification(activity: String, previousStreak: Int) {
        let content = UNMutableNotificationContent()
        content.title = "💔 Streak Broken"
        content.body = "Your \(previousStreak)-day \(activity) streak has ended. Start fresh today!"
        content.sound = .default
        
        let request = UNNotificationRequest(
            identifier: "broken_\(UUID().uuidString)",
            content: content,
            trigger: UNTimeIntervalNotificationTrigger(timeInterval: 1, repeats: false)
        )
        
        UNUserNotificationCenter.current().add(request)
    }
    
    // MARK: - Test Notification
    
    func sendTestNotification() {
        let content = UNMutableNotificationContent()
        content.title = "🔔 Test Notification"
        content.body = "Notifications are working! You'll receive daily reminders."
        content.sound = .default
        
        let request = UNNotificationRequest(
            identifier: "test_\(UUID().uuidString)",
            content: content,
            trigger: UNTimeIntervalNotificationTrigger(timeInterval: 2, repeats: false)
        )
        
        UNUserNotificationCenter.current().add(request)
    }
    
    // MARK: - Cancel Reminders
    
    func cancelAllReminders() {
        UNUserNotificationCenter.current().removeAllPendingNotificationRequests()
    }
    
    func updateReminderTimes(morning: Int, afternoon: Int, evening: Int) {
        let center = UNUserNotificationCenter.current()
        center.removeAllPendingNotificationRequests()
        
        scheduleReminder(
            identifier: "\(reminderIdentifier)_morning",
            title: "Good Morning! ☀️",
            body: "Ready to build your streak today?",
            hour: morning,
            minute: 0
        )
        
        scheduleReminder(
            identifier: "\(reminderIdentifier)_afternoon",
            title: "Afternoon Check-in 📝",
            body: "Don't forget to log your progress!",
            hour: afternoon,
            minute: 0
        )
        
        scheduleReminder(
            identifier: "\(reminderIdentifier)_evening",
            title: "⚠️ Streak at Risk!",
            body: "Check in before midnight to keep your streak!",
            hour: evening,
            minute: 0
        )
    }
}
