import math
from datetime import datetime, timezone
from app.utils.platform_detection import detect_platform


def normalize_raw(raw_json: dict) -> dict:
    """
    삼성 ZIP(raw_json)과 애플 API(raw_json)를 모두
    23개 정규화 스키마로 통합하는 함수.
    """

    # ---------------------------------------------------------
    # 0) 플랫폼 강제 보정 (가장 먼저 수행)
    # ---------------------------------------------------------
    # 삼성 ZIP은 totalCaloriesBurned 필드를 갖는다
    if "totalCaloriesBurned" in raw_json:
        platform = "samsung"
    else:
        platform = detect_platform(raw_json)

    # ---------------------------------------------------------
    # 1) Sleep 처리
    # 삼성 ZIP : sleep = 분 단위
    # 애플 API : sleepHours = 시간 단위
    # ---------------------------------------------------------
    # 1) Sleep 처리
    if platform == "samsung":
        # 삼성 ZIP은 sleep = 분 단위
        sleep_min = raw_json.get("sleep", 0)
        sleep_hr = sleep_min / 60

    elif "sleepHours" in raw_json:
        # 애플 API는 sleepHours = 시간 단위
        sleep_hr = raw_json.get("sleepHours", 0)
        sleep_min = sleep_hr * 60

    else:
        sleep_min = 0
        sleep_hr = 0

    # ---------------------------------------------------------
    # 2) Weight
    # 삼성 ZIP → db_parser에서 이미 kg로 변환됨
    # ---------------------------------------------------------
    weight = raw_json.get("weight", 0)

    # ---------------------------------------------------------
    # 3) Height 단위 통합
    # 삼성 ZIP : meter
    # 애플 : cm → m
    # ---------------------------------------------------------
    h = raw_json.get("height", 0)

    if platform == "apple":
        height_m = h / 100 if h else 0
    else:
        # meter 기반, 예외값 처리
        if 0.3 < h < 2.5:
            height_m = h
        elif 30 <= h <= 250:
            height_m = h / 100
        else:
            height_m = h

    # ---------------------------------------------------------
    # 4) BMI 계산
    # 애플: bmi 필드 제공 가능
    # 삼성: weight/height² 직접 계산
    # ---------------------------------------------------------
    if raw_json.get("bmi", 0) > 0:
        bmi = raw_json["bmi"]
    elif weight > 0 and height_m > 0:
        bmi = weight / (height_m**2)
    else:
        bmi = 0

    # ---------------------------------------------------------
    # 5) Distance 단위 통합 (항상 meter → km)
    # ---------------------------------------------------------
    if "distance" in raw_json:
        distance_km = raw_json["distance"] / 1000
    else:
        distance_km = 0

    # ---------------------------------------------------------
    # 6) Calories 처리
    # 삼성:
    #   calories = active_calories
    #   totalCaloriesBurned = total_cal
    #
    # 애플:
    #   activeEnergy = active_calories
    #   calories = calories_intake(섭취 칼로리)
    # ---------------------------------------------------------
    if platform == "samsung":
        active_cal = raw_json.get("calories", 0)
        total_cal = raw_json.get("totalCaloriesBurned", 0)
        calories_intake = 0
    else:
        active_cal = raw_json.get("activeEnergy", 0)
        total_cal = 0
        calories_intake = raw_json.get("calories", 0)

    # ---------------------------------------------------------
    # 7) oxygen 처리 (기본 fallback)
    # ---------------------------------------------------------
    oxygen_sat = raw_json.get("oxygenSaturation") or raw_json.get("oxygen") or 0

    # ---------------------------------------------------------
    # 최종 23개 스키마 완성
    # ---------------------------------------------------------
    return {
        "sleep_min": sleep_min,
        "sleep_hr": round(sleep_hr, 1),
        "weight": weight,
        "height_m": height_m,
        "bmi": bmi,
        "body_fat": raw_json.get("bodyFat", 0),
        "lean_body": raw_json.get("leanBody", 0),
        "distance_km": distance_km,
        "steps": raw_json.get("steps", 0),
        "steps_cadence": raw_json.get("stepsCadence", 0),
        "exercise_min": raw_json.get("exerciseTime", 0),
        "flights": raw_json.get("flights", 0),
        "active_calories": active_cal,
        "total_calories": total_cal,
        "calories_intake": calories_intake,
        "oxygen_saturation": oxygen_sat,
        "heart_rate": raw_json.get("heartRate", 0),
        "resting_heart_rate": raw_json.get("restingHeartRate", 0),
        "walking_heart_rate": raw_json.get("walkingHeartRate", 0),
        "hrv": raw_json.get("hrv", 0),
        "systolic": raw_json.get("systolic", 0),
        "diastolic": raw_json.get("diastolic", 0),
        "glucose": raw_json.get("glucose", 0),
    }


