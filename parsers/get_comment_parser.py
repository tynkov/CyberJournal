"""Парсер получения комментария/комментариев через API"""

from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument("get_field", action="append",
                    choices=["id", "author", "article_id", "text", "image", "create_date"],
                    default=["id", "author", "article_id"])

range_parser = parser.copy()
range_parser.add_argument("limit", type=int)
range_parser.add_argument("offset", type=int)

find_parser = range_parser.copy()
find_parser.add_argument("author", type=int)
find_parser.add_argument("article", type=int)
