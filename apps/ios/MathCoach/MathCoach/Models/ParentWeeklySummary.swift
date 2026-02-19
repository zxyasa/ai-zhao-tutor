import Foundation

struct ParentWeeklySummary: Codable, Identifiable {
    let studentId: String
    let studentName: String
    let avatar: String
    let fromDate: String
    let toDate: String
    let completedDays: Int
    let totalCompletedQuestions: Int
    let totalEvents: Int
    let accuracyPercent: Double
    let currentStreak: Int
    let longestStreak: Int

    enum CodingKeys: String, CodingKey {
        case studentId = "student_id"
        case studentName = "student_name"
        case avatar
        case fromDate = "from_date"
        case toDate = "to_date"
        case completedDays = "completed_days"
        case totalCompletedQuestions = "total_completed_questions"
        case totalEvents = "total_events"
        case accuracyPercent = "accuracy_percent"
        case currentStreak = "current_streak"
        case longestStreak = "longest_streak"
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
