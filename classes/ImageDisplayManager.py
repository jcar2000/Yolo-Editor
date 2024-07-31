import os
from PIL import Image, ImageTk, ImageDraw
from utils.image_utils import draw_bbox, convert_polygon_to_bbox

class ImageDisplayManager:
    def __init__(self, manager):
        self.manager = manager

    def display_class_images(self, event):
        selected_class_index = self.manager.class_listbox.curselection()
        if not selected_class_index:
            return
        selected_class = selected_class_index[0]
        self.update_image_listbox(selected_class)

    def update_image_listbox(self, selected_class):
        self.manager.image_listbox.delete(*self.manager.image_listbox.get_children())
        self.manager.filtered_images = [image for image, labels in self.manager.image_labels.items() if any(int(label.split()[0]) == selected_class for label in labels)]
        self.manager.filtered_images.sort(reverse=not self.manager.sort_ascending)
        self.display_filtered_images()

    def display_filtered_images(self):
        filter_text = self.manager.filter_entry.get().lower()
        self.manager.image_listbox.delete(*self.manager.image_listbox.get_children())
        for image in self.manager.filtered_images:
            if filter_text in image.lower():
                self.manager.image_listbox.insert('', 'end', image, text=image, image=self.manager.image_icons[image])

    def display_image_with_bboxes(self, event):
        selected_item = self.manager.image_listbox.selection()
        if not selected_item:
            return
        image_name = self.manager.image_listbox.item(selected_item, 'text')
        img_path = os.path.join(self.manager.dataset_dir, 'images', image_name)
        img = Image.open(img_path)

        draw = ImageDraw.Draw(img)
        labels = self.manager.image_labels[image_name]
        for label in labels:
            parts = label.split()
            if len(parts) > 5:  # Handle polygon segments
                class_id, polygon = int(parts[0]), list(map(float, parts[1:]))
                bbox = convert_polygon_to_bbox(polygon)
            elif len(parts) == 5:  # Handle normal bounding boxes
                class_id = int(parts[0])
                bbox = list(map(float, parts[1:]))
            else:
                continue  # Skip invalid labels

            draw_bbox(draw, bbox, img.size, class_id, self.manager.classes[class_id])

        img = img.resize((400, 400), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        self.manager.img_label.config(image=img)
        self.manager.img_label.image = img