//
//  Feedback.swift
//  MathCoach
//
//  Sound + haptic feedback helpers fired on answer result reveal.
//

import AudioToolbox
import UIKit

enum Feedback {
    /// Pleasant chime + light tap when an answer is correct.
    static func correct() {
        // 1057 = "Tink" / "Received" — short, friendly, non-jarring.
        AudioServicesPlaySystemSound(1057)
        UIImpactFeedbackGenerator(style: .light).impactOccurred()
    }

    /// Soft negative tone + error haptic when an answer is wrong.
    static func incorrect() {
        // 1053 = "SMSReceived_Selection" — gentle low tone, no harsh buzz.
        AudioServicesPlaySystemSound(1053)
        UINotificationFeedbackGenerator().notificationOccurred(.error)
    }
}
