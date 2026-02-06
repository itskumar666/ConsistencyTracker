import SwiftUI

struct AddActivityView: View {
    @EnvironmentObject var streakManager: StreakManager
    @Environment(\.dismiss) private var dismiss
    
    @State private var name: String = ""
    @State private var selectedIcon: String = "star.fill"
    @State private var selectedColor: String = "blue"
    @State private var showCustom = false
    
    let colors = ["red", "orange", "yellow", "green", "blue", "purple", "pink", "mint", "cyan", "indigo"]
    
    let icons = [
        "star.fill", "heart.fill", "bolt.fill", "leaf.fill", "book.fill",
        "pencil", "laptopcomputer", "gamecontroller.fill", "music.note", "paintbrush.fill",
        "figure.run", "brain.head.profile", "lightbulb.fill", "graduationcap.fill", "hammer.fill",
        "chevron.left.forwardslash.chevron.right", "doc.text.fill", "camera.fill", "mic.fill", "chart.line.uptrend.xyaxis"
    ]
    
    var body: some View {
        VStack(spacing: 20) {
            // Header
            Text("Add Activity")
                .font(.title2)
                .fontWeight(.bold)
            
            // Presets
            VStack(alignment: .leading, spacing: 12) {
                Text("Quick Add")
                    .font(.headline)
                
                LazyVGrid(columns: [GridItem(.adaptive(minimum: 130))], spacing: 8) {
                    ForEach(ActivityPresets.all, id: \.name) { preset in
                        Button {
                            addPreset(preset)
                        } label: {
                            HStack {
                                Image(systemName: preset.icon)
                                    .foregroundColor(colorValue(preset.color))
                                Text(preset.name)
                                    .foregroundColor(.primary)
                            }
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                            .frame(maxWidth: .infinity)
                            .background(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(colorValue(preset.color), lineWidth: 1)
                            )
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
            
            Divider()
            
            // Custom Activity
            DisclosureGroup("Custom Activity", isExpanded: $showCustom) {
                VStack(spacing: 16) {
                    // Name
                    TextField("Activity Name", text: $name)
                        .textFieldStyle(.roundedBorder)
                    
                    // Icon Picker
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Icon")
                            .font(.subheadline)
                            .fontWeight(.medium)
                        
                        LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 10), spacing: 8) {
                            ForEach(icons, id: \.self) { icon in
                                Button {
                                    selectedIcon = icon
                                } label: {
                                    Image(systemName: icon)
                                        .font(.system(size: 18))
                                        .frame(width: 32, height: 32)
                                        .background(
                                            RoundedRectangle(cornerRadius: 6)
                                                .fill(selectedIcon == icon ? colorValue(selectedColor).opacity(0.3) : Color.clear)
                                        )
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 6)
                                                .stroke(selectedIcon == icon ? colorValue(selectedColor) : Color.clear, lineWidth: 2)
                                        )
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }
                    
                    // Color Picker
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Color")
                            .font(.subheadline)
                            .fontWeight(.medium)
                        
                        HStack(spacing: 8) {
                            ForEach(colors, id: \.self) { color in
                                Button {
                                    selectedColor = color
                                } label: {
                                    Circle()
                                        .fill(colorValue(color))
                                        .frame(width: 28, height: 28)
                                        .overlay(
                                            Circle()
                                                .stroke(Color.white, lineWidth: selectedColor == color ? 3 : 0)
                                        )
                                        .shadow(color: .black.opacity(0.2), radius: 2)
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }
                    
                    // Preview
                    HStack {
                        Text("Preview:")
                            .foregroundColor(.secondary)
                        
                        HStack(spacing: 8) {
                            ZStack {
                                Circle()
                                    .fill(colorValue(selectedColor).opacity(0.2))
                                    .frame(width: 36, height: 36)
                                
                                Image(systemName: selectedIcon)
                                    .foregroundColor(colorValue(selectedColor))
                            }
                            
                            Text(name.isEmpty ? "Activity Name" : name)
                                .fontWeight(.medium)
                        }
                    }
                    
                    Button {
                        if !name.isEmpty {
                            streakManager.addActivity(name: name, icon: selectedIcon, color: selectedColor)
                            dismiss()
                        }
                    } label: {
                        Text("Add Custom Activity")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(name.isEmpty)
                }
                .padding(.top, 12)
            }
            
            Spacer()
            
            Button("Cancel") {
                dismiss()
            }
            .buttonStyle(.plain)
        }
        .padding(24)
        .frame(width: 450, height: 550)
    }
    
    private func addPreset(_ preset: (name: String, icon: String, color: String)) {
        streakManager.addActivity(name: preset.name, icon: preset.icon, color: preset.color)
        dismiss()
    }
    
    private func colorValue(_ color: String) -> Color {
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
}

#Preview {
    AddActivityView()
        .environmentObject(StreakManager.shared)
}
