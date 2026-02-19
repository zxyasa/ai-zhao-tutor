import SwiftUI

struct AchievementsView: View {
    let student: Student
    @Environment(\.dismiss) private var dismiss
    @State private var achievements: [Achievement] = []
    @State private var isLoading = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            VStack(spacing: 12) {
                if isLoading {
                    ProgressView("加载徽章中...")
                } else {
                    if let errorMessage {
                        Text(errorMessage)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .padding(8)
                            .background(Color.yellow.opacity(0.2))
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                    }

                    if achievements.isEmpty {
                        Text("还没有解锁徽章，继续练习吧。")
                            .foregroundColor(.secondary)
                    } else {
                        List(achievements) { achievement in
                            VStack(alignment: .leading, spacing: 6) {
                                Text(achievement.title)
                                    .font(.headline)
                                Text(achievement.description)
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                                Text(achievement.badgeKey)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            .padding(.vertical, 4)
                        }
                        .listStyle(.plain)
                    }
                }
            }
            .padding()
            .navigationTitle("\(student.name) 的徽章")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("关闭") { dismiss() }
                }
            }
            .task {
                await loadAchievements()
            }
        }
    }

    private func loadAchievements() async {
        isLoading = true
        errorMessage = nil

        do {
            achievements = try await APIClient.shared.fetchAchievements(studentId: student.id)
        } catch {
            errorMessage = "后端暂不可用，暂时无法加载徽章。"
            achievements = []
        }

        isLoading = false
    }
}

#Preview {
    AchievementsView(student: Student(id: "preview", name: "Preview", yearLevel: 4))
}
