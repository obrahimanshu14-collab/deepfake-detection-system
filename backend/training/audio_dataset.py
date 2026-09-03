"""PyTorch Dataset for audio deepfake detection: converts each audio
file into a spectrogram image on the fly, then applies the same
normalization pipeline used for the image model (so the pretrained
MobileNetV2 backbone receives inputs in the distribution it expects)."""
import sys
from pathlib import Path

import albumentations as A
import pandas as pd
import torch
from albumentations.pytorch import ToTensorV2
from torch.utils.data import Dataset

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training import config
from app.ml_model.audio_utils import audio_to_spectrogram_image

LABEL_TO_IDX = {"REAL": 0, "FAKE": 1}

train_transform = A.Compose([
    A.HorizontalFlip(p=0.3),  # a mild augmentation; spectrograms aren't
                                # natural images, so we keep augmentation
                                # lighter/more conservative than for faces
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2(),
])

eval_transform = A.Compose([
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2(),
])


class AudioSpectrogramDataset(Dataset):
    def __init__(self, dataframe: pd.DataFrame, transform, img_size: int = 160):
        self.df = dataframe.reset_index(drop=True)
        self.transform = transform
        self.img_size = img_size

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        spec_image = audio_to_spectrogram_image(row["filepath"], img_size=self.img_size)
        transformed = self.transform(image=spec_image)["image"]
        label = torch.tensor(float(LABEL_TO_IDX[row["label"]]))
        return transformed, label