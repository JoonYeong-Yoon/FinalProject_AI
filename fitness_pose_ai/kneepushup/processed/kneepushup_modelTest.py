"""
============================================================
니푸시업 Model5Cond 테스트 / 평가 / 영상 추론 스크립트
============================================================

- 본 스크립트는 Colab 기준
- YOLOv8 Pose 사용

이 테스트 코드는 로직은 공통이고,
경로와 환경 설정만 Colab/로컬에 맞게 바꿔서 쓰면 됩니다.
"""

# ==========================================================
# 0. 기본 설정
# ==========================================================
import os
import torch
import numpy as np
import pandas as pd
from torch.utils.data import DataLoader

device = "cuda" if torch.cuda.is_available() else "cpu"

ROOT = "/content/stage3_kneepushup"
IMAGE_ROOT = "/content/stage3_model5"
MODEL_PATH = "/content/model5cond_best_kneepushup.pth"


# ==========================================================
# 1. Dataset / Model 로드
# ==========================================================
valid_ds = kneepuPushupDataset(ROOT, IMAGE_ROOT, "valid", transform=valid_tf)
valid_loader = DataLoader(valid_ds, batch_size=16, shuffle=False)

cond_names = valid_ds.cond_names
cond_dim = valid_ds.cond_dim

model = Model5Cond(cond_dim).to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

print("✔ model & validation data ready")


# ==========================================================
# 2. 정확도 계산 함수
# ==========================================================
def exact_match_accuracy(model, loader, threshold=0.5):
    """
    모든 조건을 동시에 맞춘 경우만 정답으로 계산
    (매우 엄격한 지표)
    """
    correct, total = 0, 0
    with torch.no_grad():
        for img, seq, cond, label in loader:
            img, seq, cond, label = (
                img.to(device),
                seq.to(device),
                cond.to(device),
                label.to(device),
            )
            pred = model(img, seq, cond)
            pred_bin = (pred >= threshold).float()
            correct += (pred_bin == label).all(dim=1).sum().item()
            total += label.size(0)
    return correct / total


def condition_accuracy(model, loader, threshold=0.5):
    """
    조건별 독립 accuracy 계산
    """
    correct = np.zeros(cond_dim)
    total = np.zeros(cond_dim)

    with torch.no_grad():
        for img, seq, cond, label in loader:
            img, seq, cond, label = (
                img.to(device),
                seq.to(device),
                cond.to(device),
                label.to(device),
            )
            pred = model(img, seq, cond)
            pred_bin = (pred >= threshold).float()
            correct += (pred_bin == label).sum(dim=0).cpu().numpy()
            total += label.size(0)

    return correct / total


# ==========================================================
# 3. 정확도 계산 및 CSV 저장
# ==========================================================
exact_acc = exact_match_accuracy(model, valid_loader)
cond_acc = condition_accuracy(model, valid_loader)

rows = []
for name, acc in zip(cond_names, cond_acc):
    rows.append({"Metric": f"Condition Accuracy - {name}", "Value": round(float(acc), 3)})

rows.append({"Metric": "Model Exact Match Accuracy", "Value": round(float(exact_acc), 3)})

df_result = pd.DataFrame(rows)
df_result.to_csv("/content/kneepushup_accuracy_summary.csv", index=False)

print(df_result)


# ==========================================================
# 4. YOLO Pose + 시각화 설정
# ==========================================================
!pip install ultralytics
!apt-get -y install fonts-nanum

from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import cv2
from torchvision import transforms

pose_model = YOLO("yolov8n-pose.pt")

tf = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((256,256)),
    transforms.ToTensor()
])

# COCO keypoint index 기준 관절 매핑
COND_JOINT_MAP = {
    0: [5,7,9,6,8,10],     # 팔꿈치/팔
    1: [5,6,11,12],        # 몸통 정렬
    2: [9,10],             # 손 위치
    3: [11,12,13,14],      # 깊이
    4: list(range(17)),    # 전체 안정성
}

def score_to_color(s, th=0.5):
    return (0,255,0) if s >= th else (0,0,255)

FONT_PATH = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
FONT = ImageFont.truetype(FONT_PATH, 24)

def put_korean_text(frame, text, pos, color):
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    draw.text(pos, text, font=FONT, fill=(color[2], color[1], color[0]))
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


# ==========================================================
# 5. 영상 추론 함수
# ==========================================================
def run_kneepushup_video(video_path, out_video_path, model, cond_names, SEQ=16):
    """
    - 슬라이딩 윈도우 기반 추론
    - 프레임별 관절 색상 + 조건 점수 시각화
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    writer = cv2.VideoWriter(out_video_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W,H))

    frames, keypoints = [], []

    # --- keypoint 추출 ---
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frames.append(frame)
        res = pose_model(frame, verbose=False)[0]

        if res.keypoints is None or res.keypoints.xy is None or res.keypoints.xy.shape[0] == 0:
            keypoints.append(None)
        else:
            xy = res.keypoints.xy[0].cpu().numpy().reshape(-1)
            if xy.shape[0] < 48:
                xy = np.concatenate([xy, np.zeros(48 - xy.shape[0])])
            keypoints.append(xy)

    cap.release()

    # --- 추론 + 시각화 ---
    for i in range(len(frames)):
        frame = frames[i].copy()

        if i >= SEQ and keypoints[i] is not None:
            seq = torch.tensor(
                [keypoints[j] if keypoints[j] is not None else np.zeros(48)
                 for j in range(i-SEQ+1, i+1)],
                dtype=torch.float32
            ).unsqueeze(0).to(device)

            img_in = tf(frame).unsqueeze(0).to(device)

            # inference 시 조건 벡터는 unknown → ones 사용
            cond_vec = torch.ones((1, cond_dim), device=device)

            with torch.no_grad():
                scores = model(img_in, seq, cond_vec)[0].cpu().numpy()

            joint_colors = {}
            for c_idx, joints in COND_JOINT_MAP.items():
                for j in joints:
                    joint_colors[j] = score_to_color(scores[c_idx])

            pts = keypoints[i].reshape(-1,2).astype(int)
            for j,(x,y) in enumerate(pts):
                cv2.circle(frame, (x,y), 4, joint_colors.get(j,(200,200,200)), -1)

            y0 = 30
            for name, s in zip(cond_names, scores):
                frame = put_korean_text(frame, f"{name}: {s:.2f}", (20,y0), score_to_color(s))
                y0 += 28

        writer.write(frame)

    writer.release()
    print("✔ output saved:", out_video_path)


# ==========================================================
# 6. 실행 예시
# ==========================================================
run_kneepushup_video(
    video_path="/content/니푸쉬업.mp4",   # 타 운동 테스트 예시
    out_video_path="/content/output_kneepushup.mp4",
    model=model,
    cond_names=cond_names
)
