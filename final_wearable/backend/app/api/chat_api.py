from fastapi import APIRouter
from pydantic import BaseModel
from app.service.chat_service import ChatService

router = APIRouter(prefix="/api")
chat_service = ChatService()


# ================================
# 1) 자유형 챗봇
# ================================
class ChatRequest(BaseModel):
    user_id: str   # 이메일 ID
    message: str
    character: str = "healing"

@router.post("/chat")
async def chat(req: ChatRequest):

    result = chat_service.handle_chat(
        user_id=req.user_id,
        message=req.message,
        character=req.character
    )

    return result


# ================================
# 2) 고정형 챗봇
# ================================
class FixedRequest(BaseModel):
    user_id: str
    question_type: str
    character: str = "healing"

@router.post("/chat/fixed")
async def chat_fixed(req: FixedRequest):

    result = chat_service.handle_fixed_chat(
        user_id=req.user_id,
        question_type=req.question_type,
        character=req.character
    )

    return result
