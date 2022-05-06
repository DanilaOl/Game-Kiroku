from PIL import Image
import os

temp_dir = os.path.join(os.path.dirname(__file__), 'static', 'temp')


def crop_user_photo(filename):
    img = Image.open(os.path.join(temp_dir, filename))
    img_width, img_height = img.size
    left = (img_width - min(img.size)) // 2
    up = (img_height - min(img.size)) // 2
    right = (img_width + min(img.size)) // 2
    bottom = (img_height + min(img.size)) // 2
    # TODO delete original img file
    return img.crop((left, up, right, bottom)).resize((300, 300))
