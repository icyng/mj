from ultralytics import YOLO
import os

# os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'

model = YOLO('yolov8n.yaml')
model = YOLO('yolov8n.pt')
model = YOLO('yolov8n.yaml').load('yolov8n.pt')

results = model.train(
    data='../datasets/coco128-20240217.yml', 
    epochs=3, 
    batch=2,
    device='mps'
)

# Evaluate the model's performance on the validation set
results = model.val()
