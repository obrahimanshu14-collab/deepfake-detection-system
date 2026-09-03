"""
Normalization pipeline applied to every image before it goes into the model.
Must be identical at training time and inference time.
"""
import albumentations as A
from albumentations.pytorch import ToTensorV2

IMG_SIZE = 160

# These specific mean/std values match ImageNet's statistics, required
# because our backbone (MobileNetV2) was pretrained on ImageNet.
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

eval_transform = A.Compose([
    A.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ToTensorV2(),
])