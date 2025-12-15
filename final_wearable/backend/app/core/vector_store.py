# ============================================================
#  ChromaDB 기반 Vector Store (고도화 + 기존 안정성 기능 유지)
# ============================================================
import os, json, chromadb
from chromadb import PersistentClient
from openai import OpenAI
from app.utils.preprocess_for_embedding import summary_to_natural_text


# ------------------------------------------------
# 1) OpenAI Client
# ------------------------------------------------
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("❌ OPENAI_API_KEY가 설정되지 않았습니다. ")
    return OpenAI(api_key=api_key)


# ------------------------------------------------
# 2) ChromaDB Client
#    - DB 파일은 ./chroma_data 폴더에 자동 저장됨
# ------------------------------------------------
chroma_client = PersistentClient(path="./chroma_data")

collection = chroma_client.get_or_create_collection(
    name="summaries", metadata={"hnsw:space": "cosine"}
)


# ------------------------------------------------
# 3) 임베딩 + 캐싱
# ------------------------------------------------
embedding_cache = {}


def embed_text(text: str):
    """
    OpenAI 임베딩 생성 (text-embedding-3-small)
    """
    client = get_openai_client()
    resp = client.embeddings.create(
        model="text-embedding-3-small", input=text  # 비용↓ 속도↑ 정확도 충분
    )
    return resp.data[0].embedding


def get_cached_embedding(text: str):
    if text in embedding_cache:
        return embedding_cache[text]

    emb = embed_text(text)
    embedding_cache[text] = emb
    return emb


# ------------------------------------------------
# 4) Summary 저장 → Chroma DB (고도화 버전)
# ------------------------------------------------
def save_daily_summary(summary: dict, user_id: str):
    """
    요약 데이터를 VectorDB에 저장
      - natural embedding 적용
      - 날짜 기반 upsert 구조
      - summary 전체 metadata에 저장
      - 기존 안정성 코드 최대한 유지
    """
    # 날짜 추출
    created_at = summary.get("created_at")
    if not created_at:
        raise ValueError("❌ summary['created_at']가 존재하지 않습니다.")

    date = created_at[:10]  # yyyy-mm-dd

    # 문서 ID = user_id + 날짜
    doc_id = f"{user_id}_{date}"

    # 1) Natural embedding 텍스트 생성
    embedding_text = summary_to_natural_text(summary)

    # 2) 임베딩 생성 + 캐시 적용
    embedding = get_cached_embedding(embedding_text)

    # 3) summary(raw 포함)을 안전하게 metadata에 저장
    try:
        summary_json = json.dumps(summary, ensure_ascii=False)
    except Exception as e:
        print(f"[WARN] Summary JSON 직렬화 실패: {e}")
        summary_json = str(summary)

    metadata = {
        "user_id": user_id,
        "date": date,
        "source": summary.get("raw", {}).get("source", "unknown"),
        "summary_text": summary.get("summary_text", ""),
        "summary_json": summary_json,
    }

    # 4) Upsert 저장 (add → upsert 변경)
    collection.upsert(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[embedding_text],  # 자연어 기반 embedding 문장
        metadatas=[metadata],
    )

    return {"status": "saved", "document_id": doc_id, "date": date, "user_id": user_id}


# ------------------------------------------------
# 5) 유사 Summary 검색
# ------------------------------------------------
def search_similar_summaries(query_dict: dict, user_id: str, top_k=3):
    """
    RAG 검색 기능
      - natural text embedding 기반 검색
      - user_id(email) 기반 필터링 적용
    """

    # natural embedding 텍스트 생성
    q_text = summary_to_natural_text(query_dict)

    # query embedding 생성
    q_vec = get_cached_embedding(q_text)

    # 검색 (user_id 기준으로 filtering)
    result = collection.query(
        query_embeddings=[q_vec],
        n_results=top_k,
        where={"user_id": user_id},
    )

    ids = result.get("ids", [[]])[0]
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    ranked = []
    for doc_id, doc_text, meta, dist in zip(ids, docs, metas, distances):
        similarity = round(1 - dist, 4)

        # metadata에 저장된 summary_json 문자열을 파싱
        summary_dict = {}
        if "summary_json" in meta:
            try:
                summary_dict = json.loads(meta["summary_json"])
            except:
                summary_dict = {}

        ranked.append(
            {
                "document_id": doc_id,
                "date": meta.get("date"),
                "similarity": similarity,
                "summary_text": summary_dict.get("summary_text"),
                "raw": summary_dict.get("raw"),
            }
        )

    # 유사도 내림차순 정렬 후 top_k 반환
    ranked = sorted(ranked, key=lambda x: x["similarity"], reverse=True)

    return {"similar_days": ranked, "count": len(ranked)}
