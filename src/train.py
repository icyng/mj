from ultralytics import YOLO
import os

# os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'
model = YOLO('yolov8n.pt')

results = model.train(
    data='../datasets/coco128-20240217.yml', 
    epochs=100, 
    batch=5,
    # device='mps',
    # device=[0,1]
)

results = model.val()
