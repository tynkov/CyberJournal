from flask import jsonify
from flask_restful import abort as fr_abort, Resource
from flask_login import current_user
from model_workers.article_like import ArticleLikeModelWorker
from tools.errors import ArticleNotFoundError, LikeNotFoundError, LikeAlreadyThereError
from tools.check_authorization import check_authorization


class ArticleLikeResource(Resource):
    """Ресурс для взаимодействия с лайками через API"""
    def get(self, article_id):
        """Проверить, поставил ли пользователь лайк под записью"""
        check_authorization()
        return jsonify({"like_exist": ArticleLikeModelWorker.like_exist({
            "article_id": article_id,
            "user_id": current_user.id
        })})

    def post(self, article_id):
        """Поставить лайк"""
        check_authorization()
        try:
            ArticleLikeModelWorker.new_like({
                "article_id": article_id,
                "user_id": current_user.id
            })
        except ArticleNotFoundError:
            fr_abort(404, message="Article not found")
        except LikeAlreadyThereError:
            fr_abort(400, message="Like already there")
        else:
            return jsonify({"success": "ok"})

    def delete(self, article_id):
        """Убрать лайк"""
        check_authorization()
        try:
            ArticleLikeModelWorker.delete_like({
                "article_id": article_id,
                "user_id": current_user.id
            })
        except ArticleNotFoundError:
            fr_abort(404, message="Article not found")
        except LikeNotFoundError:
            fr_abort(404, message="Like not found")
        else:
            return jsonify({"success": "ok"})
