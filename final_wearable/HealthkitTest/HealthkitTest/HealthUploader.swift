import Foundation

class HealthUploader {

    // ⭐ URL은 이미 올바름
    let serverURL = URL(string: "http://192.168.0.15:8000/api/auto/upload")!

    func upload(_ data: HealthUploadModel, completion: @escaping (Bool) -> Void) {

        // ⭐⭐⭐ 수정: 이제 data가 올바른 구조를 가짐
        guard let jsonData = try? JSONEncoder().encode(data) else {
            print("❌ JSON 인코딩 실패")
            completion(false)
            return
        }
        
        // ⭐⭐⭐ 추가: 전송 데이터 로깅
        if let jsonString = String(data: jsonData, encoding: .utf8) {
            print("📤 전송 데이터:")
            print(jsonString)
        }

        // 요청 설정
        var request = URLRequest(url: serverURL)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData

        // 업로드
        URLSession.shared.dataTask(with: request) { data, response, error in

            if let error = error {
                print("❌ 업로드 실패:", error.localizedDescription)
                completion(false)
                return
            }

            if let http = response as? HTTPURLResponse {
                print("📡 서버 응답 코드:", http.statusCode)

                if let data = data,
                   let body = String(data: data, encoding: .utf8) {
                    print("📨 서버 응답 내용:", body)
                }

                // 성공 여부 반환
                completion(http.statusCode == 200)
                return
            }

            print("❌ 알 수 없는 응답")
            completion(false)

        }.resume()
    }
}

