from ultralytics import YOLO
import os

folder_path = '../datasets/test/images/'
file_names = os.listdir(folder_path)
file_pathes = [folder_path+f for f in file_names]

model = YOLO('runs/detect/train3/weights/best.pt')
results = model(file_pathes)
class_names = model.names

with open("res/res.txt","w") as o:
    for result,name in zip(results,file_names):
        boxes = result.boxes
        print(f"# result : {name}",file=o)
        for box in boxes:
            class_id = int(box.cls[0])
            confidence = box.conf[0]
            class_name = class_names[class_id]
            print(f"Class: {class_name}, Confidence: {confidence:.3f}",file=o)
        print('\n',file=o)
            
        result.save(filename=f"res/r{name}")  # save to disk