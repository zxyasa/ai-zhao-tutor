//
//  WrongItemsView.swift
//  MathCoach
//
//  Mistake-book sheet: shows recent wrong answers with comparison + explanation.
//

import SwiftUI

struct WrongItemsView: View {
    let student: Student
    @Environment(\.dismiss) private var dismiss
    @State private var items: [WrongItem] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var range: Range = .today
    @State private var expandedIds: Set<String> = []

    enum Range: String, CaseIterable, Identifiable {
        case today
        case sevenDays
        case thirtyDays

        var id: String { rawValue }

        var apiValue: String {
            switch self {
            case .today: return "today"
            case .sevenDays: return "7d"
            case .thirtyDays: return "30d"
            }
        }

        var label: String {
            switch self {
            case .today: return "今天"
            case .sevenDays: return "近 7 天"
            case .thirtyDays: return "近 30 天"
            }
        }
    }

    init(student: Student) {
        self.student = student
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 12) {
                Picker("时间范围", selection: $range) {
                    ForEach(Range.allCases) { option in
                        Text(option.label).tag(option)
                    }
                }
                .pickerStyle(.segmented)
                .padding(.horizontal)
                .onChange(of: range) { _, _ in
                    Task { await loadItems() }
                }

                if isLoading {
                    Spacer()
                    ProgressView("加载错题中...")
                    Spacer()
                } else if let errorMessage {
                    Spacer()
                    VStack(spacing: 8) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.system(size: 40))
                            .foregroundColor(.orange)
                        Text(errorMessage)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                    }
                    Spacer()
                } else if items.isEmpty {
                    emptyState
                } else {
                    list
                }
            }
            .padding(.top, 8)
            .navigationTitle("\(student.name) 的错题本")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("关闭") { dismiss() }
                }
            }
            .task {
                await loadItems()
            }
            .refreshable {
                await loadItems()
            }
        }
    }

    // MARK: - Subviews

    private var emptyState: some View {
        VStack(spacing: 16) {
            Spacer()
            Image(systemName: "party.popper.fill")
                .font(.system(size: 60))
                .foregroundColor(.pink)
            Text(emptyStateText)
                .font(.title3)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
            Spacer()
        }
    }

    private var emptyStateText: String {
        switch range {
        case .today: return "今天没错题哦 🎉"
        case .sevenDays: return "近 7 天没错题，继续保持！"
        case .thirtyDays: return "近 30 天没错题，太厉害了！"
        }
    }

    private var list: some View {
        List {
            ForEach(items) { item in
                card(for: item)
                    .listRowInsets(EdgeInsets(top: 6, leading: 12, bottom: 6, trailing: 12))
                    .listRowSeparator(.hidden)
            }
        }
        .listStyle(.plain)
    }

    private func card(for item: WrongItem) -> some View {
        let isExpanded = expandedIds.contains(item.id)
        return VStack(alignment: .leading, spacing: 12) {
            Text(item.questionText)
                .font(.system(size: 22, weight: .semibold))
                .foregroundColor(.primary)
                .fixedSize(horizontal: false, vertical: true)

            HStack(spacing: 16) {
                answerChip(label: "你的答案", value: item.yourAnswer, color: .red)
                answerChip(label: "正确答案", value: item.correctAnswer, color: .green)
            }

            Button {
                withAnimation(.easeInOut(duration: 0.2)) {
                    if isExpanded {
                        expandedIds.remove(item.id)
                    } else {
                        expandedIds.insert(item.id)
                    }
                }
            } label: {
                HStack(spacing: 6) {
                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                    Text(isExpanded ? "收起解释" : "查看解释")
                }
                .font(.subheadline)
                .foregroundColor(.blue)
            }
            .buttonStyle(.plain)

            if isExpanded {
                Text(item.explanation)
                    .font(.body)
                    .foregroundColor(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
                    .padding(10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.blue.opacity(0.08))
                    .cornerRadius(8)
            }

            HStack {
                Text(item.skillId)
                    .font(.caption2)
                    .foregroundColor(.secondary)
                Spacer()
                Text(formattedTimestamp(item.timestamp))
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding(14)
        .background(Color.white)
        .cornerRadius(14)
        .shadow(color: .black.opacity(0.06), radius: 2, y: 1)
    }

    private func answerChip(label: String, value: String, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value)
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(color)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background(color.opacity(0.1))
        .cornerRadius(8)
    }

    // MARK: - Loading

    private func loadItems() async {
        isLoading = true
        errorMessage = nil
        do {
            let scopedStudentId = APIClient.shared.isStudentRole ? nil : student.id
            items = try await APIClient.shared.fetchWrongItems(
                studentId: scopedStudentId,
                since: range.apiValue
            )
        } catch {
            items = []
            errorMessage = "暂时无法加载错题本，请稍后重试。"
        }
        isLoading = false
    }

    private func formattedTimestamp(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .short
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

#Preview {
    WrongItemsView(student: Student(id: "preview", name: "Preview", yearLevel: 4))
}
