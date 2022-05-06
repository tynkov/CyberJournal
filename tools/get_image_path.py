import os
from string import ascii_letters, digits
from random import choices


def get_image_path(dir_path):
    """Генерация пути для нового изображения"""
    while True:
        filename = f"{''.join(choices(ascii_letters + digits, k=64))}.png"
        if not os.path.exists(f"{dir_path}/{filename}"):
            return filename
