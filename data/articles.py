from datetime import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Article(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "articles"
    serialize_rules = ("-comments", "-likes", "-user")
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id",
                                                                         ondelete="CASCADE"))
    title = sqlalchemy.Column(sqlalchemy.String(128), nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String(4096), nullable=False)
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
    image = sqlalchemy.Column(sqlalchemy.String(256))
    likes_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    user = orm.relation("User")
    comments = orm.relation("Comment", back_populates="article", cascade="all,delete-orphan")
    likes = orm.relation("ArticleLike", back_populates="article", cascade="all,delete-orphan")

    def user_can_delete(self, user):
        if self.user == user:
            return True
        if self.user.is_admin:
            return False
        if self.user.is_moderator:
            return user.is_admin
        return user.is_admin or user.is_moderator
