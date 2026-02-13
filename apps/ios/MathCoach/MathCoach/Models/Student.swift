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
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case yearLevel = "year_level"
        case createdAt = "created_at"
    }

    init(id: String, name: String, yearLevel: Int, createdAt: Date = Date()) {
        self.id = id
        self.name = name
        self.yearLevel = yearLevel
        self.createdAt = createdAt
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        yearLevel = try container.decode(Int.self, forKey: .yearLevel)

        // Try to decode date as string first, then as Date
        if let dateString = try? container.decode(String.self, forKey: .createdAt) {
            let formatter = ISO8601DateFormatter()
            createdAt = formatter.date(from: dateString) ?? Date()
        } else {
            createdAt = try container.decode(Date.self, forKey: .createdAt)
        }
    }
}
