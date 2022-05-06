"""Парсер редактирования аккаунта пользователя через API"""

from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument("name", type=str)
parser.add_argument("surname", type=str)
parser.add_argument("nickname", type=str)
parser.add_argument("email", type=str)
parser.add_argument("new_password", type=str)
parser.add_argument("new_password_again", type=str)
parser.add_argument("description", type=str)
parser.add_argument("avatar", type=str)
parser.add_argument("password", type=str, required=True)
