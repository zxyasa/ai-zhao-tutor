//
//  QuestionView.swift
//  MathCoach
//
//  Main question display and answer input view
//

import SwiftUI

struct QuestionView: View {
    private let student: Student
    @StateObject private var viewModel: QuestionViewModel
    @FocusState private var answerFieldFocused: Bool
    @State private var showAchievements = false
    @State private var showWrongItems = false

    init(student: Student) {
        self.student = student
        let scopedStudentId = APIClient.shared.isStudentRole ? nil : student.id
        _viewModel = StateObject(wrappedValue: QuestionViewModel(studentId: scopedStudentId))
    }

    var body: some View {
        ZStack {
            // Background gradient
            LinearGradient(
                gradient: Gradient(colors: [Color.blue.opacity(0.1), Color.purple.opacity(0.1)]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            if viewModel.isLoading {
                loadingView
            } else if let error = viewModel.errorMessage {
                errorView(message: error)
            } else if viewModel.showExplanation, let item = viewModel.currentItem {
                explanationView(item: item)
            } else if let item = viewModel.currentItem {
                questionView(item: item)
            } else {
                welcomeView
            }

            // Phase 9.3 overlays (top of z-stack)
            if let example = viewModel.pendingWorkedExample, viewModel.pendingCelebrationLabel == nil {
                WorkedExampleView(
                    skillLabel: viewModel.currentItem?.skillId,
                    example: example
                ) {
                    viewModel.dismissWorkedExample()
                    answerFieldFocused = true
                }
                .transition(.opacity)
                .zIndex(20)
            }

            if let label = viewModel.pendingCelebrationLabel {
                GraduationCelebrationView(stageLabel: label) {
                    viewModel.dismissCelebration()
                }
                .transition(.opacity)
                .zIndex(30)
            }
        }
        .animation(.easeInOut(duration: 0.25), value: viewModel.pendingCelebrationLabel)
        .animation(.easeInOut(duration: 0.25), value: viewModel.pendingWorkedExample)
        .task {
            // Check backend health on appear
            let isHealthy = await viewModel.checkBackendHealth()
            if isHealthy {
                await viewModel.loadNextQuestion()
            } else {
                viewModel.errorMessage = "无法连接到后端服务。请检查网络，或回到登录页确认 API 地址。"
            }
        }
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button("徽章") {
                    showAchievements = true
                }
            }
            ToolbarItem(placement: .topBarTrailing) {
                Button("错题本") {
                    showWrongItems = true
                }
            }
        }
        .sheet(isPresented: $showAchievements) {
            AchievementsView(student: student)
        }
        .sheet(isPresented: $showWrongItems) {
            WrongItemsView(student: student)
        }
    }

    // MARK: - Welcome View

    private var welcomeView: some View {
        VStack(spacing: 30) {
            Image(systemName: "brain.head.profile")
                .font(.system(size: 100))
                .foregroundColor(.blue)

            Text("MathCoach")
                .font(.system(size: 48, weight: .bold))

            Text("\(student.name) 的 AI 数学训练")
                .font(.title2)
                .foregroundColor(.secondary)

            Button("开始练习") {
                Task {
                    await viewModel.loadNextQuestion()
                }
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
        }
        .padding()
    }

    // MARK: - Loading View

    private var loadingView: some View {
        VStack(spacing: 20) {
            ProgressView()
                .scaleEffect(2)

            Text("加载中...")
                .font(.title3)
                .foregroundColor(.secondary)
        }
    }

    // MARK: - Error View

    private func errorView(message: String) -> some View {
        VStack(spacing: 30) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 80))
                .foregroundColor(.red)

            Text("出错了")
                .font(.title)
                .fontWeight(.bold)

