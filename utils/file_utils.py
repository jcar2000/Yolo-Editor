import os
import yaml
from tkinter import messagebox

def load_yaml(yaml_path):
    with open(yaml_path, 'r') as file:
        data = yaml.safe_load(file)
    return data['names']

def load_images_and_labels(images_dir, labels_dir):
    if not os.path.exists(images_dir) or not os.path.exists(labels_dir):
        messagebox.showerror("Error", "Images or Labels directory not found.")
        return [], {}, {}

    images = [f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    image_labels = {}
    for image in images:
        label_path = os.path.join(labels_dir, os.path.splitext(image)[0] + '.txt')
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                image_labels[image] = [line.strip() for line in f.readlines()]
        else:
            image_labels[image] = []

    return images, image_labels

def truncate_name(name, max_length):
    if len(name) > max_length:
        return name[:max_length-3] + '...'
    return name

def delete_files(image_paths, label_paths):
    for img_path, label_path in zip(image_paths, label_paths):
        if os.path.exists(img_path):
            os.remove(img_path)
        if os.path.exists(label_path):
            os.remove(label_path)

def rename_file(dataset_dir, old_image_name, new_image_name, image_labels):
    old_img_path = os.path.join(dataset_dir, 'images', old_image_name)
    new_img_path = os.path.join(dataset_dir, 'images', new_image_name)
    os.rename(old_img_path, new_img_path)

    old_label_path = os.path.join(dataset_dir, 'labels', os.path.splitext(old_image_name)[0] + '.txt')
    new_label_path = os.path.join(dataset_dir, 'labels', os.path.splitext(new_image_name)[0] + '.txt')
    os.rename(old_label_path, new_label_path)

    image_labels[new_image_name] = image_labels.pop(old_image_name)

def rename_class_in_labels(dataset_dir, class_index, new_class_name, classes):
    labels_dir = os.path.join(dataset_dir, 'labels')
    for label_file in os.listdir(labels_dir):
        if label_file.endswith('.txt'):
            label_path = os.path.join(labels_dir, label_file)
            with open(label_path, 'r') as file:
                lines = file.readlines()
            with open(label_path, 'w') as file:
                for line in lines:
                    parts = line.split()
                    if int(parts[0]) == class_index:
                        parts[0] = str(classes.index(new_class_name))
                    file.write(' '.join(parts) + '\n')

def update_yaml(yaml_path, classes):
    with open(yaml_path, 'r') as file:
        data = yaml.safe_load(file)
    data['names'] = classes
    with open(yaml_path, 'w') as file:
        yaml.safe_dump(data, file)