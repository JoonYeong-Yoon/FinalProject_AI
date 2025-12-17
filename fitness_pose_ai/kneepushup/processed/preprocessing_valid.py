import os
import json
import numpy as np
from tqdm import tqdm
import cv2
from PIL import Image

SEQ_LEN = 16
STRIDE = 4
TARGET_SIZE = (256, 256)

VALID_LABEL_ROOT = r"D:\013.피트니스자세\2.Validation\라벨링데이터"
VALID_RAW_ROOT   = r"D:\013.피트니스자세\2.Validation\원시데이터\valid_body_data"

OUT_VALID = r"D:\fitness_dataset\stage3_model5\valid"


def load_image_unicode(path):
    try:
        img = Image.open(path).convert("RGB")
        return np.array(img)
    except:
        return None


def extract_keypoints(view):
    pts = view.get("pts", {})
    vec = []
    for k, p in pts.items():
        vec.append(p["x"])
        vec.append(p["y"])
    return np.array(vec, dtype=np.float32)


def process_validation(label_root, raw_root, out_root):
    print("===== Validation JSON 스캔 시작 =====")

    json_files = []
    for root, _, files in os.walk(label_root):
        for f in files:
            if f.endswith(".json"):
                json_files.append(os.path.join(root, f))

    print("[INFO] JSON 파일 수:", len(json_files))

    os.makedirs(out_root, exist_ok=True)
    img_out_root = os.path.join(out_root, "images")
    os.makedirs(img_out_root, exist_ok=True)

    created = 0

    for json_path in tqdm(json_files, desc="Validation 처리"):

        data = json.load(open(json_path, "r", encoding="utf-8"))

        frames = data.get("frames", [])
        if len(frames) < SEQ_LEN:
            continue

        type_name = data.get("type", "")
        type_info = data.get("type_info", "")

        for start in range(0, len(frames) - SEQ_LEN + 1, STRIDE):

            seq = []
            img_keys = []
            frame_meta = []
            fail = False

            for i in range(start, start + SEQ_LEN):

                view1 = frames[i].get("view1")
                if view1 is None:
                    fail = True
                    break

                kp = extract_keypoints(view1)
                seq.append(kp)

                img_key = view1["img_key"]

                # RAW 경로 조합 (정답)
                raw_img_path = os.path.join(raw_root, img_key)

                img = load_image_unicode(raw_img_path)
                if img is None:
                    print("이미지 없음:", raw_img_path)
                    fail = True
                    break

                # 리사이즈
                img_resized = cv2.resize(img, TARGET_SIZE)

                out_img_path = os.path.join(img_out_root, img_key)
                os.makedirs(os.path.dirname(out_img_path), exist_ok=True)
                cv2.imwrite(out_img_path, img_resized)

                rel_path = os.path.join("images", img_key)
                img_keys.append(rel_path)

                frame_meta.append({"frame_idx": i, "img_key": img_key})

            if fail:
                continue

            seq = np.stack(seq)

            out_npz = os.path.join(
                out_root,
                os.path.basename(json_path).replace(".json", f"_seq_{start}.npz")
            )

            np.savez_compressed(
                out_npz,
                seq=seq,
                img_keys=np.array(img_keys),
                frame_meta=frame_meta,
                type=type_name,
                type_info=type_info
            )

            created += 1

    print("===== Validation 전처리 완료 =====")
    print("생성된 NPZ =", created)


process_validation(VALID_LABEL_ROOT, VALID_RAW_ROOT, OUT_VALID)
