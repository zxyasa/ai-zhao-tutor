//
//  Mastery.swift
//  MathCoach
//
//  Student skill mastery model
//

import Foundation

struct Mastery: Codable, Identifiable {
    let studentId: String
    let skillId: String
    let totalAttempts: Int
    let correctAttempts: Int
    let masteryScore: Double
    let lastUpdated: Date

    // Composite ID for Identifiable
    var id: String {
        "\(studentId)_\(skillId)"
    }

    enum CodingKeys: String, CodingKey {
        case studentId = "student_id"
        case skillId = "skill_id"
        case totalAttempts = "total_attempts"
        case correctAttempts = "correct_attempts"
        case masteryScore = "mastery_score"
        case lastUpdated = "last_updated"
    }

    init(
        studentId: String,
        skillId: String,
        totalAttempts: Int,
        correctAttempts: Int,
        masteryScore: Double,
        lastUpdated: Date = Date()
    ) {
        self.studentId = studentId
        self.skillId = skillId
        self.totalAttempts = totalAttempts
        self.correctAttempts = correctAttempts
        self.masteryScore = masteryScore
        self.lastUpdated = lastUpdated
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        studentId = try container.decode(String.self, forKey: .studentId)
        skillId = try container.decode(String.self, forKey: .skillId)
        totalAttempts = try container.decode(Int.self, forKey: .totalAttempts)
        correctAttempts = try container.decode(Int.self, forKey: .correctAttempts)
        masteryScore = try container.decode(Double.self, forKey: .masteryScore)

        // Try to decode date as string first, then as Date
        if let dateString = try? container.decode(String.self, forKey: .lastUpdated) {
            let formatter = ISO8601DateFormatter()
            lastUpdated = formatter.date(from: dateString) ?? Date()
        } else {
            lastUpdated = try container.decode(Date.self, forKey: .lastUpdated)
        }
    }

    // Computed property: mastery percentage
    var masteryPercentage: Double {
        guard totalAttempts > 0 else { return 0 }
        return (Double(correctAttempts) / Double(totalAttempts)) * 100
    }

    // Computed property: mastery level label
    var masteryLevel: String {
        switch masteryScore {
        case 0..<0.3:
            return "Beginner"
        case 0.3..<0.6:
            return "Developing"
        case 0.6..<0.8:
            return "Proficient"
        case 0.8...1.0:
            return "Mastered"
        default:
            return "Unknown"
        }
    }
}
