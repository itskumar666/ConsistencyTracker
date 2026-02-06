import Foundation
import SwiftUI

struct Badge: Identifiable, Codable {
    let id: UUID
    let type: BadgeType
    let activityId: UUID?
    let activityName: String?
    let earnedAt: Date
    
    init(type: BadgeType, activityId: UUID? = nil, activityName: String? = nil) {
        self.id = UUID()
        self.type = type
        self.activityId = activityId
        self.activityName = activityName
        self.earnedAt = Date()
    }
}

enum BadgeType: String, Codable, CaseIterable {
    // Streak milestones
    case firstDay = "first_day"
    case weekWarrior = "week_warrior"
    case twoWeeks = "two_weeks"
    case monthMaster = "month_master"
    case fiftyDays = "fifty_days"
    case hundredDays = "hundred_days"
    case yearLegend = "year_legend"
    
    // Special achievements
    case earlyBird = "early_bird"
    case nightOwl = "night_owl"
    case weekendWarrior = "weekend_warrior"
    case multiTasker = "multi_tasker"
    case comeback = "comeback"
    
    var name: String {
        switch self {
        case .firstDay: return "First Step"
        case .weekWarrior: return "Week Warrior"
        case .twoWeeks: return "Fortnight Fighter"
        case .monthMaster: return "Month Master"
        case .fiftyDays: return "Fifty & Fabulous"
        case .hundredDays: return "Century Club"
        case .yearLegend: return "Year Legend"
        case .earlyBird: return "Early Bird"
        case .nightOwl: return "Night Owl"
        case .weekendWarrior: return "Weekend Warrior"
        case .multiTasker: return "Multi-Tasker"
        case .comeback: return "Comeback King"
        }
    }
    
    var description: String {
        switch self {
        case .firstDay: return "Complete your first day"
        case .weekWarrior: return "7 day streak"
        case .twoWeeks: return "14 day streak"
        case .monthMaster: return "30 day streak"
        case .fiftyDays: return "50 day streak"
        case .hundredDays: return "100 day streak"
        case .yearLegend: return "365 day streak"
        case .earlyBird: return "Check in before 8 AM"
        case .nightOwl: return "Check in after 10 PM"
        case .weekendWarrior: return "Check in on weekend"
        case .multiTasker: return "Track 3+ activities"
        case .comeback: return "Restart after breaking streak"
        }
    }
    
    var icon: String {
        switch self {
        case .firstDay: return "star.fill"
        case .weekWarrior: return "7.circle.fill"
        case .twoWeeks: return "14.circle.fill"
        case .monthMaster: return "calendar.badge.checkmark"
        case .fiftyDays: return "50.circle.fill"
        case .hundredDays: return "100.circle.fill"
        case .yearLegend: return "crown.fill"
        case .earlyBird: return "sunrise.fill"
        case .nightOwl: return "moon.stars.fill"
        case .weekendWarrior: return "figure.walk"
        case .multiTasker: return "square.stack.3d.up.fill"
        case .comeback: return "arrow.counterclockwise"
        }
    }
    
    var color: Color {
        switch self {
        case .firstDay: return .yellow
        case .weekWarrior: return .orange
        case .twoWeeks: return .green
        case .monthMaster: return .blue
        case .fiftyDays: return .purple
        case .hundredDays: return .red
        case .yearLegend: return .yellow
        case .earlyBird: return .orange
        case .nightOwl: return .indigo
        case .weekendWarrior: return .green
        case .multiTasker: return .cyan
        case .comeback: return .mint
        }
    }
    
    static func forStreak(_ days: Int) -> BadgeType? {
        switch days {
        case 1: return .firstDay
        case 7: return .weekWarrior
        case 14: return .twoWeeks
        case 30: return .monthMaster
        case 50: return .fiftyDays
        case 100: return .hundredDays
        case 365: return .yearLegend
        default: return nil
        }
    }
}
