from fastapi import APIRouter, Query, HTTPException
from app.service.auto_upload_service import AutoUploadService
from pydantic import BaseModel

router = APIRouter(prefix="/api/auto", tags=["Auto Upload"])
service = AutoUploadService()


class UploadRequest(BaseModel):
    user_id: str
    raw_json: dict
    summary: dict | None = None
    difficulty: str = "중"
    duration: int = 30


@router.post("/upload")
async def upload_json(payload: UploadRequest):
    print("=== JSON 업로드 요청 도착 ===")
    print("user_id:", payload.user_id)
    print("difficulty:", payload.difficulty)  # 상, 중, 하
    print("duration:", payload.duration)  # 10분, 30분, 60분
    print("data keys:", list(payload.raw_json.keys()))

    try:
        result = await service.process_json(
            json_data=payload.raw_json,
            user_id=payload.user_id,
            difficulty=payload.difficulty,
            duration=payload.duration,
        )
        print("=== JSON 처리 성공 ===")
        return result

    except Exception as e:
        print("=== JSON 처리 중 서버 에러 발생 ===")
        print("에러:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
