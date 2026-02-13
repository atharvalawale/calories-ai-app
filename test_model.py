import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# ===== IMAGE PATH =====
IMAGE_PATH = r"C:\Calorie AI app\dataset\test\pizza\pizza6.jpg"   # change later

# ===== CLASSES =====
classes = ['dal','egg','paneer','pizza','rice','roti','salad']

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ===== TRANSFORM =====
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
])

# ===== LOAD MODEL =====
model = models.mobilenet_v2(weights=None)
model.classifier[1] = nn.Linear(model.last_channel, len(classes))
model.load_state_dict(torch.load("food_model.pth", map_location=DEVICE))
model = model.to(DEVICE)
model.eval()

# ===== LOAD IMAGE =====
img = Image.open(IMAGE_PATH).convert("RGB")
img = transform(img).unsqueeze(0).to(DEVICE)

# ===== PREDICT =====
with torch.no_grad():
    outputs = model(img)
    _, pred = torch.max(outputs,1)

print("Predicted:", classes[pred.item()])
