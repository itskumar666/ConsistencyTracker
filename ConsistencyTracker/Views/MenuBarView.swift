import SwiftUI

struct MenuBarView: View {
    @EnvironmentObject var streakManager: StreakManager
    @State private var showingAddActivity = false
    @State private var showingBadges = false
    @State private var showingStats = false
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            headerView
            
            Divider()
            
            // Activities List
            if streakManager.activities.isEmpty {
                emptyStateView
            } else {
                activitiesListView
            }
            
            Divider()
            
            // Quick Stats
            quickStatsView
            
            Divider()
            
            // Bottom Actions
            bottomActionsView
        }
        .frame(width: 320)
        .sheet(isPresented: $showingAddActivity) {
            AddActivityView()
                .environmentObject(streakManager)
        }
        .sheet(isPresented: $showingBadges) {
            BadgesView()
                .environmentObject(streakManager)
        }
        .sheet(isPresented: $showingStats) {
            StatsView()
                .environmentObject(streakManager)
        }
    }
    
    // MARK: - Header
    
    private var headerView: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text("Consistency Tracker")
                    .font(.headline)
                    .fontWeight(.bold)
                
                Text(dateString)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            // Total Streak Badge
            HStack(spacing: 4) {
                Image(systemName: "flame.fill")
                    .foregroundColor(.orange)
                Text("\(streakManager.totalStreak)")
                    .fontWeight(.bold)
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 5)
            .background(Color.orange.opacity(0.2))
            .cornerRadius(12)
        }
        .padding()
    }
    
    private var dateString: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "EEEE, MMMM d"
        return formatter.string(from: Date())
    }
    
    // MARK: - Empty State
    
    private var emptyStateView: some View {
        VStack(spacing: 12) {
            Image(systemName: "plus.circle.fill")
                .font(.system(size: 40))
                .foregroundColor(.blue.opacity(0.6))
            
            Text("No activities yet")
                .font(.headline)
            
            Text("Add an activity to start tracking!")
                .font(.caption)
                .foregroundColor(.secondary)
            
            Button {
                showingAddActivity = true
            } label: {
                Label("Add Activity", systemImage: "plus")
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
            }
            .buttonStyle(.borderedProminent)
        }
        .padding(30)
    }
    
    // MARK: - Activities List
    
    private var activitiesListView: some View {
        ScrollView {
            LazyVStack(spacing: 8) {
                ForEach(streakManager.activities) { activity in
                    ActivityRowView(activity: activity)
                        .environmentObject(streakManager)
                }
            }
            .padding()
        }
        .frame(maxHeight: 300)
    }
    
    // MARK: - Quick Stats
    
    private var quickStatsView: some View {
        HStack(spacing: 20) {
            StatItem(
                icon: "calendar",
                value: "\(streakManager.totalDaysLogged)",
                label: "Total Days"
            )
            
            StatItem(
                icon: "trophy.fill",
                value: "\(streakManager.badges.count)",
                label: "Badges"
            )
            
            StatItem(
                icon: "snowflake",
                value: "\(streakManager.freezeTokens)",
                label: "Freezes"
            )
        }
        .padding()
    }
    
    // MARK: - Bottom Actions
    
    private var bottomActionsView: some View {
        HStack {
            Button {
                showingAddActivity = true
            } label: {
                Label("Add", systemImage: "plus")
            }
            
            Spacer()
            
            Button {
                showingBadges = true
            } label: {
                Label("Badges", systemImage: "trophy")
            }
            
            Spacer()
            
            Button {
                showingStats = true
            } label: {
                Label("Stats", systemImage: "chart.bar")
            }
            
            Spacer()
            
            Button {
                NSApp.terminate(nil)
            } label: {
                Label("Quit", systemImage: "power")
            }
        }
        .buttonStyle(.plain)
        .padding()
    }
}

// MARK: - Stat Item

struct StatItem: View {
    let icon: String
    let value: String
    let label: String
    
    var body: some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .font(.title3)
                .foregroundColor(.secondary)
            Text(value)
                .font(.headline)
                .fontWeight(.bold)
            Text(label)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
    }
}

#Preview {
    MenuBarView()
        .environmentObject(StreakManager.shared)
}
