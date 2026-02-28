//
//  ContentView.swift
//  MathCoach
//
//  Created by Michael Zhao on 13/2/2026.
//

import SwiftUI

struct ContentView: View {
    @State private var selectedStudent: Student?
    @State private var showParentDashboard = false
    @State private var hasAuthToken: Bool = APIClient.shared.hasAccessToken
    @AppStorage("auth_role") private var authRole: String = ""
    @AppStorage("selected_student_id") private var selectedStudentId: String = ""
    @AppStorage("selected_student_name") private var selectedStudentName: String = ""
    @AppStorage("selected_student_year") private var selectedStudentYear: Int = 0
    @AppStorage("selected_student_avatar") private var selectedStudentAvatar: String = "star"

    var body: some View {
        NavigationStack {
            if !hasAuthToken {
                AuthView { token in
                    hasAuthToken = APIClient.shared.hasAccessToken
                    authRole = token.role
                    if token.role == "student" {
                        Task { await selectStudentById(token.subject) }
                    }
                }
                .navigationTitle("AJ Math Tutor")
            } else {
                if let student = selectedStudent {
                    QuestionView(student: student)
                        .navigationTitle(student.name)
                        .toolbar {
                            if authRole != "student" {
                                ToolbarItem(placement: .topBarLeading) {
                                    Button("家长") {
                                        showParentDashboard = true
                                    }
                                }
                            }
                            ToolbarItem(placement: .topBarTrailing) {
                                Menu("更多") {
                                    if authRole != "student" {
                                        Button("切换学生") { clearSelection() }
                                    }
                                    Button("退出登录", role: .destructive) { logout() }
                                }
                            }
                        }
                } else {
                    StudentPickerView { student in
                        select(student)
                    }
                    .toolbar {
                        ToolbarItem(placement: .topBarTrailing) {
                            Menu("更多") {
                                if authRole != "student" {
                                    Button("家长面板") { showParentDashboard = true }
                                }
                                Button("退出登录", role: .destructive) { logout() }
                            }
                        }
                    }
                }
            }
        }
        .onAppear {
            hasAuthToken = APIClient.shared.hasAccessToken
            restoreSelection()
        }
        .onReceive(NotificationCenter.default.publisher(for: .apiClientUnauthorized)) { _ in
            logout()
        }
        .sheet(isPresented: $showParentDashboard) {
            ParentDashboardView()
        }
    }

    private func restoreSelection() {
        guard selectedStudent == nil, !selectedStudentId.isEmpty else { return }
        selectedStudent = Student(
            id: selectedStudentId,
            name: selectedStudentName.isEmpty ? "Student" : selectedStudentName,
            yearLevel: selectedStudentYear == 0 ? 3 : selectedStudentYear,
            avatar: selectedStudentAvatar
        )
    }

    private func select(_ student: Student) {
        selectedStudent = student
        selectedStudentId = student.id
        selectedStudentName = student.name
        selectedStudentYear = student.yearLevel
        selectedStudentAvatar = student.avatar
    }

    private func clearSelection() {
        selectedStudent = nil
        selectedStudentId = ""
        selectedStudentName = ""
        selectedStudentYear = 0
        selectedStudentAvatar = "star"
    }

    private func logout() {
        // Avoid notification feedback loop: clear token locally without reposting unauthorized event.
        APIClient.shared.setAccessToken(nil)
        hasAuthToken = false
        authRole = ""
        clearSelection()
        showParentDashboard = false
    }

    private func selectStudentById(_ studentId: String) async {
        do {
            let students = try await APIClient.shared.fetchStudents()
            if let matched = students.first(where: { $0.id == studentId }) {
                select(matched)
                return
            }
        } catch {
            // Keep fallback below.
        }
        select(
            Student(
                id: studentId,
                name: studentId,
                yearLevel: 3,
                avatar: "star"
            )
        )
    }
}

#Preview {
    ContentView()
}
