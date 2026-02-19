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
    @AppStorage("selected_student_id") private var selectedStudentId: String = ""
    @AppStorage("selected_student_name") private var selectedStudentName: String = ""
    @AppStorage("selected_student_year") private var selectedStudentYear: Int = 0
    @AppStorage("selected_student_avatar") private var selectedStudentAvatar: String = "star"

    var body: some View {
        NavigationStack {
            if let student = selectedStudent {
                QuestionView(student: student)
                    .navigationTitle(student.name)
                    .toolbar {
                        ToolbarItem(placement: .topBarLeading) {
                            Button("家长") {
                                showParentDashboard = true
                            }
                        }
                        ToolbarItem(placement: .topBarTrailing) {
                            Button("切换") {
                                clearSelection()
                            }
                        }
                    }
            } else {
                StudentPickerView { student in
                    select(student)
                }
                .toolbar {
                    ToolbarItem(placement: .topBarTrailing) {
                        Button("家长") {
                            showParentDashboard = true
                        }
                    }
                }
            }
        }
        .onAppear {
            restoreSelection()
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
}

#Preview {
    ContentView()
}
