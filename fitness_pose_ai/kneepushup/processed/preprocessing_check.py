import json

j = r"D:\013.피트니스자세\1.Training\라벨링데이터\맨몸운동_Labeling_new_220128\맨몸운동_01\Day05_200925_F\D05-1-001.json"
data = json.load(open(j, "r", encoding="utf-8"))

frame = data["frames"][0]["view1"]
img_key = frame["img_key"]

print("원본 img_key =", repr(img_key))         # 숨겨진 문자 확인용
print("split =", img_key.split("/"))
print("첫 요소 repr =", repr(img_key.split("/")[0]))

print("경로 join 테스트:")
import os
raw_root = r"D:\013.피트니스자세\1.Training\원시데이터"
raw_folder = "body_01"
img_parts = img_key.split("/")
test = os.path.join(raw_root, raw_folder, *img_parts)
print(test)

import os

root = r"D:\013.피트니스자세\1.Training\원시데이터\body_01"

for name in os.listdir(root):
    print(name)

import os

path = r"D:\013.피트니스자세\1.Training\원시데이터\body_01\Day05_200925_F"
for name in os.listdir(path):
    print(name)

import os

target = "001-1-1-01-Z17_A-0000001.jpg"
root = r"D:\013.피트니스자세\1.Training\원시데이터\body_01"

found = []

for r, _, files in os.walk(root):
    if target in files:
        found.append(os.path.join(r, target))

print("발견된 경로 수:", len(found))
for f in found:
    print(f)



import os

json_path = r"D:\013.피트니스자세\1.Training\라벨링데이터\맨몸운동_Labeling_new_220128\맨몸운동_01\Day05_200925_F\D05-1-001.json"

print("split('|'):", json_path.split("|"))
print("split('/'):", json_path.split("/"))
print("split('\\\\'):", json_path.split("\\"))
print("split(os.sep):", json_path.split(os.sep))

label_folder = json_path.split("\\")[-3]
print("label_folder:", label_folder)
