import SwiftUI

/// Which signal chip on a daily card the parent tapped.
///
/// File-scoped so `DailySummaryCardView` and `ParentDashboardView` can both
/// reference it. Was previously nested inside `ParentDashboardView`.
enum SignalKind: String {
    case newBadge
    case streakRisk
    case learningRisk
}

/// Per-student trend + volatility snapshot rendered on the daily card.
///
/// File-scoped so the enrichment code in `ParentDashboardView` and the
/// display code in `DailySummaryCardView` share one struct definition.
struct ProgressMetricsSnapshot {
    let completionRatePercent: Double
    let accuracyVolatility: Double
    let recoverySpeedDays: Int?
}

/// All the per-student signal state a `DailySummaryCardView` needs to render
/// its chips and inline trend. Bundling the six upstream `@State` maps into
/// one struct keeps the card view's prop list to three values.
struct DailySummarySignals {
    let newBadgeCount: Int
    let streakAtRisk: Bool
    let learningRiskLevel: String?
    let learningRiskReasons: [String]
    let progressMetrics: ProgressMetricsSnapshot?
    let progressTrend: [ParentProgress.DayPoint]?
    let badgeUnread: Bool
    let streakUnread: Bool
    let learningUnread: Bool

    static let empty = DailySummarySignals(
        newBadgeCount: 0,
        streakAtRisk: false,
        learningRiskLevel: nil,
        learningRiskReasons: [],
        progressMetrics: nil,
        progressTrend: nil,
        badgeUnread: false,
        streakUnread: false,
        learningUnread: false
    )
}

/// One student's daily summary card — badges/streak header, risk chips, trend
/// bars, and progress/accuracy footer.
///
/// Extracted from the 1,145-line `ParentDashboardView.swift` so future
/// signals don't have to be threaded through another map on the parent view.
/// Pure display: no `@State`, no network calls, no auth.
struct DailySummaryCardView: View {
    let summary: ParentDailySummary
    let signals: DailySummarySignals
    let onSignalTapped: (SignalKind) -> Void

    var body: some View {
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

                    if signals.newBadgeCount > 0 {
                        Button("🆕 今日新徽章 \(signals.newBadgeCount)") {
                            onSignalTapped(.newBadge)
                        }
                        .buttonStyle(.plain)
                        .font(.caption)
                        .foregroundColor(signals.badgeUnread ? .green : .secondary)
                    }

                    if signals.streakAtRisk {
                        Button("⚠️ 连击今天有中断风险") {
                            onSignalTapped(.streakRisk)
                        }
                        .buttonStyle(.plain)
                        .font(.caption)
                        .foregroundColor(signals.streakUnread ? .orange : .secondary)
                    }

                    if let riskLevel = signals.learningRiskLevel,
                       riskLevel == "high" || riskLevel == "medium" {
                        Button("📉 学习风险：\(riskLevelLabel(riskLevel))") {
                            onSignalTapped(.learningRisk)
                        }
                        .buttonStyle(.plain)
                        .font(.caption)
                        .foregroundColor(signals.learningUnread ? riskLevelColor(riskLevel) : .secondary)
                    }

                    if !signals.learningRiskReasons.isEmpty {
                        Text("主要信号 \(riskReasonLabel(signals.learningRiskReasons[0]))")
                            .font(.caption2.weight(.medium))
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(riskLevelColor(signals.learningRiskLevel ?? "low").opacity(0.12))
                            .foregroundColor(.secondary)
                            .clipShape(RoundedRectangle(cornerRadius: 6))
                    }

                    if let metrics = signals.progressMetrics {
                        Text(
                            "完成率 \(String(format: "%.0f", metrics.completionRatePercent))% · " +
                            "波动 \(String(format: "%.2f", metrics.accuracyVolatility)) · " +
                            "恢复 \(metrics.recoverySpeedDays.map { "\($0)天" } ?? "未恢复")"
                        )
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    }

                    if let trend = signals.progressTrend, !trend.isEmpty {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("最近7天准确率")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                            HStack(alignment: .bottom, spacing: 4) {
                                ForEach(trend) { point in
                                    Capsule()
                                        .fill(cardTrendBarColor(point.accuracyPercent, hasData: point.eventsTotal > 0))
                                        .frame(
                                            width: 10,
                                            height: cardTrendBarHeight(point.accuracyPercent, hasData: point.eventsTotal > 0)
                                        )
                                }
                            }
                        }
                    }

                    if let aiInsight = summary.aiInsight,
                       !aiInsight.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                        Text("AI 洞察：\(aiInsight)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .padding(.top, 2)
                    }
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
        .clipShape(RoundedRectangle(cornerRadius: 14))
        .overlay(
            RoundedRectangle(cornerRadius: 14)
                .stroke(Color.primary.opacity(0.06), lineWidth: 1)
        )
        .shadow(color: Color.black.opacity(0.03), radius: 8, x: 0, y: 4)
    }

    // MARK: - Private helpers

    /// Compact chip label ("高"/"中"/"低") — matches the pre-extraction summary
    /// card. The full-sheet detail view uses its own longer form (`riskBadgeText`).
    private func riskLevelLabel(_ level: String) -> String {
        switch level {
        case "high":
            return "高"
        case "medium":
            return "中"
        default:
            return "低"
        }
    }

    private func riskLevelColor(_ level: String) -> Color {
        switch level {
        case "high":
            return .red
        case "medium":
            return .orange
        default:
            return .green
        }
    }

    private func cardTrendBarHeight(_ accuracy: Double, hasData: Bool) -> CGFloat {
        guard hasData else { return 6 }
        let bounded = min(max(accuracy, 0.0), 100.0)
        return max(8, CGFloat(bounded / 100.0) * 26.0)
    }

    private func cardTrendBarColor(_ accuracy: Double, hasData: Bool) -> Color {
        guard hasData else { return Color(.systemGray4) }
        if accuracy >= 80 { return .green }
        if accuracy >= 60 { return .orange }
        return .red
    }
}
