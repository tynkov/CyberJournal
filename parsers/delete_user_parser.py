"""Парсер удаления аккаунта пользователя через API"""

from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument("password", type=str, required=True)
