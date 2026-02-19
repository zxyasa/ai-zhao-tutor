import Foundation

struct ParentDailySummary: Codable, Identifiable {
    let studentId: String
    let studentName: String
    let avatar: String
    let sessionDate: String
    let completedQuestions: Int
    let targetQuestions: Int
    let isCompleted: Bool
    let eventsTotal: Int
    let correctAnswers: Int
    let accuracyPercent: Double
    let averageTimeSpentSeconds: Double
    let currentStreak: Int
    let longestStreak: Int
    let badgeCount: Int

    enum CodingKeys: String, CodingKey {
        case studentId = "student_id"
        case studentName = "student_name"
        case avatar
        case sessionDate = "session_date"
        case completedQuestions = "completed_questions"
        case targetQuestions = "target_questions"
        case isCompleted = "is_completed"
        case eventsTotal = "events_total"
        case correctAnswers = "correct_answers"
        case accuracyPercent = "accuracy_percent"
        case averageTimeSpentSeconds = "average_time_spent_seconds"
        case currentStreak = "current_streak"
        case longestStreak = "longest_streak"
        case badgeCount = "badge_count"
    }

    var id: String { studentId }

    var avatarEmoji: String {
        switch avatar {
        case "lion":
            return "🦁"
        case "unicorn":
            return "🦄"
        case "fox":
            return "🦊"
        case "owl":
            return "🦉"
        default:
            return "⭐️"
        }
    }
}
