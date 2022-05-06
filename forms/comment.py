from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import FileField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    """Для добавления и редактирования комментариев"""
    text = TextAreaField("Текст (не более 255 символов)", validators=[DataRequired()])
    image = FileField("Картинка", validators=[FileAllowed(["png", "jpg", "jpeg"])])
    submit = SubmitField("Добавить комментарий")
