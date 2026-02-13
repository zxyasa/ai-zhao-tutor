//
//  Item.swift
//  MathCoach
//
//  Math question/item model
//

import Foundation

struct Item: Codable, Identifiable {
    let id: String
    let skillId: String
    let questionText: String
    let questionType: String
    let difficulty: Int
    let parameters: [String: AnyCodable]
    let correctAnswer: String
    let hint: String
    let explanation: String
    let validationRule: String

    enum CodingKeys: String, CodingKey {
        case id = "item_id"
        case skillId = "skill_id"
        case questionText = "question_text"
        case questionType = "question_type"
        case difficulty
        case parameters
        case correctAnswer = "correct_answer"
        case hint
        case explanation
        case validationRule = "validation_rule"
    }

    init(
        id: String,
        skillId: String,
        questionText: String,
        questionType: String,
        difficulty: Int,
        parameters: [String: AnyCodable],
        correctAnswer: String,
        hint: String,
        explanation: String,
        validationRule: String
    ) {
        self.id = id
        self.skillId = skillId
        self.questionText = questionText
        self.questionType = questionType
        self.difficulty = difficulty
        self.parameters = parameters
        self.correctAnswer = correctAnswer
        self.hint = hint
        self.explanation = explanation
        self.validationRule = validationRule
    }
}
