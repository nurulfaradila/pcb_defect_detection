from ultralytics import YOLO
import os

def evaluate_model():
    model_path = '/app/ml/yolov8_model/best.pt'
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}, using yolov8n.pt")
        model_path = 'yolov8n.pt'

    model = YOLO(model_path)

    metrics = model.val(data='/app/ml/data.yaml')
    
    print(f"mAP50: {metrics.box.map50}")
    print(f"mAP50-95: {metrics.box.map}")
    print(f"Precision: {metrics.box.mp}")
    print(f"Recall: {metrics.box.mr}")

if __name__ == '__main__':
    evaluate_model()
