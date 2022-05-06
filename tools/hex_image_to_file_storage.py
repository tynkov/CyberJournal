from io import BytesIO
from werkzeug.datastructures import FileStorage
from tools.errors import IncorrectImageError


def hex_image_to_file_storage(hex_image):
    """Преобразование hex строки в объект FileStorage для обработки при помощи PIL"""
    try:
        return FileStorage(BytesIO(bytes.fromhex(hex_image)), "qq.png")
    except Exception:
        raise IncorrectImageError
