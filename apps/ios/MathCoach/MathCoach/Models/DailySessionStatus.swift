import Foundation

struct DailySessionStatus: Codable {
    let studentId: String
    let sessionDate: String
    let completedQuestions: Int
    let targetQuestions: Int
    let isCompleted: Bool
    let currentStreak: Int?
    let longestStreak: Int?

    enum CodingKeys: String, CodingKey {
        case studentId = "student_id"
        case sessionDate = "session_date"
        case completedQuestions = "completed_questions"
        case targetQuestions = "target_questions"
        case isCompleted = "is_completed"
        case currentStreak = "current_streak"
        case longestStreak = "longest_streak"
    }
}
