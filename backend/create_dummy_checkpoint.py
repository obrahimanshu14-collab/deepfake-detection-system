"""
One-time script: creates an untrained (random-weight) model checkpoint,
purely to test the end-to-end pipeline (upload -> model -> database)
before real training is done. Replace this checkpoint later with the
actual trained weights.
"""
import os
import torch
from app.ml_model.model import DeepfakeDetector

os.makedirs("models", exist_ok=True)

model = DeepfakeDetector(pretrained=False)
torch.save(model.state_dict(), "models/best_model.pt")

print("Dummy checkpoint created at: models/best_model.pt")
print("Remember: this model has NOT been trained, predictions will be meaningless")
print("until you run real training later.")