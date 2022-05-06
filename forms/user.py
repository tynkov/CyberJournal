from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, FileField, BooleanField, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField("Почта", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired()])
    surname = StringField("Фамилия", validators=[DataRequired()])
    nickname = StringField("Никнейм", validators=[DataRequired()])
    email = EmailField("Почта", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    password_again = PasswordField("Повторите пароль", validators=[DataRequired()])
    description = TextAreaField("Описание (не более 4096 символов)")
    avatar = FileField("Аватар", validators=[FileAllowed(["png", "jpg", "jpeg"])])
    submit = SubmitField("Зарегистрироваться")


class EditUserForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired()])
    surname = StringField("Фамилия", validators=[DataRequired()])
    nickname = StringField("Никнейм", validators=[DataRequired()])
    email = EmailField("Почта", validators=[DataRequired()])
    new_password = PasswordField("Новый пароль")
    new_password_again = PasswordField("Повторите пароль")
    description = TextAreaField("Описание (не более 4096 символов)")
    avatar = FileField("Аватар", validators=[FileAllowed(["png", "jpg", "jpeg"])])
    password = PasswordField("Введите текущий пароль для подтверждения", validators=[DataRequired()])
    submit = SubmitField("Подтвердить")


class DeleteUserForm(FlaskForm):
    password = PasswordField("Введите текущий пароль для подтверждения", validators=[DataRequired()])
    submit = SubmitField("Да, уверен(а)")


class FindUserByNicknameForm(FlaskForm):
    nickname_search_string = StringField("Поиск по никнейму")
    submit = SubmitField("Поиск")
