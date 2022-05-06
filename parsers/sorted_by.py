"""Парсер метода сортировки статей"""

from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument("sorted_by", location="args",
                    choices=["create_date", "likes_count"],
                    required=False, default="create_date")
