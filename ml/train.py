from ultralytics import YOLO
import os

def train_model():
    model = YOLO('yolov8n.pt')

    
    print("Starting training...")
    results = model.train(
        data='/app/ml/data.yaml',
        epochs=20, 
        imgsz=640, 
        batch=8, 
        optimizer='Adam',
        project='/app/ml/runs', 
        name='pcb_defect_v1'
    )
    
    success = model.export(format='torchscript')
    
    best_model_path = '/app/ml/runs/pcb_defect_v1/weights/best.pt'
    target_path = '/app/ml/yolov8_model/best.pt'
    
    if os.path.exists(best_model_path):
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        os.rename(best_model_path, target_path)
        print(f"Model saved to {target_path}")
    else:
        print("Training finished but best.pt not found (maybe run locally?)")

if __name__ == '__main__':
    train_model()
