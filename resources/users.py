from flask import jsonify
from flask_restful import abort as fr_abort, Resource
from flask_login import current_user, logout_user
from model_workers.user import UserModelWorker
from parsers import login_parser, register_parser, get_user_parser, \
    put_user_parser, delete_user_parser
from tools.errors import UserNotFoundError, IncorrectPasswordError, PasswordMismatchError, \
    UserAlreadyExistError, EmailAlreadyUseError, IncorrectNicknameLengthError, \
    NicknameContainsInvalidCharactersError, IncorrectPasswordLengthError, \
    NotSecurePasswordError, IncorrectImageError, IncorrectEmailFormatError, ForbiddenToUserError
from tools.hex_image_to_file_storage import hex_image_to_file_storage
from tools.image_to_byte_array import image_to_byte_array
from tools.constants import USERS_AVATARS_DIR
from tools.check_authorization import check_authorization


class LoginResource(Resource):
    """Ресурс для авторизации через API"""
    def post(self):
        """Авторизация"""
        args = login_parser.parser.parse_args()
        try:
            UserModelWorker.login({
                "email": args["email"],
                "password": args["password"],
                "remember_me": args["remember_me"]
            })
        except UserNotFoundError:
            fr_abort(404, message="Incorrect email or password")
        except IncorrectPasswordError:
            fr_abort(404, message="Incorrect email or password")
        else:
            return jsonify({"success": "ok"})


class LogoutResource(Resource):
    """Ресурс для выхода из аккаунта через API"""
    def post(self):
        """Выход из аккаунта"""
        check_authorization()
        logout_user()
        return jsonify({"success": "ok"})


class UserResource(Resource):
    """Ресурс для взаимодействия с пользователями через API"""
    def get(self, user_id):
        """Получение пользователя"""
        args = get_user_parser.parser.parse_args()
        if current_user.is_authenticated and current_user.id == user_id:
            fields = ("id", "name", "surname", "nickname", "email",
                      "description", "avatar", "modified_date",
                      "is_moderator", "is_admin")
        else:  # Фильтрация полей по доступу к информации для сторонних пользователей
            fields = ("id", "nickname", "description", "avatar",
                      "is_moderator", "is_admin")
        fields = tuple(field for field in fields if field in args["get_field"])
        try:
            user = UserModelWorker.get_user(user_id, fields)
        except UserNotFoundError:
            fr_abort(404, message="User not found")
        else:
            if "avatar" in fields:
                if user["avatar"] is not None:
                    user["avatar"] = image_to_byte_array(
                        f"{USERS_AVATARS_DIR}/{user['avatar']}"
                    ).hex()
            return jsonify({"user": user})

    def put(self, user_id):
        """Редактирование аккаунта"""
        args = put_user_parser.parser.parse_args()
        check_authorization()
        if current_user.id != user_id:
            fr_abort(403, message=f"Forbidden")
        user_data = {
                "name": args["name"],
                "surname": args["surname"],
                "nickname": args["nickname"],
                "email": args["email"],
                "new_password": args["new_password"],
                "new_password_again": args["new_password_again"],
                "description": args["description"],
                "password": args["password"]
            }
        try:
            if args.get("avatar") is not None:
                user_data["avatar"] = hex_image_to_file_storage(args["avatar"])
            UserModelWorker.edit_user(user_id, user_data)
        except IncorrectPasswordError:
            fr_abort(400, message="Incorrect password")
        except PasswordMismatchError:
            fr_abort(400, message="Password mismatch")
        except UserAlreadyExistError:
            fr_abort(400, message=f"User already exist")
        except EmailAlreadyUseError:
            fr_abort(400, message=f"Email already use")
        except IncorrectNicknameLengthError:
            fr_abort(400, message="Length of the nickname must be between 3 and 32")
        except NicknameContainsInvalidCharactersError:
            fr_abort(400, message="Nickname contains invalid characters")
        except IncorrectPasswordLengthError:
            fr_abort(400, message="Length of password must be between 8 and 512")
        except NotSecurePasswordError:
            fr_abort(400, message="Password must contain at least 1 non-whitespace character")
        except IncorrectImageError:
            fr_abort(400, message="Incorrect image")
        except IncorrectEmailFormatError:
            fr_abort(400, message="Incorrect email format")
        else:
            return jsonify({"success": "ok"})

    def delete(self, user_id):
        """Удаление аккаунта"""
        args = delete_user_parser.parser.parse_args()
        check_authorization()
        if current_user.id != user_id:
            fr_abort(403, message=f"Forbidden")
        try:
            UserModelWorker.delete_user(user_id, args["password"])
        except UserNotFoundError:
            fr_abort(404, message=f"User not found")
        except IncorrectPasswordError:
            fr_abort(400, message="Incorrect password")
        return jsonify({"success": "ok"})


class UsersListResource(Resource):
    """Ресурс для взаимодействия с пользователями через API"""
    def post(self):
        """Регистрация пользователя"""
        args = register_parser.parser.parse_args()
        user_data = {
            "name": args["name"],
            "surname": args["surname"],
            "nickname": args["nickname"],
            "email": args["email"],
            "password": args["password"],
            "password_again": args["password_again"],
            "description": args["description"]
        }
        try:
            if args.get("avatar") is not None:
                user_data["avatar"] = hex_image_to_file_storage(args["avatar"])
            UserModelWorker.new_user(user_data)
        except PasswordMismatchError:
            fr_abort(400, message="Password mismatch")
        except UserAlreadyExistError:
            fr_abort(400, message="User already exist")
        except EmailAlreadyUseError:
            fr_abort(400, message="Email already use")
        except IncorrectNicknameLengthError:
            fr_abort(400, message="Length of the nickname must be between 3 and 32")
        except NicknameContainsInvalidCharactersError:
            fr_abort(400, message="Nickname contains invalid characters")
        except IncorrectPasswordLengthError:
            fr_abort(400, message="Length of password must be between 8 and 512")
        except NotSecurePasswordError:
            fr_abort(400, message="Password must contain at least 1 non-whitespace character")
        except IncorrectImageError:
            fr_abort(400, message="Incorrect image")
        except IncorrectEmailFormatError:
            fr_abort(400, message="Incorrect email format")
        else:
            return jsonify({"success": "ok"})

    def get(self):
        """Получение списка пользователей"""
        args = get_user_parser.find_parser.parse_args()
        fields = tuple(field for field in ("id", "nickname", "description",
                                           "avatar", "is_moderator", "is_admin")
                       if field in args["get_field"])
        users = UserModelWorker.get_all_users(fields,
                                              args["limit"], args["offset"],
                                              args["nickname_search_string"],
                                              args["nickname_filter"], args["sorted_by"])
        if "avatar" in fields:
            for user in users:
                if user["avatar"] is not None:
                    user["avatar"] = image_to_byte_array(
                        f"{USERS_AVATARS_DIR}/{user['avatar']}"
                    ).hex()
        return jsonify({"users": users})


class ModeratorResource(Resource):
    def post(self, user_id):
        check_authorization()
        try:
            UserModelWorker.make_moderator(user_id, current_user.id)
        except UserNotFoundError:
            fr_abort(404, message="User not found")
        except ForbiddenToUserError:
            fr_abort(403, message="Forbidden")
        else:
            return jsonify({"success": "ok"})

    def delete(self, user_id):
        check_authorization()
        try:
            UserModelWorker.make_simple_user(user_id, current_user.id)
        except UserNotFoundError:
            fr_abort(404, message="User not found")
        except ForbiddenToUserError:
            fr_abort(403, message="Forbidden")
        else:
            return jsonify({"success": "ok"})
