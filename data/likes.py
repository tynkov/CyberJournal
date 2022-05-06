import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class ArticleLike(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "articles_likes"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(
        "users.id", ondelete="CASCADE"
    ), nullable=False)
    article_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(
        "articles.id", ondelete="CASCADE"
    ), nullable=False)
    user = orm.relation("User")
    article = orm.relation("Article")
