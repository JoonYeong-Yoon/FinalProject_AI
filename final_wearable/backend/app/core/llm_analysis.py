import os
import json
import textwrap

from dotenv import load_dotenv
from openai import OpenAI
from app.config import LLM_MODEL_MAIN, LLM_TEMPERATURE, LLM_MAX_TOKENS

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ==========================================================
# 1) 유틸 : 코드블럭 제거
# ==========================================================
def clean_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    return text


# ==========================================================
# 2) 유틸 : JSON 파싱
# ==========================================================
def try_parse_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None


# ==========================================================
# 3) 깨진 JSON 자동 복구
# ==========================================================
def repair_json_with_llm(broken_text: str) -> str:
    fix_prompt = textwrap.dedent(
        f"""
    다음 텍스트는 JSON 형식이 잘못되었습니다.
    형식을 고쳐 **오직 JSON만 반환하세요.**
    설명 금지, 코드블록 금지.

    잘못된 JSON:
    {broken_text}
    """
    )

    resp = client.chat.completions.create(
        model=LLM_MODEL_MAIN,
        messages=[
            {"role": "system", "content": "너는 JSON 복원기다. 출력은 JSON ONLY."},
            {"role": "user", "content": fix_prompt},
        ],
        max_tokens=700,
        temperature=0.0,
    )
    fixed = resp.choices[0].message.content
    return clean_json_text(fixed)


# ==========================================================
# 4) 운동 Seed(17종)
# ==========================================================
EXERCISE_REFERENCE = [
    {"name": "standing side crunch", "category": [2, 3], "difficulty": 3, "met": 4},
    {"name": "standing knee up", "category": [1, 3], "difficulty": 3, "met": 3.8},
    {"name": "burpee test", "category": [4], "difficulty": 5, "met": 8},
    {"name": "step forward dynamic lunge", "category": [3], "difficulty": 4, "met": 4},
    {"name": "step backward dynamic lunge", "category": [3], "difficulty": 4, "met": 4},
    {"name": "side lunge", "category": [3], "difficulty": 5, "met": 5},
    {"name": "cross lunge", "category": [3, 2], "difficulty": 4, "met": 3.8},
    {"name": "good morning exercise", "category": [3], "difficulty": 5, "met": 5},
    {"name": "lying leg raise", "category": [3, 2], "difficulty": 4, "met": 4},
    {"name": "crunch", "category": [2], "difficulty": 4, "met": 4.5},
    {"name": "bicycle crunch", "category": [3, 2], "difficulty": 5, "met": 5},
    {"name": "scissor cross", "category": [2, 3], "difficulty": 4, "met": 4.5},
    {"name": "hip thrust", "category": [3, 2], "difficulty": 3, "met": 3.5},
    {"name": "plank", "category": [4], "difficulty": 5, "met": 8},
    {"name": "push up", "category": [1, 2], "difficulty": 4, "met": 6},
    {"name": "knee push up", "category": [1, 2], "difficulty": 3, "met": 5},
    {"name": "Y-exercise", "category": [1, 2], "difficulty": 3, "met": 4.5},
]

SEED_JSON = json.dumps(EXERCISE_REFERENCE, ensure_ascii=False)


