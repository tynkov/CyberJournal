from io import BytesIO
from flask import jsonify
from flask_restful import abort as fr_abort, Resource
from flask_login import current_user
from werkzeug.datastructures import FileStorage
from parsers import add_article_parser, get_article_parser, put_article_parser
from model_workers.article import ArticleModelWorker
from tools.errors import ArticleNotFoundError, ForbiddenToUserError, IncorrectImageError
from tools.image_to_byte_array import image_to_byte_array
from tools.hex_image_to_file_storage import hex_image_to_file_storage
from tools.constants import ARTICLES_IMAGES_DIR
from tools.check_authorization import check_authorization


class ArticleResource(Resource):
    """Ресурс для взаимодействия со статьями через API"""
    def get(self, article_id):
        """Получение статьи"""
        args = get_article_parser.parser.parse_args()
        try:
            article = ArticleModelWorker.get_article(article_id, args["get_field"])
        except ArticleNotFoundError:
            fr_abort(404, message=f"Article not found")
        else:
            if "image" in article:
                if article["image"] is not None:
                    article["image"] = image_to_byte_array(
                        f"{ARTICLES_IMAGES_DIR}/{article['image']}"
                    ).hex()
            return jsonify({"article": article})

    def put(self, article_id):
        """Редактирование статьи"""
        args = put_article_parser.parser.parse_args()
        check_authorization()
        article_data = {}
        keys = ("title", "content")
        for key in keys:
            if key in args:
                article_data[key] = args[key]
        try:
            if args.get("image") is not None:
                article_data["image"] = hex_image_to_file_storage(args["image"])
            ArticleModelWorker.edit_article(article_id, current_user.id, article_data)
        except ArticleNotFoundError:
            fr_abort(404, message=f"Article not found")
        except ForbiddenToUserError:
            fr_abort(403, message=f"Forbidden")
        except IncorrectImageError:
            fr_abort(400, message="Incorrect image")
        else:
            return jsonify({"success": "ok"})

    def delete(self, article_id):
        """Удаление статьи"""
        check_authorization()
        try:
            ArticleModelWorker.delete_article(article_id, current_user.id)
        except ArticleNotFoundError:
            fr_abort(404, message=f"Article not found")
        except ForbiddenToUserError:
            fr_abort(403, message=f"Forbidden")
        else:
            return jsonify({"success": "ok"})


class ArticlesListResource(Resource):
    """Ресурс для взаимодействия со статьями через API"""
    def post(self):
        """Добавление статьи"""
        args = add_article_parser.parser.parse_args()
        check_authorization()
        article_data = {
            "title": args["title"],
            "content": args["content"],
            "author": current_user.id
        }
        try:
            if args.get("image") is not None:
                article_data["image"] = hex_image_to_file_storage(args["image"])
            ArticleModelWorker.new_article(article_data)
        except IncorrectImageError:
            fr_abort(400, message="Incorrect image")
        return jsonify({"success": "ok"})

    def get(self):
        """Получение списка статей"""
        args = get_article_parser.range_parser.parse_args()
        articles = ArticleModelWorker.get_all_articles(args["get_field"], args["author"],
                                                       args["sorted_by"],
                                                       args["limit"], args["offset"])
        if "image" in args["get_field"]:
            for article in articles:
                if article["image"] is not None:
                    article["image"] = image_to_byte_array(
                        f"{ARTICLES_IMAGES_DIR}/{article['image']}"
                    ).hex()
        return jsonify({"articles": articles})
