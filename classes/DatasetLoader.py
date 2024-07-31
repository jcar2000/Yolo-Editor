import os
import threading
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from utils.file_utils import load_yaml, load_images_and_labels
from utils.image_utils import create_thumbnail

class DatasetLoader:
    def __init__(self, manager):
        self.manager = manager

    def load_dataset(self):
        self.manager.dataset_dir = filedialog.askdirectory(title="Select Dataset Directory")
        if not self.manager.dataset_dir:
            return
        
        self.manager.progress['value'] = 0
        self.manager.root.update_idletasks()
        
        # Start a new thread to load the dataset
        threading.Thread(target=self.load_dataset_thread).start()

    def load_dataset_thread(self):
        self.load_yaml()
        self.load_images_and_labels_dir()
        self.manager.load_classes()
        self.manager.stats_manager.update_stats()
        self.manager.update_class_listbox() 

    def load_yaml(self):
        yaml_path = os.path.join(self.manager.dataset_dir, 'data.yaml')
        if not os.path.exists(yaml_path):
            messagebox.showerror("Error", "data.yaml file not found in the selected directory.")
            return

        self.manager.classes = load_yaml(yaml_path)

    def load_images_and_labels_dir(self):
        images_dir = os.path.join(self.manager.dataset_dir, 'images')
        labels_dir = os.path.join(self.manager.dataset_dir, 'labels')

        self.manager.images, self.manager.image_labels = load_images_and_labels(images_dir, labels_dir)

        total_images = len(self.manager.images)
        self.manager.image_icons = {}
        for i, image in enumerate(self.manager.images):
            img_path = os.path.join(images_dir, image)
            img = Image.open(img_path)
            img = create_thumbnail(img, size=(40, 40))
            icon = ImageTk.PhotoImage(img)
            self.manager.image_icons[image] = icon
            
            self.manager.progress['value'] = (i + 1) / total_images * 100
            self.manager.root.update_idletasks()