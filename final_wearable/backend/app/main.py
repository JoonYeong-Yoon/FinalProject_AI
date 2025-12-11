from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.file_upload_api import router as file_upload_router
from app.api.auto_upload_api import router as auto_upload_router
from app.api.similar_api import router as similar_router
from app.api.chat_api import router as chat_router
from app.api.user_api import router as user_router

from dotenv import load_dotenv

load_dotenv()

print("🔥🔥 FASTAPI SERVER LOADED: VERSION TEST 🔥🔥")
# ==========================
# 1) FastAPI 앱 생성
# ==========================
app = FastAPI(
    title="Health Trainer API",
    description="DB → JSON → AI 분석 트레이너 서비스",
    version="0.1.0",
    default_response_class=ORJSONResponse,
)

# ==========================
# 2) CORS 설정
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 앱 테스트 / APK 테스트 / WiFi 환경 바뀌어도 OK
    allow_credentials=True,
    allow_methods=["*"],  # GET/POST/PUT/DELETE/OPTIONS 등 모두 허용
    allow_headers=["*"],  # 모든 헤더 허용 (파일 업로드 필수)
)

# ==========================
# 3) 라우터 등록
# ==========================
app.include_router(file_upload_router)  # ZIP 파일 업로드(수동, 헬스커넥트)
app.include_router(auto_upload_router)  # JSON 데이터(자동, 헬스커넥트, 애플 헬스킷)
app.include_router(similar_router)
app.include_router(chat_router)
app.include_router(user_router)


# ==========================
# 4) 기본 라우트
# ==========================
@app.get("/")
def root():
    return {"message": "API is running(VectorDB mode)"}


# ==========================
# 5) Global Exception Handlers
# ==========================
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"success": False, "error": exc.errors()},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "type": type(exc).__name__,
        },
    )
