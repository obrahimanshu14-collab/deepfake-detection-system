"""
DeepfakeDetector model: partially-frozen MobileNetV2 backbone + classification head.
"""
import torch
import torch.nn as nn
import torchvision


class DeepfakeDetector(nn.Module):
    """Outputs a single raw logit per image. Apply torch.sigmoid() to get P(FAKE)."""

    def __init__(self, freeze_until_block: int = 14, dropout_p: float = 0.3, pretrained: bool = True):
        super().__init__()

        weights = torchvision.models.MobileNet_V2_Weights.IMAGENET1K_V1 if pretrained else None
        backbone = torchvision.models.mobilenet_v2(weights=weights)

        self.features = backbone.features
        for i, layer in enumerate(self.features):
            requires_grad = i >= freeze_until_block
            for param in layer.parameters():
                param.requires_grad = requires_grad

        self.pool = nn.AdaptiveAvgPool2d(1)

        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(p=dropout_p),
            nn.Linear(1280, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_p),
            nn.Linear(128, 1),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x)
        x = self.head(x)
        return x.squeeze(1)


def load_trained_model(checkpoint_path: str, device: str = "cpu") -> DeepfakeDetector:
    """Reconstruct the architecture and load trained weights for inference."""
    model = DeepfakeDetector(pretrained=False).to(device)
    state_dict = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(state_dict)
    model.eval()
    return model