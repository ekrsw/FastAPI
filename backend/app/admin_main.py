import logging

from fastapi import FastAPI
from sqladmin import Admin

from app.admin.core.auth import AdminAuth
from app.admin.views.users import UserAdminView
from app.core.config import settings
from app.db.database import Database


""" 管理画面用のmain処理 """

# loggingセットアップ
logger = logging.getLogger(__name__)


# 管理画面用のFastAPIアプリケーションの作成
app = FastAPI(
    title=settings.title,
    version=settings.version,
    debug=settings.debug or False,
)

# 管理画面用
database = Database()
async_session_factory = database.get_session_factory()
admin_manager = Admin(
    app,
    title="管理画面",
    session_maker=async_session_factory,  # SQLAlchemyのセッションを作成する関数
    # 認証用のクラスを指定
    authentication_backend=AdminAuth(secret_key=settings.jwt_secret_key),
)

# 管理画面のviewを追加する
admin_manager.add_view(UserAdminView)