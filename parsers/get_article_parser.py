"""Парсер получения статьи/статей через API"""

from parsers.sorted_by import parser

get_article_parser = parser.copy()
get_article_parser.add_argument("get_field", action="append",
                                choices=["id", "title", "content", "image",
                                         "author", "likes_count", "create_date"],
                                default=["id", "title"])
get_article_parser.add_argument("author", type=int)

range_parser = get_article_parser.copy()
range_parser.add_argument("limit", type=int)
range_parser.add_argument("offset", type=int)
