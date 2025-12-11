import Foundation

class HealthUploader {

    let serverURL = URL(string: "http://192.168.0.27:8000/ios/upload")!   // ⭐ 하늘의 PC 주소

    func upload(_ data: HealthUploadModel, completion: @escaping (Bool) -> Void) {

        guard let jsonData = try? JSONEncoder().encode(data) else {
            print("❌ JSON 인코딩 실패")
            completion(false)
            return
        }

        var request = URLRequest(url: serverURL)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData

        URLSession.shared.dataTask(with: request) { _, response, error in

            if let error = error {
                print("❌ 업로드 실패:", error.localizedDescription)
                completion(false)
                return
            }

            if let http = response as? HTTPURLResponse {
                print("📡 서버 응답 코드:", http.statusCode)
                completion(http.statusCode == 200)
                return
            }

            completion(false)
        }.resume()
    }
}

