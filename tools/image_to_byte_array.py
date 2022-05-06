from io import BytesIO
from PIL import Image


def image_to_byte_array(image_filename):
    """Преобразование изображения в набор байтов"""
    image = Image.open(image_filename)
    image_byte_array = BytesIO()
    image.save(image_byte_array, format="PNG")
    return image_byte_array.getvalue()
