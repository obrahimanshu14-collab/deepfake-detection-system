"""Reusable inference logic for the audio deepfake detector."""
import albumentations as A
from albumentations.pytorch import ToTensorV2
import torch

from app.ml_model.audio_utils import audio_to_spectrogram_image
from app.ml_model.inference import classify_probability

AUDIO_IMG_SIZE = 160

eval_transform = A.Compose([
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2(),
])


def predict_audio(filepath: str, model, device: str = "cpu") -> dict:
    spec_image = audio_to_spectrogram_image(filepath, img_size=AUDIO_IMG_SIZE)
    tensor = eval_transform(image=spec_image)["image"].unsqueeze(0).to(device)
    with torch.no_grad():
        logit = model(tensor)
        fake_prob = torch.sigmoid(logit).item()
    return {
        "label": classify_probability(fake_prob),
        "raw_fake_probability": round(fake_prob, 4),
        "real_percent": round((1 - fake_prob) * 100, 1),
        "fake_percent": round(fake_prob * 100, 1),
    }