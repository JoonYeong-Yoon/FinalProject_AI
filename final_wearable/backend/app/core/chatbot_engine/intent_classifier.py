"""
Intent Classifier - 중복 키워드 충돌 방지 최적화 버전 (v5.0)
삼성 + 애플 22개 raw 데이터 완전 대응
routine / health / default 명확히 분리
"""

import time
import os
import json
from openai import OpenAI
from app.config import LLM_MODEL_MAIN

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ================================================================
#  캐싱 (1분 TTL)
# ================================================================
_intent_cache = {}
CACHE_TTL = 60  # 60초


def _cache_get(key):
    data = _intent_cache.get(key)
    if not data:
        return None
    intent, timestamp = data
    if time.time() - timestamp > CACHE_TTL:
        return None
    return intent


def _cache_set(key, intent):
    _intent_cache[key] = (intent, time.time())


# ================================================================
#  HEALTH KEYWORDS (데이터 기반 묘사: 삼성+애플 22개 항목)
# ================================================================
HEALTH_KEYWORDS = [
    # 수면
    "수면",
    "잠",
    "sleep",
    # 신체
    "체중",
    "몸무게",
    "weight",
    "키",
    "신장",
    "height",
    "bmi",
    "체지방",
    "제지방",
    "lean body",
    # 활동 (데이터)
    "걸음",
    "보폭",
    "steps",
    "cadence",
    "이동거리",
    "distance",
    "운동시간",
    "활동시간",
    "계단",
    "flights",
    # 칼로리
    "칼로리",
    "active calorie",
    "열량",
    "섭취 칼로리",
    # 바이탈
    "심박",
    "맥박",
    "heart rate",
    "산소포화",
    "oxygen",
    "hrv",
    "혈압",
    "수축기",
    "이완기",
    "glucose",
]

# ================================================================
#  ROUTINE KEYWORDS (행동 의지/요청 기반)
# ================================================================
ROUTINE_EXPLICIT_KEYWORDS = [
    # 명확히 '운동 추천/루틴'을 의미하는 패턴
    "운동 추천",
    "추천 운동",
    "운동 루틴",
    "루틴",
    "routine",
    "운동 알려줘",
    "30분 운동",
    "20분 운동",
    "40분 운동",
    "하체 루틴",
    "상체 루틴",
    "전신 루틴",
    "유산소 루틴",
    "홈트",
]

# 문맥 기반 키워드: 단독으로는 ambiguous → 문장 패턴 분석 필요
ROUTINE_CONTEXT_KEYWORDS = [
    "운동 뭐",
    "운동할까",
    "오늘 운동",
    "뭐 운동",
    "workout",
]


# ================================================================
#  1차 규칙 기반: 중복 키워드 충돌 방지
# ================================================================
def _rule_based_intent(message: str):
    msg = message.strip().lower()

    # (A) 명확한 루틴 요청 문구 먼저 확인 → 100% 루틴 요청
    for kw in ROUTINE_EXPLICIT_KEYWORDS:
        if kw in msg:
            return "routine_request"

    # (B) 문맥 기반 루틴 요청 ("운동 뭐", "운동할까") → health 키워드 포함돼도 routine이 우선
    for kw in ROUTINE_CONTEXT_KEYWORDS:
        if kw in msg:
            return "routine_request"

    # (C) 그 외 health_query (측정 데이터 기반)
    for kw in HEALTH_KEYWORDS:
        if kw in msg:
            return "health_query"

    # (D) rule 기반 판단 불가 → GPT fallback
    return None


# ================================================================
#  GPT fallback
# ================================================================
def _gpt_intent(message: str) -> str:
    prompt = f"""
너는 사용자의 메시지를 아래 세 종류 중 하나로 분류한다.

1) health_query: 건강 데이터 관련 질문(수면/칼로리/걸음수/심박/혈압 등)
2) routine_request: 운동 루틴/운동 추천 요구
3) default_chat: 일반 대화

사용자 메시지:
{message}

JSON ONLY:
{{"intent": "health_query" 또는 "routine_request" 또는 "default_chat"}}
"""

    resp = client.chat.completions.create(
        model=LLM_MODEL_MAIN,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    try:
        parsed = json.loads(resp.choices[0].message.content)
        return parsed.get("intent", "default_chat")
    except:
        return "default_chat"


# ================================================================
#  메인 intent 함수
# ================================================================
def classify_intent(message: str) -> str:

    # 캐시 확인
    cached = _cache_get(message)
    if cached:
        return cached

    # 규칙 기반 pre-filter
    intent = _rule_based_intent(message)
    if intent:
        _cache_set(message, intent)
        return intent

    # LLM 기반 fallback
    intent = _gpt_intent(message)
    _cache_set(message, intent)
    return intent
