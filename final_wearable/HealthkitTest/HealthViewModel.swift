import Foundation
import HealthKit
import Combine

class HealthViewModel: ObservableObject {

    private let manager = HealthKitManager()

    // MARK: - 활동
    @Published var steps = 0.0
    @Published var distance = 0.0
    @Published var flights = 0.0

    // MARK: - 운동
    @Published var activeEnergy = 0.0
    @Published var exerciseTime = 0.0

    // MARK: - 심박/HRV
    @Published var heartRate = 0.0
    @Published var restingHeartRate = 0.0
    @Published var walkingHeartRate = 0.0
    @Published var hrv = 0.0

    // MARK: - 수면
    @Published var sleepHours = 0.0

    // MARK: - 신체 계측
    @Published var weight = 0.0
    @Published var height = 0.0
    @Published var bmi = 0.0
    @Published var bodyFat = 0.0
    @Published var leanBody = 0.0

    // MARK: - 바이탈
    @Published var systolic = 0.0
    @Published var diastolic = 0.0
    @Published var glucose = 0.0
    @Published var oxygen = 0.0

    // MARK: - 영양
    @Published var calories = 0.0   // water 제거됨


    // ===============================================================
    // MARK: - 전체 데이터 로드
    // ===============================================================
    func loadAllData() {

        manager.fetchSteps { value in
            DispatchQueue.main.async { self.steps = value }
        }

        manager.fetchDistance { value in
            DispatchQueue.main.async { self.distance = value }
        }

        manager.fetchFlightsClimbed { value in
            DispatchQueue.main.async { self.flights = value }
        }

        manager.fetchActiveEnergy { value in
            DispatchQueue.main.async { self.activeEnergy = value }
        }

        manager.fetchExerciseTime { value in
            DispatchQueue.main.async { self.exerciseTime = value }
        }

        manager.fetchHeartRate { value in
            DispatchQueue.main.async { self.heartRate = value }
        }

        manager.fetchRestingHeartRate { value in
            DispatchQueue.main.async { self.restingHeartRate = value }
        }

        manager.fetchWalkingHeartRateAvg { value in
            DispatchQueue.main.async { self.walkingHeartRate = value }
        }

        manager.fetchHRV { value in
            DispatchQueue.main.async { self.hrv = value }
        }

        manager.fetchSleep { value in
            DispatchQueue.main.async { self.sleepHours = value }
        }

        manager.fetchWeight { value in
            DispatchQueue.main.async { self.weight = value }
        }

        manager.fetchHeight { value in
            DispatchQueue.main.async { self.height = value }
        }

        manager.fetchBMI { value in
            DispatchQueue.main.async { self.bmi = value }
        }

        manager.fetchBodyFat { value in
            DispatchQueue.main.async { self.bodyFat = value }
        }

        manager.fetchLeanBodyMass { value in
            DispatchQueue.main.async { self.leanBody = value }
        }

        manager.fetchBloodPressure { sys, dia in
            DispatchQueue.main.async {
                self.systolic = sys
                self.diastolic = dia
            }
        }

        manager.fetchBloodGlucose { value in
            DispatchQueue.main.async { self.glucose = value }
        }

        manager.fetchOxygen { value in
            DispatchQueue.main.async { self.oxygen = value }
        }

        manager.fetchDietaryCalories { value in
            DispatchQueue.main.async { self.calories = value }
        }

        // 🔥 water 완전 제거됨
    }
}

extension HealthViewModel {
    func asUploadModel() -> HealthUploadModel {

        let email = UserDefaults.standard.string(forKey: "userEmail") ?? ""

        return HealthUploadModel(
            email: email,
            steps: steps,
            distance: distance,
            flights: flights,
            activeEnergy: activeEnergy,
            exerciseTime: exerciseTime,
            heartRate: heartRate,
            restingHeartRate: restingHeartRate,
            walkingHeartRate: walkingHeartRate,
            hrv: hrv,
            sleepHours: sleepHours,
            weight: weight,
            height: height,
            bmi: bmi,
            bodyFat: bodyFat,
            leanBody: leanBody,
            systolic: systolic,
            diastolic: diastolic,
            glucose: glucose,
            oxygen: oxygen,
            calories: calories
        )
    }
}
