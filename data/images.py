import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase

image_to_user = sqlalchemy.Table(
    "image_to_user",
    SqlAlchemyBase.metadata,
    sqlalchemy.Column("user", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")),
    sqlalchemy.Column("image", sqlalchemy.Integer, sqlalchemy.ForeignKey("images.id"))
)

image_to_article = sqlalchemy.Table(
    "image_to_article",
    SqlAlchemyBase.metadata,
    sqlalchemy.Column("article", sqlalchemy.Integer, sqlalchemy.ForeignKey("articles.id")),
    sqlalchemy.Column("image", sqlalchemy.Integer, sqlalchemy.ForeignKey("images.id"))
)

image_to_comment = sqlalchemy.Table(
    "image_to_comment",
    SqlAlchemyBase.metadata,
    sqlalchemy.Column("comment", sqlalchemy.Integer, sqlalchemy.ForeignKey("comments.id")),
    sqlalchemy.Column("image", sqlalchemy.Integer, sqlalchemy.ForeignKey("images.id"))
)


class Image(SqlAlchemyBase):
    __tablename__ = "images"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    filename = sqlalchemy.Column(sqlalchemy.String(256), nullable=False)
