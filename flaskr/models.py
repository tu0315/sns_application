# models.py

from flaskr import db, login_magager
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timedelta
from uuid import uuid4


@login_magager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(UserMixin, db.model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128), default=generate_password_hash("snsflaskapp"))
    picture_path = db.Column(db.Text)

    # 有効か無効かのフラグ
    is_activate = db.Column(db.Boolean, unique=False, default=False)
    create_at = db.Column(db.Datetime, default=datetime.now)
    update_at = db.Column(db.Datetime, default=datetime.now)

    # コンストラクタを定義
    def __init__(self, username, email):
        self.username = username
        self.email = email

    # クラスメソッド
    @classmethod
    def select_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    # パスワードが正しいかチェックする
    def validate_password(self, password):
        return check_password_hash(self.password, password)

    # ユーザー新規作成
    def create_new_user(self):
        db.session.add(self)

    # クラスメソッド
    @classmethod
    # idからユーザーを取得
    def select_user_by_id(cls, id):
        return cls.query.get(id)

    # 新しく設定したパスワードをDBに反映する
    def save_new_password(self, new_password):
        self.password = generate_password_hash(new_password)
        self.is_active = True


# パスワードリセット時に利用する
class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, index=True, server_default=str(uuid4))

    id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    expire_at = db.Column(db.Datetime, default=datetime.now)
    create_at = db.Column(db.Datetime, default=datetime.now)
    update_at = db.Column(db.Datetime, default=datetime.now)

    # コンストラクタを定義
    def __init__(self, token, user_id, expire_at):
        self.token = token
        self.user_id = user_id
        self.expire_at = expire_at

    # クラスメソッド
    @classmethod
    def publish_token(cls, user):
        # パスワード生成用のURLを生成する
        token = str(uuid4())
        new_token = cls(
            token, user.id, datetime.now() + timedelta(days=1)  # 明日までにパスワード設定してね
        )
        db.session.add(new_token)
        return token

    # クラスメソッド
    @classmethod
    # トークンに紐ついたユーザーIDを取得する
    def get_user_id_by_token(cls, token):
        now = datetime.now()
        record = (
            cls.query.filter_by(token=str(token)).filter(cls.expire_at > now).first()
        )
        return record.user_id

    # クラスメソッド
    @classmethod
    # トークン使用後、削除する
    def delete_token(cls, token):
        cls.query.filter_by(token=str(token)).delete()
