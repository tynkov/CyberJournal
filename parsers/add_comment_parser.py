"""Парсер добавления комментария через API"""

from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument("article_id", type=int, required=True)
parser.add_argument("text", type=str, required=True)
parser.add_argument("image", type=str)
