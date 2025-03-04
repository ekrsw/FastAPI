FROM postgres:17.4-alpine

# テスト用の初期設定
ENV POSTGRES_DB=test_db
ENV POSTGRES_USER=test_user
ENV POSTGRES_PASSWORD=test_password

# データベースの初期化スクリプトを追加
COPY init.sql /docker-entrypoint-initdb.d/