def build_summary_text(raw: dict) -> str:
    """
    정규화된 raw dict 기반으로 summary_text 생성
    """
    parts = []

    if raw["sleep_min"] > 0:
        parts.append(f"수면 {raw['sleep_hr']}시간({raw['sleep_min']}분)")

    if raw["bmi"] > 0:
        if raw["bmi"] < 18.5:
            bmi_desc = "저체중"
        elif raw["bmi"] < 23:
            bmi_desc = "정상"
        elif raw["bmi"] < 25:
            bmi_desc = "과체중"
        else:
            bmi_desc = "비만"
        parts.append(f"BMI {raw['bmi']:.1f}({bmi_desc})")

    if raw["distance_km"] > 0:
        parts.append(f"이동거리 {raw['distance_km']:.2f}km")

    if raw["steps"] > 0:
        parts.append(f"걸음수 {raw['steps']:,}보")

    if raw["steps_cadence"] > 0:
        parts.append(f"걸음 속도 {raw['steps_cadence']}보/분")

    if raw["exercise_min"] > 0:
        parts.append(f"운동시간 {raw['exercise_min']}분")

    if raw["flights"] > 0:
        parts.append(f"오른 계단 {raw['flights']}층")

    if raw["total_calories"] > 0:
        parts.append(f"총 소모 칼로리 {raw['total_calories']}kcal")

    if raw["active_calories"] > 0:
        parts.append(f"활동 칼로리 {raw['active_calories']}kcal")

    if raw["calories_intake"] > 0:
        parts.append(f"섭취 칼로리 {raw['calories_intake']}kcal")

    if raw["oxygen_saturation"] > 0:
        parts.append(f"산소포화도 {raw['oxygen_saturation']}%")

    if raw["heart_rate"] > 0:
        parts.append(f"심박수 {raw['heart_rate']}bpm")

    if raw["resting_heart_rate"] > 0:
        parts.append(f"휴식기 심박수 {raw['resting_heart_rate']}bpm")

    if raw["walking_heart_rate"] > 0:
        parts.append(f"걷기 심박수 {raw['walking_heart_rate']}bpm")

    if raw["hrv"] > 0:
        parts.append(f"심박변이도 {raw['hrv']}ms")

    if raw["systolic"] > 0 and raw["diastolic"] > 0:
        parts.append(f"혈압 {raw['systolic']}/{raw['diastolic']}mmHg")

    if raw["glucose"] > 0:
        parts.append(f"혈당 {raw['glucose']}mg/dL")

    if raw["body_fat"] > 0:
        parts.append(f"체지방률 {raw['body_fat']}%")

    if raw["lean_body"] > 0:
        parts.append(f"제지방량 {raw['lean_body']}kg")

    if raw["weight"] > 0 and raw["height_m"] > 0:
        parts.append(f"체중 {raw['weight']}kg / 키 {raw['height_m']:.2f}m")

    return " / ".join(parts)


def preprocess_health_json(raw_json: dict) -> dict:
    """
    단일 통합 summary 생성
      - created_at
      - summary_text
      - raw: 정규화된 모든 수치
    """
    raw_norm = normalize_raw(raw_json)
    summary_text = build_summary_text(raw_norm)

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "summary_text": summary_text,  # LLM 요약용
        "raw": raw_norm,  # 핵심: 정규화된 원본 수치
    }
