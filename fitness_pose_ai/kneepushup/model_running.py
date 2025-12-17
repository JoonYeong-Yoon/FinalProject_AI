# ==========================================================
# 0. 기본 설정
# ==========================================================
import os
import cv2
import torch
import numpy as np
import pandas as pd
from torch.utils.data import DataLoader
from torchvision import transforms
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import torch.nn as nn
import timm

device = "cuda" if torch.cuda.is_available() else "cpu"

# -------------------------
# 로컬 경로
# -------------------------
ROOT = "kneepushup_npzs"
IMAGE_ROOT = "kneepushup_images"
MODEL_PATH = "model_kneepushup.pth"

VIDEO_PATH = "video_kneepushup.mp4"
OUT_VIDEO_PATH = "output_video_kneepushup.mp4"

FONT_PATH = r"C:\Windows\Fonts\NanumGothic.ttf"


# ==========================================================
# 1. Dataset 정의
# ==========================================================
class NipuPushupDataset(torch.utils.data.Dataset):
    def __init__(self, root, image_root, split, transform=None):
        self.root = root
        self.image_root = image_root
        self.split = split
        self.exercise = "니푸쉬업"
        self.transform = transform

        self.dir = os.path.join(root, split, self.exercise)
        self.files = [f for f in os.listdir(self.dir) if f.endswith(".npz")]

        sample = np.load(os.path.join(self.dir, self.files[0]), allow_pickle=True)
        self.cond_names = [c["condition"] for c in sample["type_info"].item()["conditions"]]
        self.cond_dim = len(self.cond_names)

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        data = np.load(os.path.join(self.dir, self.files[idx]), allow_pickle=True)

        img_name = os.path.basename(data["img_keys"][0])
        img_path = os.path.join(
            self.image_root,
            self.split,
            self.exercise,
            img_name
        )


        img = cv2.imread(img_path)
        if img is None:
            raise FileNotFoundError(img_path)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if self.transform:
            img = self.transform(img)

        seq = torch.tensor(data["seq"], dtype=torch.float32)

        conds = data["type_info"].item()["conditions"]
        label = torch.tensor([1.0 if c["value"] else 0.0 for c in conds], dtype=torch.float32)

        cond_vec = label.clone()
        return img, seq, cond_vec, label


# ==========================================================
# 2. Model 정의
# ==========================================================
class Model5Cond(nn.Module):
    def __init__(self, cond_dim):
        super().__init__()

        self.img_encoder = timm.create_model(
            "efficientnet_b0",
            pretrained=False,
            num_classes=0
        )
        img_dim = self.img_encoder.num_features

        self.lstm = nn.LSTM(
            input_size=48,
            hidden_size=256,
            batch_first=True,
            bidirectional=True
        )

        self.cond_fc = nn.Sequential(
            nn.Linear(cond_dim, 32),
            nn.ReLU()
        )

        self.head = nn.Sequential(
            nn.Linear(img_dim + 512 + 32, 256),
            nn.ReLU(),
            nn.Linear(256, cond_dim),
            nn.Sigmoid()
        )

    def forward(self, img, seq, cond):
        img_f = self.img_encoder(img)
        lstm_out, _ = self.lstm(seq)
        seq_f = lstm_out[:, -1]
        cond_f = self.cond_fc(cond)
        x = torch.cat([img_f, seq_f, cond_f], dim=1)
        return self.head(x)


# ==========================================================
# 3. 데이터 / 모델 로드
# ==========================================================
tf = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((256,256)),
    transforms.ToTensor()
])

valid_ds = NipuPushupDataset(ROOT, IMAGE_ROOT, "valid", transform=tf)
valid_loader = DataLoader(valid_ds, batch_size=16, shuffle=False)

cond_names = valid_ds.cond_names
cond_dim = valid_ds.cond_dim

model = Model5Cond(cond_dim).to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

print("✔ model & dataset loaded")


