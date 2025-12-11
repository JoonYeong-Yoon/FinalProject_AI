import Foundation
import HealthKit

class HealthKitManager {
    let healthStore = HKHealthStore()

    // MARK: - 전체 HealthKit 타입 목록
    var allReadTypes: Set<HKObjectType> = [

        // ===== 활동 =====
        HKObjectType.quantityType(forIdentifier: .stepCount)!,
        HKObjectType.quantityType(forIdentifier: .distanceWalkingRunning)!,
        HKObjectType.quantityType(forIdentifier: .flightsClimbed)!,

        // ===== 운동 =====
        HKObjectType.quantityType(forIdentifier: .activeEnergyBurned)!,
        HKObjectType.quantityType(forIdentifier: .appleExerciseTime)!,

        // ===== 심박 =====
        HKObjectType.quantityType(forIdentifier: .heartRate)!,
        HKObjectType.quantityType(forIdentifier: .restingHeartRate)!,
        HKObjectType.quantityType(forIdentifier: .walkingHeartRateAverage)!,
        HKObjectType.quantityType(forIdentifier: .heartRateVariabilitySDNN)!,

        // ===== 수면 =====
        HKObjectType.categoryType(forIdentifier: .sleepAnalysis)!,

        // ===== 신체 측정 =====
        HKObjectType.quantityType(forIdentifier: .bodyMass)!,
        HKObjectType.quantityType(forIdentifier: .height)!,
        HKObjectType.quantityType(forIdentifier: .bodyMassIndex)!,
        HKObjectType.quantityType(forIdentifier: .bodyFatPercentage)!,
        HKObjectType.quantityType(forIdentifier: .leanBodyMass)!,

        // ===== 바이탈 =====
        HKObjectType.quantityType(forIdentifier: .bloodPressureSystolic)!,
        HKObjectType.quantityType(forIdentifier: .bloodPressureDiastolic)!,
        HKObjectType.quantityType(forIdentifier: .bloodGlucose)!,
        HKObjectType.quantityType(forIdentifier: .oxygenSaturation)!,

        // ===== 영양 =====
        HKObjectType.quantityType(forIdentifier: .dietaryEnergyConsumed)!,
        HKObjectType.quantityType(forIdentifier: .dietaryWater)!,

        // ===== 생리주기 =====
        HKObjectType.categoryType(forIdentifier: .menstrualFlow)!,
        HKObjectType.categoryType(forIdentifier: .ovulationTestResult)!,
        HKObjectType.categoryType(forIdentifier: .sexualActivity)!,
        HKObjectType.categoryType(forIdentifier: .pregnancy)!,
        HKObjectType.categoryType(forIdentifier: .pregnancyTestResult)!,
        HKObjectType.categoryType(forIdentifier: .lactation)!
    ]

    // MARK: - 권한 요청
    func requestAuthorization(completion: @escaping (Bool) -> Void) {
        healthStore.requestAuthorization(toShare: [], read: allReadTypes) { success, _ in
            completion(success)
        }
    }

    // MARK: - 걸음수
    func fetchSteps(completion: @escaping (Double) -> Void) {
        fetchTodaySum(type: .stepCount, unit: HKUnit.count(), completion: completion)
    }

    func fetchDistance(completion: @escaping (Double) -> Void) {
        fetchTodaySum(type: .distanceWalkingRunning, unit: HKUnit.meter(), completion: completion)
    }

    func fetchFlightsClimbed(completion: @escaping (Double) -> Void) {
        fetchTodaySum(type: .flightsClimbed, unit: HKUnit.count(), completion: completion)
    }

    // MARK: - 운동
    func fetchActiveEnergy(completion: @escaping (Double) -> Void) {
        fetchTodaySum(type: .activeEnergyBurned, unit: HKUnit.kilocalorie(), completion: completion)
    }

    func fetchExerciseTime(completion: @escaping (Double) -> Void) {
        fetchTodaySum(type: .appleExerciseTime, unit: HKUnit.minute(), completion: completion)
    }

    // MARK: - 심박
    func fetchHeartRate(completion: @escaping (Double) -> Void) {
        fetchLatest(type: .heartRate, unit: HKUnit(from: "count/min"), completion: completion)
    }

    func fetchRestingHeartRate(completion: @escaping (Double) -> Void) {
        fetchLatest(type: .restingHeartRate, unit: HKUnit.count().unitDivided(by: HKUnit.minute()), completion: completion)
    }

    func fetchWalkingHeartRateAvg(completion: @escaping (Double) -> Void) {
        fetchLatest(type: .walkingHeartRateAverage, unit: HKUnit(from: "count/min"), completion: completion)
    }

    func fetchHRV(completion: @escaping (Double) -> Void) {
        fetchLatest(type: .heartRateVariabilitySDNN, unit: HKUnit.secondUnit(with: .milli), completion: completion)
    }

    // MARK: - 수면
    func fetchSleep(completion: @escaping (Double) -> Void) {
        guard let type = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) else { return }

        let start = Calendar.current.startOfDay(for: Date())
        let predicate = HKQuery.predicateForSamples(withStart: start, end: Date(), options: [])

        let query = HKSampleQuery(sampleType: type, predicate: predicate, limit: 0, sortDescriptors: nil) { _, samples, _ in
            guard let samples = samples as? [HKCategorySample] else {
                completion(0)
                return
            }

            let asleepSamples = samples.filter { $0.value == HKCategoryValueSleepAnalysis.asleep.rawValue }

            let total = asleepSamples.reduce(0) {
                $0 + $1.endDate.timeIntervalSince($1.startDate)
            }

            completion(total)
        }

