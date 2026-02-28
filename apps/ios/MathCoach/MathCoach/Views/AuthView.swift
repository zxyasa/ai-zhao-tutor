import SwiftUI
import LocalAuthentication

struct AuthView: View {
    enum AccountType: String, CaseIterable {
        case parent = "家长"
        case student = "学生"
    }

    enum Mode: String, CaseIterable {
        case login = "登录"
        case register = "注册"
    }

    @State private var accountType: AccountType = .parent
    @State private var mode: Mode = .login
    @State private var email: String = ""
    @State private var password: String = ""
    @State private var displayName: String = ""
    @State private var studentId: String = ""
    @State private var studentPin: String = ""
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var infoMessage: String?
    @State private var biometricContext: LAContext?
    @State private var hasAutoPromptedBiometrics = false

    @AppStorage("last_auth_account_type") private var lastAuthAccountType: String = ""
    @AppStorage("last_parent_email") private var lastParentEmail: String = ""
    @AppStorage("last_student_id") private var lastStudentId: String = ""

    let onSuccess: (AuthTokenResponse) -> Void

    var body: some View {
        VStack(spacing: 14) {
            Text("账号登录")
                .font(.title2.bold())

            Picker("账号类型", selection: $accountType) {
                ForEach(AccountType.allCases, id: \.self) { type in
                    Text(type.rawValue).tag(type)
                }
            }
            .pickerStyle(.segmented)

            if accountType == .parent {
                Picker("模式", selection: $mode) {
                    ForEach(Mode.allCases, id: \.self) { mode in
                        Text(mode.rawValue).tag(mode)
                    }
                }
                .pickerStyle(.segmented)
            }

            if accountType == .parent {
                VStack(spacing: 10) {
                    TextField("邮箱", text: $email)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .keyboardType(.emailAddress)
                        .textFieldStyle(.roundedBorder)

                    SecureField("密码（至少8位）", text: $password)
                        .textFieldStyle(.roundedBorder)

                    if mode == .register {
                        TextField("显示名称（可选）", text: $displayName)
                            .textFieldStyle(.roundedBorder)
                    }
                }
            } else {
                VStack(spacing: 10) {
                    TextField("学生ID", text: $studentId)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .textFieldStyle(.roundedBorder)
                    SecureField("PIN", text: $studentPin)
                        .textFieldStyle(.roundedBorder)
                }
            }

            if let errorMessage {
                Text(errorMessage)
                    .font(.caption)
                    .foregroundColor(.red)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }

            if let infoMessage {
                Text(infoMessage)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }

            Button {
                Task { await submit() }
            } label: {
                HStack {
                    if isLoading {
                        ProgressView()
                    }
                    Text(buttonTitle)
                }
                .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .disabled(!canSubmit)
        }
        .padding()
        .onAppear {
            if let restoredType = AccountType(rawValue: lastAuthAccountType) {
                accountType = restoredType
            }
            autoPromptBiometricsIfNeeded()
        }
    }

    private var canSubmit: Bool {
        if isLoading { return false }
        switch accountType {
        case .parent:
            return !email.isEmpty && password.count >= 8
        case .student:
            return !studentId.isEmpty && studentPin.count >= 4
        }
    }

    private var buttonTitle: String {
        switch accountType {
        case .parent:
            return mode == .login ? "家长登录" : "家长注册并登录"
        case .student:
            return "学生 PIN 登录"
        }
    }

    private var hasSavedBasicProfile: Bool {
        !lastParentEmail.isEmpty || !lastStudentId.isEmpty
    }

    private func submit() async {
        isLoading = true
        errorMessage = nil
        infoMessage = nil
        defer { isLoading = false }

        do {
            let token: AuthTokenResponse
            if accountType == .student {
                token = try await APIClient.shared.loginStudent(studentId: studentId, pin: studentPin)
            } else {
                if mode == .login {
                    token = try await APIClient.shared.loginParent(email: email, password: password)
                } else {
                    token = try await APIClient.shared.registerParent(
                        email: email,
                        password: password,
                        displayName: displayName.isEmpty ? nil : displayName
                    )
                }
            }
            saveBasicProfile()
            onSuccess(token)
        } catch {
            errorMessage = friendlyAuthErrorMessage(error)
        }
    }

    private func restoreSavedProfileWithBiometrics() {
        let context = LAContext()
        context.localizedCancelTitle = "取消"
        infoMessage = nil
        errorMessage = nil
        var authError: NSError?
        let policy: LAPolicy = .deviceOwnerAuthentication
        guard context.canEvaluatePolicy(policy, error: &authError) else {
            errorMessage = "此设备未启用生物识别或设备密码"
            return
        }

        // Keep context alive until callback to avoid silent no-op on some devices.
        biometricContext = context
        context.evaluatePolicy(
            policy,
            localizedReason: "验证后填充上次登录账号"
        ) { success, evaluateError in
            DispatchQueue.main.async {
                self.biometricContext = nil
                if success {
                    if let restoredType = AccountType(rawValue: self.lastAuthAccountType) {
                        self.accountType = restoredType
                    }
                    if self.accountType == .parent {
                        self.email = self.lastParentEmail
                    } else {
                        self.studentId = self.lastStudentId
                    }
                    self.errorMessage = nil
                    self.infoMessage = "已填充上次账号，请输入密码/PIN 登录"
                } else {
                    if let laError = evaluateError as? LAError,
                       laError.code == .userCancel || laError.code == .systemCancel {
                        self.infoMessage = "已取消验证"
                    } else {
                        self.errorMessage = "身份验证失败，请重试"
                    }
                }
            }
        }
    }

    private func autoPromptBiometricsIfNeeded() {
        guard hasSavedBasicProfile else { return }
        guard !hasAutoPromptedBiometrics else { return }
        guard email.isEmpty, studentId.isEmpty else { return }
        hasAutoPromptedBiometrics = true
        restoreSavedProfileWithBiometrics()
    }

    private func saveBasicProfile() {
        lastAuthAccountType = accountType.rawValue
        if accountType == .parent {
            lastParentEmail = email
        } else {
            lastStudentId = studentId
        }
    }

    private func friendlyAuthErrorMessage(_ error: Error) -> String {
        let lowercased = error.localizedDescription.lowercased()

        if lowercased.contains("invalid credentials") {
            return "Incorrect email or password. Please try again."
        }
        if lowercased.contains("invalid student pin") {
            return "Incorrect student ID or PIN. Please try again."
        }
        if lowercased.contains("student not found") {
            return "Student account not found. Please check the student ID."
        }
        if lowercased.contains("email already registered") {
            return "This email is already registered. Please sign in."
        }
        if lowercased.contains("inactive") {
            return "This account is unavailable. Please contact support."
        }
        if lowercased.contains("network error") || lowercased.contains("cannot find host") {
            return "Network error. Make sure your iPad and backend are on the same network."
        }
        if lowercased.contains("timed out") {
            return "Request timed out. Please try again."
        }
        if lowercased.contains("http 5") {
            return "Service is temporarily unavailable. Please try again later."
        }
        return "Sign-in failed. Please try again."
    }
}

#Preview {
    AuthView(onSuccess: { _ in })
}
