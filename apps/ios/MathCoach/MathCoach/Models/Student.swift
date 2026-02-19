//
//  Student.swift
//  MathCoach
//
//  Student profile model
//

import Foundation

struct Student: Codable, Identifiable {
    let id: String
    let name: String
    let yearLevel: Int
    let avatar: String
    let targetDailyQuestions: Int
    let currentStreak: Int
    let longestStreak: Int
    let lastPracticeDate: Date?
    let totalSessions: Int
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case yearLevel = "year_level"
        case avatar
        case targetDailyQuestions = "target_daily_questions"
        case currentStreak = "current_streak"
        case longestStreak = "longest_streak"
        case lastPracticeDate = "last_practice_date"
        case totalSessions = "total_sessions"
        case createdAt = "created_at"
    }

    init(
        id: String,
        name: String,
        yearLevel: Int,
        avatar: String = "star",
        targetDailyQuestions: Int = 10,
        currentStreak: Int = 0,
        longestStreak: Int = 0,
        lastPracticeDate: Date? = nil,
        totalSessions: Int = 0,
        createdAt: Date = Date()
    ) {
        self.id = id
        self.name = name
        self.yearLevel = yearLevel
        self.avatar = avatar
        self.targetDailyQuestions = targetDailyQuestions
        self.currentStreak = currentStreak
        self.longestStreak = longestStreak
        self.lastPracticeDate = lastPracticeDate
        self.totalSessions = totalSessions
        self.createdAt = createdAt
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        yearLevel = try container.decode(Int.self, forKey: .yearLevel)
        avatar = try container.decodeIfPresent(String.self, forKey: .avatar) ?? "star"
        targetDailyQuestions = try container.decodeIfPresent(Int.self, forKey: .targetDailyQuestions) ?? 10
        currentStreak = try container.decodeIfPresent(Int.self, forKey: .currentStreak) ?? 0
        longestStreak = try container.decodeIfPresent(Int.self, forKey: .longestStreak) ?? 0
        totalSessions = try container.decodeIfPresent(Int.self, forKey: .totalSessions) ?? 0

        if let practiceDate = try? container.decode(String.self, forKey: .lastPracticeDate) {
            let formatter = ISO8601DateFormatter()
            if let parsed = formatter.date(from: practiceDate) {
                lastPracticeDate = parsed
            } else {
                let dateFormatter = DateFormatter()
                dateFormatter.dateFormat = "yyyy-MM-dd"
                dateFormatter.locale = Locale(identifier: "en_US_POSIX")
                lastPracticeDate = dateFormatter.date(from: practiceDate)
            }
        } else {
            lastPracticeDate = try container.decodeIfPresent(Date.self, forKey: .lastPracticeDate)
        }

        // Try to decode date as string first, then as Date
        if let dateString = try? container.decode(String.self, forKey: .createdAt) {
            let formatter = ISO8601DateFormatter()
            createdAt = formatter.date(from: dateString) ?? Date()
        } else {
            createdAt = try container.decode(Date.self, forKey: .createdAt)
        }
    }

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
