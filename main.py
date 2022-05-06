from flask import Flask, render_template, redirect, request, make_response, abort, session
from flask_login import LoginManager, logout_user, login_required, current_user
from flask_restful import Api

from data import db_session
from data.articles import Article
from data.comments import Comment
from data.users import User
from forms.article import ArticleForm
from forms.comment import CommentForm
from forms.user import RegisterForm, LoginForm, EditUserForm, DeleteUserForm, FindUserByNicknameForm
from model_workers.article import ArticleModelWorker
from model_workers.article_like import ArticleLikeModelWorker
from model_workers.comment import CommentModelWorker
from model_workers.user import UserModelWorker
from parsers.redirect_url import parser as redirect_url_parser
from parsers.sorted_by import parser as sorted_by_parser
from resources.article_likes import ArticleLikeResource
from resources.articles import ArticleResource, ArticlesListResource
from resources.comments import CommentResource, CommentsListResource
from resources.users import LoginResource, UserResource, UsersListResource, \
    LogoutResource, ModeratorResource
from tools.errors import PasswordMismatchError, EmailAlreadyUseError, \
    UserAlreadyExistError, IncorrectPasswordError, ArticleNotFoundError, LikeAlreadyThereError, \
    UserNotFoundError, ForbiddenToUserError, IncorrectNicknameLengthError, \
    NicknameContainsInvalidCharactersError, IncorrectPasswordLengthError, \
    NotSecurePasswordError, CommentNotFoundError, IncorrectImageError, IncorrectEmailFormatError

app = Flask(__name__)
api = Api(app)
app.config["SECRET_KEY"] = "cyberjournal"
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(f"/?sorted_by={session.get('sorted_by', 'create_date')}")


@app.route("/register", methods=["GET", "POST"])
def register():
    template_name = "register.html"
    title = "Регистрация"
    form = RegisterForm()
    sorted_by = session.get("sorted_by", "create_date")
    if form.validate_on_submit():
        try:
            UserModelWorker.new_user({
                "name": form.name.data,
                "surname": form.surname.data,
                "nickname": form.nickname.data,
                "email": form.email.data,
                "password": form.password.data,
                "password_again": form.password_again.data,
                "description": form.description.data,
                "avatar": form.avatar.data
            })
        except PasswordMismatchError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Пароли не совпадают",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except EmailAlreadyUseError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Почта уже используется",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except UserAlreadyExistError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Такой пользователь уже есть",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except IncorrectNicknameLengthError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Длина никнейма должна быть от 3 до 32 символов",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except NicknameContainsInvalidCharactersError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Никнейм может содержать только буквы латинского "
                                           "алфавита, арабские цифры и знаки подчёркивания",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except IncorrectPasswordLengthError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Длина пароля должна быть от 8 до 512 символов",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except NotSecurePasswordError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Пароль должен содержать минимум 1 непробельный символ",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except IncorrectImageError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Не удалось обработать изображение",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except IncorrectEmailFormatError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Некорректный формат email",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        return redirect("/login")
    return render_template(template_name, title=title, form=form, sorted_by=sorted_by)


