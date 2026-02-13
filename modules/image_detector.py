import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

CLASSES = ['dal', 'egg', 'paneer', 'pizza', 'rice', 'roti', 'salad']

model = models.mobilenet_v2(weights=None)
model.classifier[1] = nn.Linear(model.last_channel, len(CLASSES))
model.load_state_dict(torch.load("food_model.pth", map_location="cpu"))
model.eval()

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor()
])

def predict_food(image_path):
    img = Image.open(image_path).convert("RGB")
    img = transform(img).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img)
        probs = torch.softmax(outputs, dim=1)
        conf, pred = torch.max(probs, 1)

    return [{
        "food": CLASSES[pred.item()],
        "quantity": 1,
        "unit": "unit",
        "confidence": round(conf.item()*100, 2)
    }]
