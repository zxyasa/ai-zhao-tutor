import SwiftUI
import UIKit

struct ParentDashboardView: View {
    // `ProgressMetricsSnapshot` — moved to Views/DailySummaryCardView.swift (file scope).
    // `SignalKind` — moved to Views/DailySummaryCardView.swift (file scope).

    struct StudentAccount: Identifiable {
        let id: String
        let name: String
    }

    enum Mode: String, CaseIterable {
        case daily = "日报"
        case weekly = "周报"
    }

    @Environment(\.dismiss) private var dismiss
    @StateObject private var viewModel = ParentDashboardViewModel()
    @State private var mode: Mode = .daily
    @State private var selectedDailySummary: ParentDailySummary?
    @State private var selectedContextStudentId: String = ""
    @State private var selectedContextTags: Set<String> = []
    @State private var contextFreeText: String = ""
    @State private var isSubmittingContext = false
    @State private var contextSubmitMessage: String?
    @State private var showAddStudentSheet = false
    @State private var newStudentName = ""
    @State private var newStudentYearLevel = 3
    @State private var newStudentPin = ""
    @State private var isCreatingStudent = false
    @State private var addStudentMessage: String?
    @State private var createdStudentId: String?
    @State private var accountListMessage: String?
    @State private var currentPasswordInput = ""
    @State private var newPasswordInput = ""
    @State private var confirmPasswordInput = ""
    @State private var isChangingPassword = false
    @State private var changePasswordMessage: String?
    @AppStorage("parent_signal_seen_date") private var seenDate: String = ""
    @AppStorage("parent_signal_seen_keys") private var seenSignalKeysCSV: String = ""

