"""Парсер авторизации через API"""

from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument("email", type=str, required=True)
parser.add_argument("password", type=str, required=True)
parser.add_argument("remember_me", type=bool, default=False)
