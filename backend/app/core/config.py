from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Any


class Settings(BaseSettings):
    """
    アプリケーションの設定を管理するクラスです。

    Attributes
    ----------
    database_host : str
        データベースのホスト名。環境変数 `DATABASE_HOST` から取得します。デフォルトは `"db"` です。
    database_port : int
        データベースのポート番号。環境変数 `DATABASE_PORT` から取得します。デフォルトは `5432` です。
    database_user : str
        データベースのユーザー名。環境変数 `DATABASE_USER` から取得します。デフォルトは `"admin"` です。
    database_password : str
        データベースのパスワード。環境変数 `DATABASE_PASSWORD` から取得します。デフォルトは `"my_database_password"` です。
    database_name : str
        データベースの名前。環境変数 `DATABASE_NAME` から取得します。デフォルトは `"my_database"` です。
    
    api_host : str
        APIサーバーのホスト名。環境変数 `API_HOST` から取得します。デフォルトは `"0.0.0.0"` です。
    api_port : int
        APIサーバーのポート番号。環境変数 `API_PORT` から取得します。デフォルトは `8000` です。
    
    nginx_port : int
        Nginxのポート番号。環境変数 `NGINX_PORT` から取得します。デフォルトは `8080` です。
    
    initial_admin_username : str
        初期管理者ユーザーのユーザー名。環境変数 `INITIAL_ADMIN_USERNAME` から取得します。必須項目です。
    initial_admin_password : str
        初期管理者ユーザーのパスワード。環境変数 `INITIAL_ADMIN_PASSWORD` から取得します。必須項目です。
    """

    # データベース設定
    database_host: str = Field(default="localhost", json_schema_extra={"env": "DATABASE_HOST"})
    database_port: int = Field(default=5432, json_schema_extra={"env": "DATABASE_PORT"})
    database_user: str = Field(default="my_database_user", json_schema_extra={"env": "DATABASE_USER"})
    database_password: str = Field(default="my_database_password", json_schema_extra={"env": "DATABASE_PASSWORD"})
    database_name: str = Field(default="my_database", json_schema_extra={"env": "DATABASE_NAME"})
    
    # API設定
    api_host: str = Field(default="localhost", json_schema_extra={"env": "API_HOST"})
    api_port: int = Field(default=8000, json_schema_extra={"env": "API_PORT"})

    # ADMIN設定
    admin_host: str = Field(default="localhost", json_schema_extra={"env": "ADMIN_HOST"})
    admin_port: int = Field(default=8001, json_schema_extra={"env": "ADMIN_PORT"})
    title: str = "FastAPI Admin"
    version: str = "0.1.0"
    debug: bool = False

    # JWT設定
    jwt_secret_key: str = Field(default="my_secret_key", json_schema_extra={"env": "JWT_SECRET_KEY"})
    jwt_algorithm: str = Field(default="HS256", json_schema_extra={"env": "JWT_ALGORITHM"})
    jwt_access_token_expire_minutes: int = Field(default=30, json_schema_extra={"env": "JWT_ACCESS_TOKEN_EXPIRE_MINUTES"})
    jwt_refresh_secret_key: str = Field(default="my_secret_key", json_schema_extra={"env": "JWT_REFRESH_SECRET_KEY"})
    jwt_refresh_algorithm: str = Field(default="HS256", json_schema_extra={"env": "JWT_REFRESH_ALGORITHM"})
    jwt_refresh_token_expire_minutes: int = Field(default=1440, json_schema_extra={"env": "JWT_REFRESH_TOKEN_EXPIRE_MINUTES"})
    
    # Nginx設定
    nginx_port: int = Field(default=8080, json_schema_extra={"env": "NGINX_PORT"})
    
    # 初期管理者ユーザー設定
    initial_admin_username: str = Field(default="admin", json_schema_extra={"env": "INITIAL_ADMIN_USERNAME"})
    initial_admin_password: str = Field(default="admin123", json_schema_extra={"env": "INITIAL_ADMIN_PASSWORD"})
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="",
    )


settings = Settings()
