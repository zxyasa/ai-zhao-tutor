//
//  QuestionViewModel.swift
//  MathCoach
//
//  ViewModel for managing question display and answer submission
//

import Foundation
import SwiftUI
import Combine

@MainActor
class QuestionViewModel: ObservableObject {
    // MARK: - Published Properties

    @Published var currentItem: Item?
    @Published var studentAnswer: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var showHint: Bool = false
    @Published var showExplanation: Bool = false
    @Published var isCorrect: Bool?
    @Published var timeSpent: Double = 0
    @Published var dailyCompleted: Int = 0
    @Published var dailyTarget: Int = 10

    // MARK: - Private Properties

    private let apiClient = APIClient.shared
    private let studentId: String
    private var startTime: Date?
    private var timer: Timer?

    // MARK: - Initialization

    init(studentId: String = "test_001") {
        self.studentId = studentId
    }

    // MARK: - Public Methods

    /// Load the next question for the student
    func loadNextQuestion() async {
        isLoading = true
        errorMessage = nil
        isCorrect = nil
        showHint = false
        showExplanation = false
        studentAnswer = ""
        timeSpent = 0

        do {
            _ = try? await apiClient.startDailySession(studentId: studentId)
            await loadDailyStatus()
            let item = try await apiClient.fetchNextItem(studentId: studentId)
            currentItem = item
            startTimer()
        } catch {
            errorMessage = handleError(error)
        }

        isLoading = false
    }

    /// Submit the student's answer
    func submitAnswer() async {
        guard let item = currentItem else { return }

        stopTimer()

        isLoading = true
        errorMessage = nil

        // Validate answer
        let correct = validateAnswer(item: item, answer: studentAnswer)
        isCorrect = correct

        // Create event
        let event = Event(
            studentId: studentId,
            itemId: item.id,
            answerGiven: studentAnswer,
            isCorrect: correct,
            timeSpent: timeSpent,
            hintRequested: showHint
        )

        do {
            try await apiClient.submitEvent(event)
            await loadDailyStatus()
            showExplanation = true
        } catch {
            errorMessage = handleError(error)
        }

        isLoading = false
    }

    /// Toggle hint visibility
    func toggleHint() {
        showHint.toggle()
    }

    /// Move to next question after viewing explanation
    func nextQuestion() {
        Task {
            await loadNextQuestion()
        }
    }

    /// Check backend health
    func checkBackendHealth() async -> Bool {
        return await apiClient.checkHealth()
    }

    // MARK: - Private Methods

    private func startTimer() {
        let start = Date()
        startTime = start
        timeSpent = 0

        // Update time every second
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            guard let self = self else { return }
            Task { @MainActor in
                self.timeSpent = Date().timeIntervalSince(start)
            }
        }
    }

    private func stopTimer() {
        timer?.invalidate()
        timer = nil
        if let startTime = startTime {
            timeSpent = Date().timeIntervalSince(startTime)
        }
    }

    private func validateAnswer(item: Item, answer: String) -> Bool {
        let trimmedAnswer = answer.trimmingCharacters(in: .whitespaces)
        let correctAnswer = item.correctAnswer.trimmingCharacters(in: .whitespaces)

        // Basic validation - can be enhanced based on validation_rule
        switch item.validationRule {
        case "exact":
            return trimmedAnswer.lowercased() == correctAnswer.lowercased()
        case "numeric":
            // Handle numeric comparison
            if let studentValue = Double(trimmedAnswer),
               let correctValue = Double(correctAnswer) {
                return abs(studentValue - correctValue) < 0.0001
            }
            return false
        case "fraction":
            // Handle fraction comparison (e.g., "1/2" == "2/4")
            return compareFractions(trimmedAnswer, correctAnswer)
        default:
            return trimmedAnswer.lowercased() == correctAnswer.lowercased()
        }
    }

    private func compareFractions(_ answer: String, _ correct: String) -> Bool {
        // Parse fractions like "1/2"
        let answerParts = answer.split(separator: "/").compactMap { Double($0.trimmingCharacters(in: .whitespaces)) }
        let correctParts = correct.split(separator: "/").compactMap { Double($0.trimmingCharacters(in: .whitespaces)) }

        guard answerParts.count == 2, correctParts.count == 2,
              answerParts[1] != 0, correctParts[1] != 0 else {
            return answer == correct
        }

        let answerValue = answerParts[0] / answerParts[1]
        let correctValue = correctParts[0] / correctParts[1]

        return abs(answerValue - correctValue) < 0.0001
    }

    private func handleError(_ error: Error) -> String {
        if let apiError = error as? APIError {
            switch apiError {
            case .invalidURL:
                return "Invalid URL configuration"
            case .noData:
                return "No data received from server"
            case .decodingError(let error):
                return "Data parsing error: \(error.localizedDescription)"
            case .serverError(let message):
                return "Server error: \(message)"
            case .networkError(let error):
                return "Network error: \(error.localizedDescription)"
            }
        }
        return "Unknown error: \(error.localizedDescription)"
    }

    deinit {
        timer?.invalidate()
    }

    private func loadDailyStatus() async {
        if let status = try? await apiClient.fetchDailySessionStatus(studentId: studentId) {
            dailyCompleted = status.completedQuestions
            dailyTarget = status.targetQuestions
        }
    }
}
