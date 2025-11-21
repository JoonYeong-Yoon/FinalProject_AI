import os, json
from tqdm import tqdm

TRAIN_LABEL_BASE = r"D:\013.피트니스자세\1.Training\라벨링데이터\맨몸운동_Labeling_new_220128"

def list_json_files(base_dir):
    files = []
    for root, _, fs in os.walk(base_dir):
        for f in fs:
            if f.endswith(".json"):
                files.append(os.path.join(root, f))
    return files

jsons = list_json_files(TRAIN_LABEL_BASE)
print("JSON 개수:", len(jsons))

total_frames = 0
for jp in tqdm(jsons):
    with open(jp, "r", encoding="utf-8") as f:
        total_frames += len(json.load(f)["frames"])

print("전체 frame 수 =", total_frames)
