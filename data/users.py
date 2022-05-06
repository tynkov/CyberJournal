from datetime import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "users"
    serialize_rules = ("-articles", "-comments", "-likes")
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String(64))
    name = sqlalchemy.Column(sqlalchemy.String(64))
    nickname = sqlalchemy.Column(sqlalchemy.String(32), unique=True, index=True)
    email = sqlalchemy.Column(sqlalchemy.String(256), unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String(512))
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
    avatar = sqlalchemy.Column(sqlalchemy.String(256), nullable=True)  # Название файла
    description = sqlalchemy.Column(sqlalchemy.String(4096), nullable=True)
    is_moderator = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)  # Администратор наделён
    # правами модератора независимо от значения поля is_moderator
    articles = orm.relation("Article", back_populates="user", cascade="all,delete-orphan")
    comments = orm.relation("Comment", back_populates="user", cascade="all,delete-orphan")
    likes = orm.relation("ArticleLike", back_populates="user", cascade="all,delete-orphan")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"<User #{self.id}> {self.name} {self.surname} @{self.nickname} {self.email}"
