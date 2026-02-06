import Foundation
import SwiftUI

struct Activity: Identifiable, Codable, Hashable {
    let id: UUID
    var name: String
    var icon: String
    var color: String
    var currentStreak: Int
    var longestStreak: Int
    var totalDays: Int
    var lastCheckedIn: Date?
    var checkedInDates: [Date]
    var createdAt: Date
    
    init(id: UUID = UUID(), name: String, icon: String, color: String) {
        self.id = id
        self.name = name
        self.icon = icon
        self.color = color
        self.currentStreak = 0
        self.longestStreak = 0
        self.totalDays = 0
        self.lastCheckedIn = nil
        self.checkedInDates = []
        self.createdAt = Date()
    }
    
    var colorValue: Color {
        switch color {
        case "red": return .red
        case "orange": return .orange
        case "yellow": return .yellow
        case "green": return .green
        case "blue": return .blue
        case "purple": return .purple
        case "pink": return .pink
        case "mint": return .mint
        case "cyan": return .cyan
        case "indigo": return .indigo
        default: return .blue
        }
    }
    
    var hasCheckedInToday: Bool {
        guard let lastDate = lastCheckedIn else { return false }
        return Calendar.current.isDateInToday(lastDate)
    }
    
    var streakStatus: StreakStatus {
        guard let lastDate = lastCheckedIn else { return .noStreak }
        if Calendar.current.isDateInToday(lastDate) {
            return .checkedInToday
        } else if Calendar.current.isDateInYesterday(lastDate) {
            return .atRisk
        } else {
            return .broken
        }
    }
}

enum StreakStatus {
    case noStreak
    case checkedInToday
    case atRisk
    case broken
    
    var message: String {
        switch self {
        case .noStreak: return "Start your streak!"
        case .checkedInToday: return "You're on fire! 🔥"
        case .atRisk: return "Check in to keep your streak!"
        case .broken: return "Streak broken. Start fresh!"
        }
    }
}

// Preset activities
struct ActivityPresets {
    static let all: [(name: String, icon: String, color: String)] = [
        ("Coding", "chevron.left.forwardslash.chevron.right", "orange"),
        ("Study", "book.fill", "blue"),
        ("Reading", "books.vertical.fill", "green"),
        ("Exercise", "figure.run", "red"),
        ("Writing", "pencil.line", "purple"),
        ("Meditation", "brain.head.profile", "mint"),
        ("Language Learning", "character.book.closed.fill", "indigo"),
        ("Music Practice", "music.note", "pink"),
        ("Drawing", "paintbrush.fill", "cyan"),
        ("Side Project", "hammer.fill", "yellow")
    ]
}
