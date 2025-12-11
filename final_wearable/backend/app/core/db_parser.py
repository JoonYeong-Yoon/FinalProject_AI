import statistics

# -------------------------------------------------------------
# 삼성 ZIP(DB) → raw_json(23개 스키마) 추출
# -------------------------------------------------------------


def parse_db_json_to_raw_data(db_json: dict) -> dict:
    """
    Health Connect SQLite DB(JSON 변환 결과)를 기반으로
    최신 날짜의 건강 데이터를 23개 항목(raw_json)으로 변환한다.

    ※ preprocess()에서 정규화되므로 여기서는 원본 값만 추출한다.
    """
    print("--- DEBUG: DB Raw Data Parsing (REAL SAMSUNG ZIP) ---")

    if not db_json:
        return {}

    # 날짜별 그룹핑
    grouped = {}

    def add(date_key, key, value):
        if date_key not in grouped:
            grouped[date_key] = {
                "sleep": [],
                "steps": [],
                "distance": [],
                "steps_cadence": [],
                "active_calories": [],
                "total_calories": [],
                "oxygen_saturation": [],
                "heart_rate": [],
                "resting_heart_rate": [],
                "weight": [],
                "height": [],
            }
        grouped[date_key][key].append(value)

    # ---------------------------------------------------------
    # 걸음수
    # ---------------------------------------------------------
    for row in db_json.get("steps_record_table", []):
        add(row["local_date"], "steps", row.get("count", 0))

    # ---------------------------------------------------------
    # 이동거리 (meter 단위)
    # ---------------------------------------------------------
    for row in db_json.get("distance_record_table", []):
        add(row["local_date"], "distance", row.get("distance", 0))

    # ---------------------------------------------------------
    # 걸음 빈도(step cadence)
    # ---------------------------------------------------------
    for row in db_json.get("steps_cadence_record_table", []):
        samples = row.get("samples") or row.get("samples_list") or None
        if samples and isinstance(samples, list):
            add(row["local_date"], "steps_cadence", statistics.mean(samples))
    # ---------------------------------------------------------
    # 총 칼로리 (energy = millikalories)
    # ---------------------------------------------------------
    for row in db_json.get("total_calories_burned_record_table", []):
        kcal = row.get("energy", 0) / 1000
        add(row["local_date"], "total_calories", kcal)

    # ---------------------------------------------------------
    # 활동 칼로리
    # ---------------------------------------------------------
    for row in db_json.get("active_calories_burned_record_table", []):
        kcal = row.get("energy", 0) / 1000
        add(row["local_date"], "active_calories", kcal)

    # ---------------------------------------------------------
    # 심박수
    # ---------------------------------------------------------
    for row in db_json.get("heart_rate_record_table", []):
        add(row["local_date"], "heart_rate", row.get("value", 0))

    # ---------------------------------------------------------
    # 휴식기 심박수
    # ---------------------------------------------------------
    for row in db_json.get("resting_heart_rate_record_table", []):
        add(row["local_date"], "resting_heart_rate", row.get("value", 0))

    # ---------------------------------------------------------
    # 산소포화도 (%)
    # ---------------------------------------------------------
    for row in db_json.get("oxygen_saturation_record_table", []):
        add(row["local_date"], "oxygen_saturation", row.get("percentage", 0))

    # ---------------------------------------------------------
    # 체중 (gram)
    # ---------------------------------------------------------
    for row in db_json.get("weight_record_table", []):
        w = row.get("weight", 0)
        if w > 0:
            w = w / 1000
        add(row["local_date"], "weight", w)

    # ---------------------------------------------------------
    # 키 (meter)
    # ---------------------------------------------------------
    for row in db_json.get("height_record_table", []):
        add(row["local_date"], "height", row.get("height", 0))

    # ---------------------------------------------------------
    # 수면 (start~end → minutes)
    # ---------------------------------------------------------
    for row in db_json.get("sleep_session_record_table", []):
        s, e = row.get("start_time"), row.get("end_time")
        if s and e:
            minutes = (e - s) / 1000 / 60
            add(row["local_date"], "sleep", minutes)

    # ---------------------------------------------------------
    # 최신 날짜 선택
    # ---------------------------------------------------------
    if not grouped:
        return {}

    latest_date = max(grouped.keys())
    d = grouped[latest_date]

    def mean(v):
        return statistics.mean(v) if v else 0

    def total(v):
        return sum(v) if v else 0

    # ---------------------------------------------------------
    # 최종 raw_json (23개 스키마)
    # ---------------------------------------------------------
    return {
        # 수면
        "sleep": total(d["sleep"]),
        # 신체
        "weight": mean(d["weight"]),
        "height": mean(d["height"]),
        # 활동
        "distance": total(d["distance"]),
        "steps": total(d["steps"]),
        "stepsCadence": mean(d["steps_cadence"]),
        # 칼로리
        "calories": total(d["active_calories"]),
        "totalCaloriesBurned": total(d["total_calories"]),
        # 바이탈
        "oxygenSaturation": mean(d["oxygen_saturation"]),
        "heartRate": mean(d["heart_rate"]),
        "restingHeartRate": mean(d["resting_heart_rate"]),
        # 삼성 데이터에서는 제공되지 않는 항목은 0 고정
        "exerciseTime": 0,
        "flights": 0,
        "bodyFat": 0,
        "leanBody": 0,
        "walkingHeartRate": 0,
        "hrv": 0,
        "systolic": 0,
        "diastolic": 0,
        "glucose": 0,
    }
