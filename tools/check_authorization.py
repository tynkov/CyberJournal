from flask_login import current_user
from flask_restful import abort


def check_authorization():
    """Проверка авторизации для API (декоратор login_required вызывает ошибку)"""
    if not current_user.is_authenticated:
        abort(401, message="Authorization required")
