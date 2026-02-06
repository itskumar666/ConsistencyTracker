import SwiftUI

struct ActivityRowView: View {
    let activity: Activity
    @EnvironmentObject var streakManager: StreakManager
    @State private var showingDetails = false
    @State private var isHovering = false
    
    var body: some View {
        HStack(spacing: 12) {
            // Icon
            ZStack {
                Circle()
                    .fill(activity.colorValue.opacity(0.2))
                    .frame(width: 40, height: 40)
                
                Image(systemName: activity.icon)
                    .font(.system(size: 18))
                    .foregroundColor(activity.colorValue)
            }
            
            // Info
            VStack(alignment: .leading, spacing: 2) {
                Text(activity.name)
                    .font(.headline)
                    .lineLimit(1)
                
                HStack(spacing: 8) {
                    // Streak
                    Label("\(activity.currentStreak) days", systemImage: "flame.fill")
                        .font(.caption)
                        .foregroundColor(activity.currentStreak > 0 ? .orange : .secondary)
                    
                    // Status
                    Text(activity.streakStatus.message)
                        .font(.caption2)
                        .foregroundColor(statusColor)
                }
            }
            
            Spacer()
            
            // Check-in Button
            Button {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.6)) {
                    streakManager.checkIn(for: activity.id)
                }
            } label: {
                ZStack {
                    Circle()
                        .fill(activity.hasCheckedInToday ? Color.green : Color.blue)
                        .frame(width: 36, height: 36)
                    
                    Image(systemName: activity.hasCheckedInToday ? "checkmark" : "plus")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.white)
                }
            }
            .buttonStyle(.plain)
            .disabled(activity.hasCheckedInToday)
            .opacity(activity.hasCheckedInToday ? 0.7 : 1)
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(nsColor: .controlBackgroundColor))
                .shadow(color: .black.opacity(isHovering ? 0.1 : 0.05), radius: isHovering ? 4 : 2)
        )
        .onHover { hovering in
            withAnimation(.easeInOut(duration: 0.2)) {
                isHovering = hovering
            }
        }
        .contextMenu {
            Button {
                showingDetails = true
            } label: {
                Label("View Details", systemImage: "info.circle")
            }
            
            if activity.streakStatus == .atRisk && streakManager.freezeTokens > 0 {
                Button {
                    _ = streakManager.useFreezeToken(for: activity.id)
                } label: {
                    Label("Use Freeze Token", systemImage: "snowflake")
                }
            }
            
            Divider()
            
            Button(role: .destructive) {
                streakManager.deleteActivity(activity)
            } label: {
                Label("Delete", systemImage: "trash")
            }
        }
        .sheet(isPresented: $showingDetails) {
            ActivityDetailView(activity: activity)
                .environmentObject(streakManager)
        }
    }
    
    private var statusColor: Color {
        switch activity.streakStatus {
        case .checkedInToday: return .green
        case .atRisk: return .orange
        case .broken, .noStreak: return .secondary
        }
    }
}

// MARK: - Activity Detail View

struct ActivityDetailView: View {
    let activity: Activity
    @EnvironmentObject var streakManager: StreakManager
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        VStack(spacing: 20) {
            // Header
            HStack {
                ZStack {
                    Circle()
                        .fill(activity.colorValue.opacity(0.2))
                        .frame(width: 60, height: 60)
                    
                    Image(systemName: activity.icon)
                        .font(.system(size: 28))
                        .foregroundColor(activity.colorValue)
                }
                
                VStack(alignment: .leading) {
                    Text(activity.name)
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    Text("Started \(activity.createdAt.formatted(date: .abbreviated, time: .omitted))")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
            }
            
            // Stats Grid
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 16) {
                DetailStatCard(title: "Current Streak", value: "\(activity.currentStreak)", icon: "flame.fill", color: .orange)
                DetailStatCard(title: "Longest Streak", value: "\(activity.longestStreak)", icon: "trophy.fill", color: .yellow)
                DetailStatCard(title: "Total Days", value: "\(activity.totalDays)", icon: "calendar", color: .blue)
                DetailStatCard(title: "Status", value: statusText, icon: statusIcon, color: statusColor)
            }
            
            // Calendar Preview (Placeholder)
            VStack(alignment: .leading, spacing: 8) {
                Text("Recent Activity")
                    .font(.headline)
                
                HStack(spacing: 4) {
                    ForEach(0..<7, id: \.self) { index in
                        let date = Calendar.current.date(byAdding: .day, value: -6 + index, to: Date())!
                        let isActive = activity.checkedInDates.contains { Calendar.current.isDate($0, inSameDayAs: date) }
                        
                        VStack(spacing: 4) {
                            Text(dayLetter(for: date))
                                .font(.caption2)
                                .foregroundColor(.secondary)
                            
                            RoundedRectangle(cornerRadius: 4)
                                .fill(isActive ? activity.colorValue : Color.gray.opacity(0.2))
                                .frame(width: 30, height: 30)
                        }
                    }
                }
            }
            
            Spacer()
            
            Button("Done") {
                dismiss()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding(24)
        .frame(width: 400, height: 450)
    }
    
    private var statusText: String {
        switch activity.streakStatus {
        case .checkedInToday: return "Done!"
        case .atRisk: return "At Risk"
        case .broken: return "Broken"
        case .noStreak: return "New"
        }
    }
    
    private var statusIcon: String {
        switch activity.streakStatus {
        case .checkedInToday: return "checkmark.circle.fill"
        case .atRisk: return "exclamationmark.triangle.fill"
        case .broken: return "xmark.circle.fill"
        case .noStreak: return "star.fill"
        }
    }
    
    private var statusColor: Color {
        switch activity.streakStatus {
        case .checkedInToday: return .green
        case .atRisk: return .orange
        case .broken: return .red
        case .noStreak: return .blue
        }
    }
    
    private func dayLetter(for date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "E"
        return String(formatter.string(from: date).prefix(1))
    }
}

struct DetailStatCard: View {
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
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(nsColor: .controlBackgroundColor))
        )
    }
}
