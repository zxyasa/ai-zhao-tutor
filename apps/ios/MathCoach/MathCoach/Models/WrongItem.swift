//
//  WrongItem.swift
//  MathCoach
//
//  Mistake-book entry returned by GET /api/v1/wrong-items.
//

import Foundation

struct WrongItem: Codable, Identifiable {
    let itemId: String
    let skillId: String
    let questionText: String
    let yourAnswer: String
    let correctAnswer: String
    let explanation: String
    let timestamp: Date

    var id: String { itemId + timestamp.description }

    enum CodingKeys: String, CodingKey {
        case itemId = "item_id"
        case skillId = "skill_id"
        case questionText = "question_text"
        case yourAnswer = "your_answer"
        case correctAnswer = "correct_answer"
        case explanation
        case timestamp
    }

    init(
        itemId: String,
        skillId: String,
        questionText: String,
        yourAnswer: String,
        correctAnswer: String,
        explanation: String,
        timestamp: Date
    ) {
        self.itemId = itemId
        self.skillId = skillId
        self.questionText = questionText
        self.yourAnswer = yourAnswer
        self.correctAnswer = correctAnswer
        self.explanation = explanation
        self.timestamp = timestamp
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        itemId = try container.decode(String.self, forKey: .itemId)
        skillId = try container.decode(String.self, forKey: .skillId)
        questionText = try container.decode(String.self, forKey: .questionText)
        yourAnswer = try container.decode(String.self, forKey: .yourAnswer)
        correctAnswer = try container.decode(String.self, forKey: .correctAnswer)
        explanation = try container.decode(String.self, forKey: .explanation)

        if let dateString = try? container.decode(String.self, forKey: .timestamp) {
            let isoFractional = ISO8601DateFormatter()
            isoFractional.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
            if let parsed = isoFractional.date(from: dateString) {
                timestamp = parsed
            } else {
                let iso = ISO8601DateFormatter()
                timestamp = iso.date(from: dateString) ?? Date()
            }
        } else {
            timestamp = try container.decode(Date.self, forKey: .timestamp)
        }
    }
}
