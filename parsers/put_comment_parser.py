"""Парсер редактирования комментария через API"""

from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument("text", type=str)
parser.add_argument("image", type=str)
