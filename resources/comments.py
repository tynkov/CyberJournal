from flask import jsonify
from flask_restful import abort as fr_abort, Resource
from flask_login import current_user
from parsers import get_comment_parser, add_comment_parser, put_comment_parser
from tools.image_to_byte_array import image_to_byte_array
from tools.hex_image_to_file_storage import hex_image_to_file_storage
from tools.constants import COMMENTS_IMAGES_DIR
from tools.errors import CommentNotFoundError, ArticleNotFoundError, \
    ForbiddenToUserError, IncorrectImageError
from tools.check_authorization import check_authorization
from model_workers.comment import CommentModelWorker


class CommentResource(Resource):
    """Ресурс для взаимодействия с комментариями через API"""
    def get(self, comment_id):
        """Получение комментария"""
        args = get_comment_parser.parser.parse_args()
        try:
            comment = CommentModelWorker.get_comment(comment_id, args["get_field"])
        except CommentNotFoundError:
            fr_abort(404, message="Comment not found")
        else:
            if "image" in comment:
                if comment["image"] is not None:
                    comment["image"] = image_to_byte_array(
                        f"{COMMENTS_IMAGES_DIR}/{comment['image']}"
                    ).hex()
            return jsonify({"comment": comment})

    def put(self, comment_id):
        """Редактирование комментария"""
        args = put_comment_parser.parser.parse_args()
        check_authorization()
        comment_data = {"text": args["text"]}
        try:
            if args.get("image") is not None:
                comment_data["image"] = hex_image_to_file_storage(args["image"])
            CommentModelWorker.edit_comment(comment_id, current_user.id, comment_data)
        except CommentNotFoundError:
            fr_abort(404, message="Comment not found")
        except ForbiddenToUserError:
            fr_abort(403, message="Forbidden")
        except IncorrectImageError:
            fr_abort(400, message="Incorrect image")
        else:
            return jsonify({"success": "ok"})

    def delete(self, comment_id):
        """Удаление комментария"""
        check_authorization()
        try:
            CommentModelWorker.delete_comment(comment_id, current_user.id)
        except CommentNotFoundError:
            fr_abort(404, message="Comment not found")
        except ForbiddenToUserError:
            fr_abort(403, message="Forbidden")
        else:
            return jsonify({"success": "ok"})


class CommentsListResource(Resource):
    """Ресурс для взаимодействия с комментариями через API"""
    def get(self):
        """Получение списка комментариев"""
        args = get_comment_parser.find_parser.parse_args()
        comments = CommentModelWorker.get_all_comments(args["get_field"], args["author"],
                                                       args["article"], args["limit"],
                                                       args["offset"])
        if "image" in args["get_field"]:
            for comment in comments:
                if comment["image"] is not None:
                    comment["image"] = image_to_byte_array(
                        f"{COMMENTS_IMAGES_DIR}/{comment['image']}"
                    ).hex()
        return jsonify({"comments": comments})

    def post(self):
        """Добавление комментария"""
        args = add_comment_parser.parser.parse_args()
        check_authorization()
        comment_data = {
            "author": current_user.id,
            "article_id": args["article_id"],
            "text": args["text"]
        }
        try:
            if args["image"] is not None:
                comment_data["image"] = hex_image_to_file_storage(args["image"])
            CommentModelWorker.new_comment(comment_data)
        except ArticleNotFoundError:
            fr_abort(404, message=f"Article not found")
        except IncorrectImageError:
            fr_abort(400, message="Incorrect image")
        else:
            return jsonify({"success": "ok"})
