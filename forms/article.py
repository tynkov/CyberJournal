from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, FileField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class ArticleForm(FlaskForm):
    """Для добавления и редактирования статей"""
    title = StringField("Название", validators=[DataRequired()])
    content = TextAreaField("Контент (не более 4096 символов)", validators=[DataRequired()])
    image = FileField("Картинка", validators=[FileAllowed(["png", "jpg", "jpeg"])])
    submit = SubmitField("Добавить статью")
