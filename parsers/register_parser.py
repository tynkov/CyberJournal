"""Парсер регистрации пользователя через API"""

from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument("name", type=str, required=True)
parser.add_argument("surname", type=str, required=True)
parser.add_argument("nickname", type=str, required=True)
parser.add_argument("email", type=str, required=True)
parser.add_argument("password", type=str, required=True)
parser.add_argument("password_again", type=str, required=True)
parser.add_argument("description", type=str)
parser.add_argument("avatar", type=str)
