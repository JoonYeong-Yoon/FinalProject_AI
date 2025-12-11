from app.core.chatbot_engine.chat_generator import ChatGenerator
from app.core.chatbot_engine.fixed_responses import generate_fixed_response


class ChatService:
    """
    Chat 관련 비즈니스 로직을 담당하는 Service 계층.
    """

    def __init__(self):
        self.generator = ChatGenerator()

    # -------------------------------------------
    # 1) 자유형 (intent → sentiment → RAG → LLM)
    # -------------------------------------------
    def handle_chat(self, user_id: str, message: str, character: str):
        response = self.generator.generate(
            user_id=user_id,
            message=message,
            character=character,
        )

        return {"response": response}

    # -------------------------------------------
    # 2) 고정형
    # -------------------------------------------
    @staticmethod
    def handle_fixed_chat(user_id: str, question_type: str, character: str):
        response = generate_fixed_response(
            user_id=user_id,
            question_type=question_type,
            character=character,
        )
        return {"response": response}