# ==========================================================
# 5) 최종 LLM 운동 분석 엔진 (RAG 포함)
# ==========================================================
def run_llm_analysis(
    summary: dict,
    rag_result: dict | None,
    difficulty_level: str,
    duration_min: int,
) -> dict:

    summary_text = summary.get("summary_text", "")
    raw = summary.get("raw", {})
    seed_text = SEED_JSON

    # ------------------------------------------------------
    # 1) RAG 안전 처리
    # ------------------------------------------------------
    similar_days = []
    if rag_result and isinstance(rag_result, dict):
        similar_days = rag_result.get("similar_days", []) or []

    # ------------------------------------------------------
    # 2) RAG 표현 블록
    # ------------------------------------------------------
    rag_items = []
    for item in similar_days[:3]:
        created = item.get("created_at")
        summary_txt = item.get("summary_text")
        sim = item.get("similarity")
        rag_items.append(f"- {created} | 유사도 {sim}, 요약: {summary_txt}")

    rag_block = "\n".join(rag_items) if rag_items else "유사 데이터 없음"

    # ------------------------------------------------------
    # 3) raw block
    # ------------------------------------------------------
    raw_block = textwrap.dedent(
        f"""
    [정규화된 건강 수치(raw)]
    운동 추천의 최우선 기준입니다.

    # 수면
    sleep_min: {raw.get('sleep_min', 0)}
    sleep_hr: {raw.get('sleep_hr', 0)}

    # 신체
    weight: {raw.get('weight', 0)}
    height_m: {raw.get('height_m', 0)}
    bmi: {raw.get('bmi', 0)}
    body_fat: {raw.get('body_fat', 0)}
    lean_body: {raw.get('lean_body', 0)}

    # 활동
    distance_km: {raw.get('distance_km', 0)}
    steps: {raw.get('steps', 0)}
    steps_cadence: {raw.get('steps_cadence', 0)}
    exercise_min: {raw.get('exercise_min', 0)}
    flights: {raw.get('flights', 0)}

    # 칼로리
    total_calories: {raw.get('total_calories', 0)}
    active_calories: {raw.get('active_calories', 0)}
    calories_intake: {raw.get('calories_intake', 0)}

    # 바이탈
    oxygen_saturation: {raw.get('oxygen_saturation', 0)}
    heart_rate: {raw.get('heart_rate', 0)}
    resting_heart_rate: {raw.get('resting_heart_rate', 0)}
    walking_heart_rate: {raw.get('walking_heart_rate', 0)}
    hrv: {raw.get('hrv', 0)}
    systolic: {raw.get('systolic', 0)}
    diastolic: {raw.get('diastolic', 0)}
    glucose: {raw.get('glucose', 0)}
    """
    )

    # ------------------------------------------------------
    # 4) SYSTEM PROMPT
    # ------------------------------------------------------
    system_prompt = textwrap.dedent(
        """
    너는 건강 데이터 분석 + 운동 처방 전문가다.
    사용자의 데이터를 기반으로 과학적인 운동 루틴을 생성한다.

    [절대 규칙]
    - 반드시 JSON ONLY 출력
    - 설명문 금지
    - 코드블록 금지
    - 운동 17종 외 사용 금지
    - 스키마 절대 변경 금지
    """
    )

    # ------------------------------------------------------
    # 5) JSON schema
    # ------------------------------------------------------
    schema_block = textwrap.dedent(
        """
    {
        "analysis": "...",
        "ai_recommended_routine": {
            "total_time_min": number,
            "total_calories": number,
            "items": [
                {
                    "exercise_name": "...",
                    "category": [...],
                    "difficulty": number,
                    "met": number,
                    "duration_sec": number,
                    "rest_sec": number,
                    "set_count": number,
                    "reps": number | null
                }
            ]
        },
        "used_data_ranked": {
            "summary_text": { "feature": score },
            "raw": { "metric": score },
            "rag_pattern": { "pattern": score }
        }
    }
    """
    )

    # ------------------------------------------------------
    # 6) user prompt (summary + raw + RAG)
    # ------------------------------------------------------
    user_prompt = textwrap.dedent(
        f"""
    {raw_block}

    [summary_text]
    {summary_text}

    [RAG 기반 최근 건강 패턴]
    {rag_block}

    [입력 정보]
    난이도: {difficulty_level}
    운동 시간: {duration_min}분

    [운동 Seed]
    {seed_text}

    ─────────────────────────────────────
    ■ 난이도 규칙
    ─────────────────────────────────────
    하: MET 2.5-4
    중: MET 4-5
    상: MET 5-8

    ─────────────────────────────────────
    ■ 운동 시간 규칙 (절대 준수)
    ─────────────────────────────────────
    total_time_sec = Σ(ex.duration_sec * ex.set_count) + Σ(ex.rest_sec * ex.set_count)

    total_time_sec must be within:
    duration_min * 60 * 0.95  ~  duration_min * 60 * 1.05

    즉, 전체 운동 시간은 요청된 운동 시간의 ±5% 이내여야 한다.
    # 절대 규칙
    - total_time_sec 규칙은 가장 중요한 제약 조건이다.
    - 이를 위반하는 JSON은 자동으로 실패로 처리된다.

    ─────────────────────────────────────
    ■ 개인화 규칙(summary.raw + RAG)
    ─────────────────────────────────────
    - sleep_hr < 5 → 고강도 금지(MET ≤ 4.5)
    - oxygen_saturation < 94 → plank·burpee 제한
    - bmi ≥ 25 → 유산소 비중 ↑
    - steps > 10000 → 하체 피로 고려
    - heart_rate > 90 → 휴식시간 +30%

    ─────────────────────────────────────
    ■ JSON 스키마
    ─────────────────────────────────────
    {schema_block}

    **JSON만 출력하세요**
    """
    )

    # ------------------------------------------------------
    # 7) GPT 실행
    # ------------------------------------------------------
    resp = client.chat.completions.create(
        model=LLM_MODEL_MAIN,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1500,
        temperature=0.1,
    )

    raw_text = resp.choices[0].message.content
    cleaned = clean_json_text(raw_text)

    parsed = try_parse_json(cleaned)
    if parsed and "analysis" in parsed and "ai_recommended_routine" in parsed:
        return parsed

    # 자동 복구
    repaired = repair_json_with_llm(cleaned)
    parsed2 = try_parse_json(repaired)
    if parsed2 and "analysis" in parsed2 and "ai_recommended_routine" in parsed2:
        return parsed2

    # 완전 실패 → fallback JSON
    return {
        "analysis": "LLM 분석 실패",
        "ai_recommended_routine": {
            "total_time_min": 0,
            "total_calories": 0,
            "items": [],
        },
        "used_data_ranked": {
            "error": "LLM 출력 오류 또는 JSON 복구 실패",
        },
    }
