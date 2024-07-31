import numpy as np
import tkinter as tk
from utils.file_utils import truncate_name

class StatsManager:
    def __init__(self, manager):
        self.manager = manager

    def update_stats(self):
        total_images = len(self.manager.images)
        total_bboxes = sum(len(labels) for labels in self.manager.image_labels.values())
        counts_per_class = {cls: 0 for cls in self.manager.classes}
        
        bboxes_per_image = [len(labels) for labels in self.manager.image_labels.values()]
        average_bboxes_per_image = np.mean(bboxes_per_image)
        std_bboxes_per_image = np.std(bboxes_per_image)
        no_bboxes_images = sum(1 for count in bboxes_per_image if count == 0)
        percentage_no_bboxes_images = (no_bboxes_images / total_images) * 100 if total_images > 0 else 0

        for labels in self.manager.image_labels.values():
            for label in labels:
                class_id = int(label.split()[0])
                counts_per_class[self.manager.classes[class_id]] += 1

        sorted_counts = sorted(counts_per_class.items(), key=lambda x: x[1], reverse=True)

        # Clear the text widget
        self.manager.stats_text.delete(1.0, tk.END)

        # Add the header
        self.manager.stats_text.insert(tk.END, f"Total Images: {total_images}\n")
        self.manager.stats_text.insert(tk.END, f"Total BBoxes: {total_bboxes}\n")
        self.manager.stats_text.insert(tk.END, f"Average BBoxes per Image: {average_bboxes_per_image:.2f}\n")
        self.manager.stats_text.insert(tk.END, f"Std Dev of BBoxes per Image: {std_bboxes_per_image:.2f}\n")
        self.manager.stats_text.insert(tk.END, f"Percentage of Images with No BBoxes: {percentage_no_bboxes_images:.2f}%\n")
        self.manager.stats_text.insert(tk.END, f"Number of Classes: {len(self.manager.classes)}\n\n")

        self.manager.stats_text.insert(tk.END, "\nBBoxes per Class:\n\n")
        for cls, count in sorted_counts:
            percentage = (count / total_bboxes) * 100 if total_bboxes > 0 else 0
            truncated_name = truncate_name(cls, 30)
            self.manager.stats_text.insert(tk.END, f"{truncated_name:<30} : {count:>5} ({percentage:>6.2f}%)\n")
        
        self.manager.stats_text.config(state=tk.DISABLED)
        self.manager.stats = counts_per_class  # Store the stats for the graph