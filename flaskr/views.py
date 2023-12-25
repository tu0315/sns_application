from flask import Blueprint, abort, request, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from flaskr.models import User, PasswordResetToken
from flaskr import db
from os import path  # 使わないかも?
from flaskr.forms import LoginForm, RegisterForm, ResetPasswordForm

bp = Blueprint("app", __name__, url_prefix="")


@bp.route("/")
def home():
    return render_template("home.html")


@bp.route("/logout")
def logout():
    logout_user()  # ログアウト
    return redirect("app.home")


@bp.route("/login", methods=["GET", "POST"])
def login():  # ログイン画面の関数
    form = LoginForm(request.form)
    # POSTかつバリデーション突破したか
    if request.method == "POST" and form.validate():
        user = User.select_user_by_email(form.email.data)
        # ユーザーが存在してアクティブでパスワードが正しいか
        if user and user.is_active and user.validate_password(form.password.data):
            # ログインの処理
            login_user(user, remember=True)
            next = request.args.get("next")
            if not next:
                next = url_for("app.home")
            return redirect(next)
        # ユーザーが存在しない場合
        elif not user:
            flash("存在しないユーザーです")
        # アクティブでない場合
        elif not user.is_active:
            flash("無効なユーザーです。パスワードを再設定してください")
        # パスワードが間違っている場合
        elif not user.validate_password(form.password.data):
            flash("メールアドレスとパスワードの組み合わせが間違っています。")
    return render_template("login.html", form=form)


@bp.route("/register", methods=["GET", "POST"])
def register():  # 登録画面の関数
    form = RegisterForm(request.form)
    # POSTかつバリデーション突破したか
    if request.method == "POST" and form.validate():
        # ユーザーを作成
        user = User(username=form.username.data, email=form.email.data)
        with db.session.begin(subtransactions=True):
            user.create_new_user()
        db.session.commit()
        token = ""
        with db.session.begin(subtransactions=True):
            token = PasswordResetToken.publish_token(user)
        db.session.commit()
        # メールに飛ばす方がいいけど一旦これで
        print(f"パスワードリセット用URL: http://127.0.0.1.5000/reset_password/{token}")
        flash("パスワード設定用のURLを送りました。ご確認ください。")
        return redirect(url_for("app.login"))
    return render_template("register.html", form=form)


# パスワード設定用の画面を作成する
@bp.route("/reset_password/<uuid:token>", methods=["GET", "POST"])
def reset_password(token):  # パスワード設定画面の関数
    form = ResetPasswordForm(request.form)
    reset_user_id = PasswordResetToken.get_user_id_by_token(token)
    if not reset_user_id:
        abort(500)
    if request.method == "POST" and form.validate():
        password = form.password.data
        user = User.select_user_by_id(reset_user_id)
        with db.session.begin(subtransactions=True):
            user.save_new_password(password)
            PasswordResetToken.delete_token(token)
        db.session.commit()
        flash("パスワードを更新しました。")
        return redirect(url_for("app.login"))
    return render_template("reset_password.html", form=form)
