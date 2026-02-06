import SwiftUI

struct StatsView: View {
    @EnvironmentObject var streakManager: StreakManager
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        VStack(spacing: 20) {
            // Header
            Text("Your Statistics")
                .font(.title2)
                .fontWeight(.bold)
            
            ScrollView {
                VStack(spacing: 20) {
                    // Overview Cards
                    LazyVGrid(columns: [
                        GridItem(.flexible()),
                        GridItem(.flexible())
                    ], spacing: 16) {
                        OverviewCard(
                            title: "Total Days Logged",
                            value: "\(streakManager.totalDaysLogged)",
                            icon: "calendar.badge.checkmark",
                            color: .blue
                        )
                        
                        OverviewCard(
                            title: "Active Streaks",
                            value: "\(activeStreaksCount)",
                            icon: "flame.fill",
                            color: .orange
                        )
                        
                        OverviewCard(
                            title: "Longest Streak",
                            value: "\(longestStreak)",
                            icon: "trophy.fill",
                            color: .yellow
                        )
                        
                        OverviewCard(
                            title: "Badges Earned",
                            value: "\(streakManager.badges.count)",
                            icon: "medal.fill",
                            color: .purple
                        )
                    }
                    
                    Divider()
                    
                    // Activity Breakdown
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Activity Breakdown")
                            .font(.headline)
                        
                        if streakManager.activities.isEmpty {
                            Text("No activities yet")
                                .foregroundColor(.secondary)
                                .frame(maxWidth: .infinity, alignment: .center)
                                .padding()
                        } else {
                            ForEach(streakManager.activities.sorted { $0.totalDays > $1.totalDays }) { activity in
                                ActivityStatRow(activity: activity, maxDays: maxActivityDays)
                            }
                        }
                    }
                    
                    Divider()
                    
                    // Weekly Activity
                    VStack(alignment: .leading, spacing: 12) {
                        Text("This Week")
                            .font(.headline)
                        
                        HStack(spacing: 8) {
                            ForEach(0..<7, id: \.self) { index in
                                let date = Calendar.current.date(byAdding: .day, value: -6 + index, to: Date())!
                                let count = checkInsOnDate(date)
                                
                                VStack(spacing: 4) {
                                    Text(dayLetter(for: date))
                                        .font(.caption2)
                                        .foregroundColor(.secondary)
                                    
                                    RoundedRectangle(cornerRadius: 6)
                                        .fill(activityColor(for: count))
                                        .frame(height: 40)
                                    
                                    Text("\(count)")
                                        .font(.caption2)
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                        
                        HStack(spacing: 16) {
                            ForEach([0, 1, 2, 3], id: \.self) { level in
                                HStack(spacing: 4) {
                                    RoundedRectangle(cornerRadius: 2)
                                        .fill(activityColor(for: level))
                                        .frame(width: 12, height: 12)
                                    Text(levelLabel(level))
                                        .font(.caption2)
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                    }
                    
                    Divider()
                    
                    // Consistency Score
                    VStack(spacing: 12) {
                        Text("Consistency Score")
                            .font(.headline)
                        
                        ZStack {
                            Circle()
                                .stroke(Color.gray.opacity(0.2), lineWidth: 12)
                            
                            Circle()
                                .trim(from: 0, to: consistencyScore)
                                .stroke(scoreColor, style: StrokeStyle(lineWidth: 12, lineCap: .round))
                                .rotationEffect(.degrees(-90))
                            
                            VStack {
                                Text("\(Int(consistencyScore * 100))%")
                                    .font(.title)
                                    .fontWeight(.bold)
                                Text("This Week")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                        .frame(width: 120, height: 120)
                    }
                }
            }
            
            Button("Done") {
                dismiss()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding(24)
        .frame(width: 450, height: 600)
    }
    
    // MARK: - Computed Properties
    
    private var activeStreaksCount: Int {
        streakManager.activities.filter { $0.currentStreak > 0 }.count
    }
    
    private var longestStreak: Int {
        streakManager.activities.map { $0.longestStreak }.max() ?? 0
    }
    
    private var maxActivityDays: Int {
        streakManager.activities.map { $0.totalDays }.max() ?? 1
    }
    
    private var consistencyScore: Double {
        let last7Days = (0..<7).map { offset -> Date in
            Calendar.current.date(byAdding: .day, value: -offset, to: Date())!
        }
        
        guard !streakManager.activities.isEmpty else { return 0 }
        
        var daysWithActivity = 0
        for date in last7Days {
            if checkInsOnDate(date) > 0 {
                daysWithActivity += 1
            }
        }
        
        return Double(daysWithActivity) / 7.0
    }
    
    private var scoreColor: Color {
        switch consistencyScore {
        case 0..<0.3: return .red
        case 0.3..<0.6: return .orange
        case 0.6..<0.85: return .yellow
        default: return .green
        }
    }
    
    // MARK: - Helper Functions
    
    private func checkInsOnDate(_ date: Date) -> Int {
        var count = 0
        for activity in streakManager.activities {
            if activity.checkedInDates.contains(where: { Calendar.current.isDate($0, inSameDayAs: date) }) {
                count += 1
            }
        }
        return count
    }
    
    private func activityColor(for count: Int) -> Color {
        switch count {
        case 0: return .gray.opacity(0.2)
        case 1: return .green.opacity(0.4)
        case 2: return .green.opacity(0.6)
        default: return .green
        }
    }
    
    private func levelLabel(_ level: Int) -> String {
        switch level {
        case 0: return "None"
        case 1: return "Low"
        case 2: return "Medium"
        default: return "High"
        }
    }
    
    private func dayLetter(for date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "E"
        return String(formatter.string(from: date).prefix(1))
    }
}

struct OverviewCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
            
            Text(value)
                .font(.title)
                .fontWeight(.bold)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(nsColor: .controlBackgroundColor))
        )
    }
}

struct ActivityStatRow: View {
    let activity: Activity
    let maxDays: Int
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: activity.icon)
                .foregroundColor(activity.colorValue)
                .frame(width: 24)
            
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(activity.name)
                        .font(.subheadline)
                    
                    Spacer()
                    
                    Text("\(activity.totalDays) days")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                GeometryReader { geometry in
                    RoundedRectangle(cornerRadius: 4)
                        .fill(activity.colorValue)
                        .frame(width: geometry.size.width * progress)
                }
                .frame(height: 6)
                .background(Color.gray.opacity(0.2))
                .cornerRadius(4)
            }
        }
        .padding(.vertical, 4)
    }
    
    private var progress: CGFloat {
        guard maxDays > 0 else { return 0 }
        return CGFloat(activity.totalDays) / CGFloat(maxDays)
    }
}

#Preview {
    StatsView()
        .environmentObject(StreakManager.shared)
}
