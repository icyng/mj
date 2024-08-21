from ultralytics import YOLO

name = "3198.jpg"

model = YOLO('runs/detect/train3/weights/best.pt')
results = model([f"../datasets/test/images/{name}"])
class_names = model.names

for result in results:
    boxes = result.boxes
    print("\n結果 : ")
    for box in boxes:
        class_id = int(box.cls[0])
        confidence = box.conf[0]
        class_name = class_names[class_id]
        print(f"Class: {class_name}, Confidence: {confidence:.3f}")
        
    result.save(filename=f"res/{name}")  # save to disk