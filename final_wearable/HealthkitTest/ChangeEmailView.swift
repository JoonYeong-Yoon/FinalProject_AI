import SwiftUI

struct ChangeEmailView: View {

    @Environment(\.dismiss) var dismiss
    @State private var email: String = UserDefaults.standard.string(forKey: "userEmail") ?? ""
    @State private var errorMessage: String = ""

    var body: some View {
        NavigationView {
            VStack(spacing: 20) {

                Text("이메일을 입력하세요")
                    .font(.title2)
                    .bold()

                TextField("example@email.com", text: $email)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding(.horizontal)

                if !errorMessage.isEmpty {
                    Text(errorMessage)
                        .foregroundColor(.red)
                        .font(.footnote)
                }

                Button(action: saveEmail) {
                    Text("저장하기")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.blue)
                        .cornerRadius(10)
                }
                .padding(.horizontal)

                Spacer()
            }
            .padding()
            .navigationTitle("이메일 설정")
            .navigationBarItems(trailing: Button("닫기") {
                dismiss()
            })
        }
    }

    func saveEmail() {
        let trimmed = email.trimmingCharacters(in: .whitespacesAndNewlines)

        // 간단 이메일 형식 체크
        if !trimmed.contains("@") || !trimmed.contains(".") {
            errorMessage = "올바른 이메일 형식이 아닙니다."
            return
        }

        UserDefaults.standard.set(trimmed, forKey: "userEmail")
        print("📩 이메일 저장됨:", trimmed)
        dismiss()
    }
}