@app.route("/login", methods=["GET", "POST"])
def login():
    template_name = "login.html"
    title = "Авторизация"
    form = LoginForm()
    sorted_by = session.get("sorted_by", "create_date")
    if form.validate_on_submit():
        try:
            UserModelWorker.login({
                "email": form.email.data,
                "password": form.password.data,
                "remember_me": form.remember_me.data
            })
        except UserNotFoundError:
            return render_template(template_name,
                                   form=form,
                                   message="Неправильная почта или пароль",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except IncorrectPasswordError:
            return render_template(template_name,
                                   form=form,
                                   message="Неправильная почта или пароль",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        else:
            return redirect(f"/?sorted_by={sorted_by}")
    return render_template(template_name, title=title, form=form, sorted_by=sorted_by)


@app.route("/edit_user", methods=["GET", "POST"])
@login_required
def edit_user():
    template_name = "edit_user.html"
    title = "Редактировать аккаунт"
    form = EditUserForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    sorted_by = session.get("sorted_by", "create_date")
    if request.method == "GET":
        form.name.data = user.name
        form.surname.data = user.surname
        form.nickname.data = user.nickname
        form.email.data = user.email
        form.description.data = user.description
    if form.validate_on_submit():
        try:
            UserModelWorker.edit_user(user.id, {
                "name": form.name.data,
                "surname": form.surname.data,
                "nickname": form.nickname.data,
                "email": form.email.data,
                "description": form.description.data,
                "avatar": form.avatar.data,
                "password": form.password.data,
                "new_password": form.new_password.data,
                "new_password_again": form.new_password_again.data
            })
        except IncorrectPasswordError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Неверный пароль",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except UserAlreadyExistError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Такой пользователь уже есть",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except EmailAlreadyUseError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Почта уже используется",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except PasswordMismatchError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Пароли не совпадают",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except IncorrectNicknameLengthError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Длина никнейма должна быть от 3 до 32 символов",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except NicknameContainsInvalidCharactersError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Никнейм может содержать только буквы латинского "
                                           "алфавита, арабские цифры и знаки подчёркивания",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except IncorrectPasswordLengthError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Длина пароля должна быть от 8 до 512 символов",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except NotSecurePasswordError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Пароль должен содержать минимум 1 непробельный символ",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except IncorrectImageError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Не удалось обработать изображение",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        except IncorrectEmailFormatError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Некорректный формат email",
                                   message_class="alert-danger",
                                   sorted_by=sorted_by)
        return redirect(f"/user_page/{user.id}?sorted_by={sorted_by}")
    return render_template(template_name, title=title, form=form, sorted_by=sorted_by)


@app.route("/delete_user", methods=["GET", "POST"])
@login_required
def delete_user():
    template_name = "delete_user.html"
    title = "Удалить аккаунт"
    form = DeleteUserForm()
    sorted_by = session.get("sorted_by", "create_date")
    if form.validate_on_submit():
        try:
            UserModelWorker.delete_user(current_user.id, form.password.data)
        except UserNotFoundError:
            abort(404)
        except IncorrectPasswordError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   sorted_by=sorted_by,
                                   message="Неверный пароль",
                                   message_class="alert-danger")
        else:
            return redirect(f"/page1?sorted_by={sorted_by}")
    return render_template(template_name, title=title,
                           form=form, sorted_by=sorted_by)


@app.route("/make_simple_user/<int:user_id>")
@login_required
def make_simple_user(user_id):
    try:
        UserModelWorker.make_simple_user(user_id, current_user.id)
    except UserNotFoundError:
        abort(404)
    except ForbiddenToUserError:
        abort(403)
    return redirect(f"/user_page/{user_id}")


@app.route("/make_moderator/<int:user_id>")
@login_required
def make_moderator(user_id):
    try:
        UserModelWorker.make_moderator(user_id, current_user.id)
    except UserNotFoundError:
        abort(404)
    except ForbiddenToUserError:
        abort(403)
    return redirect(f"/user_page/{user_id}")


@app.route("/user_page/<int:user_id>")
@app.route("/user_page/<int:user_id>/page<int:page_index>")
def user_page(user_id, page_index=1):
    args = sorted_by_parser.parse_args()
    session["sorted_by"] = args["sorted_by"]
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        abort(404)
    articles_count = 10
    user_articles_count = len(user.articles)
    max_page_index = max((user_articles_count // articles_count +
                          (0 if user_articles_count % articles_count == 0 else 1)), 1)
    if page_index > max_page_index:
        abort(404)
    articles = sorted(
        user.articles,
        key=(lambda x: x.create_date)
        if args["sorted_by"] == "create_date"
        else (lambda x: (x.likes_count, x.create_date)),
        reverse=True
    )[
               (page_index - 1) * articles_count:page_index * articles_count
               ]
    return render_template("user_page.html", title=f"@{user.nickname}", user=user,
                           articles_list=articles, page_index=page_index,
                           max_page_index=max_page_index, sorted_by=session["sorted_by"])


