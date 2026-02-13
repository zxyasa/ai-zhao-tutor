//
//  Event.swift
//  MathCoach
//
//  Answer submission event model
//

import Foundation

struct Event: Codable {
    let eventId: String
    let studentId: String
    let itemId: String
    let answerGiven: String
    let isCorrect: Bool
    let timeSpent: Double
    let hintRequested: Bool
    let timestamp: Date

    enum CodingKeys: String, CodingKey {
        case eventId = "event_id"
        case studentId = "student_id"
        case itemId = "item_id"
        case answerGiven = "answer_given"
        case isCorrect = "is_correct"
        case timeSpent = "time_spent"
        case hintRequested = "hint_requested"
        case timestamp
    }

    init(
        eventId: String = UUID().uuidString,
        studentId: String,
        itemId: String,
        answerGiven: String,
        isCorrect: Bool,
        timeSpent: Double,
        hintRequested: Bool = false,
        timestamp: Date = Date()
    ) {
        self.eventId = eventId
        self.studentId = studentId
        self.itemId = itemId
        self.answerGiven = answerGiven
        self.isCorrect = isCorrect
        self.timeSpent = timeSpent
        self.hintRequested = hintRequested
        self.timestamp = timestamp
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        eventId = try container.decode(String.self, forKey: .eventId)
        studentId = try container.decode(String.self, forKey: .studentId)
        itemId = try container.decode(String.self, forKey: .itemId)
        answerGiven = try container.decode(String.self, forKey: .answerGiven)
        isCorrect = try container.decode(Bool.self, forKey: .isCorrect)
        timeSpent = try container.decode(Double.self, forKey: .timeSpent)
        hintRequested = try container.decode(Bool.self, forKey: .hintRequested)

        // Try to decode date as string first, then as Date
        if let dateString = try? container.decode(String.self, forKey: .timestamp) {
            let formatter = ISO8601DateFormatter()
            timestamp = formatter.date(from: dateString) ?? Date()
        } else {
            timestamp = try container.decode(Date.self, forKey: .timestamp)
        }
    }
}
