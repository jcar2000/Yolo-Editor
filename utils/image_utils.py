from PIL import Image, ImageDraw, ImageTk

def create_thumbnail(img, size=(40, 40)):
    img.thumbnail(size, Image.LANCZOS)
    background = Image.new('RGBA', size, (255, 255, 255, 0))
    img_w, img_h = img.size
    offset = ((size[0] - img_w) // 2, (size[1] - img_h) // 2)
    background.paste(img, offset)
    return background

def draw_bbox(draw, bbox, image_size, class_id, class_name):
    x_center, y_center, width, height = bbox
    img_width, img_height = image_size

    left = max(0, (x_center - width / 2) * img_width)
    top = max(0, (y_center - height / 2) * img_height)
    right = min(img_width, (x_center + width / 2) * img_width)
    bottom = min(img_height, (y_center + height / 2) * img_height)

    if right > left and bottom > top:  # Ensure the coordinates are valid
        draw.rectangle([left, top, right, bottom], outline="red", width=2)
        draw.text((left, top), class_name, fill="red")

def convert_polygon_to_bbox(polygon):
    # Function to convert polygon points to bounding box coordinates
    xs = polygon[::2]
    ys = polygon[1::2]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    width = x_max - x_min
    height = y_max - y_min
    return [x_center, y_center, width, height]