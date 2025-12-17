import os
import json
import numpy as np
from tqdm import tqdm
import cv2
from PIL import Image

# ============================================
# 설정
# ============================================
SEQ_LEN = 16
STRIDE = 4
TARGET_SIZE = (256, 256)

TRAIN_LABEL_ROOT = r"D:\013.피트니스자세\1.Training\라벨링데이터"
TRAIN_RAW_ROOT   = r"D:\013.피트니스자세\1.Training\원시데이터"

VALID_LABEL_ROOT = r"D:\013.피트니스자세\2.Validation\라벨링데이터"
VALID_RAW_ROOT   = r"D:\013.피트니스자세\2.Validation\원시데이터"

OUT_ROOT = r"D:\fitness_dataset\stage3_model5"


# ============================================
# OpenCV imread가 한글 경로를 못 읽기 때문에
# PIL 기반 이미지 로딩으로 완전 대체
# ============================================
def load_image_unicode(path):
    try:
        img = Image.open(path).convert("RGB")
        return np.array(img)
    except Exception as e:
        # print("이미지 로드 실패:", path, e)
        return None


# ============================================
# Keypoints 추출
# ============================================
def extract_keypoints(view):
    pts = view.get("pts", {})
    vec = []
    for k, p in pts.items():
        vec.append(p["x"])
        vec.append(p["y"])
    return np.array(vec, dtype=np.float32)


# ============================================
# 메인 전처리
# ============================================
def process_split(label_root, raw_root, out_root):
    os.makedirs(out_root, exist_ok=True)
    img_out_root = os.path.join(out_root, "images")
    os.makedirs(img_out_root, exist_ok=True)

    # JSON 파일 수집
    json_files = []
    for root, _, files in os.walk(label_root):
        for f in files:
            if f.endswith(".json"):
                json_files.append(os.path.join(root, f))

    print(f"[INFO] JSON 파일 수: {len(json_files)}")

    for json_path in tqdm(json_files, desc=f"{out_root} 처리"):

        # JSON 로드
        try:
            data = json.load(open(json_path, "r", encoding="utf-8"))
        except:
            print("❌ JSON 로드 실패:", json_path)
            continue

        frames = data.get("frames", [])
        if len(frames) < SEQ_LEN:
            continue

        type_name = data.get("type", "")
        type_info = data.get("type_info", "")

        # -------------------------------------------------------------
        # 라벨 폴더명 (맨몸운동_04) → 원시데이터 폴더명 (body_04) 매핑
        # -------------------------------------------------------------
        json_norm = os.path.normpath(json_path)
        parts = json_norm.split(os.sep)
        label_folder = parts[-3]                           # ex) 맨몸운동_04
        raw_folder = label_folder.replace("맨몸운동_", "body_")

        # -------------------------------------------------------------
        # 시퀀스 단위 슬라이딩 처리
        # -------------------------------------------------------------
        for start in range(0, len(frames) - SEQ_LEN + 1, STRIDE):
            seq = []
            img_keys = []
            frame_meta = []
            fail = False

            for i in range(start, start + SEQ_LEN):
                frame = frames[i]

                view1 = frame.get("view1", None)
                if view1 is None:
                    fail = True
                    break

                # --- Keypoint ---
                kp = extract_keypoints(view1)
                seq.append(kp)

                # --- 이미지 경로 정보 ---
                img_key = view1.get("img_key", None)
                if img_key is None:
                    fail = True
                    break

                # img_key → 안전한 OS 경로로 변환
                img_parts = img_key.split("/")
                raw_img_path = os.path.join(raw_root, raw_folder, *img_parts)

                # --- PIL로 이미지 로딩 (한글 경로 지원) ---
                img = load_image_unicode(raw_img_path)
                if img is None:
                    # print("⚠️ 이미지 로드 실패:", raw_img_path)
                    fail = True
                    break

                # --- 리사이즈 ---
                img_resized = cv2.resize(img, TARGET_SIZE)

                # --- 결과 이미지 저장 ---
                out_img_path = os.path.join(img_out_root, raw_folder, *img_parts)
                os.makedirs(os.path.dirname(out_img_path), exist_ok=True)
                cv2.imwrite(out_img_path, img_resized)

                # npz 저장용 상대경로
                rel_saved_path = os.path.join("images", raw_folder, *img_parts)
                img_keys.append(rel_saved_path)

                frame_meta.append({
                    "frame_idx": i,
                    "img_key": img_key
                })

            if fail:
                continue

            seq = np.stack(seq, axis=0)

            # --- npz 저장 ---
            out_npz_path = os.path.join(
                out_root,
                os.path.basename(json_path).replace(".json", f"_seq_{start}.npz")
            )

            np.savez_compressed(
                out_npz_path,
                seq=seq,
                img_keys=np.array(img_keys),
                frame_meta=frame_meta,
                type=type_name,
                type_info=type_info
            )


# ============================================
# 실행
# ============================================
print("====== Train 전처리 시작 ======")
process_split(TRAIN_LABEL_ROOT, TRAIN_RAW_ROOT, os.path.join(OUT_ROOT, "train"))

print("====== Valid 전처리 시작 ======")
process_split(VALID_LABEL_ROOT, VALID_RAW_ROOT, os.path.join(OUT_ROOT, "valid"))

print("====== 전체 Stage3(Model5) 전처리 완료 ======")
