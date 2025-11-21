import os
import json
from tqdm import tqdm
from PIL import Image
import re

# ==========================================================
# 0. 기본 경로 설정
# ==========================================================
TRAIN_LABEL_BASE = r"D:\013.피트니스자세\1.Training\라벨링데이터\맨몸운동_Labeling_new_220128"
TRAIN_RAW_BASE   = r"D:\013.피트니스자세\1.Training\원시데이터"

OUT_BASE = r"D:\fitness_dataset"

# Stage 1 = 운동 분류
S1_TRAIN_IMG = os.path.join(OUT_BASE, "stage1_classification", "train", "images")
S1_TRAIN_LAB = os.path.join(OUT_BASE, "stage1_classification", "train", "labels")

# Stage 2 = 자세 교정
S2_TRAIN_IMG = os.path.join(OUT_BASE, "stage2_pose_correction", "train", "images")
S2_TRAIN_LAB = os.path.join(OUT_BASE, "stage2_pose_correction", "train", "labels")

for d in [
    S1_TRAIN_IMG, S1_TRAIN_LAB,
    S2_TRAIN_IMG, S2_TRAIN_LAB
]:
    os.makedirs(d, exist_ok=True)


# ==========================================================
# 1. JSON 스캔
# ==========================================================
def list_json_files(base_dir):
    jsons = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".json"):
                jsons.append(os.path.join(root, f))
    return jsons


# ==========================================================
# 2. 라벨 경로에서 body_xx 추출 (정확한 버전)
# ==========================================================
def extract_body_name_from_label_path(path):
    m = re.search(r"맨몸운동_(\d+)", path)
    if not m:
        return None
    num = int(m.group(1))
    return f"body_{num:02d}"


# ==========================================================
# 3. 이미지 경로 해석
# ==========================================================
def resolve_path(img_key, raw_dir):
    path = os.path.join(raw_dir, img_key.replace("/", "\\"))
    return path if os.path.exists(path) else None


# ==========================================================
# 4. 리사이즈 (256x256)
# ==========================================================
def resize(src, dst, size=(256,256)):
    try:
        img = Image.open(src).resize(size)
        img.save(dst)
        return True
    except:
        return False


# ==========================================================
# 5. 전처리 핵심
# ==========================================================
def parse(json_list, raw_base, mode, pbar):

    existing_s1 = len(os.listdir(S1_TRAIN_IMG))
    counter = existing_s1

    for jp in json_list:

        # 💥 가장 중요한 부분: 정확한 body 매칭
        source_body = extract_body_name_from_label_path(jp)
        if not source_body:
            pbar.update(1)
            continue

        raw_dir = os.path.join(raw_base, source_body)

        with open(jp, "r", encoding="utf-8") as f:
            data = json.load(f)

        frames = data.get("frames", [])
        ex = data.get("type_info", {}).get("exercise", "unknown")
        pose = data.get("type_info", {}).get("pose", "unknown")
        cond_raw = data.get("type_info", {}).get("conditions", [])
        cond_dict = {c["condition"]: c["value"] for c in cond_raw}

        for fr in frames:

            v = fr.get("view1") or fr.get("view2") or fr.get("view3")
            if not v:
                pbar.update(1)
                continue

            img_key = v.get("img_key")
            if not img_key:
                pbar.update(1)
                continue

            raw_path = resolve_path(img_key, raw_dir)
            if not raw_path:
                pbar.update(1)
                continue

            counter += 1
            img_id = f"{mode}_{counter:07d}.jpg"

            s1_img = os.path.join(S1_TRAIN_IMG, img_id)
            s1_lab = os.path.join(S1_TRAIN_LAB, img_id.replace(".jpg", ".json"))

            s2_img = os.path.join(S2_TRAIN_IMG, img_id)
            s2_lab = os.path.join(S2_TRAIN_LAB, img_id.replace(".jpg", ".json"))

            if os.path.exists(s1_img):
                pbar.update(1)
                continue

            resize(raw_path, s1_img)
            resize(raw_path, s2_img)

            with open(s1_lab, "w", encoding="utf-8") as lf:
                json.dump({
                    "image": img_id,
                    "exercise": ex,
                    "source": source_body
                }, lf, ensure_ascii=False, indent=2)

            with open(s2_lab, "w", encoding="utf-8") as lf:
                json.dump({
                    "image": img_id,
                    "exercise": ex,
                    "pose": pose,
                    "conditions": cond_dict,
                    "keypoints": v.get("pts", {}),
                    "active": v.get("active", "Yes"),
                    "source": source_body
                }, lf, ensure_ascii=False, indent=2)

            pbar.update(1)

    print(f"✔ {mode} 완료 (누적): {counter:,}개")


# ==========================================================
# 실행 (TRAIN ONLY)
# ==========================================================
train_jsons = list_json_files(TRAIN_LABEL_BASE)

total_frames = 0
for j in train_jsons:
    with open(j, "r", encoding="utf-8") as f:
        total_frames += len(json.load(f)["frames"])

print("🚀 전처리 시작 (TRAIN ONLY)...\n")

with tqdm(total=total_frames, desc="전체 전처리", unit="frame") as pbar:
    parse(train_jsons, TRAIN_RAW_BASE, "train", pbar)

print("\n🎉 전체 완료!")
