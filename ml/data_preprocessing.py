import cv2
import os
import json
import numpy as np
from pathlib import Path
import shutil
import random
import yaml

DATA_SOURCE = '/app/ml/data'
BASE_OUTPUT = '/app/ml/dataset'
IMAGES_DIR = os.path.join(BASE_OUTPUT, 'images')
LABELS_DIR = os.path.join(BASE_OUTPUT, 'labels')

for split in ['train', 'val']:
    os.makedirs(os.path.join(IMAGES_DIR, split), exist_ok=True)
    os.makedirs(os.path.join(LABELS_DIR, split), exist_ok=True)

def find_images(root_dir):
    image_map = {}
    print(f"Scanning for images in {root_dir}...")
    exts = {'.jpg', '.jpeg', '.png', '.bmp'}
    for path in Path(root_dir).rglob('*'):
        if path.suffix.lower() in exts:
            image_map[path.stem] = str(path)
    print(f"Found {len(image_map)} images.")
    return image_map

def json_to_yolo(json_path, classes, image_map):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    base_name = os.path.splitext(os.path.basename(json_path))[0]
    
    if base_name in image_map:
        image_path = image_map[base_name]
    else:
        image_name_in_json = data.get('imagePath', '')
        potential_path = os.path.join(os.path.dirname(json_path), image_name_in_json)
        if os.path.exists(potential_path):
             image_path = potential_path
        else:
            print(f"Image not found for {json_path} (basename: {base_name})")
            return None, None

    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not read image {image_path}")
        return None, None
        
    height, width, _ = img.shape
    
    yolo_lines = []
    
    for shape in data['shapes']:
        label = shape['label']
        if label not in classes:
            classes.append(label)
        
        class_id = classes.index(label)
        points = np.array(shape['points'])
        
        x_min = np.min(points[:, 0])
        x_max = np.max(points[:, 0])
        y_min = np.min(points[:, 1])
        y_max = np.max(points[:, 1])
        
        x_center = (x_min + x_max) / 2 / width
        y_center = (y_min + y_max) / 2 / height
        w = (x_max - x_min) / width
        h = (y_max - y_min) / height
        
        x_center = max(0, min(1, x_center))
        y_center = max(0, min(1, y_center))
        w = max(0, min(1, w))
        h = max(0, min(1, h))
        
        yolo_lines.append(f"{class_id} {x_center} {y_center} {w} {h}")
        
    return image_path, yolo_lines

def prepare_dataset():
    classes = ['exc_solder', 'good', 'no_good', 'poor_solder', 'spike']
    json_files = list(Path(DATA_SOURCE).rglob('*.json'))
    
    if not json_files:
        print(f"No JSON files found in {DATA_SOURCE}")
        return
        
    image_map = find_images(DATA_SOURCE)

    random.shuffle(json_files)
    split_idx = int(len(json_files) * 0.8)
    train_files = json_files[:split_idx]
    val_files = json_files[split_idx:]
    
    print(f"Found {len(json_files)} JSON files. Split: {len(train_files)} train, {len(val_files)} val")
    
    def process_files(files, split):
        count = 0
        for json_file in files:
            image_src, yolo_lines = json_to_yolo(str(json_file), classes, image_map)
            
            if image_src:
                base_name = os.path.splitext(os.path.basename(json_file))[0]
                
                image_dst = os.path.join(IMAGES_DIR, split, os.path.basename(image_src))
                shutil.copy(image_src, image_dst)
                
                label_dst = os.path.join(LABELS_DIR, split, base_name + '.txt')
                with open(label_dst, 'w') as f:
                    f.write('\n'.join(yolo_lines))
                count += 1
        print(f"Processed {count} files for {split}")

    print("Processing training set...")
    process_files(train_files, 'train')
    print("Processing validation set...")
    process_files(val_files, 'val')
    
    yaml_content = {
        'path': BASE_OUTPUT,
        'train': 'images/train',
        'val': 'images/val',
        'names': {i: name for i, name in enumerate(classes)}
    }
    
    with open('/app/ml/data.yaml', 'w') as f:
        yaml.dump(yaml_content, f)
        
    print("Dataset preparation complete.")
    print(f"Classes: {classes}")
    print(f"Data YAML saved to /app/ml/data.yaml")

if __name__ == "__main__":
    if not os.path.exists(DATA_SOURCE):
        print(f"Data source {DATA_SOURCE} does not exist. Please mount your dataset there.")
    else:
        prepare_dataset()
