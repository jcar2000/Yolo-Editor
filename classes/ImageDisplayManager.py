import os
import tkinter as tk
from tkinter import ttk, messagebox
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
        self.manager.filtered_images = [image for image, labels in self.manager.image_labels.items() if any(len(label.split()) > 1 and int(label.split()[0]) == selected_class for label in labels)]
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

    def open_image_viewer(self):
        selected_item = self.manager.image_listbox.selection()
        if not selected_item:
            return
        image_name = self.manager.image_listbox.item(selected_item, 'text')
        img_path = os.path.join(self.manager.dataset_dir, 'images', image_name)
        ImageViewer(self.manager, img_path, self.manager.image_labels[image_name])

class ImageViewer:
    def __init__(self, manager, img_path, labels):
        self.manager = manager
        self.img_path = img_path
        self.labels = labels.copy()  # Make a copy of the labels to ensure changes are not saved unless intended
        self.zoom_level = 1.0
        self.pan_start = None
        self.pan_offset = [0, 0]  # Track panning offset
        self.drawing_bbox = False
        self.new_bbox_start = None
        self.changes_made = False  # Track if changes have been made

        self.window = tk.Toplevel(self.manager.root)
        self.window.title("Image Viewer")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.canvas = tk.Canvas(self.window, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.img = Image.open(self.img_path)
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)

        self.canvas.bind("<Button-4>", self.zoom_in)  # For scrolling up
        self.canvas.bind("<Button-5>", self.zoom_out)  # For scrolling down
        self.canvas.bind("<ButtonPress-1>", self.on_left_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_button_release)

        self.zoom_in_button = tk.Button(self.window, text="+", command=self.zoom_in_button_click)
        self.zoom_in_button.place(relx=1.0, rely=0.0, anchor='ne')

        self.zoom_out_button = tk.Button(self.window, text="-", command=self.zoom_out_button_click)
        self.zoom_out_button.place(relx=1.0, rely=0.05, anchor='ne')

        self.draw_button = tk.Button(self.window, text="Draw BBox", command=self.start_drawing_bbox)
        self.draw_button.place(relx=1.0, rely=0.1, anchor='ne')

        self.save_button = tk.Button(self.window, text="Save", command=self.save_changes)
        self.save_button.place(relx=1.0, rely=0.15, anchor='ne')

        self.window.geometry("800x800")  # Set default window size
        self.update_image()  # Draw image and bounding boxes

    def zoom_in(self, event=None):
        self.zoom_level *= 1.1
        self.update_image()

    def zoom_out(self, event=None):
        self.zoom_level /= 1.1
        self.update_image()

    def zoom_in_button_click(self):
        self.zoom_in()

    def zoom_out_button_click(self):
        self.zoom_out()

    def on_left_button_press(self, event):
        if self.drawing_bbox:
            self.new_bbox_start = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        else:
            self.pan_start = (event.x, event.y)

    def on_mouse_drag(self, event):
        if self.drawing_bbox and self.new_bbox_start is not None:
            self.canvas.delete("new_bbox")
            x1, y1 = self.new_bbox_start
            x2, y2 = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="blue", tags="new_bbox")
        elif self.pan_start is not None:
            x_diff = event.x - self.pan_start[0]
            y_diff = event.y - self.pan_start[1]
            self.canvas.move(self.image_on_canvas, x_diff, y_diff)
            self.canvas.move("bbox", x_diff, y_diff)
            self.pan_offset[0] += x_diff
            self.pan_offset[1] += y_diff
            self.pan_start = (event.x, event.y)

    def on_left_button_release(self, event):
        if self.drawing_bbox and self.new_bbox_start is not None:
            x1, y1 = self.new_bbox_start
            x2, y2 = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            bbox = [x1, y1, x2, y2]
            self.select_class(bbox)
            self.drawing_bbox = False
            self.new_bbox_start = None

    def start_drawing_bbox(self):
        self.drawing_bbox = True

    def select_class(self, bbox=None):
        top = tk.Toplevel(self.window)
        top.title("Select Class")

        tk.Label(top, text="Choose a class:").pack(side=tk.TOP, fill=tk.X, pady=10)

        selected_class = tk.StringVar()
        combobox = ttk.Combobox(top, textvariable=selected_class)
        combobox['values'] = self.manager.classes
        combobox.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        def on_ok():
            top.destroy()
            selected_class_index = self.manager.classes.index(selected_class.get())
            if bbox:
                x1, y1, x2, y2 = bbox
                x_center = (x1 + x2 - 2 * self.pan_offset[0]) / 2 / (self.img.width * self.zoom_level)
                y_center = (y1 + y2 - 2 * self.pan_offset[1]) / 2 / (self.img.height * self.zoom_level)
                width = (x2 - x1) / (self.img.width * self.zoom_level)
                height = (y2 - y1) / (self.img.height * self.zoom_level)
                self.labels.append(f"{selected_class_index} {x_center} {y_center} {width} {height}")
                self.changes_made = True  # Mark changes as made
            self.update_image()

        ok_button = tk.Button(top, text="OK", command=on_ok)
        ok_button.pack(side=tk.TOP, pady=10)

        top.transient(self.window)
        top.grab_set()
        self.window.wait_window(top)

    def draw_bboxes(self):
        self.canvas.delete("bbox")
        img_width, img_height = self.img.size
        for index, label in enumerate(self.labels):
            parts = label.split()
            if len(parts) > 1:
                class_id, bbox = int(parts[0]), list(map(float, parts[1:]))
                if len(bbox) == 4:
                    x_center, y_center, width, height = bbox
                    x1 = (x_center - width / 2) * img_width * self.zoom_level + self.pan_offset[0]
                    y1 = (y_center - height / 2) * img_height * self.zoom_level + self.pan_offset[1]
                    x2 = (x_center + width / 2) * img_width * self.zoom_level + self.pan_offset[0]
                    y2 = (y_center + height / 2) * img_height * self.zoom_level + self.pan_offset[1]
                    if x1 < x2 and y1 < y2:  # Ensure valid coordinates
                        bbox_tag = f"bbox_{index}"
                        self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", tags=(bbox_tag, "bbox"))
                        self.canvas.create_text(x1, y1, anchor=tk.NW, text=self.manager.classes[class_id], fill="red", tags=(bbox_tag, "bbox"))
                        self.canvas.tag_bind(bbox_tag, "<Button-1>", lambda event, lbl=label: self.on_bbox_click(event, lbl))

    def on_bbox_click(self, event, label):
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="Delete", command=lambda: self.delete_bbox(label))
        menu.add_command(label="Change Class", command=lambda: self.change_bbox_class(label))
        menu.post(event.x_root, event.y_root)

    def delete_bbox(self, label):
        self.labels = [lbl for lbl in self.labels if lbl != label]
        self.changes_made = True  # Mark changes as made
        self.update_image()

    def change_bbox_class(self, label):
        top = tk.Toplevel(self.window)
        top.title("Change Class")

        tk.Label(top, text="Choose a new class:").pack(side=tk.TOP, fill=tk.X, pady=10)

        selected_class = tk.StringVar()
        combobox = ttk.Combobox(top, textvariable=selected_class)
        combobox['values'] = self.manager.classes
        combobox.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        def on_ok():
            top.destroy()
            new_class_id = self.manager.classes.index(selected_class.get())
            parts = label.split()
            new_label = f"{new_class_id} " + ' '.join(parts[1:])
            self.labels = [new_label if lbl == label else lbl for lbl in self.labels]
            self.changes_made = True  # Mark changes as made
            self.update_image()

        ok_button = tk.Button(top, text="OK", command=on_ok)
        ok_button.pack(side=tk.TOP, pady=10)

        top.transient(self.window)
        top.grab_set()
        self.window.wait_window(top)

    def update_image(self):
        width, height = self.img.size
        new_size = int(width * self.zoom_level), int(height * self.zoom_level)
        resized_img = self.img.resize(new_size, Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(resized_img)
        self.canvas.itemconfig(self.image_on_canvas, image=self.tk_img)
        self.canvas.config(scrollregion=self.canvas.bbox(self.image_on_canvas))

        # Redraw bounding boxes
        self.draw_bboxes()

    def save_changes(self):
        label_path = os.path.join(self.manager.dataset_dir, 'labels', os.path.splitext(os.path.basename(self.img_path))[0] + '.txt')
        with open(label_path, 'w') as file:
            for label in self.labels:
                file.write(label + '\n')
        self.manager.image_labels[os.path.basename(self.img_path)] = self.labels.copy()  # Save the changes to the main label list
        self.manager.image_display_manager.display_image_with_bboxes(None)  # Update main screen preview
        if self.manager.class_listbox.curselection():
            self.manager.image_display_manager.update_image_listbox(self.manager.class_listbox.curselection()[0])  # Update image list
        self.changes_made = False  # Reset changes made flag
        self.window.destroy()

    def on_close(self):
        if self.changes_made:
            if messagebox.askokcancel("Quit", "Do you want to close without saving?"):
                self.window.destroy()
        else:
            self.window.destroy()