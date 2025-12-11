from fastapi import APIRouter, HTTPException, Query
from app.core.vector_store import search_similar_summaries
from app.core.vector_store import collection

import json

router = APIRouter(prefix="/api/user", tags=["User Data"])


# ------------------------------------------------------------
# 1) 가장 최근 summary 조회
# ------------------------------------------------------------
@router.get("/latest-summary")
def get_latest_summary(user_id: str = Query(...)):
    """
    해당 사용자의 가장 최근 summary + raw + 분석 결과 반환
    """

    # VectorDB에서 최근 1개 검색
    result = search_similar_summaries({"summary_text": ""}, user_id, top_k=1)
    days = result.get("similar_days", [])

    if not days:
        raise HTTPException(404, "사용자 데이터가 없습니다.")

    latest = days[0]

    return {
        "summary_text": latest.get("summary_text"),
        "raw": latest.get("raw"),
        "date": latest.get("date"),
        "similarity": latest.get("similarity"),
    }


# ------------------------------------------------------------
# 2) RAW-HISTORY 조회 (ZIP/앱에서 업로드된 모든 summary 조회)
# ------------------------------------------------------------
@router.get("/raw-history")
def get_raw_history(user_id: str = Query(...)):
    """
    사용자가 업로드한 summary/raw 전체 조회
    VectorDB에 저장된 summary_json을 파싱하여 반환
    """
    result = collection.get(where={"user_id": user_id})

    ids = result.get("ids", [])
    metas = result.get("metadatas", [])

    history = []

    for doc_id, meta in zip(ids, metas):

        summary_dict = {}
        if "summary_json" in meta:
            try:
                summary_dict = json.loads(meta["summary_json"])
            except:
                summary_dict = {}

        history.append(
            {"document_id": doc_id, "date": meta.get("date"), "summary": summary_dict}
        )

    if not history:
        raise HTTPException(404, f"데이터 없음: user_id={user_id}")

    return {"user_id": user_id, "count": len(history), "history": history}


# ------------------------------------------------------------
# 3) VectorDB 디버그용 API
# ------------------------------------------------------------
@router.get("/debug/vector")
def debug_vector(user_id: str = Query(None)):
    """
    VectorDB에 저장된 metadata, document 등을 모두 반환 (개발용)
    """

    # user_id 필터링 가능 / 필터 없으면 전체 조회
    if user_id:
        result = collection.get(where={"user_id": user_id})
    else:
        result = collection.get()

    return {
        "count": len(result.get("ids", [])),
        "ids": result.get("ids", []),
        "metadatas": result.get("metadatas", []),
        "documents": result.get("documents", []),
    }
