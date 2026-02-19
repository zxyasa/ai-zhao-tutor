//
//  APIClient.swift
//  MathCoach
//
//  API client for backend communication
//

import Foundation

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

    // Use Mac's IP address for testing on real iPad
    // Change back to "localhost" for simulator testing
    private let baseURL = "http://192.168.86.63:8000/api/v1"
    private let session: URLSession

    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        self.session = URLSession(configuration: config)
    }

    // MARK: - Fetch Next Item

    /// Fetch available students.
    func fetchStudents() async throws -> [Student] {
        guard let url = URL(string: "\(baseURL)/students") else {
            throw APIError.invalidURL
        }

        do {
            let (data, response) = try await session.data(from: url)
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.serverError("Invalid response")
            }
            guard httpResponse.statusCode == 200 else {
                throw APIError.serverError("HTTP \(httpResponse.statusCode)")
            }

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
    func startDailySession(studentId: String) async throws -> DailySessionStatus {
        guard var components = URLComponents(string: "\(baseURL)/daily-session/start") else {
            throw APIError.invalidURL
        }
        components.queryItems = [URLQueryItem(name: "student_id", value: studentId)]
        guard let url = components.url else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"

        do {
            let (data, response) = try await session.data(for: request)
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.serverError("Invalid response")
            }
            guard httpResponse.statusCode == 200 else {
                throw APIError.serverError("HTTP \(httpResponse.statusCode)")
            }

            let decoder = JSONDecoder()
            return try decoder.decode(DailySessionStatus.self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    /// Fetch today's progress status for the student.
    func fetchDailySessionStatus(studentId: String) async throws -> DailySessionStatus {
        guard let url = URL(string: "\(baseURL)/daily-session/status/\(studentId)") else {
            throw APIError.invalidURL
        }

        do {
            let (data, response) = try await session.data(from: url)
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.serverError("Invalid response")
            }
            guard httpResponse.statusCode == 200 else {
                throw APIError.serverError("HTTP \(httpResponse.statusCode)")
            }

            let decoder = JSONDecoder()
            return try decoder.decode(DailySessionStatus.self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    /// Fetch the next math item for a student
    /// - Parameter studentId: The student's ID
    /// - Returns: The next Item to practice
    func fetchNextItem(studentId: String) async throws -> Item {
        guard var components = URLComponents(string: "\(baseURL)/next-item") else {
            throw APIError.invalidURL
        }

        components.queryItems = [
            URLQueryItem(name: "student_id", value: studentId)
        ]

        guard let url = components.url else {
            throw APIError.invalidURL
        }

        do {
            let (data, response) = try await session.data(from: url)

            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.serverError("Invalid response")
            }

            guard httpResponse.statusCode == 200 else {
                throw APIError.serverError("HTTP \(httpResponse.statusCode)")
            }

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
            let (data, response) = try await session.data(from: url)
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.serverError("Invalid response")
            }
            guard httpResponse.statusCode == 200 else {
                throw APIError.serverError("HTTP \(httpResponse.statusCode)")
            }

            let decoder = JSONDecoder()
            return try decoder.decode([ParentDailySummary].self, from: data)
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
            let (data, response) = try await session.data(from: url)
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.serverError("Invalid response")
            }
            guard httpResponse.statusCode == 200 else {
                throw APIError.serverError("HTTP \(httpResponse.statusCode)")
            }

            let decoder = JSONDecoder()
            return try decoder.decode([ParentWeeklySummary].self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    /// Fetch achievements for a specific student.
    func fetchAchievements(studentId: String) async throws -> [Achievement] {
        guard let url = URL(string: "\(baseURL)/achievements/\(studentId)") else {
            throw APIError.invalidURL
        }

        do {
            let (data, response) = try await session.data(from: url)
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.serverError("Invalid response")
            }
            guard httpResponse.statusCode == 200 else {
                throw APIError.serverError("HTTP \(httpResponse.statusCode)")
            }

            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            return try decoder.decode([Achievement].self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
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

        let encoder = JSONEncoder()
        // Note: Event already defines CodingKeys, so don't use automatic conversion
        encoder.dateEncodingStrategy = .iso8601

        do {
            request.httpBody = try encoder.encode(event)

            let (data, response) = try await session.data(for: request)

            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.serverError("Invalid response")
            }

            guard httpResponse.statusCode == 200 else {
                // Try to decode error message
                if let errorMessage = String(data: data, encoding: .utf8) {
                    throw APIError.serverError("HTTP \(httpResponse.statusCode): \(errorMessage)")
                } else {
                    throw APIError.serverError("HTTP \(httpResponse.statusCode)")
                }
            }

        } catch let error as EncodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    // MARK: - Get Mastery

    /// Get mastery data for a student
    /// - Parameter studentId: The student's ID
    /// - Returns: Array of all mastery data for the student
    func getMastery(studentId: String) async throws -> [Mastery] {
        guard let url = URL(string: "\(baseURL)/mastery/\(studentId)") else {
            throw APIError.invalidURL
        }

        do {
            let (data, response) = try await session.data(from: url)

            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.serverError("Invalid response")
            }

            guard httpResponse.statusCode == 200 else {
                throw APIError.serverError("HTTP \(httpResponse.statusCode)")
            }

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
