//
//  WorkedExampleView.swift
//  MathCoach
//
//  Shown the very first time a student sees a new skill — example walkthrough
//  with an "I get it" dismiss button. Backed by /next-item.worked_example.
//

import SwiftUI

struct WorkedExample: Codable, Equatable {
    let question: String
    let answer: String
    let walkthrough: String

    enum CodingKeys: String, CodingKey {
        case question
        case answer
        case walkthrough
    }
}

struct WorkedExampleView: View {
    let skillLabel: String?
    let example: WorkedExample
    var onAcknowledge: () -> Void

    var body: some View {
        ZStack {
            Color.black.opacity(0.4).ignoresSafeArea()

            VStack(spacing: 0) {
                Spacer().frame(height: 18)

                HStack(spacing: 8) {
                    Image(systemName: "lightbulb.fill")
                        .foregroundColor(.yellow)
                    Text("新题型示范")
                        .font(.title3.bold())
                    Spacer()
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 12)

                if let label = skillLabel {
                    Text(label)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding(.horizontal, 24)
                        .padding(.bottom, 12)
                }

                VStack(alignment: .leading, spacing: 16) {
                    SectionBlock(title: "题目", text: example.question)
                    SectionBlock(title: "答案", text: example.answer, accent: .green)
                    SectionBlock(title: "怎么想", text: example.walkthrough, accent: .blue)
                }
                .padding(.horizontal, 24)

                Spacer().frame(height: 20)

                Button {
                    onAcknowledge()
                } label: {
                    Label("我懂了！开始练习", systemImage: "checkmark.circle.fill")
                        .font(.title3.bold())
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
                .padding(.horizontal, 24)
                .padding(.bottom, 24)
            }
            .background(
                RoundedRectangle(cornerRadius: 24)
                    .fill(Color(UIColor.systemBackground))
                    .shadow(color: .black.opacity(0.25), radius: 24, y: 8)
            )
            .padding(.horizontal, 24)
        }
    }
}

private struct SectionBlock: View {
    let title: String
    let text: String
    var accent: Color = .primary

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption.bold())
                .foregroundColor(.secondary)
            Text(text)
                .font(.body)
                .foregroundColor(accent)
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.gray.opacity(0.08))
        )
    }
}

#Preview {
    WorkedExampleView(
        skillLabel: "Year 4 等价分数",
        example: WorkedExample(
            question: "1/2 的等价分数（分母 4）= ?",
            answer: "2/4",
            walkthrough: "把分子分母都乘以 2：1×2 / 2×2 = 2/4。"
        ),
        onAcknowledge: {}
    )
}
