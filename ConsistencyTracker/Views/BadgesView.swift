import SwiftUI

struct BadgesView: View {
    @EnvironmentObject var streakManager: StreakManager
    @Environment(\.dismiss) private var dismiss
    
    let columns = [
        GridItem(.adaptive(minimum: 100), spacing: 16)
    ]
    
    var body: some View {
        VStack(spacing: 20) {
            // Header
            HStack {
                VStack(alignment: .leading) {
                    Text("Your Badges")
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    Text("\(streakManager.badges.count) of \(BadgeType.allCases.count) earned")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
            }
            
            ScrollView {
                // Earned Badges
                if !streakManager.badges.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Earned")
                            .font(.headline)
                        
                        LazyVGrid(columns: columns, spacing: 16) {
                            ForEach(streakManager.badges) { badge in
                                BadgeCard(type: badge.type, isEarned: true, earnedAt: badge.earnedAt)
                            }
                        }
                    }
                    
                    Divider()
                        .padding(.vertical)
                }
                
                // Locked Badges
                VStack(alignment: .leading, spacing: 12) {
                    Text("Locked")
                        .font(.headline)
                    
                    let earnedTypes = Set(streakManager.badges.map { $0.type })
                    let lockedTypes = BadgeType.allCases.filter { !earnedTypes.contains($0) }
                    
                    if lockedTypes.isEmpty {
                        Text("You've earned all badges! 🎉")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity, alignment: .center)
                            .padding()
                    } else {
                        LazyVGrid(columns: columns, spacing: 16) {
                            ForEach(lockedTypes, id: \.self) { type in
                                BadgeCard(type: type, isEarned: false)
                            }
                        }
                    }
                }
            }
            
            Button("Done") {
                dismiss()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding(24)
        .frame(width: 450, height: 500)
    }
}

struct BadgeCard: View {
    let type: BadgeType
    let isEarned: Bool
    var earnedAt: Date? = nil
    
    @State private var isHovering = false
    
    var body: some View {
        VStack(spacing: 8) {
            ZStack {
                Circle()
                    .fill(isEarned ? type.color.opacity(0.2) : Color.gray.opacity(0.1))
                    .frame(width: 50, height: 50)
                
                Image(systemName: type.icon)
                    .font(.system(size: 24))
                    .foregroundColor(isEarned ? type.color : .gray.opacity(0.4))
            }
            
            Text(type.name)
                .font(.caption)
                .fontWeight(.medium)
                .multilineTextAlignment(.center)
                .foregroundColor(isEarned ? .primary : .secondary)
            
            if isEarned, let date = earnedAt {
                Text(date.formatted(date: .abbreviated, time: .omitted))
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .frame(width: 100, height: 110)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(nsColor: .controlBackgroundColor))
                .shadow(color: .black.opacity(isHovering ? 0.1 : 0.05), radius: isHovering ? 4 : 2)
        )
        .opacity(isEarned ? 1 : 0.6)
        .onHover { hovering in
            withAnimation(.easeInOut(duration: 0.2)) {
                isHovering = hovering
            }
        }
        .help(type.description)
    }
}

#Preview {
    BadgesView()
        .environmentObject(StreakManager.shared)
}