# ==========================================================
# 4. 정확도 계산
# ==========================================================
def exact_match_accuracy(model, loader, th=0.5):
    correct, total = 0, 0
    with torch.no_grad():
        for img, seq, cond, label in loader:
            img, seq, cond, label = img.to(device), seq.to(device), cond.to(device), label.to(device)
            pred = model(img, seq, cond)
            pred_bin = (pred >= th).float()
            correct += (pred_bin == label).all(dim=1).sum().item()
            total += label.size(0)
    return correct / total


def condition_accuracy(model, loader, th=0.5):
    correct = np.zeros(cond_dim)
    total = np.zeros(cond_dim)
    with torch.no_grad():
        for img, seq, cond, label in loader:
            img, seq, cond, label = img.to(device), seq.to(device), cond.to(device), label.to(device)
            pred = model(img, seq, cond)
            pred_bin = (pred >= th).float()
            correct += (pred_bin == label).sum(dim=0).cpu().numpy()
            total += label.size(0)
    return correct / total


exact_acc = exact_match_accuracy(model, valid_loader)
cond_acc = condition_accuracy(model, valid_loader)

print("Exact Match Accuracy:", round(exact_acc, 3))
for n, a in zip(cond_names, cond_acc):
    print(f"{n}: {a:.3f}")


# ==========================================================
# 5. 폰트 로딩 (🔥 수정 핵심)
# ==========================================================
def load_font_safe(font_path, size):
    try:
        with open(font_path, "rb") as f:
            font_bytes = f.read()
        return ImageFont.truetype(BytesIO(font_bytes), size)
    except Exception as e:
        print("⚠ font load failed, fallback:", e)
        return ImageFont.load_default()

FONT = load_font_safe(FONT_PATH, 24)


def put_korean_text(frame, text, pos, color):
    assert frame.dtype == np.uint8
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    draw.text(pos, text, font=FONT, fill=(color[2], color[1], color[0]))
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


# ==========================================================
# 6. 영상 추론 / 시각화
# ==========================================================
pose_model = YOLO("yolov8n-pose.pt")

COND_JOINT_MAP = {
    0: [5,7,9,6,8,10],
    1: [5,6,11,12],
    2: [9,10],
    3: [11,12,13,14],
    4: list(range(17)),
}

def score_to_color(s, th=0.5):
    return (0,255,0) if s >= th else (0,0,255)


def run_nipushup_video(video_path, out_video_path, model, cond_names, SEQ=16):
    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps is None or fps <= 1:
        fps = 30  # 🔥 필수 fallback
    
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # 🔥 Windows 안정 코덱 (재생 100%)
    # 🔥 mp4 + H.264 (Windows / VLC / 브라우저 전부 OK)
    fourcc = cv2.VideoWriter_fourcc(*"avc1")  # H.264
    out_video_path = out_video_path.replace(".avi", ".mp4")
    
    writer = cv2.VideoWriter(out_video_path, fourcc, fps, (W, H))
    if not writer.isOpened():
        raise RuntimeError("VideoWriter failed to open (avc1)")

    if not writer.isOpened():
        raise RuntimeError("VideoWriter failed to open")

    frames, keypoints = [], []

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

    for i in range(len(frames)):
        frame = frames[i].copy()
        if i >= SEQ and keypoints[i] is not None:
            seq = torch.tensor(
                [keypoints[j] if keypoints[j] is not None else np.zeros(48)
                 for j in range(i-SEQ+1, i+1)],
                dtype=torch.float32
            ).unsqueeze(0).to(device)

            img_in = tf(frame).unsqueeze(0).to(device)
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
    print("✔ output video saved:", out_video_path)


# ==========================================================
# 7. 실행
# ==========================================================
run_nipushup_video(
    video_path=VIDEO_PATH,
    out_video_path=OUT_VIDEO_PATH,
    model=model,
    cond_names=cond_names
)