@app.route("/article", methods=["GET", "POST"])
@login_required
def add_article():
    template_name = "add_article.html"
    title = "Добавить статью"
    form = ArticleForm()
    sorted_by = session.get("sorted_by", "create_date")
    if form.validate_on_submit():
        ArticleModelWorker.new_article({
            "title": form.title.data,
            "content": form.content.data,
            "author": current_user.id,
            "image": form.image.data
        })
        return redirect(f"/user_page/{current_user.id}?sorted_by="
                        f"{sorted_by}")
    return render_template(template_name, title=title, form=form, sorted_by=sorted_by)


@app.route("/edit_article/<int:article_id>", methods=["GET", "POST"])
@login_required
def edit_article(article_id):
    template_name = "add_article.html"
    title = "Редактировать статью"
    form = ArticleForm()
    try:
        article = ArticleModelWorker.get_article(article_id, ("id", "author", "title", "content"))
    except ArticleNotFoundError:
        abort(404)
    if article["author"] != current_user.id:
        abort(403)
    if request.method == "GET":
        form.title.data = article["title"]
        form.content.data = article["content"]
    if form.validate_on_submit():
        try:
            ArticleModelWorker.edit_article(article_id, current_user.id, {
                "title": form.title.data,
                "content": form.content.data,
                "image": form.image.data
            })
        except ArticleNotFoundError:
            abort(404)
        except ForbiddenToUserError:
            abort(403)
        return redirect(f"/article/{article['id']}")
    sorted_by = session.get("sorted_by", "create_date")
    return render_template(template_name, title=title, form=form, sorted_by=sorted_by)


@app.route("/delete_article/<int:article_id>", methods=["GET", "POST"])
@login_required
def delete_article(article_id):
    try:
        ArticleModelWorker.delete_article(article_id, current_user.id)
    except ArticleNotFoundError:
        abort(404)
    except ForbiddenToUserError:
        abort(403)
    sorted_by = session.get("sorted_by", "create_date")
    return redirect(f"/?sorted_by={sorted_by}")


@app.route("/article/<int:article_id>")
def article_page(article_id):
    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)
    if not article:
        abort(404)
    sorted_by = session.get("sorted_by", "create_date")
    return render_template("article_page.html", title=article.title, article=article,
                           sorted_by=sorted_by)


@app.route("/add_comment/<int:article_id>", methods=["GET", "POST"])
@login_required
def add_comment(article_id):
    template_name = "add_comment.html"
    title = "Добавить комментарий"
    form = CommentForm()
    if form.validate_on_submit():
        try:
            CommentModelWorker.new_comment({
                    "text": form.text.data,
                    "image": form.image.data,
                    "article_id": article_id,
                    "author": current_user.id
                })
        except ArticleNotFoundError:
            abort(404)
        return redirect(f"/article/{article_id}")
    sorted_by = session.get("sorted_by", "create_date")
    return render_template(template_name, title=title, form=form, sorted_by=sorted_by)


@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
@login_required
def edit_comment(comment_id):
    template_name = "add_comment.html"
    title = "Редактировать комментарий"
    form = CommentForm()
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).get(comment_id)
    sorted_by = session.get("sorted_by", "create_date")
    if not comment:
        abort(404)
    if comment.user != current_user:
        abort(403)
    if request.method == "GET":
        form.text.data = comment.text
    if form.validate_on_submit():
        try:
            CommentModelWorker.edit_comment(comment_id, current_user.id, {
                "text": form.text.data,
                "image": form.image.data
            })
        except CommentNotFoundError:
            abort(404)
        except ForbiddenToUserError:
            abort(403)
        return redirect(f"/article/{comment.article_id}#commentCard{comment_id}")
    return render_template(template_name, title=title, form=form, sorted_by=sorted_by)


