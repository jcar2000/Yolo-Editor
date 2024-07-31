import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

def show_class_annotations_graph(classes, stats):
    new_window = tk.Toplevel()
    new_window.title("Class Annotations Graph")

    figure, ax = plt.subplots(figsize=(10, 6))
    classes = list(stats.keys())
    counts = list(stats.values())
    ax.bar(classes, counts)
    ax.set_xticks(range(len(classes)))
    ax.set_xticklabels(classes, rotation=45, ha='right')
    if counts:
        ax.set_yticks([i for i in range(0, max(counts) + 1, max(1, max(counts) // 10))])
    ax.tick_params(axis='x', which='major', labelsize=8)
    figure.tight_layout(pad=1.0)

    canvas = FigureCanvasTkAgg(figure, new_window)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()