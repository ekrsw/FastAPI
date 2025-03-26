#!/bin/bash
set -e

# 環境変数からホストとポートを取得（デフォルト値を設定）
HOST=${API_HOST:-"0.0.0.0"}
PORT=${API_PORT:-"8000"}

# データベースのマイグレーションを実行
echo "Running migrations..."
cd app && alembic upgrade head && cd ..

# ユーザーappuserとして実行
exec su -s /bin/bash appuser -c "uvicorn app.main:app --host $HOST --port $PORT --workers 2"
