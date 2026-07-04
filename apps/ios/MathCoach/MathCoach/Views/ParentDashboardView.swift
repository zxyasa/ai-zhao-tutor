import SwiftUI
import UIKit

struct ParentDashboardView: View {
    struct ProgressMetricsSnapshot {
        let completionRatePercent: Double
        let accuracyVolatility: Double
        let recoverySpeedDays: Int?
    }
    struct StudentAccount: Identifiable {
        let id: String
        let name: String
    }

    enum Mode: String, CaseIterable {
        case daily = "日报"
        case weekly = "周报"
    }
    enum SignalKind: String {
        case newBadge
        case streakRisk
        case learningRisk
    }

    @Environment(\.dismiss) private var dismiss
    @State private var mode: Mode = .daily
    @State private var summaries: [ParentDailySummary] = []
    @State private var weeklySummaries: [ParentWeeklySummary] = []
    @State private var newBadgeCountByStudent: [String: Int] = [:]
    @State private var streakAtRiskByStudent: [String: Bool] = [:]
    @State private var learningRiskByStudent: [String: String] = [:]
    @State private var learningRiskReasonsByStudent: [String: [String]] = [:]
    @State private var progressMetricsByStudent: [String: ProgressMetricsSnapshot] = [:]
    @State private var progressTrendByStudent: [String: [ParentProgress.DayPoint]] = [:]
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
    @State private var isLoading = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            VStack(spacing: 14) {
                if isLoading {
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

                    if let errorMessage {
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
                                if summaries.isEmpty {
                                    emptyStateView(
                                        title: "今天还没有日报数据",
                                        subtitle: "孩子完成练习后，这里会自动更新进度和风险信号。"
                                    )
                                } else {
                                    ForEach(summaries) { summary in
                                        summaryCard(summary)
                                    }
                                }
                            } else {
                                if weeklySummaries.isEmpty {
                                    emptyStateView(
                                        title: "本周还没有周报数据",
                                        subtitle: "累计几天练习后，这里会展示达标天数与周趋势。"
                                    )
                                } else {
                                    ForEach(weeklySummaries) { summary in
                                        weeklyCard(summary)
                                    }
                                }
                            }
                        }
                        .padding(.vertical, 2)
                    }
                    .scrollIndicators(.hidden)

