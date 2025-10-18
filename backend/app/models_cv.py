# app/models_cv.py
import torch
import torchvision.transforms as T
from torchvision.models import resnet18, ResNet18_Weights
from PIL import Image

class CVClassifier:
    def __init__(self, labels=None):
        self.labels = labels or ["chair", "table", "sofa", "bed", "storage", "lighting"]
        self.model = resnet18(weights=ResNet18_Weights.DEFAULT)
        self.model.fc = torch.nn.Linear(self.model.fc.in_features, len(self.labels))
        self.model.eval()
        self.tf = T.Compose([
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225]),
        ])

    @torch.no_grad()
    def predict(self, image_path: str) -> str:
        img = Image.open(image_path).convert("RGB")
        x = self.tf(img).unsqueeze(0)
        logits = self.model(x)
        return self.labels[int(logits.argmax(1).item())]
