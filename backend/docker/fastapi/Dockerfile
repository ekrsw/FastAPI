FROM python:3.12.9-slim

# 作業ディレクトリの設定
WORKDIR /workdir

# 必要な環境変数を設定
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 依存関係のインストール
COPY ./backend/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY ./backend /workdir

# 非rootユーザーを作成して実行（セキュリティ向上）
RUN adduser --disabled-password --gecos "" appuser && \
    # ボリュームマウントポイントの所有権を変更
    mkdir -p /workdir/.pytest_cache && \
    chown -R appuser:appuser /workdir

# Uvicornでアプリケーションを起動（ワーカー数を制限）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
