import SwiftUI

struct StudentPickerView: View {
    @State private var students: [Student] = []
    @State private var isLoading = false
    @State private var errorMessage: String?

    let onSelect: (Student) -> Void

    var body: some View {
        VStack(spacing: 20) {
            Text("谁来练习数学？")
                .font(.largeTitle.bold())

            if isLoading {
                ProgressView("加载学生中...")
            } else {
                if let errorMessage {
                    Text(errorMessage)
                        .font(.subheadline)
                        .multilineTextAlignment(.center)
                        .foregroundColor(.secondary)
                        .padding(8)
                        .background(Color.yellow.opacity(0.2))
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                }

                ForEach(students) { student in
                    Button {
                        onSelect(student)
                    } label: {
                        HStack(spacing: 16) {
                            Text(student.avatarEmoji)
                                .font(.system(size: 44))

                            VStack(alignment: .leading, spacing: 6) {
                                Text(student.name)
                                    .font(.title3.bold())
                                Text("Year \(student.yearLevel)")
                                    .foregroundColor(.secondary)
                                Text("🔥 \(student.currentStreak)天  目标 \(student.targetDailyQuestions)题/天")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                            Spacer()
                            Text("开始训练")
                                .font(.subheadline.weight(.semibold))
                                .padding(.horizontal, 10)
                                .padding(.vertical, 6)
                                .background(Color.blue.opacity(0.15))
                                .clipShape(RoundedRectangle(cornerRadius: 8))
                        }
                        .padding()
                        .background(Color(.secondarySystemBackground))
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                    }
                    .buttonStyle(.plain)
                }

                Button("刷新学生列表") {
                    Task { await loadStudents() }
                }
                .buttonStyle(.bordered)
            }
        }
        .padding()
        .task {
            await loadStudents()
        }
    }

    private func loadStudents() async {
        isLoading = true
        errorMessage = nil

        do {
            let fetched = try await APIClient.shared.fetchStudents()
            students = fetched.isEmpty ? defaultStudents() : fetched
        } catch {
            students = defaultStudents()
            errorMessage = "后端暂不可用，已切换到本地学生档案。"
        }

        isLoading = false
    }

    private func defaultStudents() -> [Student] {
        [
            Student(id: "jon_zhao", name: "Jon", yearLevel: 4, avatar: "lion", targetDailyQuestions: 10),
            Student(id: "astrid_zhao", name: "Astrid", yearLevel: 3, avatar: "unicorn", targetDailyQuestions: 10)
        ]
    }
}

#Preview {
    StudentPickerView { _ in }
}
