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
