from random import choices
from string import ascii_letters, digits
import os
from io import BytesIO
from PIL import Image
from data.comments import Comment
from data.articles import Article
from data.users import User
from data import db_session
from tools.errors import CommentNotFoundError, ArticleNotFoundError, \
    ForbiddenToUserError, UserNotFoundError
from tools.get_image_path import get_image_path
from tools.constants import COMMENTS_IMAGES_DIR


class CommentModelWorker:
    """Класс для работы с моделью Comment"""
    @staticmethod
    def get_comment(comment_id, fields=("id", "author", "article_id")):
        """Комментарий в JSON формате. Применяется в основном в API"""
        if not fields:
            fields = ("id",)
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).get(comment_id)
        if not comment:
            raise CommentNotFoundError
        return comment.to_dict(only=fields)

    @staticmethod
    def get_all_comments(fields=("id", "author", "article_id"), author=None, article=None,
                         limit=None, offset=None):
        """Список комментариев в JSON формате. Применяется в основном в API"""
        if not fields:
            fields = ("id",)
        db_sess = db_session.create_session()
        comments = db_sess.query(Comment)
        if author is not None:
            comments = comments.filter(Comment.author == author)
        if article is not None:
            comments = comments.filter(Comment.article_id == article)
        if offset is not None:
            comments = comments.offset(offset)
        if limit is not None:
            comments = comments.limit(limit)
        return [comment.to_dict(only=fields) for comment in comments]

    @staticmethod
    def new_comment(comment_data):
        """Создание нового комментария"""
        db_sess = db_session.create_session()
        if not db_sess.query(Article).get(comment_data["article_id"]):
            raise ArticleNotFoundError
        comment = Comment(
            author=comment_data["author"],
            article_id=comment_data["article_id"],
            text=comment_data["text"]
        )
        if comment_data.get("image"):
            image = Image.open(BytesIO(comment_data["image"].read()))
            filename = get_image_path(COMMENTS_IMAGES_DIR)
            image.save(f"{COMMENTS_IMAGES_DIR}/{filename}")
            comment.image = filename
        db_sess.add(comment)
        db_sess.commit()

    @staticmethod
    def edit_comment(comment_id, user_id, comment_data):
        """Изменение комментария"""
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).get(comment_id)
        if not comment:
            raise CommentNotFoundError
        if comment.author != user_id:
            raise ForbiddenToUserError
        if comment_data.get("text") is not None:
            comment.text = comment_data["text"]
        if comment_data.get("image"):
            image = Image.open(BytesIO(comment_data["image"].read()))
            filename = get_image_path(COMMENTS_IMAGES_DIR)
            image.save(f"{COMMENTS_IMAGES_DIR}/{filename}")
            if comment.image:
                os.remove(f"{COMMENTS_IMAGES_DIR}/{comment.image}")
            comment.image = filename
        db_sess.commit()

    @staticmethod
    def delete_comment(comment_id, user_id):
        """Удаление комментария"""
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).get(comment_id)
        user = db_sess.query(User).get(user_id)
        if not comment:
            raise CommentNotFoundError
        if not user:
            raise UserNotFoundError
        if not comment.user_can_delete(user):
            raise ForbiddenToUserError
        if comment.image:
            os.remove(f"{COMMENTS_IMAGES_DIR}/{comment.image}")
        db_sess.delete(comment)
        db_sess.commit()