                    Button {
                        Task { await loadSummaries() }
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
                await loadSummaries()
            }
            .onChange(of: mode) { _, _ in
                Task { await loadSummaries() }
            }
        }
        .sheet(item: $selectedDailySummary) { summary in
            StudentSignalsDetailView(summary: summary)
        }
        .sheet(isPresented: $showAddStudentSheet) {
            addStudentSheet
        }
    }

    private func summaryCard(_ summary: ParentDailySummary) -> some View {
        let badgeUnread = isSignalUnread(studentId: summary.studentId, kind: .newBadge)
        let streakUnread = isSignalUnread(studentId: summary.studentId, kind: .streakRisk)
        let learningUnread = isSignalUnread(studentId: summary.studentId, kind: .learningRisk)
        return VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(summary.avatarEmoji)
                    .font(.system(size: 36))
                VStack(alignment: .leading) {
                    Text(summary.studentName)
                        .font(.headline)
                    Text("连击 \(summary.currentStreak) 天 (历史 \(summary.longestStreak))")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Text("徽章 \(summary.badgeCount)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    if let newCount = newBadgeCountByStudent[summary.studentId], newCount > 0 {
                        Button("🆕 今日新徽章 \(newCount)") {
                            markSignalSeen(studentId: summary.studentId, kind: .newBadge)
                            selectedDailySummary = summary
                        }
                        .buttonStyle(.plain)
                        .font(.caption)
                        .foregroundColor(badgeUnread ? .green : .secondary)
                    }
                    if streakAtRiskByStudent[summary.studentId] == true {
                        Button("⚠️ 连击今天有中断风险") {
                            markSignalSeen(studentId: summary.studentId, kind: .streakRisk)
                            selectedDailySummary = summary
                        }
                        .buttonStyle(.plain)
                        .font(.caption)
                        .foregroundColor(streakUnread ? .orange : .secondary)
                    }
                    if let riskLevel = learningRiskByStudent[summary.studentId],
                       riskLevel == "high" || riskLevel == "medium" {
                        Button("📉 学习风险：\(riskLevelLabel(riskLevel))") {
                            markSignalSeen(studentId: summary.studentId, kind: .learningRisk)
                            selectedDailySummary = summary
                        }
                        .buttonStyle(.plain)
                        .font(.caption)
                        .foregroundColor(learningUnread ? riskLevelColor(riskLevel) : .secondary)
                    }
                    if let reasons = learningRiskReasonsByStudent[summary.studentId], !reasons.isEmpty {
                        Text("主要信号 \(riskReasonLabel(reasons[0]))")
                            .font(.caption2.weight(.medium))
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(riskLevelColor(learningRiskByStudent[summary.studentId] ?? "low").opacity(0.12))
                            .foregroundColor(.secondary)
                            .clipShape(RoundedRectangle(cornerRadius: 6))
                    }
                    if let metrics = progressMetricsByStudent[summary.studentId] {
                        Text(
                            "完成率 \(String(format: "%.0f", metrics.completionRatePercent))% · " +
                            "波动 \(String(format: "%.2f", metrics.accuracyVolatility)) · " +
                            "恢复 \(metrics.recoverySpeedDays.map { "\($0)天" } ?? "未恢复")"
                        )
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    }
                    if let trend = progressTrendByStudent[summary.studentId], !trend.isEmpty {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("最近7天准确率")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                            HStack(alignment: .bottom, spacing: 4) {
                                ForEach(trend) { point in
                                    Capsule()
                                        .fill(cardTrendBarColor(point.accuracyPercent, hasData: point.eventsTotal > 0))
                                        .frame(width: 10, height: cardTrendBarHeight(point.accuracyPercent, hasData: point.eventsTotal > 0))
                                }
                            }
                        }
                    }
                    if let aiInsight = summary.aiInsight, !aiInsight.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                        Text("AI 洞察：\(aiInsight)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .padding(.top, 2)
                    }
                }
                Spacer()
                Text(summary.isCompleted ? "完成" : "进行中")
                    .font(.caption.weight(.semibold))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(summary.isCompleted ? Color.green.opacity(0.2) : Color.orange.opacity(0.2))
                    .clipShape(RoundedRectangle(cornerRadius: 6))
            }

            HStack {
                Text("进度 \(summary.completedQuestions)/\(summary.targetQuestions)")
                Spacer()
                Text("正确率 \(String(format: "%.1f", summary.accuracyPercent))%")
            }
            .font(.subheadline)

            HStack {
                Text("答题数 \(summary.eventsTotal)")
                Spacer()
                Text("平均耗时 \(String(format: "%.1f", summary.averageTimeSpentSeconds))s")
            }
            .font(.subheadline)
            .foregroundColor(.secondary)
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

    private func loadSummaries() async {
        rolloverSeenStateIfNeeded()
        isLoading = true
        errorMessage = nil

        do {
            if mode == .daily {
                let fetched = try await APIClient.shared.fetchParentDailySummaries()
                summaries = fetched.isEmpty ? fallbackSummaries() : fetched
                await enrichDailySignals(for: summaries)
            } else {
                let fetched = try await APIClient.shared.fetchParentWeeklySummaries()
                weeklySummaries = fetched.isEmpty ? fallbackWeeklySummaries() : fetched
                newBadgeCountByStudent = [:]
                streakAtRiskByStudent = [:]
                learningRiskByStudent = [:]
                learningRiskReasonsByStudent = [:]
                progressMetricsByStudent = [:]
                progressTrendByStudent = [:]
            }
        } catch {
            if mode == .daily {
                summaries = fallbackSummaries()
            } else {
                weeklySummaries = fallbackWeeklySummaries()
            }
            errorMessage = "后端暂不可用，显示本地示例数据。"
        }

        isLoading = false
    }

    private var parentContextCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("今日情况")
                .font(.subheadline.weight(.semibold))

            Picker("学生", selection: $selectedContextStudentId) {
                Text("全部孩子").tag("")
                ForEach(summaries) { summary in
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
            await loadSummaries()
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
        if !summaries.isEmpty {
            return summaries.map { StudentAccount(id: $0.studentId, name: $0.studentName) }
        }
        if !weeklySummaries.isEmpty {
            return weeklySummaries.map { StudentAccount(id: $0.studentId, name: $0.studentName) }
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
            await loadSummaries()
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

    private func enrichDailySignals(for dailySummaries: [ParentDailySummary]) async {
        var newBadgeMap: [String: Int] = [:]
        var streakRiskMap: [String: Bool] = [:]
        var learningRiskMap: [String: String] = [:]
        var learningRiskReasonsMap: [String: [String]] = [:]
        var metricsMap: [String: ProgressMetricsSnapshot] = [:]
        var trendMap: [String: [ParentProgress.DayPoint]] = [:]

        for summary in dailySummaries {
            do {
                let newAchievements = try await APIClient.shared.fetchNewAchievements(
                    studentId: summary.studentId,
                    lookbackHours: 24
                )
                newBadgeMap[summary.studentId] = newAchievements.count
            } catch {
                newBadgeMap[summary.studentId] = 0
            }

            do {
                let streakStatus = try await APIClient.shared.fetchStreakStatus(studentId: summary.studentId)
                streakRiskMap[summary.studentId] = streakStatus.isStreakAtRisk
            } catch {
                streakRiskMap[summary.studentId] = false
            }

            do {
                let progress = try await APIClient.shared.fetchParentProgress(studentId: summary.studentId, days: 30)
                learningRiskMap[summary.studentId] = progress.riskLevel
                learningRiskReasonsMap[summary.studentId] = progress.riskReasons
                metricsMap[summary.studentId] = ProgressMetricsSnapshot(
                    completionRatePercent: progress.completionRatePercent,
                    accuracyVolatility: progress.accuracyVolatility,
                    recoverySpeedDays: progress.recoverySpeedDays
                )
                trendMap[summary.studentId] = Array(progress.timeline.suffix(7))
            } catch {
                learningRiskMap[summary.studentId] = "low"
                learningRiskReasonsMap[summary.studentId] = []
                metricsMap[summary.studentId] = ProgressMetricsSnapshot(
                    completionRatePercent: 0.0,
                    accuracyVolatility: 0.0,
                    recoverySpeedDays: nil
                )
                trendMap[summary.studentId] = []
            }
        }

        newBadgeCountByStudent = newBadgeMap
        streakAtRiskByStudent = streakRiskMap
        learningRiskByStudent = learningRiskMap
        learningRiskReasonsByStudent = learningRiskReasonsMap
        progressMetricsByStudent = metricsMap
        progressTrendByStudent = trendMap
    }

    private func cardTrendBarHeight(_ accuracy: Double, hasData: Bool) -> CGFloat {
        guard hasData else { return 6 }
        let bounded = min(max(accuracy, 0.0), 100.0)
        return max(8, CGFloat(bounded / 100.0) * 26.0)
    }

    private func cardTrendBarColor(_ accuracy: Double, hasData: Bool) -> Color {
        guard hasData else { return Color(.systemGray4) }
        if accuracy >= 80 { return .green }
        if accuracy >= 60 { return .orange }
        return .red
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

    private func riskLevelLabel(_ level: String) -> String {
        switch level {
        case "high":
            return "高"
        case "medium":
            return "中"
        default:
            return "低"
        }
    }

    private func riskLevelColor(_ level: String) -> Color {
        switch level {
        case "high":
            return .red
        case "medium":
            return .orange
        default:
            return .green
        }
    }

    private func fallbackSummaries() -> [ParentDailySummary] {
        [
            ParentDailySummary(
                studentId: "jon_zhao",
                studentName: "Jon",
                avatar: "lion",
                sessionDate: "2026-02-18",
                completedQuestions: 0,
                targetQuestions: 10,
                isCompleted: false,
                eventsTotal: 0,
                correctAnswers: 0,
                accuracyPercent: 0,
                averageTimeSpentSeconds: 0,
                currentStreak: 0,
                longestStreak: 0,
                badgeCount: 0,
                aiInsight: nil
            ),
            ParentDailySummary(
                studentId: "astrid_zhao",
                studentName: "Astrid",
                avatar: "unicorn",
                sessionDate: "2026-02-18",
                completedQuestions: 0,
                targetQuestions: 10,
                isCompleted: false,
                eventsTotal: 0,
                correctAnswers: 0,
                accuracyPercent: 0,
                averageTimeSpentSeconds: 0,
                currentStreak: 0,
                longestStreak: 0,
                badgeCount: 0,
                aiInsight: nil
            ),
        ]
    }

    private func fallbackWeeklySummaries() -> [ParentWeeklySummary] {
        [
            ParentWeeklySummary(
                studentId: "jon_zhao",
                studentName: "Jon",
                avatar: "lion",
                fromDate: "2026-02-12",
                toDate: "2026-02-18",
                completedDays: 0,
                totalCompletedQuestions: 0,
                totalEvents: 0,
                accuracyPercent: 0,
                currentStreak: 0,
                longestStreak: 0
            ),
            ParentWeeklySummary(
                studentId: "astrid_zhao",
                studentName: "Astrid",
                avatar: "unicorn",
                fromDate: "2026-02-12",
                toDate: "2026-02-18",
                completedDays: 0,
                totalCompletedQuestions: 0,
                totalEvents: 0,
                accuracyPercent: 0,
                currentStreak: 0,
                longestStreak: 0
            ),
        ]
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

