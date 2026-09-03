"""PyTorch Dataset and augmentation/normalization transform pipelines."""
import sys
from pathlib import Path

import albumentations as A
import cv2
import pandas as pd
import torch
from albumentations.pytorch import ToTensorV2
from torch.utils.data import Dataset

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training import config
from app.ml_model.face_utils import load_and_align

train_transform = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.3, brightness_limit=0.15, contrast_limit=0.15),
    A.Rotate(limit=10, p=0.3, border_mode=cv2.BORDER_REFLECT_101),
    A.GaussNoise(std_range=(0.02, 0.08), p=0.2),
    A.ImageCompression(quality_range=(70, 100), p=0.3),
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2(),
])

eval_transform = A.Compose([
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2(),
])


class FaceDataset(Dataset):
    def __init__(self, dataframe: pd.DataFrame, transform, img_size: int = config.IMG_SIZE):
        self.df = dataframe.reset_index(drop=True)
        self.transform = transform
        self.img_size = img_size

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        face = load_and_align(row["filepath"], output_size=self.img_size)
        transformed = self.transform(image=face)["image"]
        label = torch.tensor(float(config.LABEL_TO_IDX[row["label"]]))
        return transformed, label