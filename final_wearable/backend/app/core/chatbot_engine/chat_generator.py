import os
import json
from openai import OpenAI

from app.core.chatbot_engine.intent_classifier import classify_intent
from app.core.chatbot_engine.persona import get_persona_prompt
from app.core.chatbot_engine.rag_query import query_health_data
from app.core.llm_analysis import run_llm_analysis
from app.config import LLM_MODEL_MAIN, LLM_TEMPERATURE, LLM_MAX_TOKENS


class ChatGenerator:

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # ================================================================
    # 1) OpenAI 호출
    # ================================================================
    def _call_openai(self, prompt: str):
        resp = self.client.chat.completions.create(
            model=LLM_MODEL_MAIN,
            messages=[{"role": "user", "content": prompt}],
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )
        return resp.choices[0].message.content

    # ================================================================
    # 2) 공통 prompt wrapper
    # ================================================================
    def _wrap_prompt(self, persona_prompt: str, body: str):
        return f"""
[Persona]
당신은 다음 캐릭터의 말투와 성격을 유지해야 합니다:
{persona_prompt}

[Task]
아래 정보를 기반으로 전문적이며 정성스럽고 명확하게 설명하세요.

{body}

[Style]
- 캐릭터 말투 유지
- 데이터 기반 분석을 포함하되 단순하게 표현
- 공감 표현 추가
- 과학적 설명은 쉽게
"""

    # ================================================================
    # 3) RAG 데이터 포맷팅
    # ================================================================
    def _format_rag(self, rag):
        similar = rag.get("similar_days", [])
        if not similar:
            return "유사한 날짜의 건강 데이터가 없습니다."

        formatted = []
        for item in similar[:3]:
            formatted.append(
                f"- 날짜: {item.get('date')} (유사도: {item.get('similarity')})\n"
                f"  요약: {item.get('summary_text')}"
            )
        return "\n".join(formatted)

    # ================================================================
    # 4) 메인 generate()
    # ================================================================
    def generate(self, user_id: str, message: str, character: str):

        # 1) intent 분류 + persona 생성
        intent = classify_intent(message)
        persona_prompt = get_persona_prompt(character)

        # ================================================================
        # 1) 건강 데이터 기반 질문(health_query)
        # ================================================================
        if intent == "health_query":

            rag = query_health_data(message, user_id)
            similar = rag.get("similar_days", [])

            # fallback
            if not similar:
                body = f"""
[User Message]
{message}

[Health Data]
건강 데이터가 충분히 저장되어 있지 않습니다.
일반적인 건강 조언을 캐릭터 말투를 고려하여 제공하세요.
                """
                prompt = self._wrap_prompt(persona_prompt, body)
                return self._call_openai(prompt)

            # 정상 RAG 활용
            top_raw = similar[0]["raw"]  # 오늘과 가장 유사한 날의 raw
            rag_text = self._format_rag(rag)

            body = f"""
[User Message]
{message}

[오늘과 유사한 건강 데이터(raw)]
{json.dumps(top_raw, ensure_ascii=False, indent=2)}

[최근 유사 건강 패턴(RAG 기반)]
{rag_text}

이 데이터를 기반으로:
- 오늘의 건강 상태 분석
- 최근 패턴 경향 요약
- 개선이 필요한 생활 습관 또는 관리 포인트

를 캐릭터 말투를 고려하여 설명하세요.
            """

            prompt = self._wrap_prompt(persona_prompt, body)
            return self._call_openai(prompt)

        # ================================================================
        # 2) 운동 루틴 요청(routine_request)
        # ================================================================
        if intent == "routine_request":

            rag = query_health_data("routine", user_id)
            similar = rag.get("similar_days", [])

            # fallback: 운동 관련 데이터 없음
            if not similar:
                body = f"""
[User Message]
{message}

[Health Data]
최근 운동 데이터가 충분하지 않습니다.

초보자도 가능한 30분 홈트 루틴을 캐릭터 스타일에 맞게 설명하세요.
구성 예시:
- 준비운동 5분
- 하체/상체/코어 루틴 구성
- 마무리 스트레칭
                """
                prompt = self._wrap_prompt(persona_prompt, body)
                return self._call_openai(prompt)

            # RAG에서 top_raw 뽑아서 LLM 운동 분석기로 전달
            top_raw = similar[0]["raw"]

            # LLM 기반 추천
            routine_result = run_llm_analysis(
                summary=top_raw,
                rag_result=similar,
                difficulty_level="중",
                duration_min=30,
            )

            body = f"""
[User Message]
{message}

[운동 추천 결과(JSON)]
{json.dumps(routine_result, ensure_ascii=False, indent=2)}

위 운동 루틴을 사용자가 이해하기 쉽고,
부담 없이 따라올 수 있게 캐릭터 말투로 설명하세요.
            """

            prompt = self._wrap_prompt(persona_prompt, body)
            return self._call_openai(prompt)

        # ================================================================
        # 3) 일반 대화
        # ================================================================
        body = f"""
[User Message]
{message}

건강 데이터나 루틴 요청이 아닌 일반 대화입니다.
자연스럽고 공감 있게 캐릭터 말투를 고려하여 대화하세요.
"""
        prompt = self._wrap_prompt(persona_prompt, body)
        return self._call_openai(prompt)
