import os
from typing import Optional, cast

import torch
import torch.nn as nn
import torch.nn.functional as F


class InstrumentResNet(nn.Module):
    def __init__(self, num_classes: int = 10) -> None:
        super(InstrumentResNet, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.fc = nn.Linear(32 * 56 * 56, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = x.view(x.size(0), -1)
        return cast(torch.Tensor, self.fc(x))


class InstrumentInference:
    def __init__(self, model_path: Optional[str] = None) -> None:
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = InstrumentResNet().to(self.device)
        if model_path and os.path.exists(model_path):  # Fix missing os import
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

    def predict(self, spectrogram: torch.Tensor) -> int:
        # Fix linear layer mismatch by ensuring input is 224x224
        if spectrogram.shape[-2:] != (224, 224):
            spectrogram = F.interpolate(spectrogram, size=(224, 224))
        with torch.no_grad():
            outputs = self.model(spectrogram.to(self.device))
            _, predicted = torch.max(outputs, 1)
            return int(predicted.item())
