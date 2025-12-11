import os, shutil, tempfile, uuid, json
from fastapi import UploadFile, HTTPException

from app.core.unzipper import extract_zip_to_temp
from app.core.db_to_json import db_to_json
from app.core.db_parser import parse_db_json_to_raw_data

from app.utils.preprocess import preprocess_health_json
from app.core.vector_store import save_daily_summary
from app.core.llm_analysis import run_llm_analysis


class FileUploadService:
    """
    ZIP/DB 파일 업로드 처리 서비스
    (DB → raw JSON → Summary → VectorDB 저장 → LLM 분석)
    """

    @staticmethod
    def get_or_create_user_id(user_id: str | None):
        return user_id if user_id else str(uuid.uuid4())

    async def process_file(
        self, file: UploadFile, user_id: str | None, difficulty: str, duration: int
    ):
        # 1) 이메일 기반 user_id 확보
        user_id = self.get_or_create_user_id(user_id)

        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        raw_db_json = {}
        summary = None

        try:
            # 2) 파일 저장
            try:
                with open(temp_path, "wb") as buffer:
                    buffer.write(await file.read())
            except Exception as e:
                raise HTTPException(500, f"파일 저장 실패: {str(e)}")

            # ★ ZIP 파일 내부 구조 출력 ★
            try:
                import zipfile

                with zipfile.ZipFile(temp_path, "r") as z:
                    print("\n===== ZIP FILE CONTENTS =====")
                    for name in z.namelist():
                        print(" -", name)
                    print("================================\n")
            except:
                print("ZIP 파일이 아니거나, 열 수 없습니다.")

            # 3) ZIP 또는 DB 파일 판단 및 처리
            if file.filename.lower().endswith(".zip"):
                db_path = extract_zip_to_temp(temp_path)
            elif file.filename.lower().endswith(".db"):
                db_path = temp_path
            else:
                raise HTTPException(400, "ZIP 또는 DB 파일만 업로드 가능합니다.")

            if not db_path:
                raise HTTPException(500, "DB 파일 경로를 찾을 수 없습니다.")

            # 4) DB 파일 → JSON 변환
            raw_db_json = db_to_json(db_path)
            print("\n======= DB JSON RAW OUTPUT =======")
            print(json.dumps(raw_db_json, indent=2, ensure_ascii=False))
            print("==================================\n")

            # 5) JSON → raw 지표 추출(db_parser)
            raw_data_for_llm = parse_db_json_to_raw_data(raw_db_json)

            if not raw_data_for_llm:
                raise HTTPException(
                    500, "DB Parser가 건강 데이터를 추출하지 못했습니다."
                )

            # 6) raw → Summary 생성 (정규화됨)
            summary = preprocess_health_json(raw_data_for_llm)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"ZIP/DB 처리 중 오류 발생: {str(e)}")
        finally:

            # 7) 임시 디렉토리 정리 (ZIP/DB 처리 후 항상 삭제)
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

        # 8) Summary → VectorDB 저장
        try:
            save_daily_summary(summary, user_id)
        except Exception as e:
            raise HTTPException(500, f"Vector DB 저장 실패: {str(e)}")

        # 9) Summary → LLM 분석
        try:
            llm_result = run_llm_analysis(
                summary,
                {},  # rag_result 추가
                difficulty,
                duration,
            )
        except Exception as e:
            raise HTTPException(500, f"LLM 분석 실패: {str(e)}")

        # 10) 최종 반환
        return {
            "message": "ZIP/DB 업로드 및 분석 성공",
            "user_id": user_id,
            "summary": summary,
            "llm_result": llm_result,
        }
