import torch
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.transforms import ToTensor
from PIL import Image
import numpy as np
import cv2

# Load pretrained model
model = fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()

def detect_poles(image_path):
    image = Image.open(image_path).convert("RGB")
    transform = ToTensor()
    img_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        predictions = model(img_tensor)

    return predictions
