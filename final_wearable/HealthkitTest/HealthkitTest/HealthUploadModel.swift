import Foundation

// ✅ 백엔드 형식에 완벽히 맞춘 구조
struct HealthUploadModel: Codable {
    
    // 메타 정보
    let user_id: String
    let date: String          // ✅ 추가: YYYY-MM-DD 형식 (예: "2025-12-17")
    let difficulty: String
    let duration: Int
    let raw_json: HealthData
    
    // ✅ 백엔드 필드명에 맞춘 건강 데이터
    struct HealthData: Codable {
        // 수면
        let sleep_min: Double      // ✅ 분 단위
        let sleep_hr: Double       // ✅ 시간 단위
        
        // 신체 계측
        let weight: Double         // kg
        let height_m: Double       // ✅ 미터 단위
        let bmi: Double
        let body_fat: Double       // ✅ 백엔드 필드명
        let lean_body: Double      // ✅ 백엔드 필드명
        
        // 활동
        let distance_km: Double    // ✅ 킬로미터 단위
        let steps: Double
        let steps_cadence: Double  // ✅ 백엔드 필드명
        
        // 운동
        let exercise_min: Double   // ✅ 분 단위
        let flights: Double
        
        // 칼로리
        let active_calories: Double     // ✅ 백엔드 필드명
        let total_calories: Double      // ✅ 백엔드 필드명
        let calories_intake: Double     // ✅ 백엔드 필드명
        
        // 심박
        let heart_rate: Double
        let resting_heart_rate: Double
        let walking_heart_rate: Double
        let hrv: Double
        
        // 바이탈
        let systolic: Double
        let diastolic: Double
        let glucose: Double
        let oxygen_saturation: Double   // ✅ 백엔드 필드명
    }
    
    // ✅ 편리한 생성자 (단위 변환 포함)
    init(email: String,
         date: String = "",           // ✅ 추가: 날짜 파라미터
         difficulty: String = "중",
         duration: Int = 30,
         steps: Double,
         distance: Double,            // 미터
         flights: Double,
         activeEnergy: Double,
         exerciseTime: Double,        // 분
         heartRate: Double,
         restingHeartRate: Double,
         walkingHeartRate: Double,
         hrv: Double,
         sleepHours: Double,          // 초
         weight: Double,
         height: Double,              // 미터
         bmi: Double,
         bodyFat: Double,
         leanBody: Double,
         systolic: Double,
         diastolic: Double,
         glucose: Double,
         oxygen: Double,
         calories: Double) {
        
        self.user_id = email
        
        // ✅ date가 비어있으면 오늘 날짜 사용
        if date.isEmpty {
            let formatter = DateFormatter()
            formatter.dateFormat = "yyyy-MM-dd"
            formatter.timeZone = TimeZone.current
            self.date = formatter.string(from: Date())
        } else {
            self.date = date
        }
        
        self.difficulty = difficulty
        self.duration = duration
        
        // ✅ 단위 변환 및 백엔드 필드명 매칭
        self.raw_json = HealthData(
            // 수면 (초 → 분, 시간)
            sleep_min: sleepHours / 60.0,
            sleep_hr: sleepHours / 3600.0,
            
            // 신체 계측
            weight: weight,
            height_m: height,  // 이미 미터 단위
            bmi: bmi,
            body_fat: bodyFat,
            lean_body: leanBody,
            
            // 활동 (미터 → 킬로미터)
            distance_km: distance / 1000.0,
            steps: steps,
            steps_cadence: 0,  // ✅ HealthKit에서 제공 안 하면 0
            
            // 운동
            exercise_min: exerciseTime,
            flights: flights,
            
            // 칼로리
            active_calories: activeEnergy,
            total_calories: activeEnergy,  // ✅ 애플은 total_calories 따로 없음
            calories_intake: calories,
            
            // 심박
            heart_rate: heartRate,
            resting_heart_rate: restingHeartRate,
            walking_heart_rate: walkingHeartRate,
            hrv: hrv,
            
            // 바이탈
            systolic: systolic,
            diastolic: diastolic,
            glucose: glucose,
            oxygen_saturation: oxygen
        )
    }
}
