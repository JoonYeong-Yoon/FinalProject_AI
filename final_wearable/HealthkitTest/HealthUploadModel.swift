import Foundation

struct HealthUploadModel: Codable {

    // ⭐ 업로드할 때 포함되는 사용자 이메일
    let email: String

    // 활동
    let steps: Double
    let distance: Double
    let flights: Double

    // 운동
    let activeEnergy: Double
    let exerciseTime: Double

    // 심박
    let heartRate: Double
    let restingHeartRate: Double
    let walkingHeartRate: Double
    let hrv: Double

    // 수면
    let sleepHours: Double

    // 신체 계측
    let weight: Double
    let height: Double
    let bmi: Double
    let bodyFat: Double
    let leanBody: Double

    // 바이탈
    let systolic: Double
    let diastolic: Double
    let glucose: Double
    let oxygen: Double

    // 영양
    let calories: Double   // ⭐ 물(water) 삭제로 영양은 1개만 남음
}

