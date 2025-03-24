#!/bin/bash

# エラー発生時にスクリプトを停止
set -e

# 既存のコンテナをクリーンアップ
docker-compose -f docker-compose.test.yml down

# テスト用コンテナを起動
docker-compose -f docker-compose.test.yml up -d

# コンテナの起動を待機（数秒）
sleep 5

# テストを実行
docker exec -it test_app /bin/bash -c "python -m pytest -v"

# 終了時のクリーンアップ
docker-compose -f docker-compose.test.yml down