import json
from openai import OpenAI
import os

from app.config import LLM_MODEL_MAIN, LLM_TEMPERATURE, LLM_MAX_TOKENS
from app.core.chatbot_engine.persona import get_persona_prompt
from app.core.vector_store import search_similar_summaries
from app.core.llm_analysis import run_llm_analysis

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_fixed_response(user_id: str, question_type: str, character: str):
    """
    고정형 질문을 처리하는 엔진
    """

    persona = get_persona_prompt(character)

    # vector DB에서 최근 summary 3개 검색(공통)
    vector_result = search_similar_summaries(
        query_dict={"query": "health summary"}, user_id=user_id, top_k=3
    )

    summaries = vector_result.get("similar_days", []) or []

    # summary 없을 경우 fallback
    if not summaries:
        fallback = f"""
{persona}

아직 사용자에게 저장된 건강 데이터가 없습니다.
헬스 커넥트 ZIP 파일을 업로드 하면 분석을 시작할 수 있어요!
        """
        return fallback.strip()

    # 최근 summary 1개만 사용
    recent_summary = summaries[0].get("summary", {})

    # ================================
    # 1) 주간 리포트
    # ================================
    if question_type == "weekly_report":
        prompt = f"""
{persona}

아래 데이터(summary)를 기반으로
사용자의 "이번 주 건강 리포트"를 작성해줘.

summary:
{json.dumps(recent_summary, ensure_ascii=False, indent=2)}

JSON 아님. 자연스러운 말투로 대답.
"""

        resp = client.chat.completions.create(
            model=LLM_MODEL_MAIN, messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

    # ================================
    # 2) 오늘 운동 추천
    # ================================
    if question_type == "today_recommendation":
        # summary 기반 운동 루틴 생성
        routine = run_llm_analysis(recent_summary, {}, "중", 30)

        prompt = f"""
{persona}

사용자의 최근 건강 데이터를 기반으로
오늘 적합한 30분 운동을 아주 친근하게 설명해줘.

운동 루틴:
{json.dumps(routine, ensure_ascii=False, indent=2)}
"""

        resp = client.chat.completions.create(
            model=LLM_MODEL_MAIN, messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

    # ================================
    # 3) 걸음수(지난주 평균)
    # ================================
    if question_type == "weekly_steps":
        steps = recent_summary.get("steps", {})

        prompt = f"""
{persona}

다음 데이터를 기반으로
지난주 걸음수 평균을 사용자에게 설명해줘.

steps:
{json.dumps(steps, ensure_ascii=False, indent=2)}
"""

        resp = client.chat.completions.create(
            model=LLM_MODEL_MAIN, messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

    # ================================
    # 4) 수면 분석
    # ================================
    if question_type == "sleep_report":
        sleep = recent_summary.get("sleep", {})

        prompt = f"""
{persona}

아래 수면 데이터를 기반으로
사용자의 최근 수면 패턴 분석을 친절하게 설명해줘.

sleep:
{json.dumps(sleep, ensure_ascii=False, indent=2)}
"""

        resp = client.chat.completions.create(
            model=LLM_MODEL_MAIN, messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

    # ================================
    # 5) 심박수 분석
    # ================================
    if question_type == "heart_rate":
        heart = recent_summary.get("heart_rate", {})

        prompt = f"""
{persona}

다음 심박수를 기반으로
최근 심박수 안정성 평가를 해줘.

heart_rate:
{json.dumps(heart, ensure_ascii=False, indent=2)}
"""

        resp = client.chat.completions.create(
            model=LLM_MODEL_MAIN, messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

    # ================================
    # 6) 건강 점수
    # ================================
    if question_type == "health_score":
        prompt = f"""
{persona}

사용자가 최근 summary를 기반으로
0~100점 사이의 건강 점수를 계산하고 설명해줘.

summary:
{json.dumps(recent_summary, ensure_ascii=False, indent=2)}
"""

        resp = client.chat.completions.create(
            model=LLM_MODEL_MAIN, messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

    return "⚠️ 알 수 없는 question_type 입니다."