    var body: some View {
        NavigationStack {
            VStack(spacing: 14) {
                if viewModel.isLoading {
                    ProgressView(mode == .daily ? "加载日报中..." : "加载周报中...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    Picker("模式", selection: $mode) {
                        ForEach(Mode.allCases, id: \.self) { m in
                            Text(m.rawValue).tag(m)
                        }
                    }
                    .pickerStyle(.segmented)

                    if mode == .daily {
                        parentContextCard
                    }

                    if let errorMessage = viewModel.errorMessage {
                        HStack(spacing: 8) {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundColor(.orange)
                            Text(errorMessage)
                                .foregroundColor(.secondary)
                            Spacer()
                        }
                        .font(.subheadline)
                        .padding(10)
                        .background(Color.yellow.opacity(0.16))
                        .clipShape(RoundedRectangle(cornerRadius: 10))
                    }

                    ScrollView {
                        VStack(spacing: 12) {
                            studentAccountsCard
                            accountSecurityCard

                            if mode == .daily {
                                if viewModel.summaries.isEmpty {
                                    emptyStateView(
                                        title: "今天还没有日报数据",
                                        subtitle: "孩子完成练习后，这里会自动更新进度和风险信号。"
                                    )
                                } else {
                                    ForEach(viewModel.summaries) { summary in
                                        DailySummaryCardView(
                                            summary: summary,
                                            signals: makeSignals(for: summary),
                                            onSignalTapped: { kind in
                                                markSignalSeen(studentId: summary.studentId, kind: kind)
                                                selectedDailySummary = summary
                                            }
                                        )
                                    }
                                }
                            } else {
                                if viewModel.weeklySummaries.isEmpty {
                                    emptyStateView(
                                        title: "本周还没有周报数据",
                                        subtitle: "累计几天练习后，这里会展示达标天数与周趋势。"
                                    )
                                } else {
                                    ForEach(viewModel.weeklySummaries) { summary in
                                        weeklyCard(summary)
                                    }
                                }
                            }
                        }
                        .padding(.vertical, 2)
                    }
                    .scrollIndicators(.hidden)

                    Button {
                        Task { await viewModel.loadSummaries(mode: mode) }
                    } label: {
                        HStack(spacing: 6) {
                            Image(systemName: "arrow.clockwise")
                            Text("刷新")
                        }
                        .font(.subheadline.weight(.semibold))
                        .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.blue)
                }
            }
            .padding()
            .navigationTitle("家长日报")
            .animation(.easeInOut(duration: 0.2), value: mode)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("添加学生") {
                        showAddStudentSheet = true
                    }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("关闭") { dismiss() }
                }
            }
            .task {
                rolloverSeenStateIfNeeded()
                await viewModel.loadSummaries(mode: mode)
            }
            .onChange(of: mode) { _, _ in
                Task { await viewModel.loadSummaries(mode: mode) }
            }
        }
        .sheet(item: $selectedDailySummary) { summary in
            StudentSignalsDetailView(summary: summary)
        }
        .sheet(isPresented: $showAddStudentSheet) {
            addStudentSheet
        }
    }

    /// Bundle the per-student signal state into a `DailySummarySignals` value
    /// so the daily card view doesn't need to know about our six `@State` maps.
    private func makeSignals(for summary: ParentDailySummary) -> DailySummarySignals {
        DailySummarySignals(
            newBadgeCount: viewModel.newBadgeCountByStudent[summary.studentId] ?? 0,
            streakAtRisk: viewModel.streakAtRiskByStudent[summary.studentId] ?? false,
            learningRiskLevel: viewModel.learningRiskByStudent[summary.studentId],
            learningRiskReasons: viewModel.learningRiskReasonsByStudent[summary.studentId] ?? [],
            progressMetrics: viewModel.progressMetricsByStudent[summary.studentId],
            progressTrend: viewModel.progressTrendByStudent[summary.studentId],
            badgeUnread: isSignalUnread(studentId: summary.studentId, kind: .newBadge),
            streakUnread: isSignalUnread(studentId: summary.studentId, kind: .streakRisk),
            learningUnread: isSignalUnread(studentId: summary.studentId, kind: .learningRisk)
        )
    }

    private var parentContextCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("今日情况")
                .font(.subheadline.weight(.semibold))

            Picker("学生", selection: $selectedContextStudentId) {
                Text("全部孩子").tag("")
                ForEach(viewModel.summaries) { summary in
                    Text(summary.studentName).tag(summary.studentId)
                }
            }
            .pickerStyle(.menu)

            let tagOptions = ["tired", "frustrated", "confident", "distracted", "happy"]
            HStack(spacing: 6) {
                ForEach(tagOptions, id: \.self) { tag in
                    Button(tag) {
                        if selectedContextTags.contains(tag) {
                            selectedContextTags.remove(tag)
                        } else {
                            selectedContextTags.insert(tag)
                        }
                    }
                    .font(.caption2)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 5)
                    .background(selectedContextTags.contains(tag) ? Color.blue.opacity(0.2) : Color(.systemGray5))
                    .clipShape(Capsule())
                }
            }

            TextField("补充描述（例如：今天有点累，注意力一般）", text: $contextFreeText, axis: .vertical)
                .textFieldStyle(.roundedBorder)
                .lineLimit(2...4)

            HStack {
                Button(isSubmittingContext ? "提交中..." : "提交今日情况") {
                    Task { await submitParentContext() }
                }
                .buttonStyle(.borderedProminent)
                .disabled(isSubmittingContext)

                if let contextSubmitMessage {
                    Text(contextSubmitMessage)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private func submitParentContext() async {
        isSubmittingContext = true
        contextSubmitMessage = nil
        do {
            _ = try await APIClient.shared.submitParentContext(
                studentId: selectedContextStudentId.isEmpty ? nil : selectedContextStudentId,
                tags: Array(selectedContextTags).sorted(),
                freeText: contextFreeText
            )
            contextSubmitMessage = "已提交"
            contextFreeText = ""
            selectedContextTags = []
            await viewModel.loadSummaries(mode: mode)
        } catch {
            contextSubmitMessage = "提交失败"
        }
        isSubmittingContext = false
    }

    private var studentAccountsCard: some View {
        let accounts = studentAccounts
        return VStack(alignment: .leading, spacing: 10) {
            Text("Student Accounts")
                .font(.subheadline.weight(.semibold))

            if accounts.isEmpty {
                Text("No student accounts yet.")
                    .font(.caption)
                    .foregroundColor(.secondary)
            } else {
                ForEach(accounts, id: \.id) { account in
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(account.name)
                                .font(.subheadline)
                            Text(account.id)
                                .font(.caption.monospaced())
                                .foregroundColor(.secondary)
                        }
                        Spacer()
                        Button("Copy ID") {
                            UIPasteboard.general.string = account.id
                            accountListMessage = "Copied \(account.name) ID."
                        }
                        .buttonStyle(.bordered)
                        .font(.caption)
                    }
                }
            }

            if let accountListMessage {
                Text(accountListMessage)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var accountSecurityCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Account Security")
                .font(.subheadline.weight(.semibold))

            SecureField("Current password", text: $currentPasswordInput)
                .textFieldStyle(.roundedBorder)
            SecureField("New password (min 8 chars)", text: $newPasswordInput)
                .textFieldStyle(.roundedBorder)
            SecureField("Confirm new password", text: $confirmPasswordInput)
                .textFieldStyle(.roundedBorder)

            HStack {
                Button(isChangingPassword ? "Updating..." : "Change Password") {
                    Task { await changePassword() }
                }
                .buttonStyle(.borderedProminent)
                .disabled(isChangingPassword || !canChangePassword)

                if let changePasswordMessage {
                    Text(changePasswordMessage)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var studentAccounts: [StudentAccount] {
        if !viewModel.summaries.isEmpty {
            return viewModel.summaries.map { StudentAccount(id: $0.studentId, name: $0.studentName) }
        }
        if !viewModel.weeklySummaries.isEmpty {
            return viewModel.weeklySummaries.map { StudentAccount(id: $0.studentId, name: $0.studentName) }
        }
        return []
    }

    private var canChangePassword: Bool {
        guard !currentPasswordInput.isEmpty else { return false }
        guard newPasswordInput.count >= 8 else { return false }
        return newPasswordInput == confirmPasswordInput
    }

    private func changePassword() async {
        isChangingPassword = true
        changePasswordMessage = nil
        do {
            try await APIClient.shared.changeParentPassword(
                currentPassword: currentPasswordInput,
                newPassword: newPasswordInput
            )
            changePasswordMessage = "Password updated."
            currentPasswordInput = ""
            newPasswordInput = ""
            confirmPasswordInput = ""
        } catch {
            changePasswordMessage = "Update failed: \(error.localizedDescription)"
        }
        isChangingPassword = false
    }

    private var addStudentSheet: some View {
        NavigationStack {
            Form {
                Section("学生信息") {
                    TextField("姓名", text: $newStudentName)
                    Picker("年级", selection: $newStudentYearLevel) {
                        ForEach(1...12, id: \.self) { year in
                            Text("Year \(year)").tag(year)
                        }
                    }
                }
                Section("登录 PIN") {
                    SecureField("4-8位数字", text: $newStudentPin)
                        .keyboardType(.numberPad)
                }
                if let addStudentMessage {
                    Section {
                        Text(addStudentMessage)
                            .font(.footnote)
                            .foregroundColor(.secondary)
                    }
                }
                if let createdStudentId {
                    Section("New Student ID") {
                        Text(createdStudentId)
                            .font(.system(.body, design: .monospaced))
                        Button("Copy Student ID") {
                            UIPasteboard.general.string = createdStudentId
                            addStudentMessage = "Student ID copied."
                        }
                    }
                }
            }
            .navigationTitle("添加学生")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("取消") { showAddStudentSheet = false }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button(isCreatingStudent ? "创建中..." : "创建") {
                        Task { await createStudent() }
                    }
                    .disabled(isCreatingStudent || !canCreateStudent)
                }
            }
        }
    }

    private var canCreateStudent: Bool {
        let trimmedName = newStudentName.trimmingCharacters(in: .whitespacesAndNewlines)
        let trimmedPin = newStudentPin.trimmingCharacters(in: .whitespacesAndNewlines)
        return !trimmedName.isEmpty && trimmedPin.count >= 4 && trimmedPin.count <= 8
    }

    private func createStudent() async {
        isCreatingStudent = true
        addStudentMessage = nil
        createdStudentId = nil
        do {
            let student = try await APIClient.shared.createParentStudent(
                name: newStudentName.trimmingCharacters(in: .whitespacesAndNewlines),
                yearLevel: newStudentYearLevel,
                pin: newStudentPin.trimmingCharacters(in: .whitespacesAndNewlines)
            )
            createdStudentId = student.id
            addStudentMessage = "Created successfully. Student ID is shown below."
            newStudentName = ""
            newStudentYearLevel = 3
            newStudentPin = ""
            await viewModel.loadSummaries(mode: mode)
        } catch {
            addStudentMessage = "创建失败：\(error.localizedDescription)"
        }
        isCreatingStudent = false
    }

    private func rolloverSeenStateIfNeeded() {
        let today = DateFormatter.dayKey.string(from: Date())
        if seenDate != today {
            seenDate = today
            seenSignalKeysCSV = ""
        }
    }

    private func isSignalUnread(studentId: String, kind: SignalKind) -> Bool {
        let seen = Set(seenSignalKeysCSV.split(separator: ",").map(String.init))
        return !seen.contains(signalKey(studentId: studentId, kind: kind))
    }

    private func markSignalSeen(studentId: String, kind: SignalKind) {
        var seen = Set(seenSignalKeysCSV.split(separator: ",").map(String.init))
        seen.insert(signalKey(studentId: studentId, kind: kind))
        seenSignalKeysCSV = seen.sorted().joined(separator: ",")
    }

    private func signalKey(studentId: String, kind: SignalKind) -> String {
        "\(studentId)|\(kind.rawValue)"
    }

    private func weeklyCard(_ summary: ParentWeeklySummary) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(summary.avatarEmoji)
                    .font(.system(size: 36))
                VStack(alignment: .leading) {
                    Text(summary.studentName)
                        .font(.headline)
                    Text("\(summary.fromDate) - \(summary.toDate)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                Spacer()
                Text("连击 \(summary.currentStreak)")
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.blue.opacity(0.15))
                    .clipShape(RoundedRectangle(cornerRadius: 6))
            }

            HStack {
                Text("达标天数 \(summary.completedDays)/7")
                Spacer()
                Text("周正确率 \(String(format: "%.1f", summary.accuracyPercent))%")
            }
            .font(.subheadline)

            HStack {
                Text("完成题数 \(summary.totalCompletedQuestions)")
                Spacer()
                Text("答题数 \(summary.totalEvents)")
            }
            .font(.subheadline)
            .foregroundColor(.secondary)

            Divider()

            VStack(alignment: .leading, spacing: 6) {
                Text("周趋势")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.secondary)
                weeklyMetricBar(
                    title: "达标率",
                    value: "\(String(format: "%.0f", (Double(summary.completedDays) / 7.0) * 100.0))%",
                    percent: (Double(summary.completedDays) / 7.0) * 100.0,
                    color: .blue
                )
                weeklyMetricBar(
                    title: "准确率",
                    value: "\(String(format: "%.1f", summary.accuracyPercent))%",
                    percent: summary.accuracyPercent,
                    color: .green
                )
                weeklyMetricBar(
                    title: "练习量",
                    value: "\(summary.totalEvents)",
                    percent: min(Double(summary.totalEvents) / 70.0 * 100.0, 100.0),
                    color: .orange
                )
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 14))
        .overlay(
            RoundedRectangle(cornerRadius: 14)
                .stroke(Color.primary.opacity(0.06), lineWidth: 1)
        )
        .shadow(color: Color.black.opacity(0.03), radius: 8, x: 0, y: 4)
    }

    @ViewBuilder
    private func weeklyMetricBar(title: String, value: String, percent: Double, color: Color) -> some View {
        HStack(spacing: 8) {
            Text(title)
                .font(.caption2)
                .foregroundColor(.secondary)
                .frame(width: 34, alignment: .leading)

            ZStack(alignment: .leading) {
                Capsule()
                    .fill(Color(.systemGray5))
                    .frame(height: 8)

                Capsule()
                    .fill(color.opacity(0.85))
                    .frame(width: weeklyBarWidth(percent), height: 8)
            }
            .frame(maxWidth: .infinity)

            Text(value)
                .font(.caption2.weight(.semibold))
                .foregroundColor(.secondary)
                .frame(width: 48, alignment: .trailing)
        }
    }

    private func weeklyBarWidth(_ percent: Double) -> CGFloat {
        let bounded = min(max(percent, 0.0), 100.0)
        return max(8, CGFloat(bounded / 100.0) * 160.0)
    }

    @ViewBuilder
    private func emptyStateView(title: String, subtitle: String) -> some View {
        VStack(spacing: 8) {
            Image(systemName: "tray")
                .font(.title3)
                .foregroundColor(.secondary)
            Text(title)
                .font(.subheadline.weight(.semibold))
            Text(subtitle)
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 28)
        .padding(.horizontal, 16)
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }

}

private extension DateFormatter {
    static let dayKey: DateFormatter = {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter
    }()
}

// `riskReasonLabel(_:)` — moved to Views/DashboardHelpers.swift.
// `StudentSignalsDetailView` — moved to Views/StudentSignalsDetailView.swift.

#Preview {
    ParentDashboardView()
}

