import SwiftUI

/// One student's weekly rollup card — header, totals, and three trend bars
/// for 达标率 / 准确率 / 练习量.
///
/// Pure display: no `@State`, no network calls, no signals maps to worry
/// about (unlike `DailySummaryCardView`, weekly mode doesn't render risk
/// or badge chips). Just the summary struct in, the card out.
///
/// Extracted from `ParentDashboardView` to finish clearing per-mode card
/// rendering out of the parent view.
struct WeeklySummaryCardView: View {
    let summary: ParentWeeklySummary

    var body: some View {
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

            Divider()

            VStack(alignment: .leading, spacing: 6) {
                Text("周趋势")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.secondary)
                weeklyMetricBar(
                    title: "达标率",
                    value: "\(String(format: "%.0f", (Double(summary.completedDays) / 7.0) * 100.0))%",
                    percent: (Double(summary.completedDays) / 7.0) * 100.0,
                    color: .blue
                )
                weeklyMetricBar(
                    title: "准确率",
                    value: "\(String(format: "%.1f", summary.accuracyPercent))%",
                    percent: summary.accuracyPercent,
                    color: .green
                )
                weeklyMetricBar(
                    title: "练习量",
                    value: "\(summary.totalEvents)",
                    percent: min(Double(summary.totalEvents) / 70.0 * 100.0, 100.0),
                    color: .orange
                )
            }
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

    @ViewBuilder
    private func weeklyMetricBar(title: String, value: String, percent: Double, color: Color) -> some View {
        HStack(spacing: 8) {
            Text(title)
                .font(.caption2)
                .foregroundColor(.secondary)
                .frame(width: 34, alignment: .leading)

            ZStack(alignment: .leading) {
                Capsule()
                    .fill(Color(.systemGray5))
                    .frame(height: 8)

                Capsule()
                    .fill(color.opacity(0.85))
                    .frame(width: weeklyBarWidth(percent), height: 8)
            }
            .frame(maxWidth: .infinity)

            Text(value)
                .font(.caption2.weight(.semibold))
                .foregroundColor(.secondary)
                .frame(width: 48, alignment: .trailing)
        }
    }

    private func weeklyBarWidth(_ percent: Double) -> CGFloat {
        let bounded = min(max(percent, 0.0), 100.0)
        return max(8, CGFloat(bounded / 100.0) * 160.0)
    }
}