            Text(message)
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)

            Button("重试") {
                Task {
                    await viewModel.loadNextQuestion()
                }
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
        }
        .padding()
    }

    // MARK: - Question View

    private func questionView(item: Item) -> some View {
        VStack(spacing: 30) {
            // Header with timer
            HStack {
                Text("难度: \(item.difficulty)")
                    .font(.headline)
                    .foregroundColor(.secondary)

                Spacer()

                Text("今日 \(viewModel.dailyCompleted)/\(viewModel.dailyTarget)")
                    .font(.headline)
                    .foregroundColor(.secondary)

                Spacer()

                HStack(spacing: 5) {
                    Image(systemName: "clock")
                    Text(formatTime(viewModel.timeSpent))
                }
                .font(.headline)
                .foregroundColor(.secondary)
            }
            .padding(.horizontal)

            Spacer()

            // Question card
            VStack(spacing: 30) {
                if item.questionType == "fraction",
                   let fractionBar = FractionBarView.extract(from: item.parameters) {
                    fractionBar
                        .frame(maxWidth: 400)
                        .padding(.horizontal)
                }

                Text(item.questionText)
                    .font(.system(size: 36, weight: .medium))
                    .foregroundColor(.black)
                    .multilineTextAlignment(.center)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color.white)
                    .cornerRadius(20)
                    .shadow(radius: 5)

                // Answer display (read-only — keypad drives input)
                VStack(spacing: 12) {
                    Text(viewModel.studentAnswer.isEmpty ? " " : viewModel.studentAnswer)
                        .font(.system(size: 40, weight: .bold, design: .rounded))
                        .foregroundColor(.primary)
                        .frame(maxWidth: .infinity, minHeight: 64)
                        .background(Color.white)
                        .cornerRadius(14)
                        .overlay(
                            RoundedRectangle(cornerRadius: 14)
                                .stroke(Color.blue.opacity(0.3), lineWidth: 2)
                        )

                    if let validation = viewModel.inputValidationMessage {
                        Text(validation)
                            .font(.caption)
                            .foregroundColor(.red)
                            .multilineTextAlignment(.center)
                    }
                }
                .padding(.horizontal, 40)
            }

            // Hint section
            if viewModel.showHint {
                HStack {
                    Image(systemName: "lightbulb.fill")
                        .foregroundColor(.yellow)
                    Text(item.hint)
                        .font(.body)
                }
                .padding()
                .background(Color.yellow.opacity(0.1))
                .cornerRadius(10)
                .padding(.horizontal)
            }

            // Keypad + hint toggle
            VStack(spacing: 12) {
                MathKeypad(
                    value: $viewModel.studentAnswer,
                    allowSlash: item.questionType == "fraction",
                    allowDot: item.questionType == "numeric",
                    onSubmit: submitAnswer
                )
                .padding(.horizontal, 20)
                .onChange(of: viewModel.studentAnswer) { _, _ in
                    viewModel.inputValidationMessage = nil
                }

                Button {
                    viewModel.toggleHint()
                } label: {
                    Label(viewModel.showHint ? "隐藏提示" : "显示提示", systemImage: "lightbulb")
                }
                .buttonStyle(.bordered)
                .controlSize(.large)
            }
            .padding(.bottom, 20)
        }
        .padding()
    }

    // MARK: - Explanation View

    private func explanationView(item: Item) -> some View {
        VStack(spacing: 30) {
            // Result indicator
            ZStack {
                Circle()
                    .fill(viewModel.isCorrect == true ? Color.green.opacity(0.2) : Color.red.opacity(0.2))
                    .frame(width: 150, height: 150)

                Image(systemName: viewModel.isCorrect == true ? "checkmark.circle.fill" : "xmark.circle.fill")
                    .font(.system(size: 80))
                    .foregroundColor(viewModel.isCorrect == true ? .green : .red)
            }

            Text(viewModel.isCorrect == true ? "答对了！" : "不对哦")
                .font(.system(size: 48, weight: .bold))
                .foregroundColor(viewModel.isCorrect == true ? .green : .red)

            // Answer comparison
            VStack(spacing: 15) {
                HStack {
                    Text("你的答案:")
                        .font(.title3)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text(viewModel.studentAnswer)
                        .font(.title2)
                        .fontWeight(.bold)
                }

                HStack {
                    Text("正确答案:")
                        .font(.title3)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text(item.correctAnswer)
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.green)
                }
            }
            .padding()
            .background(Color.white)
            .cornerRadius(15)
            .shadow(radius: 3)
            .padding(.horizontal)

            // Explanation
            VStack(alignment: .leading, spacing: 10) {
                Text("解释:")
                    .font(.headline)

                Text(item.explanation)
                    .font(.body)
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.blue.opacity(0.1))
            .cornerRadius(15)
            .padding(.horizontal)

            // Stats
            HStack(spacing: 30) {
                VStack {
                    Text("耗时")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(formatTime(viewModel.timeSpent))
                        .font(.title3)
                        .fontWeight(.bold)
                }

                VStack {
                    Text("使用提示")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(viewModel.showHint ? "是" : "否")
                        .font(.title3)
                        .fontWeight(.bold)
                }
            }
            .padding()

            Spacer()

            // Next button
            Button {
                viewModel.nextQuestion()
            } label: {
                Label("下一题", systemImage: "arrow.right.circle.fill")
                    .font(.title3)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
            .padding(.bottom, 30)
        }
        .padding()
        .onAppear {
            if viewModel.isCorrect == true {
                Feedback.correct()
            } else if viewModel.isCorrect == false {
                Feedback.incorrect()
            }
        }
    }

    // MARK: - Helper Methods

    private func submitAnswer() {
        answerFieldFocused = false
        Task {
            await viewModel.submitAnswer()
        }
    }

    private func formatTime(_ seconds: Double) -> String {
        let minutes = Int(seconds) / 60
        let secs = Int(seconds) % 60
        return String(format: "%d:%02d", minutes, secs)
    }
}

#Preview {
    QuestionView(student: Student(id: "preview", name: "Preview", yearLevel: 4))
}
