"""
============================================================
니푸시업(Model5) 조건별 학습 전체 스크립트 (Colab 기준)
============================================================

"""

# ==========================================================
# 1. Google Drive 마운트 및 데이터 압축 해제
# ==========================================================
from google.colab import drive
drive.mount("/content/drive")

import os
import zipfile
import shutil
import numpy as np

ZIP_PATH = "/content/drive/MyDrive/stage3_model5.zip"
ROOT = "/content/stage3_model5"
OUT_ROOT = "/content/stage3_nipushup"
TARGET_EX = "니푸쉬업"
splits = ["train", "valid"]

os.makedirs(ROOT, exist_ok=True)
os.makedirs(OUT_ROOT, exist_ok=True)

with zipfile.ZipFile(ZIP_PATH, "r") as z:
    z.extractall(ROOT)

print("✔ stage3_model5 압축 해제 완료")


# ==========================================================
# 2. 니푸시업 데이터만 분리
# ==========================================================
for split in splits:
    in_dir = os.path.join(ROOT, split)
    out_dir = os.path.join(OUT_ROOT, split, TARGET_EX)
    os.makedirs(out_dir, exist_ok=True)

    for f in os.listdir(in_dir):
        if not f.endswith(".npz"):
            continue

        data = np.load(os.path.join(in_dir, f), allow_pickle=True)
        ex_name = data["type_info"].item()["exercise"]

        if ex_name == TARGET_EX:
            shutil.copy(os.path.join(in_dir, f), os.path.join(out_dir, f))

print("✔ 니푸시업 데이터 분리 완료")

for split in splits:
    d = os.path.join(OUT_ROOT, split, TARGET_EX)
    print(f"{split}: {len(os.listdir(d))} samples")


# ==========================================================
# 3. Dataset 정의
# ==========================================================
import cv2
import torch
from torch.utils.data import Dataset
from torchvision import transforms

train_tf = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((256, 256)),
    transforms.ToTensor()
])

valid_tf = train_tf


class NipuPushupDataset(Dataset):
    """
    니푸시업 조건별 학습용 Dataset
    - img      : (3,256,256)
    - seq      : (16,48)
    - cond_vec : (cond_dim,)  ← 구조 통일용
    - label    : (cond_dim,)
    """
    def __init__(self, root, image_root, split, transform=None):
        self.root = root
        self.image_root = image_root
        self.split = split
        self.exercise = TARGET_EX
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

        # ----- 이미지 -----
        img_key = data["img_keys"][0].replace("\\", "/")
        img_path = os.path.join(self.image_root, self.split, img_key)

        img = cv2.imread(img_path)
        if img is None:
            raise FileNotFoundError(img_path)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if self.transform:
            img = self.transform(img)

        # ----- 키포인트 시퀀스 -----
        seq = torch.tensor(data["seq"], dtype=torch.float32)

        # ----- 조건 라벨 -----
        conds = data["type_info"].item()["conditions"]
        label = torch.tensor(
            [1.0 if c["value"] else 0.0 for c in conds],
            dtype=torch.float32
        )

        # inference 시 구조 동일 유지를 위한 cond_vec
        cond_vec = label.clone()

        return img, seq, cond_vec, label


# ==========================================================
# 4. DataLoader 준비
# ==========================================================
from torch.utils.data import DataLoader

root = OUT_ROOT
image_root = ROOT

train_ds = NipuPushupDataset(root, image_root, "train", transform=train_tf)
print("train samples:", len(train_ds))
print("conditions:", train_ds.cond_names)

train_loader = DataLoader(
    train_ds,
    batch_size=16,
    shuffle=True,
    num_workers=2
)

valid_dir = os.path.join(root, "valid", TARGET_EX)
use_valid = os.path.exists(valid_dir) and len(os.listdir(valid_dir)) > 0

if use_valid:
    valid_ds = NipuPushupDataset(root, image_root, "valid", transform=valid_tf)
    valid_loader = DataLoader(valid_ds, batch_size=16, shuffle=False, num_workers=2)
    print("✔ valid set 사용")
else:
    valid_loader = None
    print("⚠ valid set 없음 → train only")


# ==========================================================
# 5. Model5Cond 정의
# ==========================================================
import torch.nn as nn
import timm

class Model5Cond(nn.Module):
    """
    이미지 + 키포인트 시퀀스 + 조건 벡터 기반
    조건별 점수 예측 모델
    """
    def __init__(self, cond_dim):
        super().__init__()

        self.img_encoder = timm.create_model(
            "efficientnet_b0",
            pretrained=True,
            num_classes=0
        )
        img_dim = self.img_encoder.num_features  # 1280

        self.lstm = nn.LSTM(
            input_size=48,
            hidden_size=256,
            batch_first=True,
            bidirectional=True
        )
        seq_dim = 512

        self.cond_fc = nn.Sequential(
            nn.Linear(cond_dim, 32),
            nn.ReLU()
        )

        self.head = nn.Sequential(
            nn.Linear(img_dim + seq_dim + 32, 256),
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
# 6. 학습 루프
# ==========================================================
from tqdm import tqdm

device = "cuda" if torch.cuda.is_available() else "cpu"

cond_dim = train_ds.cond_dim
model = Model5Cond(cond_dim).to(device)

criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

EPOCHS = 30
best_loss = float("inf")

for epoch in range(EPOCHS):
    model.train()
    train_loss = 0.0

    for img, seq, cond, label in tqdm(train_loader):
        img, seq, cond, label = img.to(device), seq.to(device), cond.to(device), label.to(device)

        optimizer.zero_grad()
        out = model(img, seq, cond)
        loss = criterion(out, label)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()

    train_loss /= len(train_loader)

    if valid_loader:
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for img, seq, cond, label in valid_loader:
                img, seq, cond, label = img.to(device), seq.to(device), cond.to(device), label.to(device)
                val_loss += criterion(model(img, seq, cond), label).item()

        val_loss /= len(valid_loader)
        print(f"[{epoch+1}/{EPOCHS}] Train {train_loss:.4f} | Val {val_loss:.4f}")

        if val_loss < best_loss:
            best_loss = val_loss
            torch.save(model.state_dict(), "/content/model5cond_best_nipushup.pth")
            print("🔥 Best model saved")

    else:
        print(f"[{epoch+1}/{EPOCHS}] Train {train_loss:.4f}")
        if train_loss < best_loss:
            best_loss = train_loss
            torch.save(model.state_dict(), "/content/model5cond_best_nipushup.pth")
            print("🔥 Best model saved (train only)")
