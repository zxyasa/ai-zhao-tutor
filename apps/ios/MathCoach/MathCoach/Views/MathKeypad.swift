//
//  MathKeypad.swift
//  MathCoach
//
//  Big-button numeric keypad for kid-friendly math answer input.
//  Replaces the software keyboard so the answer field never loses focus.
//

import SwiftUI

struct MathKeypad: View {
    @Binding var value: String
    let allowSlash: Bool
    let allowDot: Bool
    var onSubmit: () -> Void

    // Layout constants
    private let buttonHeight: CGFloat = 88
    private let buttonSpacing: CGFloat = 12

    var body: some View {
        VStack(spacing: buttonSpacing) {
            row(["7", "8", "9"])
            row(["4", "5", "6"])
            row(["1", "2", "3"])
            row([slashKey, "0", dotKey])

            HStack(spacing: buttonSpacing) {
                backspaceButton
                submitButton
            }
        }
        .padding(16)
        .background(Color.blue.opacity(0.06))
        .cornerRadius(20)
    }

    // MARK: - Row Builder

    private func row(_ keys: [String]) -> some View {
        HStack(spacing: buttonSpacing) {
            ForEach(keys, id: \.self) { key in
                keyButton(label: key)
            }
        }
    }

    // MARK: - Buttons

    private func keyButton(label: String) -> some View {
        let isEnabled = keyEnabled(label)
        return Button {
            tap(label)
        } label: {
            Text(label)
                .font(.system(size: 32, weight: .semibold, design: .rounded))
                .foregroundColor(isEnabled ? .primary : .secondary.opacity(0.4))
                .frame(maxWidth: .infinity)
                .frame(height: buttonHeight)
                .background(Color.white)
                .cornerRadius(16)
                .shadow(color: .black.opacity(isEnabled ? 0.08 : 0), radius: 2, y: 1)
        }
        .buttonStyle(.plain)
        .disabled(!isEnabled)
    }

    private var backspaceButton: some View {
        Button {
            backspace()
        } label: {
            Image(systemName: "delete.left")
                .font(.system(size: 28, weight: .semibold))
                .foregroundColor(.orange)
                .frame(maxWidth: .infinity)
                .frame(height: buttonHeight)
                .background(Color.white)
                .cornerRadius(16)
                .shadow(color: .black.opacity(0.08), radius: 2, y: 1)
        }
        .buttonStyle(.plain)
        .disabled(value.isEmpty)
    }

    private var submitButton: some View {
        Button {
            onSubmit()
        } label: {
            Text("提交")
                .font(.system(size: 26, weight: .bold, design: .rounded))
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .frame(height: buttonHeight)
                .background(submitEnabled ? Color.blue : Color.gray.opacity(0.4))
                .cornerRadius(16)
                .shadow(color: .black.opacity(submitEnabled ? 0.15 : 0), radius: 3, y: 2)
        }
        .buttonStyle(.plain)
        .disabled(!submitEnabled)
    }

    // MARK: - Helpers

    private var slashKey: String { "/" }
    private var dotKey: String { "." }

    private var submitEnabled: Bool {
        !value.trimmingCharacters(in: .whitespaces).isEmpty
    }

    private func keyEnabled(_ key: String) -> Bool {
        switch key {
        case "/":
            return allowSlash
        case ".":
            return allowDot
        default:
            return true
        }
    }

    private func tap(_ key: String) {
        guard keyEnabled(key) else { return }
        // Prevent duplicate slashes / dots in obviously bad positions.
        if key == "/" && value.contains("/") { return }
        if key == "." && value.contains(".") { return }
        value.append(key)
    }

    private func backspace() {
        guard !value.isEmpty else { return }
        value.removeLast()
    }
}

#Preview("Numeric") {
    StatefulPreview(value: "12.5") { binding in
        MathKeypad(value: binding, allowSlash: false, allowDot: true) {}
            .padding()
    }
}

#Preview("Fraction") {
    StatefulPreview(value: "3/4") { binding in
        MathKeypad(value: binding, allowSlash: true, allowDot: false) {}
            .padding()
    }
}

/// Small helper to drive a @Binding inside a #Preview.
private struct StatefulPreview<Content: View>: View {
    @State var value: String
    let content: (Binding<String>) -> Content

    var body: some View {
        content($value)
    }
}
