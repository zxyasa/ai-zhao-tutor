import Foundation

struct AuthTokenResponse: Codable {
    let accessToken: String
    let tokenType: String
    let role: String
    let subject: String
    let parentId: String?

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case tokenType = "token_type"
        case role
        case subject
        case parentId = "parent_id"
    }
}
