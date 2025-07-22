from ultralytics import YOLO
import os

os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'
model = YOLO('yolov12m.pt')

results = model.train(
    data='dataset/coco128.yml', 
    epochs=150,
    batch=32,
    device='cpu'
)

results = model.val()
