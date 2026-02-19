import SwiftUI

struct ParentDashboardView: View {
    enum Mode: String, CaseIterable {
        case daily = "日报"
        case weekly = "周报"
    }

    @Environment(\.dismiss) private var dismiss
    @State private var mode: Mode = .daily
    @State private var summaries: [ParentDailySummary] = []
    @State private var weeklySummaries: [ParentWeeklySummary] = []
    @State private var isLoading = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            VStack(spacing: 12) {
                if isLoading {
                    ProgressView("加载日报中...")
                } else {
                    Picker("模式", selection: $mode) {
                        ForEach(Mode.allCases, id: \.self) { m in
                            Text(m.rawValue).tag(m)
                        }
                    }
                    .pickerStyle(.segmented)

                    if let errorMessage {
                        Text(errorMessage)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .padding(8)
                            .background(Color.yellow.opacity(0.2))
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                    }

                    ScrollView {
                        VStack(spacing: 12) {
                            if mode == .daily {
                                ForEach(summaries) { summary in
                                    summaryCard(summary)
                                }
                            } else {
                                ForEach(weeklySummaries) { summary in
                                    weeklyCard(summary)
                                }
                            }
                        }
                    }

                    Button("刷新") {
                        Task { await loadSummaries() }
                    }
                    .buttonStyle(.bordered)
                }
            }
            .padding()
            .navigationTitle("家长日报")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("关闭") { dismiss() }
                }
            }
            .task {
                await loadSummaries()
            }
            .onChange(of: mode) { _, _ in
                Task { await loadSummaries() }
            }
        }
    }

    private func summaryCard(_ summary: ParentDailySummary) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(summary.avatarEmoji)
                    .font(.system(size: 36))
                VStack(alignment: .leading) {
                    Text(summary.studentName)
                        .font(.headline)
                    Text("连击 \(summary.currentStreak) 天 (历史 \(summary.longestStreak))")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Text("徽章 \(summary.badgeCount)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                Spacer()
                Text(summary.isCompleted ? "完成" : "进行中")
                    .font(.caption.weight(.semibold))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(summary.isCompleted ? Color.green.opacity(0.2) : Color.orange.opacity(0.2))
                    .clipShape(RoundedRectangle(cornerRadius: 6))
            }

            HStack {
                Text("进度 \(summary.completedQuestions)/\(summary.targetQuestions)")
                Spacer()
                Text("正确率 \(String(format: "%.1f", summary.accuracyPercent))%")
            }
            .font(.subheadline)

            HStack {
                Text("答题数 \(summary.eventsTotal)")
                Spacer()
                Text("平均耗时 \(String(format: "%.1f", summary.averageTimeSpentSeconds))s")
            }
            .font(.subheadline)
            .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private func loadSummaries() async {
        isLoading = true
        errorMessage = nil

        do {
            if mode == .daily {
                let fetched = try await APIClient.shared.fetchParentDailySummaries()
                summaries = fetched.isEmpty ? fallbackSummaries() : fetched
            } else {
                let fetched = try await APIClient.shared.fetchParentWeeklySummaries()
                weeklySummaries = fetched.isEmpty ? fallbackWeeklySummaries() : fetched
            }
        } catch {
            if mode == .daily {
                summaries = fallbackSummaries()
            } else {
                weeklySummaries = fallbackWeeklySummaries()
            }
            errorMessage = "后端暂不可用，显示本地示例数据。"
        }

        isLoading = false
    }

    private func weeklyCard(_ summary: ParentWeeklySummary) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(summary.avatarEmoji)
                    .font(.system(size: 36))
                VStack(alignment: .leading) {
                    Text(summary.studentName)
                        .font(.headline)
                    Text("\(summary.fromDate) - \(summary.toDate)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                Spacer()
                Text("连击 \(summary.currentStreak)")
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.blue.opacity(0.15))
                    .clipShape(RoundedRectangle(cornerRadius: 6))
            }

            HStack {
                Text("达标天数 \(summary.completedDays)/7")
                Spacer()
                Text("周正确率 \(String(format: "%.1f", summary.accuracyPercent))%")
            }
            .font(.subheadline)

            HStack {
                Text("完成题数 \(summary.totalCompletedQuestions)")
                Spacer()
                Text("答题数 \(summary.totalEvents)")
            }
            .font(.subheadline)
            .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private func fallbackSummaries() -> [ParentDailySummary] {
        [
            ParentDailySummary(
                studentId: "jon_zhao",
                studentName: "Jon",
                avatar: "lion",
                sessionDate: "2026-02-18",
                completedQuestions: 0,
                targetQuestions: 10,
                isCompleted: false,
                eventsTotal: 0,
                correctAnswers: 0,
                accuracyPercent: 0,
                averageTimeSpentSeconds: 0,
                currentStreak: 0,
                longestStreak: 0,
                badgeCount: 0
            ),
            ParentDailySummary(
                studentId: "astrid_zhao",
                studentName: "Astrid",
                avatar: "unicorn",
                sessionDate: "2026-02-18",
                completedQuestions: 0,
                targetQuestions: 10,
                isCompleted: false,
                eventsTotal: 0,
                correctAnswers: 0,
                accuracyPercent: 0,
                averageTimeSpentSeconds: 0,
                currentStreak: 0,
                longestStreak: 0,
                badgeCount: 0
            ),
        ]
    }

    private func fallbackWeeklySummaries() -> [ParentWeeklySummary] {
        [
            ParentWeeklySummary(
                studentId: "jon_zhao",
                studentName: "Jon",
                avatar: "lion",
                fromDate: "2026-02-12",
                toDate: "2026-02-18",
                completedDays: 0,
                totalCompletedQuestions: 0,
                totalEvents: 0,
                accuracyPercent: 0,
                currentStreak: 0,
                longestStreak: 0
            ),
            ParentWeeklySummary(
                studentId: "astrid_zhao",
                studentName: "Astrid",
                avatar: "unicorn",
                fromDate: "2026-02-12",
                toDate: "2026-02-18",
                completedDays: 0,
                totalCompletedQuestions: 0,
                totalEvents: 0,
                accuracyPercent: 0,
                currentStreak: 0,
                longestStreak: 0
            ),
        ]
    }
}

#Preview {
    ParentDashboardView()
}
