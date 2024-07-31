from PIL import Image, ImageDraw, ImageTk

def create_thumbnail(img, size=(40, 40)):
    img.thumbnail(size, Image.LANCZOS)
    background = Image.new('RGBA', size, (255, 255, 255, 0))
    img_w, img_h = img.size
    offset = ((size[0] - img_w) // 2, (size[1] - img_h) // 2)
    background.paste(img, offset)
    return background

def draw_bbox(draw, bbox, img_size, class_id, class_name):
    x_center, y_center, width, height = bbox
    x_center *= img_size[0]
    y_center *= img_size[1]
    width *= img_size[0]
    height *= img_size[1]

    left = x_center - width / 2
    right = x_center + width / 2
    top = y_center - height / 2
    bottom = y_center + height / 2

    draw.rectangle([left, top, right, bottom], outline="red", width=2)
    draw.text((left, top), class_name, fill="red")

def convert_polygon_to_bbox(polygon):
    x_coords = polygon[0::2]
    y_coords = polygon[1::2]
    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    width = x_max - x_min
    height = y_max - y_min
    return x_center, y_center, width, height