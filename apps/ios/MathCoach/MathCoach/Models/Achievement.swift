import Foundation

struct Achievement: Codable, Identifiable {
    let id: String
    let studentId: String
    let badgeKey: String
    let title: String
    let description: String
    let unlockedAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case studentId = "student_id"
        case badgeKey = "badge_key"
        case title
        case description
        case unlockedAt = "unlocked_at"
    }
}

struct NewAchievementsResponse: Codable {
    let studentId: String
    let since: Date
    let count: Int
    let items: [Achievement]

    enum CodingKeys: String, CodingKey {
        case studentId = "student_id"
        case since
        case count
        case items
    }
}

struct StreakStatus: Codable {
    let studentId: String
    let currentStreak: Int
    let longestStreak: Int
    let lastPracticeDate: Date?
    let practicedToday: Bool
    let daysSinceLastPractice: Int?
    let isStreakAtRisk: Bool

    enum CodingKeys: String, CodingKey {
        case studentId = "student_id"
        case currentStreak = "current_streak"
        case longestStreak = "longest_streak"
        case lastPracticeDate = "last_practice_date"
        case practicedToday = "practiced_today"
        case daysSinceLastPractice = "days_since_last_practice"
        case isStreakAtRisk = "is_streak_at_risk"
    }
}
