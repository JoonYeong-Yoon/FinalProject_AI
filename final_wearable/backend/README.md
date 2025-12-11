# 서버 IP 수정

# 폴더, 파일 구조

# 1. chat_api.py

- /api/chat → 자유형 챗봇
- /api/chat/fixed → 고정형 질문(레포트, 추천 등)
- ChatService를 호출하여 모든 비즈니스 로직을 넘김

# 2. upload_api.py

- .zip 또는 .db 파일 업로드 처리
- 운동 난이도(difficulty), 운동시간(duration) 파라미터 전달
- 내부 로직은 UploadService로 위임
- UploadFile로 파일 수신
- URL 쿼리파라미터(user_id, difficulty, duration) 읽기
- service.process_upload() 호출

# 3. similar_api.py

- VectorDB 기반 유사도 검색 API
- summary(dict)와 user_id를 받아 → SimilarService.find_similar 호출

# 4. chat_generator.py

- 챗봇 전체 로직의 메인 엔진
- 사용자의 메시지를 intent로 분류하고
- 캐릭터(persona)·감정(emotion)을 반영한 프롬프트를 만들고
- 필요하면 RAG(요약 DB) 조회 또는 LLM 분석(run_llm_analysis)까지 수행해
- 최종 GPT 응답을 생성하는 핵심 컨트롤러.

# 5. fixed_responses.py

- “고정형 질문 API(/chat/fixed)”의 모든 답변 생성기.
- 주간 리포트 / 오늘 운동 추천 / 심박수·수면 분석 등
- VectorDB에서 최신 summary를 꺼내와
- GPT에게 특정 형식의 답변을 생성시키는 정적 템플릿 엔진.

# 6. intent_classifier.py

- 사용자 메시지의 목적(의도)을 3가지로 분류하는 GPT 기반 분류기.
  1. health_query
  2. routine_request
  3. general_chat
- 챗봇이 어떤 흐름으로 응답할지 결정하는 스위치 역할.

# 7. persona.py

- 캐릭터별 말투 프롬프트를 제공하는 모듈.
- healing / power / expert / friend
- 각 캐릭터의 말투·톤을 정의하는 system_prompt 역할.

# 8. rag_query.py

- VectorDB(Chroma)에서 최근 건강 데이터 요약을 조회하는 RAG 모듈.
- query_text + user_id로 health summary 검색
- 챗봇이 “내 건강 데이터 알려줘” 같은 질문에 답할 수 있게 함.

# 9. predict_sentiment.py

- 한국어 감정 분석(기쁨, 분노 등 7개) 수행
- 입력 텍스트 → tokenizer → 모델 → argmax → 감정 라벨 반환

# 10. model_loader.py

- KcBERT-base 모델과 Tokenizer 로딩
- 감정 분류 라벨 수는 7개로 설정
- model.eval()로 inference 모드

# 11. db_to_json.py

- SQLite DB 파일을 읽어서 테이블 전체를 JSON(dict) 형태로 변환하는 모듈
- 매우 일반화된 DB → JSON 변환 모듈

# 12. unzipper.py

- ZIP 파일을 임시 폴더에 압축 해제한 뒤 내부에서 .db 파일을 자동 검색하여 경로 반환
- 사용자가 ZIP으로 업로드하든 DB로 업로드하든 동일한 파이프라인에서 처리

# 13. vector_store.py (변경 예정)

- ChromaDB 기반 Embedding 저장·검색 모듈 (Vector DB)
- 구성 요소
  1. 안전한 OpenAI Client 생성
  2. 안전한 Chroma Collection 생성
  3. 임베딩 생성 (OpenAI text-embedding-3-large)
  4. summary 저장
  5. summary 유사 검색
- 다음을 수행:
  1. summary JSON → string → embedding
  2. doc_id = user_id_summary_timestamp
  3. 유저별로 검색(where={"user_id": user_id})

# 14. llm_analysis.py

- GPT-4.1 기반 운동 분석 + 운동 루틴 생성 엔진
- summary / raw_json / 난이도 / 운동시간을 기반으로 LLM에게 운동 루틴 JSON을 생성시키는 모듈
- 운동 17종 시드데이터를 제공
- 절대 규칙(시간, 난이도별 MET, 칼로리 공식)을 LLM에게 강제
- JSON 파싱 실패 시
  1. JSON 정제(clean)
  2. 직접 파싱
  3. 실패 시 LLM을 이용한 JSON 복구(fix)
- 이를 통해 LLM 오류로 인한 실패 확률을 최소화.

# 15. chat_service.py

- 자유형 챗봇 + 고정형 챗봇 기능을 실제로 수행하는 서비스 레이어
- 감정 분석 추가(KcBERT 기반 predict_sentiment() 호출 / 감정(emotion) 파악)
- ChatGenerator 호출(캐릭터 스타일 + 메시지 내용 + 감정 기반 응답 생성)
- 고정형 질문(generate_fixed_response() 호출 (정적 분석))

# 16. upload_service.py

- DB 업로드 → Summary 생성 → VectorDB 저장 → LLM 분석
- 전체 파이프라인을 순서대로 수행하는 가장 중심이 되는 로직
- 세부 단계
  1. user_id 생성/유지
  2. 업로드된 ZIP/DB 임시폴더에 저장
  3. ZIP을 압축 해제하여 .db 추출
  4. .db → Raw JSON 변환 (db_to_json)
  5. Raw JSON → Summary 생성 (preprocess)
  6. Summary를 VectorDB(Chroma)에 저장
  7. summary + raw_json → LLM 분석(run_llm_analysis)
  8. 임시파일 정리
  9. 최종 결과(JSON) 반환

# 17. similar_service.py

- VectorDB(Chroma)에 저장된 summary_embedding 기반으로 유사한 날짜의 summary를 조회
- search_similar_summaries() 호출
- 결과를 가공하여 API 응답 형태로 정리

# 18. preprocess.py

- Raw JSON(DB 데이터)에서 요약 Summary 데이터 제작
- Summary 항목
  1. steps
  2. distance
  3. calories_total
  4. calories_active
  5. heart_rate
  6. resting heart rate
  7. hrv
  8. sleep
  9. exercise session
- 즉, “LLM 입력용으로 정제된 요약 데이터”를 만드는 단계.

# 19. main.py

- FastAPI 앱 생성
- CORS 설정
- API 라우터 등록(upload, chat, similar)
- 루트 엔드포인트 / 제공
- 프로젝트 전체 백엔드의 시작점
