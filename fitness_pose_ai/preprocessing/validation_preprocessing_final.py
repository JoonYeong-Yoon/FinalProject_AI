import os
import json
from tqdm import tqdm
from PIL import Image

# ============================================
# 0. Validation 경로
# ============================================
VALID_LABEL_DIR = r"D:\013.피트니스자세\2.Validation\라벨링데이터\body_01"
VALID_RAW_BASE  = r"D:\013.피트니스자세\2.Validation\원시데이터\valid_body_data"

OUT_BASE = r"D:\fitness_dataset"

S1_VALID_IMG = os.path.join(OUT_BASE, "stage1_classification", "valid", "images")
S1_VALID_LAB = os.path.join(OUT_BASE, "stage1_classification", "valid", "labels")
S2_VALID_IMG = os.path.join(OUT_BASE, "stage2_pose_correction", "valid", "images")
S2_VALID_LAB = os.path.join(OUT_BASE, "stage2_pose_correction", "valid", "labels")

for d in [S1_VALID_IMG, S1_VALID_LAB, S2_VALID_IMG, S2_VALID_LAB]:
    os.makedirs(d, exist_ok=True)


# ============================================
# JSON 수집
# ============================================
def list_json_files(base_dir):
    out = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".json"):
                out.append(os.path.join(root, f))
    return out


valid_jsons = list_json_files(VALID_LABEL_DIR)
print("VALID JSON 개수:", len(valid_jsons))


# ============================================
# RAW 이미지 경로 찾기
# ============================================
def resolve_valid_raw_path(img_key):
    # img_key 예: Day32_201104_F/1/A/473-1-2-21-Z56_A/000001.jpg
    raw_path = os.path.join(VALID_RAW_BASE, img_key.replace("/", "\\"))
    return raw_path if os.path.exists(raw_path) else None


# ============================================
# 이미지 리사이즈
# ============================================
def resize(src, dst, size=(256, 256)):
    try:
        img = Image.open(src).resize(size)
        img.save(dst)
        return True
    except:
        return False


# ============================================
# Validation 파서
# ============================================
def parse_valid(json_list):

    # 번호 이어붙이기
    counter = len(os.listdir(S1_VALID_IMG))

    # 총 프레임 수
    total = 0
    for jp in json_list:
        with open(jp, "r", encoding="utf-8") as f:
            total += len(json.load(f)["frames"])

    print("총 Validation 프레임 수:", total)

    with tqdm(total=total, desc="VALID Processing", unit="frame") as pbar:

        for jp in json_list:

            with open(jp, "r", encoding="utf-8") as f:
                data = json.load(f)

            frames = data.get("frames", [])
            type_info = data.get("type_info", {})

            exercise = type_info.get("exercise", "unknown")
            pose     = type_info.get("pose", "unknown")

            cond_raw = type_info.get("conditions", [])
            conditions = {c["condition"]: c["value"] for c in cond_raw}

            source_folder = os.path.basename(os.path.dirname(jp))  # Day32_201104_F

            for fr in frames:
                v = fr.get("view1")
                if not v:
                    pbar.update(1)
                    continue

                img_key = v.get("img_key")
                if not img_key:
                    pbar.update(1)
                    continue

                raw_path = resolve_valid_raw_path(img_key)
                if not raw_path:
                    pbar.update(1)
                    continue

                counter += 1
                img_id = f"valid_{counter:07d}.jpg"

                # 저장 경로
                s1_img = os.path.join(S1_VALID_IMG, img_id)
                s1_lab = os.path.join(S1_VALID_LAB, img_id.replace(".jpg", ".json"))
                s2_img = os.path.join(S2_VALID_IMG, img_id)
                s2_lab = os.path.join(S2_VALID_LAB, img_id.replace(".jpg", ".json"))

                # 이미지 저장
                resize(raw_path, s1_img)
                resize(raw_path, s2_img)

                # Stage1 라벨
                with open(s1_lab, "w", encoding="utf-8") as lf:
                    json.dump({
                        "image": img_id,
                        "exercise": exercise,
                        "source": source_folder
                    }, lf, ensure_ascii=False, indent=2)

                # Stage2 라벨
                with open(s2_lab, "w", encoding="utf-8") as lf:
                    json.dump({
                        "image": img_id,
                        "exercise": exercise,
                        "pose": pose,
                        "conditions": conditions,
                        "keypoints": v.get("pts", {}),
                        "active": v.get("active", "Yes"),
                        "source": source_folder
                    }, lf, ensure_ascii=False, indent=2)

                pbar.update(1)

    print(f"✔ Validation 처리 완료 – 생성된 이미지: {counter}")


# =====================================================
# 실행
# =====================================================
parse_valid(valid_jsons)
print("\n🎉 VALIDATION 전처리 완료 🎉")
