import os
import tkinter as tk
from tkinter import ttk, simpledialog
from tkinter import HORIZONTAL, VERTICAL, PanedWindow
from classes.DatasetLoader import DatasetLoader
from classes.ImageDisplayManager import ImageDisplayManager
from classes.StatsManager import StatsManager
from utils.show_graph import show_class_annotations_graph
from utils.file_utils import delete_files, rename_file, rename_class_in_labels, update_yaml

class YOLODatasetManager:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO Dataset Manager")
        self.dataset_dir = ""
        self.classes = []
        self.images = []
        self.image_labels = {}
        self.stats = {}
        self.image_icons = {}
        self.sort_ascending = True

        self.dataset_loader = DatasetLoader(self)
        self.image_display_manager = ImageDisplayManager(self)
        self.stats_manager = StatsManager(self)

        # Create main paned window
        self.main_paned = PanedWindow(self.root, orient=HORIZONTAL, sashrelief=tk.RAISED)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        # Create left and right frames
        self.left_frame = PanedWindow(self.main_paned, orient=VERTICAL, sashrelief=tk.RAISED)
        self.right_frame = PanedWindow(self.main_paned, orient=VERTICAL, sashrelief=tk.RAISED)

        self.main_paned.add(self.left_frame, minsize=300)
        self.main_paned.add(self.right_frame, minsize=600)

        # Left frame components
        self.load_dataset_btn = tk.Button(self.left_frame, text="Load Dataset", command=self.dataset_loader.load_dataset)
        self.load_dataset_btn.pack(fill=tk.X, padx=5, pady=5)

        self.progress = ttk.Progressbar(self.left_frame, orient=HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, padx=5, pady=5)

        self.class_listbox = tk.Listbox(self.left_frame, selectmode=tk.SINGLE, height=10)
        self.class_listbox.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        self.class_listbox.bind('<<ListboxSelect>>', self.image_display_manager.display_class_images)

        self.filter_frame = tk.Frame(self.left_frame)
        self.filter_frame.pack(fill=tk.X, padx=5, pady=5)

        self.filter_entry = tk.Entry(self.filter_frame)
        self.filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.filter_entry.bind('<KeyRelease>', self.filter_images)

        self.sort_btn = tk.Button(self.filter_frame, text="⇵", command=self.sort_images)
        self.sort_btn.pack(side=tk.RIGHT)

        self.image_list_frame = tk.Frame(self.left_frame)
        self.image_list_frame.pack(fill=tk.BOTH, expand=True)

        # Adjust the row height by setting the style
        style = ttk.Style()
        style.configure("Treeview", rowheight=50)

        self.image_listbox = ttk.Treeview(self.image_list_frame, columns=('Image', 'Checkbox'), show='tree', height=1)
        self.image_listbox.heading('#0', text='Image')
        self.image_listbox.pack(fill=tk.BOTH, expand=True)
        self.image_listbox.bind('<Double-Button-1>', self.image_display_manager.display_image_with_bboxes)

        self.delete_btn = tk.Button(self.left_frame, text="Delete Selected Images", command=self.delete_selected_images)
        self.delete_btn.pack(fill=tk.X, padx=5, pady=5)

        self.rename_image_btn = tk.Button(self.left_frame, text="Rename Selected Image", command=self.rename_image)
        self.rename_image_btn.pack(fill=tk.X, padx=5, pady=5)

        self.rename_class_btn = tk.Button(self.left_frame, text="Rename Selected Class", command=self.rename_class)
        self.rename_class_btn.pack(fill=tk.X, padx=5, pady=5)

        # Right frame components
        self.img_label = tk.Label(self.right_frame)
        self.right_frame.add(self.img_label, height=600)

        self.view_image_btn = tk.Button(self.img_label, text="Image Viewer", command=self.image_display_manager.open_image_viewer)
        self.view_image_btn.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        self.stats_frame = tk.Frame(self.right_frame)
        self.right_frame.add(self.stats_frame)

        self.stats_text = tk.Text(self.stats_frame, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.show_graph_btn = tk.Button(self.right_frame, text="Show Class Annotations Graph", command=self.show_graph)
        self.show_graph_btn.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

    def load_classes(self):
        self.update_class_listbox()

    def update_class_listbox(self):
        self.class_listbox.delete(0, tk.END)
        for cls in self.classes:
            self.class_listbox.insert(tk.END, cls)

    def filter_images(self, event=None):
        self.image_display_manager.display_filtered_images()

    def sort_images(self):
        self.sort_ascending = not self.sort_ascending
        self.image_display_manager.update_image_listbox(self.class_listbox.curselection()[0])

    def delete_selected_images(self):
        selected_items = self.image_listbox.selection()
        image_paths = []
        label_paths = []
        for item in selected_items:
            image_name = self.image_listbox.item(item, 'text')
            img_path = os.path.join(self.dataset_dir, 'images', image_name)
            label_path = os.path.join(self.dataset_dir, 'labels', os.path.splitext(image_name)[0] + '.txt')

            image_paths.append(img_path)
            label_paths.append(label_path)

            # Remove from the list and internal data structures
            self.images.remove(image_name)
            del self.image_labels[image_name]
            del self.image_icons[image_name]
            self.image_listbox.delete(item)

        delete_files(image_paths, label_paths)
        
        self.stats_manager.update_stats()

    def rename_class(self):
        selected_class_index = self.class_listbox.curselection()
        if not selected_class_index:
            return
        old_class_name = self.classes[selected_class_index[0]]
        new_class_name = simpledialog.askstring("Rename Class", f"Enter new name for class '{old_class_name}':", parent=self.root)
        if new_class_name:
            if new_class_name in self.classes:
                merge_class_index = self.classes.index(new_class_name)
                # Merge and remap images to the existing class
                for image, labels in self.image_labels.items():
                    updated_labels = []
                    for label in labels:
                        parts = label.split()
                        if int(parts[0]) == selected_class_index[0]:
                            parts[0] = str(merge_class_index)
                        updated_labels.append(' '.join(parts))
                    self.image_labels[image] = updated_labels
            else:
                # Rename the class
                self.classes[selected_class_index[0]] = new_class_name
                rename_class_in_labels(self.dataset_dir, selected_class_index[0], new_class_name, self.classes)
            
            update_yaml(os.path.join(self.dataset_dir, 'data.yaml'), self.classes)
            self.update_class_listbox()
            self.stats_manager.update_stats()

    def rename_image(self):
        selected_item = self.image_listbox.selection()
        if not selected_item:
            return
        old_image_name = self.image_listbox.item(selected_item, 'text')
        file_extension = os.path.splitext(old_image_name)[1]  # Get the file extension (e.g., .jpg, .png)
        new_image_base_name = simpledialog.askstring("Rename Image", f"Enter new name for image '{old_image_name}':", parent=self.root)
        if new_image_base_name and f"{new_image_base_name}{file_extension}" not in self.images:
            new_image_name = f"{new_image_base_name}{file_extension}"  # Append the file extension to the new name
            rename_file(self.dataset_dir, old_image_name, new_image_name, self.image_labels)
            self.images[self.images.index(old_image_name)] = new_image_name
            self.image_icons[new_image_name] = self.image_icons.pop(old_image_name)
            self.image_display_manager.update_image_listbox(self.class_listbox.curselection()[0])
            self.stats_manager.update_stats()

    def show_graph(self):
        show_class_annotations_graph(self.classes, self.stats)

if __name__ == "__main__":
    root = tk.Tk()
    app = YOLODatasetManager(root)
    root.mainloop()
