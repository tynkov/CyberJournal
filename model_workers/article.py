import os
from io import BytesIO

from PIL import Image

from data import db_session
from data.articles import Article
from data.users import User
from model_workers.comment import CommentModelWorker
from tools.constants import ARTICLES_IMAGES_DIR
from tools.errors import ArticleNotFoundError, ForbiddenToUserError, UserNotFoundError
from tools.get_image_path import get_image_path


class ArticleModelWorker:
    """Класс для работы с моделью Article"""
    @staticmethod
    def get_article(article_id, fields=("id", "title")):
        """Статья в JSON формате. Применяется в основном в API"""
        if not fields:  # Предотвращение ситуации, в которой вернулись бы значения всех полей модели
            fields = ("id",)
        db_sess = db_session.create_session()
        article = db_sess.query(Article).get(article_id)
        if not article:
            raise ArticleNotFoundError
        return article.to_dict(only=fields)

    @staticmethod
    def get_all_articles(fields=("id", "title"), author=None,
                         sorted_by="create_date", limit=None, offset=None):
        """Список статей в JSON формате. Применяется в основном в API"""
        if not fields:
            fields = ("id",)
        db_sess = db_session.create_session()
        articles = db_sess.query(Article)
        if author is not None:  # Фильтрация по автору
            articles = articles.filter(Article.author == author)
        if sorted_by == "create_date":  # Сортировка
            articles = articles.order_by(Article.create_date.desc())
        else:
            articles = articles.order_by(
                Article.likes_count.desc()
            ).order_by(Article.create_date.desc())
        if offset is not None:  # Пропуск заданного числа статей в начале
            articles = articles.offset(offset)
        if limit is not None:  # Ограничение на количество записей в ответе
            articles = articles.limit(limit)
        return [article.to_dict(only=fields) for article in articles]

    @staticmethod
    def new_article(article_data):
        """Создание новой статьи"""
        db_sess = db_session.create_session()
        article = Article(
            title=article_data["title"],
            content=article_data["content"],
            author=article_data["author"]
        )
        if article_data.get("image"):
            image = Image.open(BytesIO(article_data["image"].read()))
            filename = get_image_path(ARTICLES_IMAGES_DIR)
            image.save(f"{ARTICLES_IMAGES_DIR}/{filename}")
            article.image = filename
        db_sess.add(article)
        db_sess.commit()

    @staticmethod
    def edit_article(article_id, user_id, article_data):
        """Изменение статьи"""
        db_sess = db_session.create_session()
        article = db_sess.query(Article).get(article_id)
        if not article:
            raise ArticleNotFoundError
        if article.author != user_id:
            raise ForbiddenToUserError
        if article_data.get("title") is not None:
            article.title = article_data["title"]
        if article_data.get("content") is not None:
            article.content = article_data["content"]
        if article_data.get("image"):
            image = Image.open(BytesIO(article_data["image"].read()))
            filename = get_image_path(ARTICLES_IMAGES_DIR)
            image.save(f"{ARTICLES_IMAGES_DIR}/{filename}")
            if article.image:
                os.remove(f"{ARTICLES_IMAGES_DIR}/{article.image}")
            article.image = filename
        db_sess.commit()

    @staticmethod
    def delete_article(article_id, user_id):
        """Удаление статьи"""
        db_sess = db_session.create_session()
        article = db_sess.query(Article).get(article_id)
        if not article:
            raise ArticleNotFoundError
        user = db_sess.query(User).get(user_id)
        if not user:
            raise UserNotFoundError
        if not article.user_can_delete(user):
            raise ForbiddenToUserError
        if article.image:
            os.remove(f"{ARTICLES_IMAGES_DIR}/{article.image}")
        for comment in article.comments:
            CommentModelWorker.delete_comment(comment.id, comment.author)
        db_sess.delete(article)
        db_sess.commit()

    @staticmethod
    def update_likes_count(article_id, likes_delta):
        """Обновление поля likes_count"""
        db_sess = db_session.create_session()
        article = db_sess.query(Article).get(article_id)
        if not article:
            raise ArticleNotFoundError
        article.likes_count += likes_delta
        db_sess.commit()
