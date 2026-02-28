import Foundation

struct ParentProgress: Codable {
    struct DayPoint: Codable, Identifiable {
        let date: String
        let completedQuestions: Int
        let targetQuestions: Int
        let isCompleted: Bool
        let eventsTotal: Int
        let correctAnswers: Int
        let accuracyPercent: Double
        let averageTimeSpentSeconds: Double

        enum CodingKeys: String, CodingKey {
            case date
            case completedQuestions = "completed_questions"
            case targetQuestions = "target_questions"
            case isCompleted = "is_completed"
            case eventsTotal = "events_total"
            case correctAnswers = "correct_answers"
            case accuracyPercent = "accuracy_percent"
            case averageTimeSpentSeconds = "average_time_spent_seconds"
        }

        var id: String { date }
    }

    let studentId: String
    let studentName: String
    let avatar: String
    let fromDate: String
    let toDate: String
    let days: Int
    let currentStreak: Int
    let longestStreak: Int
    let riskLevel: String
    let riskScore: Int
    let riskReasons: [String]
    let completionRatePercent: Double
    let accuracyVolatility: Double
    let recoverySpeedDays: Int?
    let timeline: [DayPoint]

    enum CodingKeys: String, CodingKey {
        case studentId = "student_id"
        case studentName = "student_name"
        case avatar
        case fromDate = "from_date"
        case toDate = "to_date"
        case days
        case currentStreak = "current_streak"
        case longestStreak = "longest_streak"
        case riskLevel = "risk_level"
        case riskScore = "risk_score"
        case riskReasons = "risk_reasons"
        case completionRatePercent = "completion_rate_percent"
        case accuracyVolatility = "accuracy_volatility"
        case recoverySpeedDays = "recovery_speed_days"
        case timeline
    }
}
