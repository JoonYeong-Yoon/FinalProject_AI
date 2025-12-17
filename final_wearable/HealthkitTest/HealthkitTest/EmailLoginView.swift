import SwiftUI

struct EmailLoginView: View {

    @Binding var isLoggedIn: Bool
    @State private var email: String = ""

    var body: some View {
        VStack(spacing: 30) {

            Spacer()

            // Title
            VStack(spacing: 6) {
                Text("Welcome 👋")
                    .font(.system(size: 36, weight: .bold))
                    .foregroundColor(.primary)

                Text("AI 트레이너를 시작하려면\n이메일을 입력해주세요")
                    .font(.system(size: 16))
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
            }

            // Input Form
            VStack(spacing: 15) {
                TextField("이메일 주소", text: $email)
                    .autocapitalization(.none)
                    .keyboardType(.emailAddress)
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(12)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color(.systemGray4), lineWidth: 1)
                    )
                    .padding(.horizontal, 30)

                Button(action: saveEmail) {
                    Text("로그인")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(email.isEmpty ? Color.gray : Color.blue)
                        .cornerRadius(12)
                        .padding(.horizontal, 30)
                }
                .disabled(email.isEmpty)
            }

            Spacer()
            Spacer()
        }
        .padding()
        .background(Color(.systemGroupedBackground).ignoresSafeArea())
    }

    func saveEmail() {
        guard !email.isEmpty else { return }
        UserDefaults.standard.set(email, forKey: "userEmail")
        isLoggedIn = true
    }
}

