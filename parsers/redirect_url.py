"""Парсер адреса для перенаправления после выполнения запроса"""

from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument("redirect_url", location="args", default="/", type=str)