        healthStore.execute(query)
    }

    // MARK: - 신체 측정

    func fetchWeight(completion: @escaping (Double) -> Void) {
        fetchLatest(type: .bodyMass, unit: HKUnit.gramUnit(with: .kilo), completion: completion)
    }

    func fetchHeight(completion: @escaping (Double) -> Void) {
        fetchLatest(type: .height, unit: HKUnit.meter(), completion: completion)
    }

    func fetchBMI(completion: @escaping (Double) -> Void) {
        fetchLatest(type: .bodyMassIndex, unit: HKUnit.count(), completion: completion)
    }

    func fetchBodyFat(completion: @escaping (Double) -> Void) {
        fetchLatest(type: .bodyFatPercentage, unit: HKUnit.percent(), completion: completion)
    }

    func fetchLeanBodyMass(completion: @escaping (Double) -> Void) {
        fetchLatest(type: .leanBodyMass, unit: HKUnit.gramUnit(with: .kilo), completion: completion)
    }

    // MARK: - 바이탈

    func fetchBloodPressure(completion: @escaping (Double, Double) -> Void) {
        let systolicType = HKQuantityType.quantityType(forIdentifier: .bloodPressureSystolic)!
        let diastolicType = HKQuantityType.quantityType(forIdentifier: .bloodPressureDiastolic)!

        fetchLatest(typeObj: systolicType, unit: HKUnit.millimeterOfMercury()) { sys in
            self.fetchLatest(typeObj: diastolicType, unit: HKUnit.millimeterOfMercury()) { dia in
                completion(sys, dia)
            }
        }
    }

    func fetchBloodGlucose(completion: @escaping (Double) -> Void) {
        fetchLatest(type: .bloodGlucose, unit: HKUnit(from: "mg/dL"), completion: completion)
    }

    func fetchOxygen(completion: @escaping (Double) -> Void) {
        fetchLatest(type: .oxygenSaturation, unit: HKUnit.percent(), completion: completion)
    }

    // MARK: - 영양
    func fetchDietaryCalories(completion: @escaping (Double) -> Void) {
        fetchTodaySum(type: .dietaryEnergyConsumed, unit: HKUnit.kilocalorie(), completion: completion)
    }

    func fetchDietaryWater(completion: @escaping (Double) -> Void) {
        fetchTodaySum(type: .dietaryWater, unit: HKUnit.liter(), completion: completion)
    }

    // MARK: - 생리주기
    func fetchMenstrualFlow(completion: @escaping (String) -> Void) {
        fetchCategoryLatest(identifier: .menstrualFlow, completion: completion)
    }

    func fetchOvulationTest(completion: @escaping (String) -> Void) {
        fetchCategoryLatest(identifier: .ovulationTestResult, completion: completion)
    }

    func fetchSexualActivity(completion: @escaping (String) -> Void) {
        fetchCategoryLatest(identifier: .sexualActivity, completion: completion)
    }

    func fetchPregnancy(completion: @escaping (String) -> Void) {
        fetchCategoryLatest(identifier: .pregnancy, completion: completion)
    }

    func fetchPregnancyTest(completion: @escaping (String) -> Void) {
        fetchCategoryLatest(identifier: .pregnancyTestResult, completion: completion)
    }

    func fetchLactation(completion: @escaping (String) -> Void) {
        fetchCategoryLatest(identifier: .lactation, completion: completion)
    }

    // ================================
    // MARK: - 공통 메서드 (중복 제거)
    // ================================

    // 1) 오늘 합계
    private func fetchTodaySum(type: HKQuantityTypeIdentifier,
                               unit: HKUnit,
                               completion: @escaping (Double) -> Void) {

        guard let sampleType = HKObjectType.quantityType(forIdentifier: type) else { return }

        let start = Calendar.current.startOfDay(for: Date())
        let predicate = HKQuery.predicateForSamples(withStart: start, end: Date(), options: [])

        let query = HKStatisticsQuery(quantityType: sampleType, quantitySamplePredicate: predicate, options: .cumulativeSum) { _, result, _ in
            let total = result?.sumQuantity()?.doubleValue(for: unit) ?? 0
            completion(total)
        }

        healthStore.execute(query)
    }

    // 2) 최신값 1개
    private func fetchLatest(type: HKQuantityTypeIdentifier,
                             unit: HKUnit,
                             completion: @escaping (Double) -> Void) {

        guard let sampleType = HKObjectType.quantityType(forIdentifier: type) else { return }

        fetchLatest(typeObj: sampleType, unit: unit, completion: completion)
    }

    private func fetchLatest(typeObj: HKQuantityType,
                             unit: HKUnit,
                             completion: @escaping (Double) -> Void) {

        let predicate = HKQuery.predicateForSamples(withStart: .distantPast, end: Date(), options: [])

        let query = HKSampleQuery(sampleType: typeObj, predicate: predicate, limit: 1, sortDescriptors: [
            NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: false)
        ]) { _, samples, _ in

            guard let sample = samples?.first as? HKQuantitySample else {
                completion(0)
                return
            }

            completion(sample.quantity.doubleValue(for: unit))
        }

        healthStore.execute(query)
    }

    // 3) 카테고리 타입 최신값
    private func fetchCategoryLatest(identifier: HKCategoryTypeIdentifier,
                                     completion: @escaping (String) -> Void) {

        guard let type = HKObjectType.categoryType(forIdentifier: identifier) else {
            completion("-")
            return
        }

        let predicate = HKQuery.predicateForSamples(withStart: nil, end: Date(), options: [])

        let query = HKSampleQuery(sampleType: type, predicate: predicate, limit: 1, sortDescriptors: [
            NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: false)
        ]) { _, samples, _ in

            guard let sample = samples?.first as? HKCategorySample else {
                completion("-")
                return
            }

            completion("\(sample.value)")
        }

        healthStore.execute(query)
    }
}

