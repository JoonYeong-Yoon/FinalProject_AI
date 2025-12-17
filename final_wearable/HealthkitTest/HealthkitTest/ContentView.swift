import SwiftUI
import Combine

struct ContentView: View {

    @StateObject var viewModel = HealthViewModel()
    @State private var showEmailSheet = false

    let uploader = HealthUploader()

    var body: some View {
        VStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {

                    Text("📊 오늘의 건강 데이터")
                        .font(.title)
                        .bold()
                        .padding(.bottom, 10)

                    // 활동
                    Group {
                        Text("걸음 수: \(Int(viewModel.steps))")
                        Text("이동 거리: \(String(format: "%.2f", viewModel.distance)) m")
                        Text("오르내린 층수: \(Int(viewModel.flights))")
                    }.sectionBox(title: "활동")

                    // 운동
                    Group {
                        Text("활동 에너지: \(String(format: "%.1f", viewModel.activeEnergy)) kcal")
                        Text("운동 시간: \(String(format: "%.0f", viewModel.exerciseTime)) 분")
                    }.sectionBox(title: "운동")

                    // 심박
                    Group {
                        Text("현재 심박수: \(String(format: "%.0f", viewModel.heartRate)) BPM")
                        Text("안정시 심박수: \(String(format: "%.0f", viewModel.restingHeartRate)) BPM")
                        Text("걷기 평균 심박수: \(String(format: "%.0f", viewModel.walkingHeartRate)) BPM")
                        Text("HRV: \(String(format: "%.1f", viewModel.hrv)) ms")
                    }.sectionBox(title: "심박")

                    // 수면
                    Group {
                        Text("수면 시간: \(String(format: "%.1f", viewModel.sleepHours / 3600.0)) 시간")
                    }.sectionBox(title: "수면")

                    // 신체 계측
                    Group {
                        Text("체중: \(String(format: "%.1f", viewModel.weight)) kg")
                        Text("키: \(String(format: "%.2f", viewModel.height)) m")
                        Text("BMI: \(String(format: "%.1f", viewModel.bmi))")
                        Text("체지방률: \(String(format: "%.1f", viewModel.bodyFat)) %")
                        Text("제지방량: \(String(format: "%.1f", viewModel.leanBody)) kg")
                    }.sectionBox(title: "신체 계측")

                    // 바이탈
                    Group {
                        Text("혈압: \(Int(viewModel.systolic)) / \(Int(viewModel.diastolic)) mmHg")
                        Text("혈당: \(String(format: "%.1f", viewModel.glucose)) mg/dL")
                        Text("산소포화도: \(String(format: "%.1f", viewModel.oxygen)) %")
                    }.sectionBox(title: "바이탈")

                    // 영양
                    Group {
                        Text("섭취 칼로리: \(String(format: "%.0f", viewModel.calories)) kcal")
                    }.sectionBox(title: "영양")
                }
                .padding()
            }

            // 하단 버튼들
            HStack(spacing: 10) {

                Button(action: { viewModel.loadAllData() }) {
                    bottomButtonStyle("Refresh\nData")
                }

                Button(action: uploadToServer) {
                    bottomButtonStyle("Upload to\nServer")
                }

                Button(action: exportData) {
                    bottomButtonStyle("Export\nData")
                }

                Button(action: openHealthSettings) {
                    bottomButtonStyle("Revoke\nAccess")
                }

                Button(action: { showEmailSheet = true }) {
                    bottomButtonStyle("Change\nEmail")
                }
            }
            .padding(.horizontal)
            .padding(.bottom, 10)
        }

        .sheet(isPresented: $showEmailSheet) {
            ChangeEmailView()
        }
    }

    // MARK: - 서버 업로드 기능
    func uploadToServer() {

        let email = UserDefaults.standard.string(forKey: "userEmail") ?? ""

        // ✅ 오늘 날짜 생성 (YYYY-MM-DD 형식)
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        formatter.timeZone = TimeZone.current
        let todayDate = formatter.string(from: Date())

        let data = HealthUploadModel(
            email: email,
            date: todayDate,       // ✅ 추가: 오늘 날짜
            difficulty: "중",
            duration: 30,
            steps: viewModel.steps,
            distance: viewModel.distance,
            flights: viewModel.flights,
            activeEnergy: viewModel.activeEnergy,
            exerciseTime: viewModel.exerciseTime,
            heartRate: viewModel.heartRate,
            restingHeartRate: viewModel.restingHeartRate,
            walkingHeartRate: viewModel.walkingHeartRate,
            hrv: viewModel.hrv,
            sleepHours: viewModel.sleepHours,
            weight: viewModel.weight,
            height: viewModel.height,
            bmi: viewModel.bmi,
            bodyFat: viewModel.bodyFat,
            leanBody: viewModel.leanBody,
            systolic: viewModel.systolic,
            diastolic: viewModel.diastolic,
            glucose: viewModel.glucose,
            oxygen: viewModel.oxygen,
            calories: viewModel.calories
        )

        uploader.upload(data) { success in
            print(success ? "🔥 업로드 성공!" : "❌ 업로드 실패")
        }
    }

    func exportData() {

        let encoder = JSONEncoder()
        encoder.outputFormatting = .prettyPrinted

        guard let jsonData = try? encoder.encode(viewModel.asUploadModel()) else {
            print("❌ JSON 인코딩 실패")
            return
        }

        let fileName = "health_data_\(Int(Date().timeIntervalSince1970)).json"
        let url = FileManager.default
            .urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent(fileName)

        do {
            try jsonData.write(to: url)
            print("📁 저장 완료:", url)
        } catch {
            print("❌ 저장 실패:", error.localizedDescription)
        }
    }

    func openHealthSettings() {
        guard let url = URL(string: UIApplication.openSettingsURLString) else { return }
        UIApplication.shared.open(url)
    }

    func bottomButtonStyle(_ text: String) -> some View {
        Text(text)
            .font(.footnote)
            .multilineTextAlignment(.center)
            .foregroundColor(.white)
            .padding(.vertical, 12)
            .frame(maxWidth: .infinity)
            .background(Color.blue)
            .cornerRadius(12)
    }
}

// MARK: - Section Box
extension View {
    func sectionBox(title: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("📌 " + title)
                .font(.headline)
                .padding(.bottom, 3)

            self.padding()
                .background(Color(.secondarySystemBackground))
                .cornerRadius(12)
        }
    }
}
