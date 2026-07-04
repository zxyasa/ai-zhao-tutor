import SwiftUI

/// Full-screen sheet that expands a `ParentDailySummary` into streak status,
/// risk signals, learning trend, and last-24h achievements.
///
/// Opened from `ParentDashboardView` when the parent taps any of the three
/// signal chips on a student's daily card. Owns its own network loading
/// state so the parent view isn't responsible for pre-loading the sheet's
/// data.
///
/// Extracted from `ParentDashboardView.swift` to keep the god-view under
/// 1,000 lines. Access level is `internal` (default) — the parent view is
/// in the same module.
struct StudentSignalsDetailView: View {
    let summary: ParentDailySummary
    @Environment(\.dismiss) private var dismiss
    @State private var isLoading = false
    @State private var streakStatus: StreakStatus?
    @State private var newAchievements: [Achievement] = []
    @State private var progress: ParentProgress?
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 12) {
                if isLoading {
                    ProgressView("加载中...")
                } else {
                    if let errorMessage {
                        Text(errorMessage)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }

                    if let streakStatus {
                        VStack(alignment: .leading, spacing: 6) {
                            Text("连击状态")
                                .font(.headline)
                            Text("当前连击 \(streakStatus.currentStreak) 天")
                            Text("历史最长 \(streakStatus.longestStreak) 天")
                            Text(streakStatus.isStreakAtRisk ? "⚠️ 今日需要补练保住连击" : "✅ 连击状态安全")
                                .foregroundColor(streakStatus.isStreakAtRisk ? .orange : .green)
                        }
                    }

                    Divider()

                    if let progress {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("学习风险")
                                .font(.headline)
                            HStack {
                                Text(riskBadgeText(progress.riskLevel))
                                    .font(.caption.weight(.semibold))
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 4)
                                    .background(riskColor(progress.riskLevel).opacity(0.18))
                                    .clipShape(RoundedRectangle(cornerRadius: 6))
                                Text("分值 \(progress.riskScore)")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }

                            if progress.riskReasons.isEmpty {
                                Text("暂无风险信号")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            } else {
                                Text(progress.riskReasons.map(riskReasonLabel).joined(separator: " · "))
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }

                        Divider()

                        VStack(alignment: .leading, spacing: 8) {
                            Text("学习走势")
                                .font(.headline)
                            HStack(spacing: 8) {
                                metricPill(
                                    title: "完成率",
                                    value: "\(String(format: "%.1f", progress.completionRatePercent))%"
                                )
                                metricPill(
                                    title: "波动度",
                                    value: String(format: "%.2f", progress.accuracyVolatility)
                                )
                                metricPill(
                                    title: "恢复速度",
                                    value: recoveryText(progress.recoverySpeedDays)
                                )
                            }
                        }

                        Divider()

                        VStack(alignment: .leading, spacing: 8) {
                            Text("最近7天准确率趋势")
                                .font(.headline)
                            ForEach(recentTrendPoints(progress)) { point in
                                HStack(spacing: 8) {
                                    Text(shortDate(point.date))
                                        .font(.caption2)
                                        .foregroundColor(.secondary)
                                        .frame(width: 42, alignment: .leading)

                                    ZStack(alignment: .leading) {
                                        Capsule()
                                            .fill(Color(.systemGray5))
                                            .frame(width: 140, height: 8)

                                        if point.eventsTotal > 0 {
                                            Capsule()
                                                .fill(accuracyBarColor(point.accuracyPercent))
                                                .frame(width: accuracyBarWidth(point.accuracyPercent), height: 8)
                                        }
                                    }

                                    Text(
                                        point.eventsTotal > 0
                                            ? "\(String(format: "%.0f", point.accuracyPercent))%"
                                            : "--"
                                    )
                                    .font(.caption2)
                                    .foregroundColor(.secondary)
                                }
                            }
                        }

                        Divider()
                    }

                    VStack(alignment: .leading, spacing: 8) {
                        Text("最近24小时新徽章")
                            .font(.headline)
                        if newAchievements.isEmpty {
                            Text("暂无新徽章")
                                .foregroundColor(.secondary)
                        } else {
                            ForEach(newAchievements) { achievement in
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(achievement.title).font(.subheadline.weight(.semibold))
                                    Text(achievement.description).font(.caption).foregroundColor(.secondary)
                                }
                                .padding(.vertical, 4)
                            }
                        }
                    }
                }

                Spacer()
            }
            .padding()
            .navigationTitle("\(summary.studentName) 详情")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("关闭") { dismiss() }
                }
            }
            .task {
                await loadSignals()
            }
        }
    }

    private func loadSignals() async {
        isLoading = true
        errorMessage = nil
        do {
            async let streak = APIClient.shared.fetchStreakStatus(studentId: summary.studentId)
            async let newBadge = APIClient.shared.fetchNewAchievements(studentId: summary.studentId, lookbackHours: 24)
            async let progressPayload = APIClient.shared.fetchParentProgress(studentId: summary.studentId, days: 30)
            let (streakResult, badgeResult, progressResult) = try await (streak, newBadge, progressPayload)
            streakStatus = streakResult
            newAchievements = badgeResult.items
            progress = progressResult
        } catch {
            errorMessage = "加载失败：\(error.localizedDescription)"
        }
        isLoading = false
    }

    private func riskBadgeText(_ level: String) -> String {
        switch level {
        case "high":
            return "高风险"
        case "medium":
            return "中风险"
        default:
            return "低风险"
        }
    }

    private func riskColor(_ level: String) -> Color {
        switch level {
        case "high":
            return .red
        case "medium":
            return .orange
        default:
            return .green
        }
    }

    @ViewBuilder
    private func metricPill(title: String, value: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title)
                .font(.caption2)
                .foregroundColor(.secondary)
            Text(value)
                .font(.caption.weight(.semibold))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 8)
        .padding(.vertical, 6)
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }

    private func recoveryText(_ days: Int?) -> String {
        if let days {
            return "\(days) 天"
        }
        return "未恢复"
    }

    private func recentTrendPoints(_ progress: ParentProgress) -> [ParentProgress.DayPoint] {
        Array(progress.timeline.suffix(7))
    }

    private func shortDate(_ isoDate: String) -> String {
        String(isoDate.suffix(5))
    }

    private func accuracyBarWidth(_ accuracy: Double) -> CGFloat {
        let bounded = min(max(accuracy, 0.0), 100.0)
        return max(4, CGFloat(bounded / 100.0) * 140.0)
    }

    private func accuracyBarColor(_ accuracy: Double) -> Color {
        if accuracy >= 80 {
            return .green
        }
        if accuracy >= 60 {
            return .orange
        }
        return .red
    }
}
