//
//  APIClient.swift
//  MathCoach
//
//  API client for backend communication
//

import Foundation

extension Notification.Name {
    static let apiClientUnauthorized = Notification.Name("apiClientUnauthorized")
}

enum APIError: Error, LocalizedError {
    case invalidURL
    case noData
    case decodingError(Error)
    case serverError(String)
    case networkError(Error)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid API URL"
        case .noData:
            return "No data received from server"
        case .decodingError(let error):
            return "Failed to decode response: \(error.localizedDescription)"
        case .serverError(let message):
            return "Server error: \(message)"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription). Please check if the backend server is running on http://localhost:8000"
        }
    }
}

class APIClient {
    static let shared = APIClient()
    static let authTokenDefaultsKey = "auth_access_token_legacy"
    private static let keychainService = "ai-zhao-tutor.mathcoach"
    private static let keychainAccount = "auth_access_token"

    private static let defaultBaseURL = "https://mathcoach-api.micleah.com/api/v1"
    private static let baseURLEnvKey = "MATHCOACH_API_BASE_URL"
    private let baseURL: String
    private let session: URLSession
    private var accessToken: String?

    private init() {
        if let configuredBaseURL = ProcessInfo.processInfo.environment[Self.baseURLEnvKey],
           !configuredBaseURL.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            self.baseURL = configuredBaseURL
        } else {
            self.baseURL = Self.defaultBaseURL
        }
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        self.session = URLSession(configuration: config)
        if let token = KeychainStore.read(
            service: APIClient.keychainService,
            account: APIClient.keychainAccount
        ), !token.isEmpty {
            self.accessToken = token
        } else {
            // One-time migration from legacy UserDefaults storage.
            let legacy = UserDefaults.standard.string(forKey: APIClient.authTokenDefaultsKey)
            self.accessToken = legacy
            if let legacy, !legacy.isEmpty {
                KeychainStore.write(
                    legacy,
                    service: APIClient.keychainService,
                    account: APIClient.keychainAccount
                )
            }
            UserDefaults.standard.removeObject(forKey: APIClient.authTokenDefaultsKey)
        }
    }

    func setAccessToken(_ token: String?) {
        accessToken = token
        if let token, !token.isEmpty {
            KeychainStore.write(
                token,
                service: APIClient.keychainService,
                account: APIClient.keychainAccount
            )
        } else {
            KeychainStore.delete(
                service: APIClient.keychainService,
                account: APIClient.keychainAccount
            )
        }
        UserDefaults.standard.removeObject(forKey: APIClient.authTokenDefaultsKey)
    }

    var hasAccessToken: Bool {
        guard let accessToken else { return false }
        return !accessToken.isEmpty
    }

    var isStudentRole: Bool {
        tokenRole == "student"
    }

    func clearAccessToken() {
        setAccessToken(nil)
        NotificationCenter.default.post(name: .apiClientUnauthorized, object: nil)
    }

    private func applyAuthHeader(to request: inout URLRequest) {
        guard let accessToken, !accessToken.isEmpty else { return }
        request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
    }

    private func ensureSuccess(_ response: URLResponse, data: Data) throws {
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.serverError("Invalid response")
        }
        guard httpResponse.statusCode == 200 else {
            if httpResponse.statusCode == 401 {
                clearAccessToken()
            }
            if let errorMessage = String(data: data, encoding: .utf8), !errorMessage.isEmpty {
                throw APIError.serverError("HTTP \(httpResponse.statusCode): \(errorMessage)")
            }
            throw APIError.serverError("HTTP \(httpResponse.statusCode)")
        }
    }

    private var tokenClaims: [String: Any]? {
        guard let accessToken else { return nil }
        let parts = accessToken.split(separator: ".")
        guard parts.count == 3 else { return nil }

        var payload = String(parts[1]).replacingOccurrences(of: "-", with: "+").replacingOccurrences(of: "_", with: "/")
        while payload.count % 4 != 0 {
            payload.append("=")
        }
        guard let data = Data(base64Encoded: payload) else { return nil }
        guard let raw = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { return nil }
        return raw
    }

    private var tokenRole: String? {
        tokenClaims?["role"] as? String
    }

    struct ParentContextResponse: Codable {
        let id: String
        let studentId: String?
        let tags: [String]
        let freeText: String?
        let engineHint: String?
        let aiInsight: String?
        let createdAt: String

        enum CodingKeys: String, CodingKey {
            case id
            case studentId = "student_id"
            case tags
            case freeText = "free_text"
            case engineHint = "engine_hint"
            case aiInsight = "ai_insight"
            case createdAt = "created_at"
        }
    }

    /// Create a student profile under current parent account.
    func createParentStudent(
        name: String,
        yearLevel: Int,
        pin: String,
        avatar: String = "star",
        targetDailyQuestions: Int = 10
    ) async throws -> Student {
        guard let url = URL(string: "\(baseURL)/parent/students") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        applyAuthHeader(to: &request)
        request.httpBody = try JSONSerialization.data(withJSONObject: [
            "name": name,
            "year_level": yearLevel,
            "pin": pin,
            "avatar": avatar,
            "target_daily_questions": targetDailyQuestions
        ])

        do {
            let (data, response) = try await session.data(for: request)
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.serverError("Invalid response")
            }
            guard httpResponse.statusCode == 201 else {
                try ensureSuccess(response, data: data)
                throw APIError.serverError("HTTP \(httpResponse.statusCode)")
            }

            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            return try decoder.decode(Student.self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    // MARK: - Fetch Next Item

    /// Fetch available students.
    func fetchStudents() async throws -> [Student] {
        guard let url = URL(string: "\(baseURL)/students") else {
            throw APIError.invalidURL
        }

        do {
            var request = URLRequest(url: url)
            applyAuthHeader(to: &request)
            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)

            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            return try decoder.decode([Student].self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    /// Start or get today's daily session for the student.
    /// - Parameter studentId: Required for parent role; optional for student role.
    func startDailySession(studentId: String? = nil) async throws -> DailySessionStatus {
        guard var components = URLComponents(string: "\(baseURL)/daily-session/start") else {
            throw APIError.invalidURL
        }
        if tokenRole != "student" {
            guard let studentId, !studentId.isEmpty else {
                throw APIError.serverError("student_id is required for parent role")
            }
            components.queryItems = [URLQueryItem(name: "student_id", value: studentId)]
        }
        guard let url = components.url else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        applyAuthHeader(to: &request)

        do {
            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)

            let decoder = JSONDecoder()
            return try decoder.decode(DailySessionStatus.self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    /// Fetch today's progress status for the student.
    /// - Parameter studentId: Required for parent role; optional for student role.
    func fetchDailySessionStatus(studentId: String? = nil) async throws -> DailySessionStatus {
        let endpoint: String
        if tokenRole == "student" {
            endpoint = "\(baseURL)/daily-session/status"
        } else {
            guard let studentId, !studentId.isEmpty else {
                throw APIError.serverError("student_id is required for parent role")
            }
            endpoint = "\(baseURL)/daily-session/status/\(studentId)"
        }
        guard let url = URL(string: endpoint) else {
            throw APIError.invalidURL
        }

        do {
            var request = URLRequest(url: url)
            applyAuthHeader(to: &request)
            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)

            let decoder = JSONDecoder()
            return try decoder.decode(DailySessionStatus.self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    /// Fetch the next math item for a student
    /// - Parameter studentId: Required for parent role; optional for student role.
    /// - Returns: The next Item to practice
    func fetchNextItem(studentId: String? = nil) async throws -> Item {
        guard var components = URLComponents(string: "\(baseURL)/next-item") else {
            throw APIError.invalidURL
        }

        if tokenRole != "student" {
            guard let studentId, !studentId.isEmpty else {
                throw APIError.serverError("student_id is required for parent role")
            }
            components.queryItems = [
                URLQueryItem(name: "student_id", value: studentId)
            ]
        }

        guard let url = components.url else {
            throw APIError.invalidURL
        }

        do {
            var request = URLRequest(url: url)
            applyAuthHeader(to: &request)
            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)

            let decoder = JSONDecoder()
            // Note: Item already defines CodingKeys, so don't use automatic conversion
            decoder.dateDecodingStrategy = .iso8601

            let item = try decoder.decode(Item.self, from: data)
            return item

        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    /// Fetch parent daily summaries for all students.
    func fetchParentDailySummaries() async throws -> [ParentDailySummary] {
        guard let url = URL(string: "\(baseURL)/parent/daily-summary") else {
            throw APIError.invalidURL
        }

        do {
            var request = URLRequest(url: url)
            applyAuthHeader(to: &request)
            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)

            let decoder = JSONDecoder()
            return try decoder.decode([ParentDailySummary].self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    /// Submit parent context tags/free-text for AI hint generation.
    func submitParentContext(studentId: String?, tags: [String], freeText: String) async throws -> ParentContextResponse {
        guard let url = URL(string: "\(baseURL)/parent/context") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        applyAuthHeader(to: &request)

        var payload: [String: Any] = [
            "tags": tags,
            "free_text": freeText
        ]
        if let studentId, !studentId.isEmpty {
            payload["student_id"] = studentId
        }
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        do {
            let (data, response) = try await session.data(for: request)
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.serverError("Invalid response")
            }
            guard httpResponse.statusCode == 201 else {
                try ensureSuccess(response, data: data)
                throw APIError.serverError("HTTP \(httpResponse.statusCode)")
            }

            let decoder = JSONDecoder()
            return try decoder.decode(ParentContextResponse.self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    /// Fetch parent weekly summaries for all students.
    func fetchParentWeeklySummaries() async throws -> [ParentWeeklySummary] {
        guard let url = URL(string: "\(baseURL)/parent/weekly-summary") else {
            throw APIError.invalidURL
        }

        do {
            var request = URLRequest(url: url)
            applyAuthHeader(to: &request)
            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)

            let decoder = JSONDecoder()
            return try decoder.decode([ParentWeeklySummary].self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    /// Fetch achievements for a specific student.
    /// - Parameter studentId: Required for parent role; optional for student role.
    func fetchAchievements(studentId: String? = nil) async throws -> [Achievement] {
        let endpoint: String
        if tokenRole == "student" {
            endpoint = "\(baseURL)/achievements/me"
        } else {
            guard let studentId, !studentId.isEmpty else {
                throw APIError.serverError("student_id is required for parent role")
            }
            endpoint = "\(baseURL)/achievements/\(studentId)"
        }
        guard let url = URL(string: endpoint) else {
            throw APIError.invalidURL
        }

        do {
            var request = URLRequest(url: url)
            applyAuthHeader(to: &request)
            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)

            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            return try decoder.decode([Achievement].self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    /// Fetch newly unlocked achievements for a student.
    /// - Parameter studentId: Required for parent role; optional for student role.
    func fetchNewAchievements(studentId: String? = nil, lookbackHours: Int = 24) async throws -> NewAchievementsResponse {
        let basePath: String
        if tokenRole == "student" {
            basePath = "\(baseURL)/achievements/me/new"
        } else {
            guard let studentId, !studentId.isEmpty else {
                throw APIError.serverError("student_id is required for parent role")
            }
            basePath = "\(baseURL)/achievements/\(studentId)/new"
        }
        guard var components = URLComponents(string: basePath) else {
            throw APIError.invalidURL
        }
        components.queryItems = [
            URLQueryItem(name: "lookback_hours", value: String(lookbackHours))
        ]
        guard let url = components.url else {
            throw APIError.invalidURL
        }

        do {
            var request = URLRequest(url: url)
            applyAuthHeader(to: &request)
            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)

            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            return try decoder.decode(NewAchievementsResponse.self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    /// Fetch streak status for a student.
    /// - Parameter studentId: Required for parent role; optional for student role.
    func fetchStreakStatus(studentId: String? = nil) async throws -> StreakStatus {
        let endpoint: String
        if tokenRole == "student" {
            endpoint = "\(baseURL)/streak/me"
        } else {
            guard let studentId, !studentId.isEmpty else {
                throw APIError.serverError("student_id is required for parent role")
            }
            endpoint = "\(baseURL)/streak/\(studentId)"
        }
        guard let url = URL(string: endpoint) else {
            throw APIError.invalidURL
        }

        do {
            var request = URLRequest(url: url)
            applyAuthHeader(to: &request)
            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)

            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            return try decoder.decode(StreakStatus.self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    /// Fetch parent progress timeline and risk signals for one student.
    func fetchParentProgress(studentId: String, days: Int = 30) async throws -> ParentProgress {
        guard var components = URLComponents(string: "\(baseURL)/parent/\(studentId)/progress") else {
            throw APIError.invalidURL
        }
        components.queryItems = [URLQueryItem(name: "days", value: String(days))]
        guard let url = components.url else {
            throw APIError.invalidURL
        }

        do {
            var request = URLRequest(url: url)
            applyAuthHeader(to: &request)
            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)

            let decoder = JSONDecoder()
            return try decoder.decode(ParentProgress.self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    func registerParent(email: String, password: String, displayName: String? = nil) async throws -> AuthTokenResponse {
        guard let url = URL(string: "\(baseURL)/auth/register") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let body: [String: Any?] = [
            "email": email,
            "password": password,
            "display_name": displayName
        ]
        let sanitized = body.compactMapValues { $0 }
        request.httpBody = try JSONSerialization.data(withJSONObject: sanitized)

        do {
            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)
            let decoder = JSONDecoder()
            let token = try decoder.decode(AuthTokenResponse.self, from: data)
            setAccessToken(token.accessToken)
            return token
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    func loginParent(email: String, password: String) async throws -> AuthTokenResponse {
        guard let url = URL(string: "\(baseURL)/auth/login") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: [
            "email": email,
            "password": password
        ])

        do {
            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)
            let decoder = JSONDecoder()
            let token = try decoder.decode(AuthTokenResponse.self, from: data)
            setAccessToken(token.accessToken)
            return token
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    func loginStudent(studentId: String, pin: String) async throws -> AuthTokenResponse {
        guard let url = URL(string: "\(baseURL)/auth/student-login") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: [
            "student_id": studentId,
            "pin": pin
        ])

        do {
            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)
            let decoder = JSONDecoder()
            let token = try decoder.decode(AuthTokenResponse.self, from: data)
            setAccessToken(token.accessToken)
            return token
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    func changeParentPassword(currentPassword: String, newPassword: String) async throws {
        guard let url = URL(string: "\(baseURL)/parent/change-password") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        applyAuthHeader(to: &request)
        request.httpBody = try JSONSerialization.data(withJSONObject: [
            "current_password": currentPassword,
            "new_password": newPassword
        ])

        do {
            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)
        } catch {
            throw APIError.networkError(error)
        }
    }

    // MARK: - Submit Event

    /// Submit a student's answer event
    /// - Parameter event: The event to submit
    func submitEvent(_ event: Event) async throws {
        guard let url = URL(string: "\(baseURL)/events") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        do {
            let formatter = ISO8601DateFormatter()
            var body: [String: Any] = [
                "event_id": event.eventId,
                "item_id": event.itemId,
                "answer_given": event.answerGiven,
                "is_correct": event.isCorrect,
                "time_spent": event.timeSpent,
                "hint_requested": event.hintRequested,
                "timestamp": formatter.string(from: event.timestamp),
            ]
            if tokenRole != "student", let studentId = event.studentId {
                body["student_id"] = studentId
            }
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
            applyAuthHeader(to: &request)

            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)
        } catch {
            throw APIError.networkError(error)
        }
    }

    // MARK: - Get Mastery

    /// Get mastery data for a student
    /// - Parameter studentId: Required for parent role; optional for student role.
    /// - Returns: Array of all mastery data for the student
    func getMastery(studentId: String? = nil) async throws -> [Mastery] {
        let endpoint: String
        if tokenRole == "student" {
            endpoint = "\(baseURL)/mastery/me"
        } else {
            guard let studentId, !studentId.isEmpty else {
                throw APIError.serverError("student_id is required for parent role")
            }
            endpoint = "\(baseURL)/mastery/\(studentId)"
        }
        guard let url = URL(string: endpoint) else {
            throw APIError.invalidURL
        }

        do {
            var request = URLRequest(url: url)
            applyAuthHeader(to: &request)
            let (data, response) = try await session.data(for: request)
            try ensureSuccess(response, data: data)

            let decoder = JSONDecoder()
            // Note: Mastery already defines CodingKeys, so don't use automatic conversion
            decoder.dateDecodingStrategy = .iso8601

            let masteryList = try decoder.decode([Mastery].self, from: data)
            return masteryList

        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    // MARK: - Health Check

    /// Check if the backend API is healthy
    /// - Returns: True if healthy, false otherwise
    func checkHealth() async -> Bool {
        guard let url = URL(string: "http://192.168.86.63:8000/health") else {
            return false
        }

        do {
            let (data, response) = try await session.data(from: url)

            guard let httpResponse = response as? HTTPURLResponse,
                  httpResponse.statusCode == 200 else {
                return false
            }

            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: String],
               json["status"] == "ok" {
                return true
            }

            return false
        } catch {
            return false
        }
    }
}
