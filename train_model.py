import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader

# ==============================
# PATHS
# ==============================
TRAIN_PATH = r"C:\Calorie AI app\dataset\train"
VAL_PATH   = r"C:\Calorie AI app\dataset\val"
TEST_PATH  = r"C:\Calorie AI app\dataset\test"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", DEVICE)

# ==============================
# TRANSFORMS (AUGMENTATION)
# ==============================

train_transform = transforms.Compose([
    transforms.Resize((256,256)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.RandomResizedCrop(224, scale=(0.8,1.0)),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
])

val_transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
])

# ==============================
# DATASETS
# ==============================

train_data = datasets.ImageFolder(TRAIN_PATH, transform=train_transform)
val_data   = datasets.ImageFolder(VAL_PATH, transform=val_transform)
test_data  = datasets.ImageFolder(TEST_PATH, transform=val_transform)

train_loader = DataLoader(train_data, batch_size=8, shuffle=True)
val_loader   = DataLoader(val_data, batch_size=8)
test_loader  = DataLoader(test_data, batch_size=8)

classes = train_data.classes
num_classes = len(classes)

print("Classes:", classes)
print("Train size:", len(train_data))
print("Val size:", len(val_data))
print("Test size:", len(test_data))

# ==============================
# MODEL (TRANSFER LEARNING)
# ==============================

model = models.mobilenet_v2(weights="DEFAULT")

# freeze base layers
for param in model.parameters():
    param.requires_grad = False

# replace classifier
model.classifier[1] = nn.Linear(model.last_channel, num_classes)
model = model.to(DEVICE)

# ==============================
# LOSS + OPTIMIZER
# ==============================

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.classifier.parameters(), lr=0.001)

# ==============================
# TRAIN LOOP
# ==============================

EPOCHS = 8

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for images, labels in train_loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

        _, preds = torch.max(outputs, 1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

    acc = 100 * correct / total
    print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss:.3f} | Train Acc: {acc:.2f}%")

# ==============================
# SAVE MODEL
# ==============================

torch.save(model.state_dict(), "food_model.pth")
print("\nModel saved → food_model.pth")
