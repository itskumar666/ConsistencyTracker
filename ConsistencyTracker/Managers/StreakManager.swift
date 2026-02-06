import Foundation
import SwiftUI
import Combine

class StreakManager: ObservableObject {
    static let shared = StreakManager()
    
    @Published var activities: [Activity] = []
    @Published var badges: [Badge] = []
    @Published var freezeTokens: Int = 0
    
    private let activitiesKey = "consistency_activities"
    private let badgesKey = "consistency_badges"
    private let freezeTokensKey = "consistency_freeze_tokens"
    
    var totalStreak: Int {
        activities.map { $0.currentStreak }.max() ?? 0
    }
    
    var totalDaysLogged: Int {
        activities.map { $0.totalDays }.reduce(0, +)
    }
    
    init() {
        loadData()
        checkForBrokenStreaks()
    }
    
    // MARK: - Data Persistence
    
    private func loadData() {
        if let data = UserDefaults.standard.data(forKey: activitiesKey),
           let decoded = try? JSONDecoder().decode([Activity].self, from: data) {
            activities = decoded
        }
        
        if let data = UserDefaults.standard.data(forKey: badgesKey),
           let decoded = try? JSONDecoder().decode([Badge].self, from: data) {
            badges = decoded
        }
        
        freezeTokens = UserDefaults.standard.integer(forKey: freezeTokensKey)
    }
    
    private func saveData() {
        if let encoded = try? JSONEncoder().encode(activities) {
            UserDefaults.standard.set(encoded, forKey: activitiesKey)
        }
        if let encoded = try? JSONEncoder().encode(badges) {
            UserDefaults.standard.set(encoded, forKey: badgesKey)
        }
        UserDefaults.standard.set(freezeTokens, forKey: freezeTokensKey)
    }
    
    // MARK: - Activity Management
    
    func addActivity(name: String, icon: String, color: String) {
        let activity = Activity(name: name, icon: icon, color: color)
        activities.append(activity)
        saveData()
        
        // Check for multi-tasker badge
        if activities.count >= 3 {
            awardBadge(.multiTasker)
        }
    }
    
    func deleteActivity(_ activity: Activity) {
        activities.removeAll { $0.id == activity.id }
        saveData()
    }
    
    func checkIn(for activityId: UUID) {
        guard let index = activities.firstIndex(where: { $0.id == activityId }) else { return }
        
        var activity = activities[index]
        
        // Already checked in today
        if activity.hasCheckedInToday { return }
        
        let wasStreakBroken = activity.streakStatus == .broken
        
        // Update streak
        if activity.streakStatus == .atRisk || activity.streakStatus == .checkedInToday {
            activity.currentStreak += 1
        } else {
            activity.currentStreak = 1
        }
        
        // Update records
        activity.totalDays += 1
        if activity.currentStreak > activity.longestStreak {
            activity.longestStreak = activity.currentStreak
        }
        
        activity.lastCheckedIn = Date()
        activity.checkedInDates.append(Date())
        
        activities[index] = activity
        saveData()
        
        // Check for badges
        checkForStreakBadges(activity: activity)
        checkForTimeBadges()
        
        if wasStreakBroken && activity.currentStreak == 1 {
            awardBadge(.comeback, activityId: activity.id, activityName: activity.name)
        }
        
        // Show celebration notification for milestones
        if [7, 14, 30, 50, 100, 365].contains(activity.currentStreak) {
            NotificationManager.shared.showMilestoneNotification(
                activity: activity.name,
                streak: activity.currentStreak
            )
        }
    }
    
    // MARK: - Streak Management
    
    private func checkForBrokenStreaks() {
        let calendar = Calendar.current
        for (index, activity) in activities.enumerated() {
            guard let lastDate = activity.lastCheckedIn else { continue }
            
            // If more than 1 day has passed
            let daysSinceLastCheckIn = calendar.dateComponents([.day], from: lastDate, to: Date()).day ?? 0
            if daysSinceLastCheckIn > 1 {
                activities[index].currentStreak = 0
            }
        }
        saveData()
    }
    
    func useFreezeToken(for activityId: UUID) -> Bool {
        guard freezeTokens > 0 else { return false }
        guard let index = activities.firstIndex(where: { $0.id == activityId }) else { return false }
        
        // Simulate a check-in for yesterday to preserve streak
        activities[index].lastCheckedIn = Date()
        freezeTokens -= 1
        saveData()
        return true
    }
    
    func addFreezeToken() {
        freezeTokens += 1
        saveData()
    }
    
    // MARK: - Badge System
    
    private func checkForStreakBadges(activity: Activity) {
        if let badgeType = BadgeType.forStreak(activity.currentStreak) {
            awardBadge(badgeType, activityId: activity.id, activityName: activity.name)
        }
    }
    
    private func checkForTimeBadges() {
        let hour = Calendar.current.component(.hour, from: Date())
        
        if hour < 8 {
            awardBadge(.earlyBird)
        } else if hour >= 22 {
            awardBadge(.nightOwl)
        }
        
        let weekday = Calendar.current.component(.weekday, from: Date())
        if weekday == 1 || weekday == 7 {
            awardBadge(.weekendWarrior)
        }
    }
    
    private func awardBadge(_ type: BadgeType, activityId: UUID? = nil, activityName: String? = nil) {
        // Check if already has this badge (for activity-specific badges, check activity too)
        let alreadyHas = badges.contains { badge in
            badge.type == type && (activityId == nil || badge.activityId == activityId)
        }
        
        if !alreadyHas {
            let badge = Badge(type: type, activityId: activityId, activityName: activityName)
            badges.append(badge)
            saveData()
            
            // Show notification
            NotificationManager.shared.showBadgeNotification(badge: type)
        }
    }
    
    func hasBadge(_ type: BadgeType) -> Bool {
        badges.contains { $0.type == type }
    }
}