@app.route("/delete_comment/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    try:
        article_id = CommentModelWorker.get_comment(comment_id, ("article_id",))["article_id"]
        CommentModelWorker.delete_comment(comment_id, current_user.id)
    except CommentNotFoundError:
        abort(404)
    except UserNotFoundError:
        abort(404)
    except ForbiddenToUserError:
        abort(403)
    else:
        return redirect(f"/article/{article_id}")


@app.route("/like/<int:article_id>")
@login_required
def new_like(article_id):
    args = redirect_url_parser.parse_args()
    try:
        ArticleLikeModelWorker.new_like({
            "article_id": article_id,
            "user_id": current_user.id
        })
    except ArticleNotFoundError:
        abort(404)
    except LikeAlreadyThereError:
        ArticleLikeModelWorker.delete_like({
            "article_id": article_id,
            "user_id": current_user.id
        })
    return redirect(args["redirect_url"])


@app.route("/find_users", methods=["GET", "POST"])
def find_users():
    form = FindUserByNicknameForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        search_string = form.nickname_search_string.data
        session["nickname_search_string"] = search_string
        return redirect("/find_users")
    search_string = session.get("nickname_search_string", "")
    form.nickname_search_string.data = search_string
    users_list = []
    if len(search_string) >= 3:
        users = UserModelWorker.get_all_users(("id", "nickname"), 20, 0, search_string,
                                              "starts", "nickname")
        equal_nickname = UserModelWorker.get_all_users(("id", "nickname"), 1, 0,
                                                       search_string, "equals")
        if equal_nickname:
            if equal_nickname[0] in users:
                users.insert(0, users.pop(users.index(equal_nickname[0])))
            else:
                users.pop(-1)
                users.insert(0, equal_nickname[0])
        users_list = [db_sess.query(User).get(user["id"]) for user in users]
    sorted_by = session.get("sorted_by", "create_date")
    return render_template("find_users.html", title="Найти пользователя",
                           form=form, users_list=users_list, sorted_by=sorted_by)


@app.route("/")
@app.route("/page<int:page_index>")
def index(page_index=1):
    args = sorted_by_parser.parse_args()
    session["sorted_by"] = args["sorted_by"]
    db_sess = db_session.create_session()
    response = db_sess.query(Article)
    if args["sorted_by"] == "create_date":
        response = response.order_by(Article.create_date.desc())
    else:
        response = response.order_by(Article.likes_count.desc()).order_by(Article.create_date.desc())
    all_articles_count = response.count()
    articles_count = 10
    max_page_index = max((all_articles_count // articles_count +
                          (0 if all_articles_count % articles_count == 0 else 1)), 1)
    if page_index > max_page_index:
        abort(404)
    articles = response.slice((page_index - 1) * articles_count, page_index * articles_count)
    return render_template("index.html", title="Главная", articles_list=articles,
                           page_index=page_index, max_page_index=max_page_index,
                           sorted_by=session["sorted_by"])


@app.errorhandler(401)
def unauthorized(error):
    sorted_by = session.get("sorted_by", "create_date")
    return make_response(
        render_template("unauthorized.html",
                        title="Недоступно неавторизованным пользователям",
                        sorted_by=sorted_by),
        401
    )


@app.errorhandler(403)
def forbidden(error):
    sorted_by = session.get("sorted_by", "create_date")
    return make_response(
        render_template("forbidden.html", title="Запрещенно", sorted_by=sorted_by),
        403
    )


@app.errorhandler(404)
def page_not_found(error):
    sorted_by = session.get("sorted_by", "create_date")
    return make_response(
        render_template("page_not_found.html",
                        title="Страница не найдена",
                        sorted_by=sorted_by),
        404
    )


if __name__ == '__main__':
    db_session.global_init("db/articles.db")
    api.add_resource(ArticleResource, "/api/article/<int:article_id>")
    api.add_resource(ArticlesListResource, "/api/articles")
    api.add_resource(LoginResource, "/api/login")
    api.add_resource(LogoutResource, "/api/logout")
    api.add_resource(UserResource, "/api/user/<int:user_id>")
    api.add_resource(UsersListResource, "/api/users")
    api.add_resource(CommentResource, "/api/comment/<int:comment_id>")
    api.add_resource(CommentsListResource, "/api/comments")
    api.add_resource(ArticleLikeResource, "/api/like/<int:article_id>")
    api.add_resource(ModeratorResource, "/api/moderator/<int:user_id>")
    app.run()
