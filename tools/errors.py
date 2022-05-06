class PasswordMismatchError(Exception):
    """Пароли не совпадают"""
    pass


class EmailAlreadyUseError(Exception):
    """Указанная электронная почта уже используется на другой странице"""
    pass


class UserAlreadyExistError(Exception):
    """Указанный никнейм уже используется на другой странице"""
    pass


class IncorrectPasswordError(Exception):
    """Неверный пароль"""
    pass


class ArticleNotFoundError(Exception):
    """Статья не найдена"""
    pass


class CommentNotFoundError(Exception):
    """Комментарий не найден"""
    pass


class LikeAlreadyThereError(Exception):
    """Лайк уже стоит на статье (при попытке поставить лайк на статью)"""
    pass


class LikeNotFoundError(Exception):
    """Лайк отсутствует (при попытке убрать лайк со статьи)"""
    pass


class UserNotFoundError(Exception):
    """Пользователь не найден"""
    pass


class UnknownFilterError(Exception):
    """Неизвестный фильтр поиска пользователя по никнейму"""
    pass


class ForbiddenToUserError(Exception):
    """Пользователю запрещено это действие"""
    pass


class IncorrectNicknameLengthError(Exception):
    """Длина никнейма не соответствует требованиям"""
    pass


class NicknameContainsInvalidCharactersError(Exception):
    """Никнейм содержит недопустимые символы"""
    pass


class IncorrectPasswordLengthError(Exception):
    """Длина пароля не соответствует требованиям"""
    pass


class NotSecurePasswordError(Exception):
    """Пароль не соответствует требованиям"""
    pass


class IncorrectImageError(Exception):
    """Ошибка при обработке изображения
    (скорее всего был передан файл, не являющийся изображением)"""
    pass


class IncorrectEmailFormatError(Exception):
    """Некорректный адрес электронной почты"""
    pass
