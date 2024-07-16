from ultralytics import YOLO

model = YOLO('yolov8n.yaml')

model = YOLO('runs/detect/train8/weights/best.pt')

# Predict the model
model.predict('009.jpg', save=True)
