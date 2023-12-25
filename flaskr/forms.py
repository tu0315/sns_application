# ログインフォームの作成
from wtforms.form import Form
from wtforms.fields import (
    StringField,
    FileField,
    PasswordField,
    SubmitField,
    HiddenField,
)
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError

from flaskr.models import User


# ログイン用のフォーム
class LoginForm(Form):
    email = StringField("メール: ", validators=[DataRequired(), Email()])
    password = PasswordField(
        "パスワード: ",
        validators=[
            DataRequired(),
            EqualTo("comfirm_password", message="パスワードが一致しません。"),
        ],
    )
    confirm_password = PasswordField("パスワード再入力: ", validators=[DataRequired()])
    submit = SubmitField("ログイン")


# 登録用のフォーム
class RegisterForm(Form):
    email = StringField("メール: ", validators=[DataRequired(), Email("メールアドレスが間違っています。")])
    username = StringField("名前: ", validators=[DataRequired()])
    submit = SubmitField("登録")

    # 同じメールアドレスはバリデーションで弾く
    def validate_email(self, field):
        if User.select_user_by_email(field.data):
            raise ValidationError("メールアドレスは既に登録されています")


# パスワード設定用のフォーム
class ResetPasswordForm(Form):
    password = PasswordField(
        "パスワード: ",
        validators=[
            DataRequired(),
            EqualTo("confirm_password", message="パスワードが一致しません"),
        ],
    )
    confirm_password = PasswordField(
        "確認用パスワード: ",
        validators=[
            DataRequired(),
        ],
    )
    submit = SubmitField("パスワードを更新する")


def validate_password(self, field):
    if len(field.data) < 8:
        raise ValidationError("パスワードは8文字以上で設定してください")
