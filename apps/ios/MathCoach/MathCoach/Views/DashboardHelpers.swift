import Foundation

/// Convert backend `risk_reasons` codes into user-facing Chinese labels.
///
/// Shared by `ParentDashboardView` (compact chip on the summary card) and
/// `StudentSignalsDetailView` (full-detail listing) — extracted here so both
/// call sites hit the same source of truth. Formerly a file-private function
/// in `ParentDashboardView.swift`.
func riskReasonLabel(_ reason: String) -> String {
    switch reason {
    case "low_recent_accuracy":
        return "近期正确率偏低"
    case "high_recent_time_spent":
        return "近期耗时偏高"
    case "consecutive_wrong_answers":
        return "连续错误偏多"
    default:
        return reason
    }
}
