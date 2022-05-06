"""Парсер редактирования статьи через API"""

from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument("title", type=str)
parser.add_argument("content", type=str)
parser.add_argument("image", type=str)
