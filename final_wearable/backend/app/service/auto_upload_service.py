import uuid
import asyncio
from fastapi import HTTPException
from concurrent.futures import ThreadPoolExecutor

from app.utils.preprocess import preprocess_health_json
from app.core.vector_store import save_daily_summary
from app.core.llm_analysis import run_llm_analysis

executor = ThreadPoolExecutor()


async def run_blocking(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, lambda: func(*args))


class AutoUploadService:
    """
    앱에서 직접 전송한 JSON Health 데이터를 처리하는 서비스
    (JSON → Summary → VectorDB → LLM 분석)
    """

    @staticmethod
    def get_or_create_user_id(user_id: str | None):
        return user_id if user_id else str(uuid.uuid4())

    async def process_json(
        self,
        json_data: dict,
        user_id: str | None,
        difficulty: str = "중",
        duration: int = 30,
    ):
        # 1) 이메일 기반 user_id 확보
        user_id = self.get_or_create_user_id(user_id)

        # 2) Summary 생성 (CPU 작업 → run_blocking)
        try:
            summary = await run_blocking(preprocess_health_json, json_data)
        except Exception as e:
            raise HTTPException(500, f"Summary 생성 실패: {str(e)}")

        # 3) VectorDB 저장
        try:
            await run_blocking(save_daily_summary, summary, user_id)
        except Exception as e:
            raise HTTPException(500, f"Vector DB 저장 실패: {str(e)}")

        # 4) LLM 분석
        try:
            llm_result = await run_blocking(
                run_llm_analysis,
                summary,
                {},  # RAG 결과 없음 → 빈 dict
                difficulty,  # difficulty_level
                duration,  # duration_min
            )
        except Exception as e:
            raise HTTPException(500, f"LLM 분석 실패: {str(e)}")

        return {
            "success": True,
            "message": "자동 업로드 및 분석 성공",
            "user_id": user_id,
            "summary": summary,
            "llm_result": llm_result,
        }
