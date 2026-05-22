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
    @Published var dailyBonus: Int = 0
    @Published var inputValidationMessage: String?
    // Phase 9.3: graduation celebration + worked example overlays
    @Published var pendingCelebrationLabel: String?
    @Published var pendingWorkedExample: WorkedExample?

    // MARK: - Private Properties

    private let apiClient = APIClient.shared
    private let studentId: String?
    private var startTime: Date?
    private var timer: Timer?

    // MARK: - Initialization

    init(studentId: String? = nil) {
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
        inputValidationMessage = nil
        studentAnswer = ""
        timeSpent = 0

        do {
            if apiClient.isStudentRole {
                _ = try? await apiClient.startDailySession()
            } else {
                guard let studentId, !studentId.isEmpty else {
                    throw APIError.serverError("student_id is required for parent role")
                }
                _ = try? await apiClient.startDailySession(studentId: studentId)
            }
            await loadDailyStatus()
            let item: Item
            if apiClient.isStudentRole {
                item = try await apiClient.fetchNextItem()
            } else {
                guard let studentId, !studentId.isEmpty else {
                    throw APIError.serverError("student_id is required for parent role")
                }
                item = try await apiClient.fetchNextItem(studentId: studentId)
            }
            currentItem = item
            if let label = item.graduatedToLabel {
                pendingCelebrationLabel = label
            }
            if let example = item.workedExample {
                pendingWorkedExample = example
            }
            startTimer()
        } catch {
            errorMessage = handleError(error)
        }

        isLoading = false
    }

    /// Submit the student's answer
    func submitAnswer() async {
        guard let item = currentItem else { return }

        inputValidationMessage = nil
        if let validationError = validateInputFormat(item: item, answer: studentAnswer) {
            inputValidationMessage = validationError
            return
        }

        stopTimer()
        isLoading = true
        errorMessage = nil

        // Validate answer
        let correct = validateAnswer(item: item, answer: studentAnswer)
        isCorrect = correct

        // Create event
        let scopedStudentId: String?
        if apiClient.isStudentRole {
            scopedStudentId = nil
        } else {
            guard let studentId, !studentId.isEmpty else {
                isLoading = false
                errorMessage = "student_id is required for parent role"
                return
            }
            scopedStudentId = studentId
        }

        let event = Event(
            studentId: scopedStudentId,
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

    /// Dismiss the graduation celebration overlay
    func dismissCelebration() {
        pendingCelebrationLabel = nil
    }

    /// Dismiss the worked-example overlay
    func dismissWorkedExample() {
        pendingWorkedExample = nil
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

    private func validateInputFormat(item: Item, answer: String) -> String? {
        let trimmed = answer.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty {
            return "请输入答案"
        }

        switch item.validationRule {
        case "numeric":
            // 数字题：仅允许数字，或小数格式。
            let pattern = #"^\d+(\.\d+)?$"#
            let isNumeric = trimmed.range(of: pattern, options: .regularExpression) != nil
            if !isNumeric {
                return "这道题只能输入数字（可含小数点）"
            }
            return nil
        case "fraction":
            // 分数题：仅允许 a/b 形式，分母不能为 0。
            let pattern = #"^\d+/\d+$"#
            let isFraction = trimmed.range(of: pattern, options: .regularExpression) != nil
            if !isFraction {
                return "分数题请输入 a/b 格式（只允许数字和 /）"
            }
            let parts = trimmed.split(separator: "/")
            if parts.count == 2, let denom = Int(parts[1]), denom == 0 {
                return "分母不能为 0"
            }
            return nil
        default:
            return nil
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
        let status: DailySessionStatus?
        if apiClient.isStudentRole {
            status = try? await apiClient.fetchDailySessionStatus()
        } else {
            guard let studentId, !studentId.isEmpty else {
                inputValidationMessage = "缺少学生信息，请返回重选学生"
                return
            }
            status = try? await apiClient.fetchDailySessionStatus(studentId: studentId)
        }
        if let status {
            dailyCompleted = status.completedQuestions
            dailyTarget = status.targetQuestions
            dailyBonus = status.bonusQuestions ?? 0
        }
    }
}
