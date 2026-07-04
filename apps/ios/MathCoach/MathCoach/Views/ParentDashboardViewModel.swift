import Foundation

/// Owns the server-derived state for the parent dashboard: the two summary
/// lists, the six per-student signal maps, and the loading / error flags.
///
/// UI-local state (mode picker, form inputs for add-student /
/// change-password / submit-context, seen-signal `@AppStorage`) stays on
/// `ParentDashboardView` — those belong to the sheet or picker they live on
/// and don't need an ObservableObject to coordinate.
///
/// Extracted from `ParentDashboardView` (which was juggling 26 @State
/// properties). The remaining state on the view is now cohesive form and
/// selection state, not a mix of network results and UI toggles.
@MainActor
final class ParentDashboardViewModel: ObservableObject {
    // Server-derived summary state
    @Published var summaries: [ParentDailySummary] = []
    @Published var weeklySummaries: [ParentWeeklySummary] = []

    // Per-student signal enrichment (populated after loadSummaries in daily mode)
    @Published var newBadgeCountByStudent: [String: Int] = [:]
    @Published var streakAtRiskByStudent: [String: Bool] = [:]
    @Published var learningRiskByStudent: [String: String] = [:]
    @Published var learningRiskReasonsByStudent: [String: [String]] = [:]
    @Published var progressMetricsByStudent: [String: ProgressMetricsSnapshot] = [:]
    @Published var progressTrendByStudent: [String: [ParentProgress.DayPoint]] = [:]

    // Global network state
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    /// Refresh the appropriate summary list for the current mode + enrich
    /// daily signals when in daily mode.
    func loadSummaries(mode: ParentDashboardView.Mode) async {
        isLoading = true
        errorMessage = nil

        do {
            if mode == .daily {
                let fetched = try await APIClient.shared.fetchParentDailySummaries()
                summaries = fetched.isEmpty ? fallbackSummaries() : fetched
                await enrichDailySignals(for: summaries)
            } else {
                let fetched = try await APIClient.shared.fetchParentWeeklySummaries()
                weeklySummaries = fetched.isEmpty ? fallbackWeeklySummaries() : fetched
                clearDailySignals()
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

    // MARK: - Private helpers

    /// Weekly mode doesn't need the signal maps — wipe them so old daily
    /// state doesn't linger under the weekly card.
    private func clearDailySignals() {
        newBadgeCountByStudent = [:]
        streakAtRiskByStudent = [:]
        learningRiskByStudent = [:]
        learningRiskReasonsByStudent = [:]
        progressMetricsByStudent = [:]
        progressTrendByStudent = [:]
    }

    /// Fetch three parallel-ish signal endpoints per student and store the
    /// result in the six maps. Errors are silently absorbed into empty /
    /// low-risk defaults so one failing student doesn't blank the whole
    /// dashboard.
    private func enrichDailySignals(for dailySummaries: [ParentDailySummary]) async {
        var newBadgeMap: [String: Int] = [:]
        var streakRiskMap: [String: Bool] = [:]
        var learningRiskMap: [String: String] = [:]
        var learningRiskReasonsMap: [String: [String]] = [:]
        var metricsMap: [String: ProgressMetricsSnapshot] = [:]
        var trendMap: [String: [ParentProgress.DayPoint]] = [:]

        for summary in dailySummaries {
            do {
                let newAchievements = try await APIClient.shared.fetchNewAchievements(
                    studentId: summary.studentId,
                    lookbackHours: 24
                )
                newBadgeMap[summary.studentId] = newAchievements.count
            } catch {
                newBadgeMap[summary.studentId] = 0
            }

            do {
                let streakStatus = try await APIClient.shared.fetchStreakStatus(studentId: summary.studentId)
                streakRiskMap[summary.studentId] = streakStatus.isStreakAtRisk
            } catch {
                streakRiskMap[summary.studentId] = false
            }

            do {
                let progress = try await APIClient.shared.fetchParentProgress(studentId: summary.studentId, days: 30)
                learningRiskMap[summary.studentId] = progress.riskLevel
                learningRiskReasonsMap[summary.studentId] = progress.riskReasons
                metricsMap[summary.studentId] = ProgressMetricsSnapshot(
                    completionRatePercent: progress.completionRatePercent,
                    accuracyVolatility: progress.accuracyVolatility,
                    recoverySpeedDays: progress.recoverySpeedDays
                )
                trendMap[summary.studentId] = Array(progress.timeline.suffix(7))
            } catch {
                learningRiskMap[summary.studentId] = "low"
                learningRiskReasonsMap[summary.studentId] = []
                metricsMap[summary.studentId] = ProgressMetricsSnapshot(
                    completionRatePercent: 0.0,
                    accuracyVolatility: 0.0,
                    recoverySpeedDays: nil
                )
                trendMap[summary.studentId] = []
            }
        }

        newBadgeCountByStudent = newBadgeMap
        streakAtRiskByStudent = streakRiskMap
        learningRiskByStudent = learningRiskMap
        learningRiskReasonsByStudent = learningRiskReasonsMap
        progressMetricsByStudent = metricsMap
        progressTrendByStudent = trendMap
    }

    /// Two-student demo dataset shown when the backend is unreachable.
    /// Keeps the dashboard usable in dev / offline mode.
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
                badgeCount: 0,
                aiInsight: nil
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
                badgeCount: 0,
                aiInsight: nil
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
